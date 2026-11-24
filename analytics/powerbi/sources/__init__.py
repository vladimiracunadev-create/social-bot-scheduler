"""Adaptadores de origen: uno por motor de caso, todos de solo lectura.

Cada adaptador implementa :class:`CaseSource` y se ocupa de tres cosas nada
más: alcanzar su motor, emitir la lectura paginada que declara el contrato y
devolver diccionarios de Python cuyas claves coincidan exactamente con el
contrato. La redacción, el tipado y la escritura del CSV ocurren después.
"""

from __future__ import annotations

from analytics.powerbi.sources.base import (
    CaseSource,
    coerce_int,
    fetch_dataset,
    to_iso,
)
from analytics.powerbi.sources.case09 import Case09DuckDBSource
from analytics.powerbi.sources.case13 import Case13ClickHouseSource
from analytics.powerbi.sources.case16 import Case16TimescaleSource

# Clase de adaptador por identificador de caso soportado.
SOURCES: dict[str, type[CaseSource]] = {
    "09": Case09DuckDBSource,
    "13": Case13ClickHouseSource,
    "16": Case16TimescaleSource,
}


def build_source(case_id: str) -> CaseSource:
    """Instancia el adaptador de ``case_id``."""
    try:
        factory = SOURCES[case_id]
    except KeyError as exc:
        raise KeyError(
            f"el caso {case_id!r} no tiene adaptador de origen para Power BI; "
            f"soportados: {', '.join(sorted(SOURCES))}"
        ) from exc
    return factory()


__all__ = [
    "SOURCES",
    "Case09DuckDBSource",
    "Case13ClickHouseSource",
    "Case16TimescaleSource",
    "CaseSource",
    "build_source",
    "coerce_int",
    "fetch_dataset",
    "to_iso",
]
