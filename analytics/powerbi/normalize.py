"""Normalización de los datasets crudos de cada caso al esquema conformado.

Cada caso modela su propio mundo: el 09 cuenta peticiones y llamadas al
proveedor, el 13 y el 16 cuentan posts. Un informe que los compare necesita un
único grano, así que este módulo proyecta todos los datasets crudos sobre un
grano de evento (``fact_events``) y deriva las dimensiones por las que cortan
las medidas.

Aquí no se toca ningún motor: es una función pura de las filas que ya devolvió
un adaptador, y eso es lo que la hace directamente testeable.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Iterable, Mapping

from analytics.powerbi.contracts import (
    CASE_DIMENSION_ROWS,
    DIM_CASE,
    DIM_CHANNEL,
    DIM_DATE,
    FACT_EVENTS,
    DatasetContract,
)

# Cota superior de la dimensión de fechas generada, para que una marca temporal
# disparatada en el futuro no la expanda sin límite.
MAX_DATE_ROWS = 4_000

_UNKNOWN_CHANNEL = "unknown"


def _date_key(iso_timestamp: str) -> str:
    return iso_timestamp[:10] if iso_timestamp else ""


def _status_from_http(http_status: Any) -> str:
    try:
        code = int(http_status)
    except (TypeError, ValueError):
        return "UNKNOWN"
    return "SUCCEEDED" if 200 <= code < 300 else "FAILED"


def _event(
    event_id: str,
    case_id: str,
    event_type: str,
    channel: str,
    status: str,
    subject: str,
    occurred_at: str,
    latency_ms: Any = "",
    http_status: Any = "",
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "case_id": case_id,
        "event_type": event_type,
        "channel": channel or _UNKNOWN_CHANNEL,
        "status": status,
        "subject": subject,
        "occurred_at": occurred_at,
        "date_key": _date_key(occurred_at),
        "latency_ms": latency_ms if latency_ms != "" else "",
        "http_status": http_status if http_status != "" else "",
    }


def build_fact_events(raw: Mapping[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Une todos los datasets crudos de ``raw`` en el grano de evento conformado."""
    events: list[dict[str, Any]] = []

    requests = raw.get("case09_requests", [])
    channel_by_request = {
        row.get("request_id", ""): row.get("channel", "") for row in requests
    }

    for row in requests:
        events.append(
            _event(
                event_id=f"09-req-{row.get('request_id', '')}",
                case_id="09",
                event_type="integration_request",
                channel=str(row.get("channel", "")),
                status=str(row.get("status", "")) or "UNKNOWN",
                subject=str(row.get("action", "")),
                occurred_at=str(row.get("created_at", "")),
            )
        )

    for row in raw.get("case09_provider_calls", []):
        request_id = str(row.get("request_id", ""))
        events.append(
            _event(
                event_id=f"09-call-{row.get('call_id', '')}",
                case_id="09",
                event_type="provider_call",
                channel=str(channel_by_request.get(request_id, "gateway")),
                status=_status_from_http(row.get("http_status")),
                subject=str(row.get("provider", "")),
                occurred_at=str(row.get("created_at", "")),
                latency_ms=row.get("latency_ms", ""),
                http_status=row.get("http_status", ""),
            )
        )

    for dataset, case_id in (("case13_posts", "13"), ("case16_posts", "16")):
        for row in raw.get(dataset, []):
            events.append(
                _event(
                    event_id=f"{case_id}-post-{row.get('id', '')}",
                    case_id=case_id,
                    event_type="post",
                    channel=str(row.get("channel", "")),
                    status="SUCCEEDED",
                    subject=str(row.get("id", "")),
                    occurred_at=str(row.get("created_at", "")),
                )
            )

    events.sort(key=lambda event: (event["occurred_at"], event["event_id"]))
    return events


def build_dim_case(case_ids: Iterable[str]) -> list[dict[str, Any]]:
    """Devuelve la dimensión de casos limitada a los casos realmente exportados."""
    wanted = set(case_ids)
    return [dict(row) for row in CASE_DIMENSION_ROWS if row["case_id"] in wanted]


def build_dim_channel(events: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Deriva la dimensión de canales a partir de los hechos exportados."""
    channels = sorted(
        {str(event.get("channel") or _UNKNOWN_CHANNEL) for event in events}
    )
    return [
        {"channel": channel, "channel_label": channel.replace("_", " ").title()}
        for channel in channels
    ]


def build_dim_date(events: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Genera una dimensión de fechas sin huecos que cubre los hechos exportados."""
    keys = sorted({str(event.get("date_key") or "") for event in events} - {""})
    if not keys:
        return []
    try:
        first = dt.date.fromisoformat(keys[0])
        last = dt.date.fromisoformat(keys[-1])
    except ValueError:
        return []

    rows: list[dict[str, Any]] = []
    current = first
    while current <= last and len(rows) < MAX_DATE_ROWS:
        iso = current.isocalendar()
        rows.append(
            {
                "date_key": current.isoformat(),
                "year": current.year,
                "month": current.month,
                "day": current.day,
                "iso_week": iso.week,
                "weekday": iso.weekday,
            }
        )
        current += dt.timedelta(days=1)
    return rows


def build_star_schema(
    raw: Mapping[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    """Construye todos los datasets conformados de una exportación."""
    events = build_fact_events(raw)
    case_ids = {event["case_id"] for event in events}
    return {
        DIM_CASE.name: build_dim_case(case_ids),
        DIM_CHANNEL.name: build_dim_channel(events),
        DIM_DATE.name: build_dim_date(events),
        FACT_EVENTS.name: events,
    }


def conformed_contract(name: str) -> DatasetContract:
    """Devuelve el contrato de un dataset conformado por su nombre."""
    for contract in (DIM_CASE, DIM_CHANNEL, DIM_DATE, FACT_EVENTS):
        if contract.name == name:
            return contract
    raise KeyError(name)
