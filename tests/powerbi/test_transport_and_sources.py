"""Pruebas del guardia de solo lectura y de los adaptadores de origen.

Los adaptadores se prueban con un ``CommandRunner`` falso: no hace falta Docker
ni ningún motor, y aun así se verifica lo que de verdad importa — que la
sentencia enviada es una lectura, que va paginada y que las credenciales viajan
por entorno y no por la línea de comandos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from analytics.powerbi.contracts import CASE09_REQUESTS, CASE13_POSTS, CASE16_POSTS
from analytics.powerbi.sources import build_source
from analytics.powerbi.sources.base import coerce_int, fetch_dataset, to_iso
from analytics.powerbi.sources.case13 import Case13ClickHouseSource
from analytics.powerbi.sources.case16 import Case16TimescaleSource
from analytics.powerbi.transport import (
    CommandResult,
    DockerExecTransport,
    ReadOnlyViolation,
    TransportError,
    assert_read_only,
)

# --- guardia de solo lectura ------------------------------------------------


@pytest.mark.parametrize(
    "sentencia",
    [
        "SELECT 1",
        "select id from social_posts order by id",
        "WITH t AS (SELECT 1 AS a) SELECT a FROM t",
        "SELECT id FROM social_posts;",
    ],
)
def test_lecturas_aceptadas(sentencia: str) -> None:
    assert assert_read_only(sentencia)


@pytest.mark.parametrize(
    "sentencia",
    [
        "DELETE FROM social_posts",
        "DROP TABLE social_posts",
        "INSERT INTO social_posts VALUES (1)",
        "UPDATE social_posts SET text = 'x'",
        "SELECT 1; DROP TABLE social_posts",
        "TRUNCATE social_posts",
        "ALTER TABLE social_posts ADD COLUMN x INT",
        "SELECT * INTO copia FROM social_posts",
        "GRANT SELECT ON social_posts TO alguien",
        "",
        "   ",
    ],
)
def test_escrituras_rechazadas(sentencia: str) -> None:
    with pytest.raises(ReadOnlyViolation):
        assert_read_only(sentencia)


# --- runner falso -----------------------------------------------------------


@dataclass
class FakeRunner:
    """Sustituye a subprocess: registra las llamadas y devuelve una salida fija."""

    salida: str = ""
    returncode: int = 0
    llamadas: list[list[str]] = field(default_factory=list)
    entornos: list[dict[str, str] | None] = field(default_factory=list)

    def run(self, argv: list[str], env: dict[str, str] | None = None) -> CommandResult:
        self.llamadas.append(argv)
        self.entornos.append(env)
        if argv[1:2] == ["ps"]:
            return CommandResult(0, argv[-1] if False else self._nombre(argv), "")
        return CommandResult(self.returncode, self.salida, "fallo simulado")

    @staticmethod
    def _nombre(argv: list[str]) -> str:
        # docker ps --filter name=^X$ --format {{.Names}} -> devuelve X
        for item in argv:
            if item.startswith("name=^"):
                return item[len("name=^") : -1]
        return ""


def _transporte(runner: FakeRunner, contenedor: str) -> DockerExecTransport:
    return DockerExecTransport(container=contenedor, runner=runner)  # type: ignore[arg-type]


# --- caso 13: ClickHouse ----------------------------------------------------


def test_caso13_envia_una_lectura_paginada_y_formato_json() -> None:
    runner = FakeRunner(
        salida='{"id":"a","channel":"tw","text":"t","created_at":"2026-11-24 10:00:00"}\n'
    )
    origen = Case13ClickHouseSource(
        transport=_transporte(runner, "social-bot-clickhouse-13"),
        http_url="",
    )
    filas = origen.fetch_page(CASE13_POSTS, limit=50, offset=100)

    assert filas == [
        {
            "id": "a",
            "channel": "tw",
            "text": "t",
            "created_at": "2026-11-24T10:00:00",
        }
    ]
    consulta = runner.llamadas[-1][-1]
    assert consulta.upper().startswith("SELECT")
    assert "LIMIT 50 OFFSET 100" in consulta
    assert "FORMAT JSONEachRow" in consulta


def test_caso13_pasa_las_credenciales_por_entorno_no_por_argv() -> None:
    runner = FakeRunner(salida="")
    origen = Case13ClickHouseSource(
        transport=_transporte(runner, "social-bot-clickhouse-13"),
        http_url="",
        password="secreto-de-prueba",
    )
    origen.fetch_page(CASE13_POSTS, limit=10, offset=0)

    argv = runner.llamadas[-1]
    assert "secreto-de-prueba" not in " ".join(argv)
    assert runner.entornos[-1]["CLICKHOUSE_PASSWORD"] == "secreto-de-prueba"


def test_caso13_rechaza_un_dataset_que_no_le_corresponde() -> None:
    origen = Case13ClickHouseSource(
        transport=_transporte(FakeRunner(), "social-bot-clickhouse-13"), http_url=""
    )
    with pytest.raises(KeyError):
        origen.fetch_page(CASE09_REQUESTS, limit=10, offset=0)


def test_error_del_cliente_se_traduce_a_transport_error() -> None:
    runner = FakeRunner(salida="", returncode=1)
    origen = Case13ClickHouseSource(
        transport=_transporte(runner, "social-bot-clickhouse-13"), http_url=""
    )
    with pytest.raises(TransportError):
        origen.fetch_page(CASE13_POSTS, limit=10, offset=0)


# --- caso 16: TimescaleDB ---------------------------------------------------


def test_caso16_lee_csv_y_fija_la_sesion_en_solo_lectura() -> None:
    runner = FakeRunner(
        salida=(
            "id,channel,text,scheduled_at,created_at\r\n"
            "p1,twitter,hola,2026-11-24 11:00:00+00,2026-11-24 10:00:00+00\r\n"
        )
    )
    origen = Case16TimescaleSource(
        transport=_transporte(runner, "social-bot-db-timescaledb-16"),
        password="pg-secreto",
    )
    filas = origen.fetch_page(CASE16_POSTS, limit=25, offset=0)

    assert filas[0]["id"] == "p1"
    assert filas[0]["created_at"] == "2026-11-24T10:00:00"
    assert filas[0]["scheduled_at"] == "2026-11-24T11:00:00"

    entorno = runner.entornos[-1]
    assert entorno["PGOPTIONS"] == "-c default_transaction_read_only=on"
    assert entorno["PGPASSWORD"] == "pg-secreto"
    assert "pg-secreto" not in " ".join(runner.llamadas[-1])


# --- paginación y normalización --------------------------------------------


class OrigenPaginado:
    """Origen falso que devuelve páginas hasta agotar un total conocido."""

    case_id = "09"
    engine = "duckdb"

    def __init__(self, total: int) -> None:
        self.total = total
        self.peticiones: list[tuple[int, int]] = []

    def available(self) -> bool:
        return True

    def describe(self) -> str:
        return "origen de prueba"

    def fetch_page(self, contract, limit: int, offset: int) -> list[dict[str, Any]]:
        self.peticiones.append((limit, offset))
        filas = []
        for indice in range(offset, min(offset + limit, self.total)):
            filas.append(
                {
                    "request_id": f"req-{indice}",
                    "channel": "external-api",
                    "action": "github.repos.list",
                    "owner": "python",
                    "request_limit": 5,
                    "status": "SUCCEEDED",
                    "created_at": "2026-11-24T10:00:00",
                    "api_key_hash": "no-debe-salir",
                }
            )
        return filas


def test_fetch_dataset_pagina_y_respeta_el_techo_de_filas() -> None:
    origen = OrigenPaginado(total=25)
    filas = fetch_dataset(origen, CASE09_REQUESTS, max_rows=10, page_size=4)

    assert len(filas) == 10
    assert origen.peticiones == [(4, 0), (4, 4), (2, 8)]


def test_fetch_dataset_redacta_y_ordena_segun_el_contrato() -> None:
    origen = OrigenPaginado(total=3)
    filas = fetch_dataset(origen, CASE09_REQUESTS, max_rows=10, page_size=10)

    assert list(filas[0].keys()) == list(CASE09_REQUESTS.column_names)
    assert "api_key_hash" not in filas[0]


def test_fetch_dataset_valida_sus_parametros() -> None:
    origen = OrigenPaginado(total=1)
    with pytest.raises(ValueError):
        fetch_dataset(origen, CASE09_REQUESTS, max_rows=0)
    with pytest.raises(ValueError):
        fetch_dataset(origen, CASE09_REQUESTS, page_size=0)


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("2026-11-24 10:00:00+00", "2026-11-24T10:00:00"),
        ("2026-11-24T10:00:00", "2026-11-24T10:00:00"),
        ("2026-11-24 10:00:00", "2026-11-24T10:00:00"),
        ("", ""),
        (None, ""),
        ("no es una fecha", "no es una fecha"),
    ],
)
def test_to_iso_normaliza_las_marcas_temporales(entrada, esperado) -> None:
    assert to_iso(entrada) == esperado


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [("5", 5), (5, 5), ("5.9", 5), ("", None), (None, None), ("abc", None)],
)
def test_coerce_int(entrada, esperado) -> None:
    assert coerce_int(entrada) == esperado


def test_build_source_devuelve_el_adaptador_de_cada_caso() -> None:
    assert build_source("09").engine == "duckdb"
    assert build_source("13").engine == "clickhouse"
    assert build_source("16").engine == "timescaledb"
    with pytest.raises(KeyError):
        build_source("07")
