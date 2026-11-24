"""Reglas de redacción a nivel de columna para toda exportación a Power BI.

El laboratorio guarda material de credenciales junto a datos operativos: el
caso 09 mantiene ``api_key_prefix`` y ``api_key_hash`` en la tabla
``integration_requests``. Una exportación analítica no debe arrastrarlo nunca,
así que la redacción se aplica dos veces:

1. al construir el contrato (:func:`assert_contract_is_safe`), de modo que un
   dataset inseguro ni siquiera pueda declararse; y
2. a nivel de fila (:func:`scrub_row`), de modo que una columna añadida aguas
   arriba más adelante no pueda filtrarse por un adaptador que seleccione
   ``*``.

Las columnas de texto libre también se truncan: el objetivo de una exportación
de BI es un indicador, no una copia literal del payload de error de un
proveedor.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

# Segmentos de nombre que marcan una columna como material de credenciales. Un
# segmento es una secuencia de caracteres alfanuméricos, así que ``api_key_hash``
# queda denegada mientras ``hashtag`` no. ``key`` por sí sola *no* se deniega:
# columnas analíticas legítimas como ``date_key`` la usan, y los nombres de
# credencial ya quedan cubiertos por las reglas de subcadena de más abajo y por
# los segmentos ``hash`` / ``secret`` / ``token``.
DENIED_SEGMENTS: frozenset[str] = frozenset(
    {
        "auth",
        "authorization",
        "cookie",
        "credential",
        "credentials",
        "hash",
        "hmac",
        "jwt",
        "passwd",
        "password",
        "pwd",
        "salt",
        "secret",
        "session",
        "signature",
        "token",
    }
)

# Subcadenas denegadas en cualquier posición del nombre de la columna.
DENIED_SUBSTRINGS: tuple[str, ...] = (
    "accesskey",
    "apikey",
    "bearer",
    "privatekey",
    "secretkey",
)

# Longitud máxima que se conserva de una columna de texto libre.
MAX_TEXT_LENGTH = 500

_SEGMENT_RE = re.compile(r"[a-z0-9]+")


class RedactionError(ValueError):
    """Se lanza cuando un contrato declara una columna prohibida."""


def _segments(column: str) -> list[str]:
    return _SEGMENT_RE.findall(column.lower())


def is_denied(column: str) -> bool:
    """Devuelve ``True`` cuando ``column`` no debe llegar nunca a una exportación."""
    normalised = re.sub(r"[^a-z0-9]", "", column.lower())
    if any(token in normalised for token in DENIED_SUBSTRINGS):
        return True
    return any(segment in DENIED_SEGMENTS for segment in _segments(column))


def denied_columns(columns: Iterable[str]) -> list[str]:
    """Devuelve las columnas de ``columns`` que la redacción prohíbe."""
    return [column for column in columns if is_denied(column)]


def assert_contract_is_safe(contract_name: str, columns: Iterable[str]) -> None:
    """Falla de forma ruidosa si un contrato declara material de credenciales."""
    offending = denied_columns(columns)
    if offending:
        raise RedactionError(
            f"el dataset {contract_name!r} declara columnas prohibidas: "
            f"{', '.join(sorted(offending))}"
        )


def truncate_text(value: Any, limit: int = MAX_TEXT_LENGTH) -> Any:
    """Trunca valores de texto largos y deja intactos los demás tipos."""
    if isinstance(value, str) and len(value) > limit:
        return value[: limit - 1] + "…"
    return value


def scrub_row(row: Mapping[str, Any], limit: int = MAX_TEXT_LENGTH) -> dict[str, Any]:
    """Elimina las claves prohibidas y trunca el texto largo de una fila."""
    return {
        key: truncate_text(value, limit)
        for key, value in row.items()
        if not is_denied(key)
    }
