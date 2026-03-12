from __future__ import annotations

import html
import os
from pathlib import Path

import requests
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.infrastructure import DuckDBDatabase, DuckDBIntegrationRequestRepository, DuckDBProviderCallRepository
from app.use_cases import create_use_cases


DATA_DIR = Path("/app/data")
LOG_DIR = Path("/app/logs")
DB_PATH = DATA_DIR / "case09.duckdb"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

database = DuckDBDatabase(str(DB_PATH))
integration_repo = DuckDBIntegrationRequestRepository(database)
provider_repo = DuckDBProviderCallRepository(database)
handle_request_use_case, handle_failure_use_case = create_use_cases(integration_repo, provider_repo)

app = FastAPI(
    title="Case 09 Integration Gateway",
    version="1.0.0",
    description="FastAPI gateway with DuckDB persistence and a server-rendered dashboard.",
)


class RequestParamsDTO(BaseModel):
    owner: str
    limit: int = Field(ge=1, le=50)


class IntegrationRequestDTO(BaseModel):
    id: str
    channel: str
    action: str
    params: RequestParamsDTO
    ts: str


def validate_api_key(api_key: str | None) -> str:
    expected = os.getenv("INTEGRATION_API_KEY", "SocialBotLocalKey2026!")
    if not api_key or api_key != expected:
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key")
    return api_key


def render_table_rows(rows: list[dict], columns: list[str]) -> str:
    if not rows:
        return "<tr><td colspan='%s'>No data yet</td></tr>" % len(columns)
    rendered = []
    for row in rows:
        cells = "".join(f"<td>{html.escape(str(row.get(column, '')))}</td>" for column in columns)
        rendered.append(f"<tr>{cells}</tr>")
    return "".join(rendered)


@app.post("/webhook")
def webhook(payload: IntegrationRequestDTO, x_api_key: str | None = Header(default=None)):
    api_key = validate_api_key(x_api_key)
    try:
        return handle_request_use_case.execute(payload.model_dump(), api_key)
    except requests.HTTPError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"GitHub provider call failed with {exc.response.status_code}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/errors")
def errors(payload: dict):
    return handle_failure_use_case.execute(payload)


@app.get("/api/health")
def health() -> dict:
    stats = integration_repo.stats()
    return {"ok": True, "db_path": str(DB_PATH), "stats": stats, "provider_mode": "real" if os.getenv("GITHUB_TOKEN") else "public"}


@app.get("/api/requests")
def requests_list() -> list[dict]:
    return integration_repo.latest_requests()


@app.get("/api/stats")
def stats() -> dict:
    data = integration_repo.stats()
    data["top_repos"] = provider_repo.top_repos(10)
    return data


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    requests_rows = integration_repo.latest_requests(20)
    error_rows = integration_repo.latest_errors(20)
    top_repo_rows = provider_repo.top_repos(10)
    stats = integration_repo.stats()

    request_columns = ["request_id", "action", "owner", "limit", "status", "http_status", "latency_ms", "mode", "api_key_prefix", "created_at"]
    error_columns = ["request_id", "status", "provider", "http_status", "error_code", "error_message", "created_at"]
    top_columns = ["repo", "stars", "language", "url"]

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Case 09 Gateway Dashboard</title>
      <style>
        :root {{ --border: #334155; --text: #e5e7eb; --muted: #94a3b8; }}
        body {{ margin: 0; font-family: Arial, sans-serif; background: linear-gradient(135deg, #020617, #0f172a 55%, #1e293b); color: var(--text); }}
        .wrap {{ max-width: 1280px; margin: 0 auto; padding: 24px; }}
        .hero {{ display: grid; gap: 12px; margin-bottom: 24px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .card {{ background: rgba(15, 23, 42, 0.82); border: 1px solid var(--border); border-radius: 16px; padding: 16px; box-shadow: 0 14px 30px rgba(0, 0, 0, 0.24); }}
        .metric {{ font-size: 30px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        th, td {{ padding: 10px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }}
        th {{ color: var(--muted); background: rgba(30, 41, 59, 0.65); }}
        .table-wrap {{ overflow-x: auto; max-height: 420px; }}
        .muted {{ color: var(--muted); }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <section class="hero">
          <h1>Case 09: Python -> n8n -> FastAPI Gateway</h1>
          <div class="muted">DuckDB embebida en /app/data/case09.duckdb, auth por X-API-Key, proveedor GitHub API.</div>
        </section>
        <section class="grid">
          <div class="card"><div class="muted">Total requests</div><div class="metric">{stats['total_requests']}</div></div>
          <div class="card"><div class="muted">Succeeded</div><div class="metric">{stats['succeeded']}</div></div>
          <div class="card"><div class="muted">Failed</div><div class="metric">{stats['failed']}</div></div>
          <div class="card"><div class="muted">Provider mode</div><div class="metric">{'real' if os.getenv('GITHUB_TOKEN') else 'public'}</div></div>
        </section>
        <section class="card">
          <h2>Ultimos 20 requests</h2>
          <div class="table-wrap"><table><thead><tr><th>request_id</th><th>action</th><th>owner</th><th>limit</th><th>status</th><th>http_status</th><th>latency_ms</th><th>mode</th><th>api_key_prefix</th><th>created_at</th></tr></thead><tbody>{render_table_rows(requests_rows, request_columns)}</tbody></table></div>
        </section>
        <section class="card" style="margin-top:16px;">
          <h2>Errores ultimos 20</h2>
          <div class="table-wrap"><table><thead><tr><th>request_id</th><th>status</th><th>provider</th><th>http_status</th><th>error_code</th><th>error_message</th><th>created_at</th></tr></thead><tbody>{render_table_rows(error_rows, error_columns)}</tbody></table></div>
        </section>
        <section class="card" style="margin-top:16px;">
          <h2>Top repos por stars</h2>
          <div class="table-wrap"><table><thead><tr><th>repo</th><th>stars</th><th>language</th><th>url</th></tr></thead><tbody>{render_table_rows(top_repo_rows, top_columns)}</tbody></table></div>
        </section>
      </div>
    </body>
    </html>
    """
