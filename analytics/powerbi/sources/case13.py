"""Adaptador del caso 13: ClickHouse alimentado por el consumidor Go de Kafka.

``clickhouse-13`` no publica ningún puerto en el anfitrión, y es deliberado, así
que el transporte por defecto ejecuta ``clickhouse-client`` dentro del
contenedor. Las credenciales viajan como variables de entorno del contenedor
(``CLICKHOUSE_USER`` / ``CLICKHOUSE_PASSWORD``) y no como ``--password`` en la
línea de comandos, que las dejaría visibles en la tabla de procesos del
anfitrión.

Si se define ``CASE13_CLICKHOUSE_URL`` —por ejemplo tras publicar el 8123 en
loopback— se usa en su lugar el transporte HTTP, que además fija ``readonly=1``
en el lado de ClickHouse como segundo guardia por encima de
:func:`assert_read_only`.
"""

from __future__ import annotations

import json
import os
from typing import Any

from analytics.powerbi.contracts import DatasetContract
from analytics.powerbi.redaction import MAX_TEXT_LENGTH
from analytics.powerbi.sources.base import CaseSource, to_iso
from analytics.powerbi.transport import (
    DockerExecTransport,
    TransportError,
    assert_read_only,
)

CONTAINER = "social-bot-clickhouse-13"
DEFAULT_USER = "sbuser"
DEFAULT_PASSWORD = "change-me-case13-local"

QUERIES: dict[str, str] = {
    "case13_posts": f"""
        SELECT id,
               channel,
               substring(text, 1, {MAX_TEXT_LENGTH}) AS text,
               toString(created_at) AS created_at
        FROM social_posts
        ORDER BY created_at ASC, id ASC
    """,
}


class Case13ClickHouseSource(CaseSource):
    """Adaptador ClickHouse de solo lectura para el caso 13."""

    case_id = "13"
    engine = "clickhouse"

    def __init__(
        self,
        transport: DockerExecTransport | None = None,
        http_url: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self.transport = transport or DockerExecTransport(CONTAINER)
        self.http_url = http_url or os.getenv("CASE13_CLICKHOUSE_URL", "")
        self.user = user or os.getenv("CASE13_CLICKHOUSE_USER", DEFAULT_USER)
        self.password = password or os.getenv(
            "CASE13_CLICKHOUSE_PASSWORD", DEFAULT_PASSWORD
        )

    def available(self) -> bool:
        return bool(self.http_url) or self.transport.available()

    def describe(self) -> str:
        if self.http_url:
            return f"ClickHouse por HTTP ({self.http_url}, readonly=1)"
        return f"clickhouse-client dentro del contenedor {self.transport.container}"

    def fetch_page(
        self, contract: DatasetContract, limit: int, offset: int
    ) -> list[dict[str, Any]]:
        try:
            sql = QUERIES[contract.name]
        except KeyError as exc:
            raise KeyError(
                f"el caso 13 no puede servir el dataset {contract.name!r}"
            ) from exc

        statement = assert_read_only(sql)
        page_limit, page_offset = int(limit), int(offset)
        if page_limit <= 0 or page_offset < 0:
            raise ValueError("limit debe ser positivo y offset no negativo")
        query = (
            f"{statement} LIMIT {page_limit} OFFSET {page_offset} " "FORMAT JSONEachRow"
        )

        payload = self._read_http(query) if self.http_url else self._read_client(query)
        return [self._normalise(row) for row in payload]

    def _read_client(self, query: str) -> list[dict[str, Any]]:
        stdout = self.transport.exec(
            ["clickhouse-client", "--query", query],
            env={"CLICKHOUSE_USER": self.user, "CLICKHOUSE_PASSWORD": self.password},
        )
        return [json.loads(line) for line in stdout.splitlines() if line.strip()]

    def _read_http(self, query: str) -> list[dict[str, Any]]:
        import requests

        try:
            response = requests.post(
                self.http_url,
                params={"query": query, "readonly": "1"},
                headers={
                    "X-ClickHouse-User": self.user,
                    "X-ClickHouse-Key": self.password,
                },
                timeout=60,
            )
        except requests.RequestException as exc:
            raise TransportError(
                f"falló el transporte HTTP de ClickHouse: {exc}"
            ) from exc
        if response.status_code >= 400:
            raise TransportError(
                f"ClickHouse respondió HTTP {response.status_code}: "
                f"{response.text[:300]}"
            )
        return [json.loads(line) for line in response.text.splitlines() if line.strip()]

    @staticmethod
    def _normalise(row: dict[str, Any]) -> dict[str, Any]:
        normalised = dict(row)
        normalised["created_at"] = to_iso(row.get("created_at"))
        for key in ("id", "channel", "text"):
            normalised[key] = "" if row.get(key) is None else row[key]
        return normalised
