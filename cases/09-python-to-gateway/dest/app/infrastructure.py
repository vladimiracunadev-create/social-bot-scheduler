from __future__ import annotations

import threading
from pathlib import Path

import duckdb

from app.domain import IntegrationRequest, ProviderCall, RepoSnapshot
from app.repositories import IntegrationRequestRepository, ProviderCallRepository


class DuckDBDatabase:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.migrate()

    def connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.db_path)

    def migrate(self) -> None:
        statements = [
            """
            CREATE TABLE IF NOT EXISTS integration_requests (
                request_id TEXT PRIMARY KEY,
                fingerprint TEXT UNIQUE NOT NULL,
                channel TEXT NOT NULL,
                action TEXT NOT NULL,
                owner TEXT NOT NULL,
                request_limit INTEGER NOT NULL,
                status TEXT NOT NULL,
                api_key_prefix TEXT,
                api_key_hash TEXT,
                created_at TIMESTAMP NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS provider_calls (
                call_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                mode TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                http_status INTEGER NOT NULL,
                latency_ms INTEGER NOT NULL,
                rate_limit_remaining TEXT,
                error_code TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS repo_snapshots (
                request_id TEXT NOT NULL,
                repo TEXT NOT NULL,
                stars INTEGER NOT NULL,
                language TEXT,
                url TEXT NOT NULL
            )
            """,
            "CREATE INDEX IF NOT EXISTS idx_integration_requests_created_at ON integration_requests(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_integration_requests_status ON integration_requests(status)",
            "CREATE INDEX IF NOT EXISTS idx_provider_calls_request_id ON provider_calls(request_id)",
            "CREATE INDEX IF NOT EXISTS idx_repo_snapshots_request_id ON repo_snapshots(request_id)",
        ]

        with self._lock:
            conn = self.connect()
            try:
                for statement in statements:
                    conn.execute(statement)
            finally:
                conn.close()


class DuckDBIntegrationRequestRepository(IntegrationRequestRepository):
    def __init__(self, database: DuckDBDatabase) -> None:
        self.database = database

    def save(self, request: IntegrationRequest) -> None:
        with self.database._lock:
            conn = self.database.connect()
            try:
                conn.execute(
                    """
                    INSERT INTO integration_requests (
                        request_id, fingerprint, channel, action, owner, request_limit,
                        status, api_key_prefix, api_key_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        request.request_id.value,
                        request.fingerprint.value,
                        request.channel.value,
                        request.action.value,
                        request.owner.value,
                        request.limit.value,
                        request.status,
                        request.api_key_prefix,
                        request.api_key_hash,
                        request.created_at,
                    ],
                )
            finally:
                conn.close()

    def update_status(self, fingerprint: str, status: str) -> None:
        with self.database._lock:
            conn = self.database.connect()
            try:
                conn.execute(
                    "UPDATE integration_requests SET status = ? WHERE fingerprint = ?",
                    [status, fingerprint],
                )
            finally:
                conn.close()

    def get_by_fingerprint(self, fingerprint: str) -> dict | None:
        conn = self.database.connect()
        try:
            row = conn.execute(
                """
                SELECT request_id, fingerprint, channel, action, owner, request_limit, status,
                       api_key_prefix, api_key_hash, created_at
                FROM integration_requests
                WHERE fingerprint = ?
                """,
                [fingerprint],
            ).fetchone()
        finally:
            conn.close()

        if not row:
            return None

        keys = [
            "request_id",
            "fingerprint",
            "channel",
            "action",
            "owner",
            "limit",
            "status",
            "api_key_prefix",
            "api_key_hash",
            "created_at",
        ]
        return dict(zip(keys, row))

    def latest_requests(self, limit: int = 20) -> list[dict]:
        conn = self.database.connect()
        try:
            rows = conn.execute(
                """
                SELECT ir.request_id, ir.action, ir.owner, ir.request_limit, ir.status,
                       pc.http_status, pc.latency_ms, pc.mode, ir.api_key_prefix, ir.created_at
                FROM integration_requests ir
                LEFT JOIN (
                    SELECT *
                    FROM provider_calls
                    QUALIFY ROW_NUMBER() OVER (PARTITION BY request_id ORDER BY created_at DESC) = 1
                ) pc ON pc.request_id = ir.request_id
                ORDER BY ir.created_at DESC
                LIMIT ?
                """,
                [limit],
            ).fetchall()
        finally:
            conn.close()

        keys = [
            "request_id",
            "action",
            "owner",
            "limit",
            "status",
            "http_status",
            "latency_ms",
            "mode",
            "api_key_prefix",
            "created_at",
        ]
        return [dict(zip(keys, row)) for row in rows]

    def latest_errors(self, limit: int = 20) -> list[dict]:
        conn = self.database.connect()
        try:
            rows = conn.execute(
                """
                SELECT ir.request_id, ir.status, pc.provider, pc.http_status, pc.error_code,
                       pc.error_message, ir.created_at
                FROM integration_requests ir
                LEFT JOIN provider_calls pc ON pc.request_id = ir.request_id
                WHERE ir.status = 'FAILED'
                ORDER BY ir.created_at DESC
                LIMIT ?
                """,
                [limit],
            ).fetchall()
        finally:
            conn.close()

        keys = [
            "request_id",
            "status",
            "provider",
            "http_status",
            "error_code",
            "error_message",
            "created_at",
        ]
        return [dict(zip(keys, row)) for row in rows]

    def stats(self) -> dict:
        conn = self.database.connect()
        try:
            summary = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_requests,
                    SUM(CASE WHEN status = 'SUCCEEDED' THEN 1 ELSE 0 END) AS succeeded,
                    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed
                FROM integration_requests
                """
            ).fetchone()
        finally:
            conn.close()

        return {
            "total_requests": int(summary[0] or 0),
            "succeeded": int(summary[1] or 0),
            "failed": int(summary[2] or 0),
        }


class DuckDBProviderCallRepository(ProviderCallRepository):
    def __init__(self, database: DuckDBDatabase) -> None:
        self.database = database

    def save_call(self, provider_call: ProviderCall) -> None:
        with self.database._lock:
            conn = self.database.connect()
            try:
                conn.execute(
                    """
                    INSERT INTO provider_calls (
                        call_id, request_id, provider, mode, endpoint, http_status,
                        latency_ms, rate_limit_remaining, error_code, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        provider_call.call_id,
                        provider_call.request_id,
                        provider_call.provider,
                        provider_call.mode.value,
                        provider_call.endpoint,
                        provider_call.http_status.value,
                        provider_call.latency_ms.value,
                        provider_call.rate_limit_remaining,
                        provider_call.error_code,
                        provider_call.error_message,
                    ],
                )
            finally:
                conn.close()

    def save_snapshots(self, snapshots: list[RepoSnapshot]) -> None:
        if not snapshots:
            return

        with self.database._lock:
            conn = self.database.connect()
            try:
                conn.executemany(
                    "INSERT INTO repo_snapshots (request_id, repo, stars, language, url) VALUES (?, ?, ?, ?, ?)",
                    [
                        [
                            snapshot.request_id,
                            snapshot.repo,
                            snapshot.stars,
                            snapshot.language,
                            snapshot.url,
                        ]
                        for snapshot in snapshots
                    ],
                )
            finally:
                conn.close()

    def top_repos(self, limit: int = 10) -> list[dict]:
        conn = self.database.connect()
        try:
            rows = conn.execute(
                """
                SELECT repo, MAX(stars) AS stars, any_value(language) AS language, any_value(url) AS url
                FROM repo_snapshots
                GROUP BY repo
                ORDER BY stars DESC, repo ASC
                LIMIT ?
                """,
                [limit],
            ).fetchall()
        finally:
            conn.close()

        return [
            {"repo": row[0], "stars": row[1], "language": row[2], "url": row[3]}
            for row in rows
        ]
