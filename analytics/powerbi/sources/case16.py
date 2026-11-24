"""Adaptador del caso 16: hypertable de TimescaleDB detrás de Hasura.

El transporte por defecto ejecuta ``psql`` dentro de
``social-bot-db-timescaledb-16`` con ``--csv``, de modo que no se añade ningún
driver de PostgreSQL al repositorio. La sesión queda fijada en solo lectura a
través de ``PGOPTIONS`` (``default_transaction_read_only``), lo que significa
que el propio servidor rechaza una escritura incluso si una consulta futura se
colara por delante de :func:`assert_read_only`.

Este es además el caso cuyo motor Power BI puede consultar *en vivo*:
TimescaleDB es PostgreSQL, así que el conector nativo de PostgreSQL funciona
contra él en cuanto se publica el puerto. Ver ``compose.powerbi.yml`` y el
documento de integración.
"""

from __future__ import annotations

import csv
import io
import os
from typing import Any

from analytics.powerbi.contracts import DatasetContract
from analytics.powerbi.redaction import MAX_TEXT_LENGTH
from analytics.powerbi.sources.base import CaseSource, to_iso
from analytics.powerbi.transport import DockerExecTransport, assert_read_only

CONTAINER = "social-bot-db-timescaledb-16"
DEFAULT_DB = "social_bot"
DEFAULT_USER = "postgres"
DEFAULT_PASSWORD = "change-me-case16-local"

QUERIES: dict[str, str] = {
    "case16_posts": f"""
        SELECT id,
               channel,
               left(text, {MAX_TEXT_LENGTH}) AS text,
               scheduled_at,
               created_at
        FROM social_posts
        ORDER BY created_at ASC, id ASC
    """,
}


class Case16TimescaleSource(CaseSource):
    """Adaptador TimescaleDB de solo lectura para el caso 16."""

    case_id = "16"
    engine = "timescaledb"

    def __init__(
        self,
        transport: DockerExecTransport | None = None,
        database: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self.transport = transport or DockerExecTransport(CONTAINER)
        self.database = database or os.getenv("CASE16_DB_NAME", DEFAULT_DB)
        self.user = user or os.getenv("CASE16_DB_USER", DEFAULT_USER)
        self.password = password or os.getenv("CASE16_DB_PASSWORD", DEFAULT_PASSWORD)

    def available(self) -> bool:
        return self.transport.available()

    def describe(self) -> str:
        return (
            f"psql dentro del contenedor {self.transport.container} "
            "(default_transaction_read_only=on)"
        )

    def fetch_page(
        self, contract: DatasetContract, limit: int, offset: int
    ) -> list[dict[str, Any]]:
        try:
            sql = QUERIES[contract.name]
        except KeyError as exc:
            raise KeyError(
                f"el caso 16 no puede servir el dataset {contract.name!r}"
            ) from exc

        statement = assert_read_only(sql)
        page_limit, page_offset = int(limit), int(offset)
        if page_limit <= 0 or page_offset < 0:
            raise ValueError("limit debe ser positivo y offset no negativo")
        query = f"{statement} LIMIT {page_limit} OFFSET {page_offset}"

        stdout = self.transport.exec(
            [
                "psql",
                "--no-psqlrc",
                "--csv",
                "--quiet",
                "-v",
                "ON_ERROR_STOP=1",
                "-U",
                self.user,
                "-d",
                self.database,
                "-c",
                query,
            ],
            env={
                "PGPASSWORD": self.password,
                "PGOPTIONS": "-c default_transaction_read_only=on",
            },
        )
        reader = csv.DictReader(io.StringIO(stdout))
        return [self._normalise(row) for row in reader]

    @staticmethod
    def _normalise(row: dict[str, Any]) -> dict[str, Any]:
        normalised = dict(row)
        for key in ("scheduled_at", "created_at"):
            normalised[key] = to_iso(row.get(key))
        for key in ("id", "channel", "text"):
            normalised[key] = "" if row.get(key) is None else row[key]
        return normalised
