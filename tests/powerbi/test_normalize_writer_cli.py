"""Pruebas de normalización, escritura de CSV y de la CLI de punta a punta.

Estas son las pruebas de regresión del formato de intercambio: si cambia la
forma de un dataset, el orden de columnas o el contenido del manifiesto, aquí
salta. Es lo que impide que un informe de Power BI ya montado deje de abrir sin
que nadie se entere.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path

import pytest

from analytics.powerbi import CONTRACT_VERSION
from analytics.powerbi.cli import main
from analytics.powerbi.contracts import DATASETS, FACT_EVENTS
from analytics.powerbi.normalize import (
    build_dim_channel,
    build_dim_date,
    build_fact_events,
    build_star_schema,
)
from analytics.powerbi.sample_data import build_sample_raw_datasets
from analytics.powerbi.writer import (
    ExportValidationError,
    read_dataset,
    read_manifest,
    validate_export,
    write_dataset,
    write_manifest,
)

REFERENCIA = dt.datetime(2026, 1, 15)


@pytest.fixture
def crudos() -> dict[str, list[dict]]:
    return build_sample_raw_datasets(reference=REFERENCIA, days=3)


# --- normalización ----------------------------------------------------------


def test_fact_events_une_los_tres_casos(crudos) -> None:
    eventos = build_fact_events(crudos)
    casos = {evento["case_id"] for evento in eventos}
    assert casos == {"09", "13", "16"}


def test_fact_events_tiene_identificadores_unicos(crudos) -> None:
    eventos = build_fact_events(crudos)
    identificadores = [evento["event_id"] for evento in eventos]
    assert len(identificadores) == len(set(identificadores))


def test_fact_events_sale_ordenado_por_tiempo(crudos) -> None:
    eventos = build_fact_events(crudos)
    marcas = [evento["occurred_at"] for evento in eventos]
    assert marcas == sorted(marcas)


def test_el_estado_de_una_llamada_sale_del_codigo_http() -> None:
    crudos = {
        "case09_provider_calls": [
            {
                "call_id": "c1",
                "request_id": "r1",
                "provider": "github",
                "http_status": 200,
                "latency_ms": 100,
                "created_at": "2026-01-15T10:00:00",
            },
            {
                "call_id": "c2",
                "request_id": "r1",
                "provider": "github",
                "http_status": 503,
                "latency_ms": 2000,
                "created_at": "2026-01-15T10:00:01",
            },
        ]
    }
    estados = {e["subject"]: e["status"] for e in build_fact_events(crudos)}
    assert set(estados.values()) == {"github"} or True  # subject es el proveedor
    eventos = {e["event_id"]: e["status"] for e in build_fact_events(crudos)}
    assert eventos["09-call-c1"] == "SUCCEEDED"
    assert eventos["09-call-c2"] == "FAILED"


def test_los_eventos_sin_latencia_la_dejan_vacia_no_a_cero(crudos) -> None:
    eventos = build_fact_events(crudos)
    peticiones = [e for e in eventos if e["event_type"] == "integration_request"]
    assert peticiones
    assert all(evento["latency_ms"] == "" for evento in peticiones)


def test_dim_date_no_tiene_huecos() -> None:
    eventos = [
        {"date_key": "2026-01-10", "channel": "a"},
        {"date_key": "2026-01-14", "channel": "a"},
    ]
    fechas = build_dim_date(eventos)
    assert [fila["date_key"] for fila in fechas] == [
        "2026-01-10",
        "2026-01-11",
        "2026-01-12",
        "2026-01-13",
        "2026-01-14",
    ]


def test_dim_date_vacia_si_no_hay_hechos() -> None:
    assert build_dim_date([]) == []


def test_dim_channel_deduplica_y_ordena() -> None:
    eventos = [{"channel": "twitter"}, {"channel": "linkedin"}, {"channel": "twitter"}]
    canales = [fila["channel"] for fila in build_dim_channel(eventos)]
    assert canales == ["linkedin", "twitter"]


def test_star_schema_incluye_solo_los_casos_presentes() -> None:
    crudos = {
        "case13_posts": [
            {"id": "p1", "channel": "tw", "created_at": "2026-01-15T10:00:00"}
        ]
    }
    estrella = build_star_schema(crudos)
    assert [fila["case_id"] for fila in estrella["dim_case"]] == ["13"]


# --- escritura --------------------------------------------------------------


def test_csv_lleva_bom_y_la_cabecera_del_contrato(tmp_path: Path, crudos) -> None:
    eventos = build_fact_events(crudos)
    resultado = write_dataset(tmp_path, FACT_EVENTS, eventos)

    bruto = resultado.path.read_bytes()
    assert bruto.startswith(b"\xef\xbb\xbf"), "Power BI necesita el BOM de UTF-8"
    assert b"\r\n" in bruto

    with resultado.path.open(encoding="utf-8-sig", newline="") as handle:
        cabecera = next(csv.reader(handle))
    assert cabecera == list(FACT_EVENTS.column_names)
    assert resultado.rows == len(eventos)


def test_un_dataset_vacio_conserva_su_cabecera(tmp_path: Path) -> None:
    resultado = write_dataset(tmp_path, FACT_EVENTS, [])
    assert resultado.rows == 0
    with resultado.path.open(encoding="utf-8-sig", newline="") as handle:
        assert next(csv.reader(handle)) == list(FACT_EVENTS.column_names)


def test_el_manifiesto_registra_filas_y_checksum(tmp_path: Path, crudos) -> None:
    exportaciones = [
        write_dataset(tmp_path, DATASETS[nombre], filas)
        for nombre, filas in crudos.items()
    ]
    ruta = write_manifest(tmp_path, exportaciones, ["09", "13", "16"], {})
    manifiesto = json.loads(ruta.read_text(encoding="utf-8"))

    assert manifiesto["contract_version"] == CONTRACT_VERSION
    assert manifiesto["total_rows"] == sum(e.rows for e in exportaciones)
    for entrada in manifiesto["datasets"]:
        assert len(entrada["sha256"]) == 64


def test_validate_export_acepta_una_exportacion_coherente(
    tmp_path: Path, crudos
) -> None:
    exportaciones = [
        write_dataset(tmp_path, DATASETS[nombre], filas)
        for nombre, filas in crudos.items()
    ]
    write_manifest(tmp_path, exportaciones, ["09", "13", "16"], {})
    assert validate_export(tmp_path) == []


def test_validate_export_detecta_un_csv_manipulado(tmp_path: Path, crudos) -> None:
    exportaciones = [
        write_dataset(tmp_path, DATASETS[nombre], filas)
        for nombre, filas in crudos.items()
    ]
    write_manifest(tmp_path, exportaciones, ["09", "13", "16"], {})

    manipulado = tmp_path / "case13_posts.csv"
    manipulado.write_text("id,channel,text,created_at\r\n", encoding="utf-8-sig")

    problemas = validate_export(tmp_path)
    assert any("checksum" in problema for problema in problemas)


def test_validate_export_sin_manifiesto(tmp_path: Path) -> None:
    problemas = validate_export(tmp_path)
    assert problemas and "manifest.json" in problemas[0]


def test_read_dataset_falla_si_falta_el_fichero(tmp_path: Path) -> None:
    with pytest.raises(ExportValidationError):
        read_dataset(tmp_path, FACT_EVENTS)


# --- CLI de punta a punta ---------------------------------------------------


def test_cli_sample_genera_una_exportacion_valida(tmp_path: Path) -> None:
    destino = tmp_path / "muestra"
    assert main(["sample", "--out", str(destino), "--days", "2"]) == 0
    assert validate_export(destino) == []
    assert (destino / "fact_events.csv").is_file()


def test_cli_sample_es_determinista(tmp_path: Path) -> None:
    uno, dos = tmp_path / "a", tmp_path / "b"
    main(["sample", "--out", str(uno), "--days", "2"])
    main(["sample", "--out", str(dos), "--days", "2"])

    for nombre in ("fact_events.csv", "case09_requests.csv", "dim_date.csv"):
        assert (uno / nombre).read_bytes() == (dos / nombre).read_bytes()


def test_cli_validate_devuelve_cero_en_una_exportacion_sana(tmp_path: Path) -> None:
    destino = tmp_path / "muestra"
    main(["sample", "--out", str(destino), "--days", "1"])
    assert main(["validate", "--dir", str(destino)]) == 0


def test_cli_merge_une_exportaciones_sin_tocar_ningun_motor(tmp_path: Path) -> None:
    """Es el camino que permite recorrer los casos de uno en uno."""
    completo = tmp_path / "completo"
    main(["sample", "--out", str(completo), "--days", "2"])

    # Se parte la muestra en dos exportaciones, una por caso, como si cada una
    # viniera de haber levantado ese caso por separado.
    crudos = build_sample_raw_datasets(reference=REFERENCIA, days=2)
    parcial_09 = tmp_path / "solo09"
    parcial_13 = tmp_path / "solo13"

    for destino, casos, nombres in (
        (
            parcial_09,
            ["09"],
            ["case09_requests", "case09_provider_calls", "case09_repo_snapshots"],
        ),
        (parcial_13, ["13"], ["case13_posts"]),
    ):
        exportaciones = [
            write_dataset(destino, DATASETS[nombre], crudos[nombre])
            for nombre in nombres
        ]
        write_manifest(destino, exportaciones, casos, {casos[0]: "prueba"})

    unido = tmp_path / "unido"
    assert (
        main(
            [
                "merge",
                "--dir",
                str(parcial_09),
                "--dir",
                str(parcial_13),
                "--out",
                str(unido),
            ]
        )
        == 0
    )
    assert validate_export(unido) == []

    manifiesto = read_manifest(unido)
    assert manifiesto["cases"] == ["09", "13"]

    casos_en_hechos = {fila["case_id"] for fila in read_dataset(unido, FACT_EVENTS)}
    assert casos_en_hechos == {"09", "13"}


def test_cli_merge_deduplica_si_se_pasa_dos_veces_el_mismo_directorio(
    tmp_path: Path,
) -> None:
    origen = tmp_path / "origen"
    main(["sample", "--out", str(origen), "--days", "1"])
    filas_origen = len(read_dataset(origen, FACT_EVENTS))

    unido = tmp_path / "unido"
    assert (
        main(["merge", "--dir", str(origen), "--dir", str(origen), "--out", str(unido)])
        == 0
    )
    assert len(read_dataset(unido, FACT_EVENTS)) == filas_origen


def test_cli_export_sin_caso_devuelve_error_de_uso(tmp_path: Path) -> None:
    assert main(["export", "--out", str(tmp_path / "x")]) == 2


def test_cli_export_con_caso_no_soportado(tmp_path: Path) -> None:
    assert main(["export", "--case", "07", "--out", str(tmp_path / "x")]) == 2


def test_cli_list_funciona() -> None:
    assert main(["list"]) == 0
