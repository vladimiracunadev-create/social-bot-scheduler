"""Contrato común de los adaptadores de origen."""

from __future__ import annotations

import datetime as dt
from abc import ABC, abstractmethod
from typing import Any

from analytics.powerbi.contracts import DatasetContract
from analytics.powerbi.redaction import scrub_row

# Filas pedidas en cada viaje al motor. Mantiene la memoria acotada y hace
# recuperable una exportación parcial.
DEFAULT_PAGE_SIZE = 5_000

# Techo duro para la exportación de un solo dataset, ajustable desde la CLI.
DEFAULT_MAX_ROWS = 50_000


class SourceUnavailable(RuntimeError):
    """Se lanza cuando no se puede alcanzar el motor de un caso."""


class CaseSource(ABC):
    """Adaptador de solo lectura sobre el motor analítico de un caso."""

    case_id: str
    engine: str

    @abstractmethod
    def available(self) -> bool:
        """``True`` cuando este adaptador puede leer el motor ahora mismo."""

    @abstractmethod
    def describe(self) -> str:
        """Descripción legible del transporte que se está usando."""

    @abstractmethod
    def fetch_page(
        self, contract: DatasetContract, limit: int, offset: int
    ) -> list[dict[str, Any]]:
        """Devuelve como máximo ``limit`` filas de ``contract`` desde ``offset``."""


def coerce_int(value: Any, default: int | None = None) -> int | None:
    """Conversión a entero tolerante, que nunca falla con la salida del motor."""
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def to_iso(value: Any) -> str:
    """Normaliza una marca temporal del motor a una cadena ISO-8601 estable.

    Power BI interpreta ``AAAA-MM-DDTHH:MM:SS`` sin ambigüedad de configuración
    regional, algo que el formato con espacio que emiten psql y
    clickhouse-client no garantiza. Los valores que no se pueden parsear se
    devuelven tal cual en lugar de descartarse en silencio: así un formato
    inesperado aparece en los datos en vez de desaparecer.
    """
    if value is None or value == "":
        return ""
    if isinstance(value, dt.datetime):
        return value.replace(microsecond=0).isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    text = str(value).strip()
    candidate = text.replace(" ", "T", 1)
    for suffix in ("", "+00", "Z"):
        if suffix and candidate.endswith(suffix):
            candidate = candidate[: -len(suffix)]
    try:
        parsed = dt.datetime.fromisoformat(candidate)
    except ValueError:
        return text
    return parsed.replace(microsecond=0, tzinfo=None).isoformat()


def fetch_dataset(
    source: CaseSource,
    contract: DatasetContract,
    max_rows: int = DEFAULT_MAX_ROWS,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> list[dict[str, Any]]:
    """Pagina ``contract`` y devuelve filas redactadas con la forma del contrato.

    La paginación es lo que mantiene acotada la exportación: el adaptador nunca
    emite una consulta sin límite, y el bucle se detiene en ``max_rows`` incluso
    si la tabla sigue creciendo mientras la exportación corre.
    """
    if max_rows <= 0:
        raise ValueError("max_rows debe ser positivo")
    if page_size <= 0:
        raise ValueError("page_size debe ser positivo")

    rows: list[dict[str, Any]] = []
    offset = 0
    while len(rows) < max_rows:
        wanted = min(page_size, max_rows - len(rows))
        page = source.fetch_page(contract, wanted, offset)
        if not page:
            break
        for raw in page:
            scrubbed = scrub_row(raw)
            rows.append(
                {name: scrubbed.get(name, "") for name in contract.column_names}
            )
        if len(page) < wanted:
            break
        offset += len(page)
    return rows[:max_rows]
