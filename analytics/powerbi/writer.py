"""Escritura de CSV, manifiestos de exportación y validación de esquema.

El formato de intercambio con Power BI Desktop es una carpeta de ficheros CSV
más un ``manifest.json``. El manifiesto es lo que hace una exportación
*reproducible* y *auditable*: registra la versión del contrato, el número de
filas y el SHA-256 de cada fichero, de modo que una exportación posterior se
puede comparar byte a byte y una prueba de regresión puede afirmar que un
dataset no cambió de forma en silencio.

Detalles del CSV que importan para Power BI:

* UTF-8 **con BOM** (``utf-8-sig``) — si no, Power BI Desktop elige la página
  de códigos equivocada para el texto acentuado;
* saltos de línea ``\\r\\n``, el dialecto que espera Power Query;
* la cabecera es siempre el orden de columnas del contrato, incluso para un
  dataset vacío, para que el modelo conserve sus columnas cuando todavía no
  hay datos.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from analytics.powerbi import CONTRACT_VERSION
from analytics.powerbi.contracts import DATASETS, DatasetContract
from analytics.powerbi.redaction import denied_columns

MANIFEST_NAME = "manifest.json"


class ExportValidationError(RuntimeError):
    """Se lanza cuando un directorio de exportación no cuadra con los contratos."""


@dataclass
class DatasetExport:
    """Resultado de escribir un dataset."""

    name: str
    path: Path
    rows: int
    sha256: str
    columns: Sequence[str]

    def as_manifest_entry(self) -> dict[str, Any]:
        return {
            "dataset": self.name,
            "file": self.path.name,
            "rows": self.rows,
            "sha256": self.sha256,
            "columns": list(self.columns),
        }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_dataset(
    directory: Path,
    contract: DatasetContract,
    rows: Iterable[Mapping[str, Any]],
) -> DatasetExport:
    """Escribe ``rows`` como el CSV de ``contract`` dentro de ``directory``."""
    offending = denied_columns(contract.column_names)
    if offending:
        raise ExportValidationError(
            f"me niego a escribir {contract.name}: columnas prohibidas "
            f"{', '.join(offending)}"
        )

    directory.mkdir(parents=True, exist_ok=True)
    path = directory / contract.filename
    written = 0
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(contract.column_names),
            extrasaction="ignore",
            lineterminator="\r\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in contract.column_names})
            written += 1
    return DatasetExport(
        name=contract.name,
        path=path,
        rows=written,
        sha256=_sha256(path),
        columns=contract.column_names,
    )


def write_manifest(
    directory: Path,
    exports: Sequence[DatasetExport],
    cases: Sequence[str],
    sources: Mapping[str, str],
    generated_at: datetime | None = None,
) -> Path:
    """Escribe el ``manifest.json`` que describe la exportación."""
    moment = generated_at or datetime.now(timezone.utc)
    payload = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": moment.replace(microsecond=0).isoformat(),
        "cases": list(cases),
        "sources": dict(sources),
        "datasets": [export.as_manifest_entry() for export in exports],
        "total_rows": sum(export.rows for export in exports),
    }
    path = directory / MANIFEST_NAME
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


def read_manifest(directory: Path) -> dict[str, Any]:
    """Carga el manifiesto de un directorio de exportación."""
    path = Path(directory) / MANIFEST_NAME
    if not path.is_file():
        raise ExportValidationError(f"falta {MANIFEST_NAME} en {directory}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ExportValidationError(f"{path} no es un objeto JSON")
    return data


def read_dataset(directory: Path, contract: DatasetContract) -> list[dict[str, str]]:
    """Relee un CSV exportado como lista de diccionarios."""
    path = Path(directory) / contract.filename
    if not path.is_file():
        raise ExportValidationError(f"falta {contract.filename} en {directory}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_export(directory: Path) -> list[str]:
    """Comprueba un directorio de exportación contra los contratos y su manifiesto.

    Devuelve la lista de problemas encontrados; una lista vacía significa que la
    exportación es coherente. Lo usan la CLI y las pruebas de regresión, y por
    eso informa de todos los problemas en vez de abortar en el primero.
    """
    problems: list[str] = []
    directory = Path(directory)
    try:
        manifest = read_manifest(directory)
    except ExportValidationError as exc:
        return [str(exc)]

    if manifest.get("contract_version") != CONTRACT_VERSION:
        problems.append(
            f"versión de contrato distinta: el manifiesto dice "
            f"{manifest.get('contract_version')!r} y el código {CONTRACT_VERSION!r}"
        )

    entries = manifest.get("datasets", [])
    if not isinstance(entries, list) or not entries:
        return problems + ["el manifiesto no declara ningún dataset"]

    for entry in entries:
        name = entry.get("dataset", "")
        contract = DATASETS.get(name)
        if contract is None:
            problems.append(f"dataset desconocido en el manifiesto: {name!r}")
            continue
        path = directory / entry.get("file", contract.filename)
        if not path.is_file():
            problems.append(f"{name}: falta el fichero {path.name}")
            continue
        if _sha256(path) != entry.get("sha256"):
            problems.append(f"{name}: checksum distinto para {path.name}")
        rows = read_dataset(directory, contract)
        if len(rows) != entry.get("rows"):
            problems.append(
                f"{name}: el manifiesto dice {entry.get('rows')} filas y "
                f"el fichero tiene {len(rows)}"
            )
        header = list(rows[0].keys()) if rows else _header_of(path)
        if header != list(contract.column_names):
            problems.append(
                f"{name}: la cabecera {header} no coincide con el contrato "
                f"{list(contract.column_names)}"
            )
        leaked = denied_columns(header)
        if leaked:
            problems.append(
                f"{name}: hay columnas prohibidas presentes: {', '.join(leaked)}"
            )
    return problems


def _header_of(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.reader(handle):
            return row
    return []
