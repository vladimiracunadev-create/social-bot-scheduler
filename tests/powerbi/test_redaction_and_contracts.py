"""Pruebas de redacción y de los contratos de dataset.

La propiedad que se protege aquí es el criterio de aceptación número 4: una
exportación no puede llevar material de credenciales. Se comprueba en los dos
puntos donde se aplica la regla, el contrato y la fila.
"""

from __future__ import annotations

import pytest

from analytics.powerbi import contracts
from analytics.powerbi.contracts import Column, DatasetContract
from analytics.powerbi.redaction import (
    RedactionError,
    denied_columns,
    is_denied,
    scrub_row,
    truncate_text,
)


@pytest.mark.parametrize(
    "column",
    [
        "api_key_hash",
        "api_key_prefix",
        "apiKey",
        "access_key_id",
        "secret_key",
        "password",
        "auth_token",
        "session_id",
        "x_hmac_signature",
    ],
)
def test_columnas_de_credenciales_denegadas(column: str) -> None:
    assert is_denied(column)


@pytest.mark.parametrize(
    "column",
    [
        "date_key",
        "event_id",
        "channel",
        "hashtag",
        "latency_ms",
        "request_id",
        "http_status",
        "case_name",
    ],
)
def test_columnas_analiticas_permitidas(column: str) -> None:
    assert not is_denied(column)


def test_contrato_con_columna_prohibida_no_se_puede_declarar() -> None:
    with pytest.raises(RedactionError) as error:
        DatasetContract(
            name="dataset_inseguro",
            case_id="09",
            engine="duckdb",
            grain="una fila",
            description="contrato de prueba",
            columns=(
                Column("request_id", "text", "id"),
                Column("api_key_hash", "text", "no debería poder declararse"),
            ),
        )
    assert "api_key_hash" in str(error.value)


def test_scrub_row_elimina_credenciales_y_conserva_el_resto() -> None:
    fila = {
        "request_id": "req-1",
        "api_key_prefix": "change-m",
        "api_key_hash": "deadbeef",
        "status": "SUCCEEDED",
    }
    assert scrub_row(fila) == {"request_id": "req-1", "status": "SUCCEEDED"}


def test_truncate_text_acota_el_texto_libre() -> None:
    largo = "x" * 900
    recortado = truncate_text(largo, limit=100)
    assert len(recortado) == 100
    assert recortado.endswith("…")


def test_truncate_text_no_toca_otros_tipos() -> None:
    assert truncate_text(42) == 42
    assert truncate_text(None) is None


def test_ningun_contrato_declarado_lleva_columnas_prohibidas() -> None:
    """Regresión: recorre TODOS los contratos del módulo, no una muestra."""
    for nombre, contrato in contracts.DATASETS.items():
        assert denied_columns(contrato.column_names) == [], nombre


def test_el_contrato_del_caso_09_excluye_la_api_key() -> None:
    """La tabla de origen sí tiene esas columnas; el contrato no debe tenerlas."""
    columnas = contracts.CASE09_REQUESTS.column_names
    assert "api_key_prefix" not in columnas
    assert "api_key_hash" not in columnas
    assert "status" in columnas


def test_tipos_power_bi_declarados_para_cada_columna() -> None:
    for contrato in contracts.DATASETS.values():
        for columna in contrato.columns:
            assert columna.power_bi_type in contracts.POWER_BI_TYPES.values()


def test_tipo_de_contrato_desconocido_se_rechaza() -> None:
    with pytest.raises(ValueError):
        Column("x", "inventado", "tipo que no existe")


def test_datasets_for_case_falla_con_caso_no_soportado() -> None:
    with pytest.raises(KeyError):
        contracts.datasets_for_case("07")


def test_casos_soportados_son_los_tres_documentados() -> None:
    assert contracts.SUPPORTED_CASES == ("09", "13", "16")
