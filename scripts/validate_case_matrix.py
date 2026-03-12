#!/usr/bin/env python3
"""Validate that the 8 cases keep a consistent first-class structure."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# fmt: off


ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "cases"
WORKFLOWS_DIR = ROOT / "n8n" / "workflows"


@dataclass(frozen=True)
class CaseExpectation:
    slug: str
    case_id: str
    origin_language: str
    origin_entrypoint: str
    destination_language: str
    destination_files: tuple[str, ...]
    workflow_file: str


EXPECTED_CASES = (
    CaseExpectation(
        slug="01-python-to-php",
        case_id="01",
        origin_language="python",
        origin_entrypoint="origin/bot.py",
        destination_language="php",
        destination_files=(
            "dest/index.php",
            "dest/index.html",
            "dest/errors.php",
        ),
        workflow_file="case-01-python-to-php.json",
    ),
    CaseExpectation(
        slug="02-python-to-go",
        case_id="02",
        origin_language="python",
        origin_entrypoint="origin/bot.py",
        destination_language="go",
        destination_files=(
            "dest/main.go",
            "dest/index.html",
            "dest/Dockerfile",
        ),
        workflow_file="case-02-python-to-go.json",
    ),
    CaseExpectation(
        slug="03-go-to-node",
        case_id="03",
        origin_language="go",
        origin_entrypoint="origin/main.go",
        destination_language="nodejs",
        destination_files=(
            "dest/index.js",
            "dest/index.html",
            "dest/package.json",
        ),
        workflow_file="case-03-go-to-node.json",
    ),
    CaseExpectation(
        slug="04-node-to-fastapi",
        case_id="04",
        origin_language="nodejs",
        origin_entrypoint="origin/index.js",
        destination_language="python",
        destination_files=(
            "dest/main.py",
            "dest/index.html",
            "dest/Dockerfile",
        ),
        workflow_file="case-04-node-to-fastapi.json",
    ),
    CaseExpectation(
        slug="05-laravel-to-react",
        case_id="05",
        origin_language="php",
        origin_entrypoint="origin/ArtisanPost.php",
        destination_language="react",
        destination_files=(
            "dest/server.js",
            "dest/App.jsx",
            "dest/package.json",
        ),
        workflow_file="case-05-laravel-to-react.json",
    ),
    CaseExpectation(
        slug="06-go-to-symfony",
        case_id="06",
        origin_language="go",
        origin_entrypoint="origin/main.go",
        destination_language="php",
        destination_files=("dest/index.php",),
        workflow_file="case-06-go-to-symfony.json",
    ),
    CaseExpectation(
        slug="07-rust-to-ruby",
        case_id="07",
        origin_language="rust",
        origin_entrypoint="origin/src/main.rs",
        destination_language="ruby",
        destination_files=(
            "dest/app.rb",
            "dest/views/index.erb",
            "dest/Dockerfile",
        ),
        workflow_file="case-07-rust-to-ruby.json",
    ),
    CaseExpectation(
        slug="08-csharp-to-flask",
        case_id="08",
        origin_language="csharp",
        origin_entrypoint="origin/Program.cs",
        destination_language="python",
        destination_files=(
            "dest/app.py",
            "dest/templates/index.html",
            "dest/Dockerfile",
        ),
        workflow_file="case-08-csharp-to-flask.json",
    ),
)


def parse_scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def load_manifest(case_dir: Path) -> dict:
    manifest: dict[str, object] = {}
    current_section: str | None = None
    manifest_path = case_dir / "app.manifest.yml"

    for raw_line in manifest_path.read_text(encoding="utf-8-sig").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and line.endswith(":"):
            current_section = line[:-1]
            manifest[current_section] = {}
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        parsed_value = parse_scalar(value)

        if indent > 0 and current_section:
            section = manifest.setdefault(current_section, {})
            if isinstance(section, dict):
                section[key.strip()] = parsed_value
        else:
            manifest[key.strip()] = parsed_value
            current_section = None

    return manifest


def validate_case(case: CaseExpectation) -> list[str]:
    errors: list[str] = []
    case_dir = CASES_DIR / case.slug

    if not case_dir.exists():
        return [f"{case.slug}: missing case directory"]

    manifest_path = case_dir / "app.manifest.yml"
    readme_path = case_dir / "README.md"

    if not manifest_path.exists():
        errors.append(f"{case.slug}: missing app.manifest.yml")
        return errors

    if not readme_path.exists():
        errors.append(f"{case.slug}: missing README.md")

    manifest = load_manifest(case_dir)
    manifest_origin = manifest.get("origin", {})
    manifest_destination = manifest.get("destination", {})

    if manifest.get("id") != case.case_id:
        errors.append(
            f"{case.slug}: expected id {case.case_id}, got {manifest.get('id')}"
        )

    expected_path = f"cases/{case.slug}"
    if manifest.get("path") != expected_path:
        errors.append(
            f"{case.slug}: expected path {expected_path}, got {manifest.get('path')}"
        )

    if not isinstance(manifest_origin, dict):
        errors.append(f"{case.slug}: invalid origin section")
        manifest_origin = {}

    if not isinstance(manifest_destination, dict):
        errors.append(f"{case.slug}: invalid destination section")
        manifest_destination = {}

    if manifest_origin.get("language") != case.origin_language:
        errors.append(
            f"{case.slug}: expected origin.language {case.origin_language}, "
            f"got {manifest_origin.get('language')}"
        )

    if manifest_origin.get("entrypoint") != case.origin_entrypoint:
        errors.append(
            f"{case.slug}: expected origin.entrypoint {case.origin_entrypoint}, "
            f"got {manifest_origin.get('entrypoint')}"
        )

    if manifest_destination.get("language") != case.destination_language:
        errors.append(
            f"{case.slug}: expected destination.language "
            f"{case.destination_language}, "
            f"got {manifest_destination.get('language')}"
        )

    if not (case_dir / case.origin_entrypoint).exists():
        errors.append(
            f"{case.slug}: missing origin entrypoint {case.origin_entrypoint}"
        )

    for relative_path in case.destination_files:
        if not (case_dir / relative_path).exists():
            errors.append(f"{case.slug}: missing critical file {relative_path}")

    workflow_path = WORKFLOWS_DIR / case.workflow_file
    if not workflow_path.exists():
        errors.append(f"{case.slug}: missing n8n workflow {case.workflow_file}")

    return errors


def main() -> int:
    errors: list[str] = []

    existing_case_dirs = sorted(
        path.name for path in CASES_DIR.iterdir() if path.is_dir()
    )
    expected_case_dirs = sorted(case.slug for case in EXPECTED_CASES)

    if existing_case_dirs != expected_case_dirs:
        errors.append(
            "cases/: expected matrix does not match current directories "
            f"(expected={expected_case_dirs}, actual={existing_case_dirs})"
        )

    for case in EXPECTED_CASES:
        errors.extend(validate_case(case))

    if errors:
        print("Matrix validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Matrix validation passed for cases 01-08.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# fmt: on

