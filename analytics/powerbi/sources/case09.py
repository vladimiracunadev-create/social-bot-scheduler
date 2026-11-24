"""Adaptador del caso 09: DuckDB embebida detrás del gateway FastAPI.

Dos transportes, probados en este orden:

1. **fichero local** — el gateway monta su base de datos en
   ``cases/09-python-to-gateway/dest/data/case09.duckdb``, así que el anfitrión
   puede abrirla directamente con ``read_only=True`` cuando el paquete
   ``duckdb`` es importable. No hace falta Docker, y es lo que usan las pruebas
   unitarias.
2. **docker exec** — en caso contrario, el cliente que ya viene dentro de la
   imagen del gateway lee el mismo fichero desde ``/app/data``.

``read_only=True`` no es decorativo: DuckDB rechaza escribir a través de una
conexión así, de modo que una exportación no puede corromper el estado
transaccional del caso.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from analytics.powerbi.contracts import DatasetContract
from analytics.powerbi.sources.base import CaseSource, coerce_int, to_iso
from analytics.powerbi.transport import (
    DockerExecTransport,
    TransportError,
    assert_read_only,
)

CONTAINER = "social-bot-dest-gateway-09"
HOST_DB_PATH = Path("cases/09-python-to-gateway/dest/data/case09.duckdb")
CONTAINER_DB_PATH = "/app/data/case09.duckdb"

# Una lectura por contrato. El orden es determinista para que una exportación
# paginada no duplique ni se salte filas entre páginas.
QUERIES: dict[str, str] = {
    "case09_requests": """
        SELECT request_id, channel, action, owner, request_limit, status,
               created_at
        FROM integration_requests
        ORDER BY created_at ASC, request_id ASC
    """,
    "case09_provider_calls": """
        SELECT call_id, request_id, provider, mode, endpoint, http_status,
               latency_ms, COALESCE(error_code, '') AS error_code,
               COALESCE(error_message, '') AS error_message, created_at
        FROM provider_calls
        ORDER BY created_at ASC, call_id ASC
    """,
    "case09_repo_snapshots": """
        SELECT request_id, repo, stars, COALESCE(language, '') AS language, url
        FROM repo_snapshots
        ORDER BY request_id ASC, repo ASC
    """,
}

# Script que ejecuta dentro del contenedor el transporte Docker. Se pasa como
# argumento literal, y el SQL viaja en argv: nunca se interpola.
_REMOTE_SCRIPT = (
    "import duckdb, json, sys\n"
    "con = duckdb.connect(sys.argv[1], read_only=True)\n"
    "cur = con.execute(sys.argv[2])\n"
    "cols = [d[0] for d in cur.description]\n"
    "for row in cur.fetchall():\n"
    "    print(json.dumps(dict(zip(cols, row)), default=str))\n"
)

_INT_COLUMNS = {"request_limit", "http_status", "latency_ms", "stars"}
_TS_COLUMNS = {"created_at"}


def _paginate(sql: str, limit: int, offset: int) -> str:
    """Añade LIMIT/OFFSET validados a una consulta de lectura."""
    statement = assert_read_only(sql)
    page_limit = int(limit)
    page_offset = int(offset)
    if page_limit <= 0 or page_offset < 0:
        raise ValueError("limit debe ser positivo y offset no negativo")
    return f"{statement} LIMIT {page_limit} OFFSET {page_offset}"


def _normalise(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.items():
        if key in _INT_COLUMNS:
            out[key] = coerce_int(value, 0)
        elif key in _TS_COLUMNS:
            out[key] = to_iso(value)
        else:
            out[key] = "" if value is None else value
    return out


class Case09DuckDBSource(CaseSource):
    """Adaptador DuckDB de solo lectura para el caso 09."""

    case_id = "09"
    engine = "duckdb"

    def __init__(
        self,
        db_path: Path | str = HOST_DB_PATH,
        transport: DockerExecTransport | None = None,
        retries: int = 5,
    ) -> None:
        self.db_path = Path(db_path)
        self.transport = transport or DockerExecTransport(CONTAINER)
        self.retries = retries
        # Se pone a True en cuanto una lectura local falla por una razon
        # estructural (p.ej. el contenedor escribio el fichero con una version
        # de DuckDB mas nueva que la del anfitrion): a partir de ahi se usa el
        # cliente del contenedor y no se reintenta el fichero local.
        self._force_container = False

    # -- selección de transporte ---------------------------------------------

    def _duckdb_module(self) -> Any | None:
        try:
            import duckdb
        except ImportError:
            return None
        return duckdb

    def _can_read_local(self) -> bool:
        if self._force_container:
            return False
        return self.db_path.is_file() and self._duckdb_module() is not None

    def available(self) -> bool:
        return self._can_read_local() or self.transport.available()

    def describe(self) -> str:
        if self._can_read_local():
            return f"fichero local DuckDB ({self.db_path}, read_only)"
        return f"DuckDB dentro del contenedor {self.transport.container} (read_only)"

    # -- lecturas ------------------------------------------------------------

    def fetch_page(
        self, contract: DatasetContract, limit: int, offset: int
    ) -> list[dict[str, Any]]:
        try:
            sql = QUERIES[contract.name]
        except KeyError as exc:
            raise KeyError(
                f"el caso 09 no puede servir el dataset {contract.name!r}"
            ) from exc
        statement = _paginate(sql, limit, offset)

        if self._can_read_local():
            try:
                rows = self._read_local(statement)
            except TransportError:
                # El fichero esta ahi pero esta libreria no puede leerlo. Si el
                # contenedor esta en marcha, su propio cliente si puede.
                if not self.transport.available():
                    raise
                self._force_container = True
                rows = self._read_in_container(statement)
        else:
            rows = self._read_in_container(statement)
        return [_normalise(row) for row in rows]

    def _read_local(self, statement: str) -> list[dict[str, Any]]:
        duckdb = self._duckdb_module()
        assert duckdb is not None  # garantizado por _can_read_local
        last_error: Exception | None = None
        # El gateway abre una conexión de escritura corta por cada petición HTTP;
        # DuckDB bloquea el fichero durante esas ventanas, así que la lectura se
        # reintenta en vez de hacer fallar una exportación por lo demás sana.
        for attempt in range(self.retries):
            try:
                connection = duckdb.connect(str(self.db_path), read_only=True)
            except Exception as exc:  # duckdb.IOException y similares
                last_error = exc
                time.sleep(0.4 * (attempt + 1))
                continue
            try:
                cursor = connection.execute(statement)
                columns = [desc[0] for desc in cursor.description or []]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            finally:
                connection.close()
        raise TransportError(
            f"no se pudo abrir {self.db_path} en solo lectura tras "
            f"{self.retries} intentos: {last_error}"
        )

    def _read_in_container(self, statement: str) -> list[dict[str, Any]]:
        stdout = self.transport.exec(
            ["python", "-c", _REMOTE_SCRIPT, CONTAINER_DB_PATH, statement]
        )
        rows: list[dict[str, Any]] = []
        for line in stdout.splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        return rows
