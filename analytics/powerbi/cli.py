"""Punto de entrada por línea de comandos del módulo Power BI.

    python -m analytics.powerbi.cli list
    python -m analytics.powerbi.cli export --case 09 --out analytics/powerbi/exports/case09
    python -m analytics.powerbi.cli merge --dir exp/case09 --dir exp/case13 --out exp/all
    python -m analytics.powerbi.cli sample --out analytics/powerbi/samples
    python -m analytics.powerbi.cli validate --dir analytics/powerbi/samples

``export`` lee el motor vivo de cada caso pedido, así que necesita ese caso
levantado. ``merge`` no necesita nada levantado: une exportaciones ya hechas en
disco, que es lo que permite recorrer los casos de uno en uno sin tener los
tres consumiendo recursos a la vez. ``sample`` tampoco necesita nada: escribe
datos sintéticos deterministas para poder montar el informe en Power BI
Desktop antes de que corra ningún caso.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path
from typing import Any, Sequence

from analytics.powerbi import CONTRACT_VERSION
from analytics.powerbi.contracts import (
    CONFORMED_DATASETS,
    DATASETS,
    RAW_DATASETS,
    SUPPORTED_CASES,
    datasets_for_case,
)
from analytics.powerbi.normalize import build_star_schema
from analytics.powerbi.sample_data import build_sample_raw_datasets
from analytics.powerbi.sources import build_source
from analytics.powerbi.sources.base import (
    DEFAULT_MAX_ROWS,
    DEFAULT_PAGE_SIZE,
    fetch_dataset,
)
from analytics.powerbi.transport import TransportError
from analytics.powerbi.writer import (
    DatasetExport,
    read_dataset,
    read_manifest,
    validate_export,
    write_dataset,
    write_manifest,
)


def _cmd_list(_: argparse.Namespace) -> int:
    print(f"Contratos Power BI v{CONTRACT_VERSION}\n")
    for case_id in SUPPORTED_CASES:
        contracts = datasets_for_case(case_id)
        print(f"caso {case_id} ({contracts[0].engine}):")
        for contract in contracts:
            print(
                f"  - {contract.name:<24} {len(contract.columns):>2} col  "
                f"{contract.grain}"
            )
    print("\nconformados (derivados, se construyen en cada exportación):")
    for contract in CONFORMED_DATASETS:
        print(
            f"  - {contract.name:<24} {len(contract.columns):>2} col  "
            f"{contract.grain}"
        )
    return 0


def _export_raw(
    cases: Sequence[str],
    max_rows: int,
    page_size: int,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, str]]:
    raw: dict[str, list[dict[str, Any]]] = {}
    sources: dict[str, str] = {}
    for case_id in cases:
        source = build_source(case_id)
        if not source.available():
            raise TransportError(
                f"el caso {case_id} no es alcanzable: {source.describe()}. "
                f"Levántalo con 'docker compose --profile case{case_id} up -d'."
            )
        sources[case_id] = source.describe()
        for contract in datasets_for_case(case_id):
            rows = fetch_dataset(source, contract, max_rows, page_size)
            raw[contract.name] = rows
            print(f"  {contract.name:<24} {len(rows):>7} filas")
    return raw, sources


def _write_all(
    out: Path,
    raw: dict[str, list[dict[str, Any]]],
    cases: Sequence[str],
    sources: dict[str, str],
    raw_only: bool = False,
    generated_at: dt.datetime | None = None,
) -> tuple[list[DatasetExport], Path]:
    exports: list[DatasetExport] = []
    for name, rows in raw.items():
        exports.append(write_dataset(out, DATASETS[name], rows))
    if not raw_only:
        for name, rows in build_star_schema(raw).items():
            exports.append(write_dataset(out, DATASETS[name], rows))
            print(f"  {name:<24} {len(rows):>7} filas (derivado)")
    manifest = write_manifest(out, exports, cases, sources, generated_at)
    return exports, manifest


def _report(out: Path, exports: Sequence[DatasetExport], manifest: Path) -> int:
    print(f"\nmanifiesto: {manifest}")
    problems = validate_export(out)
    if problems:
        print("\nla exportación es INCONSISTENTE:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(
        f"validado: {len(exports)} datasets, "
        f"{sum(export.rows for export in exports)} filas"
    )
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    cases = list(SUPPORTED_CASES) if args.all else sorted(set(args.case or []))
    if not cases:
        print("nada que exportar: pasa --case NN (repetible) o --all", file=sys.stderr)
        return 2
    unknown = [case for case in cases if case not in SUPPORTED_CASES]
    if unknown:
        print(
            f"caso(s) no soportado(s): {', '.join(unknown)}; "
            f"soportados: {', '.join(SUPPORTED_CASES)}",
            file=sys.stderr,
        )
        return 2

    out = Path(args.out)
    print(f"Exportando caso(s) {', '.join(cases)} -> {out}")
    try:
        raw, sources = _export_raw(cases, args.max_rows, args.page_size)
    except TransportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    exports, manifest = _write_all(out, raw, cases, sources, args.raw_only)
    return _report(out, exports, manifest)


def _cmd_merge(args: argparse.Namespace) -> int:
    """Une exportaciones ya existentes en disco, sin tocar ningún motor.

    Es lo que permite recorrer los casos de uno en uno —levantar, exportar,
    apagar— y aun así obtener un modelo con los tres casos: los CSV ya están en
    disco, así que la unión y el esquema en estrella se recalculan sin Docker.
    """
    sources_dirs = [Path(d) for d in args.dir]
    missing = [str(d) for d in sources_dirs if not d.is_dir()]
    if missing:
        print(f"directorios inexistentes: {', '.join(missing)}", file=sys.stderr)
        return 2

    raw: dict[str, list[dict[str, Any]]] = {}
    seen: dict[str, set[tuple[Any, ...]]] = {}
    cases: list[str] = []
    sources: dict[str, str] = {}

    for directory in sources_dirs:
        try:
            manifest = read_manifest(directory)
        except Exception as exc:  # writer.ExportValidationError y similares
            print(f"error leyendo {directory}: {exc}", file=sys.stderr)
            return 1
        for case_id in manifest.get("cases", []):
            if case_id not in cases:
                cases.append(str(case_id))
        for case_id, description in (manifest.get("sources") or {}).items():
            sources[str(case_id)] = f"{description} [{directory}]"

        for case_id in manifest.get("cases", []):
            for contract in RAW_DATASETS.get(str(case_id), ()):
                path = directory / contract.filename
                if not path.is_file():
                    continue
                rows = read_dataset(directory, contract)
                bucket = raw.setdefault(contract.name, [])
                keys = seen.setdefault(contract.name, set())
                for row in rows:
                    signature = tuple(
                        row.get(name, "") for name in contract.column_names
                    )
                    if signature in keys:
                        continue
                    keys.add(signature)
                    bucket.append(row)

    if not raw:
        print(
            "no se encontró ningún dataset crudo en los directorios dados",
            file=sys.stderr,
        )
        return 1

    out = Path(args.out)
    print(f"Uniendo {len(sources_dirs)} exportación(es) -> {out}")
    for name, rows in raw.items():
        print(f"  {name:<24} {len(rows):>7} filas")
    exports, manifest_path = _write_all(out, raw, sorted(cases), sources)
    return _report(out, exports, manifest_path)


def _cmd_sample(args: argparse.Namespace) -> int:
    out = Path(args.out)
    reference = dt.datetime.fromisoformat(args.reference_date)
    raw = build_sample_raw_datasets(reference=reference, days=args.days)
    exports, manifest = _write_all(
        out,
        raw,
        list(SUPPORTED_CASES),
        {case: "muestra sintética (sin lectura de motor)" for case in SUPPORTED_CASES},
        generated_at=reference.replace(tzinfo=dt.timezone.utc),
    )
    print(f"\nmuestra sintética escrita en {out}")
    return _report(out, exports, manifest)


def _cmd_validate(args: argparse.Namespace) -> int:
    problems = validate_export(Path(args.dir))
    if problems:
        print(f"{args.dir}: {len(problems)} problema(s)", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"{args.dir}: coherente con los contratos v{CONTRACT_VERSION}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m analytics.powerbi.cli",
        description="Exportaciones de solo lectura a Power BI de los casos del laboratorio.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    listing = sub.add_parser(
        "list", help="muestra los contratos de dataset disponibles"
    )
    listing.set_defaults(func=_cmd_list)

    export = sub.add_parser("export", help="exporta a CSV los datos vivos de un caso")
    export.add_argument(
        "--case",
        action="append",
        metavar="NN",
        help="caso a exportar (repetible), por ejemplo --case 09",
    )
    export.add_argument(
        "--all", action="store_true", help="exporta todos los casos soportados"
    )
    export.add_argument("--out", required=True, help="directorio de destino")
    export.add_argument(
        "--max-rows",
        type=int,
        default=DEFAULT_MAX_ROWS,
        help=f"techo de filas por dataset (por defecto {DEFAULT_MAX_ROWS})",
    )
    export.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=f"filas por viaje al motor (por defecto {DEFAULT_PAGE_SIZE})",
    )
    export.add_argument(
        "--raw-only",
        action="store_true",
        help="omite el esquema en estrella y exporta solo los datasets crudos",
    )
    export.set_defaults(func=_cmd_export)

    merge = sub.add_parser(
        "merge", help="une exportaciones ya hechas, sin levantar ningún caso"
    )
    merge.add_argument(
        "--dir",
        action="append",
        required=True,
        help="directorio de exportación a unir (repetible)",
    )
    merge.add_argument("--out", required=True, help="directorio de destino")
    merge.set_defaults(func=_cmd_merge)

    sample = sub.add_parser("sample", help="escribe datasets sintéticos deterministas")
    sample.add_argument("--out", required=True, help="directorio de destino")
    sample.add_argument(
        "--reference-date",
        default="2026-01-15T00:00:00",
        help="marca temporal de referencia de la serie sintética",
    )
    sample.add_argument(
        "--days", type=int, default=7, help="días de historia sintética"
    )
    sample.set_defaults(func=_cmd_sample)

    validate = sub.add_parser(
        "validate", help="comprueba una exportación contra los contratos"
    )
    validate.add_argument("--dir", required=True, help="directorio a comprobar")
    validate.set_defaults(func=_cmd_validate)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
