#!/usr/bin/env python3
"""Validate that the 9 cases keep a consistent first-class structure, including Case 09."""

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
    CaseExpectation(
        slug="09-python-to-gateway",
        case_id="09",
        origin_language="python",
        origin_entrypoint="origin/bot.py",
        destination_language="python",
        destination_files=(
            "dest/main.py",
            "dest/app/api.py",
            "dest/Dockerfile",
        ),
        workflow_file="case-09-python-to-gateway.json",
    ),
    CaseExpectation(
        slug="16-graphql-to-hasura",
        case_id="16",
        origin_language="nodejs",
        origin_entrypoint="origin/index.js",
        destination_language="nodejs",
        destination_files=(
            "dest/receiver/index.js",
            "dest/receiver/index.html",
            "dest/receiver/Dockerfile",
            "dest/receiver/package.json",
        ),
        workflow_file="case-16-graphql-to-hasura.json",
    ),
    CaseExpectation(
        slug="11-elixir-to-erlang",
        case_id="11",
        origin_language="elixir",
        origin_entrypoint="origin/lib/publisher.ex",
        destination_language="erlang",
        destination_files=(
            "dest/src/social_bot_dest_app.erl",
            "dest/rebar.config",
            "dest/priv/index.html",
            "dest/Dockerfile",
        ),
        workflow_file="case-11-elixir-to-erlang.json",
    ),
    CaseExpectation(
        slug="17-mqtt-rust-to-node",
        case_id="17",
        origin_language="rust",
        origin_entrypoint="origin/src/main.rs",
        destination_language="nodejs",
        destination_files=(
            "dest/index.js",
            "dest/index.html",
            "dest/Dockerfile",
            "dest/package.json",
        ),
        workflow_file="case-17-mqtt-rust-to-node.json",
    ),
    CaseExpectation(
        slug="10-java-to-kotlin",
        case_id="10",
        origin_language="java",
        origin_entrypoint="origin/src/main/java/socialbot/OrderPublisher.java",
        destination_language="kotlin",
        destination_files=(
            "dest/src/main/kotlin/Application.kt",
            "dest/build.gradle.kts",
            "dest/Dockerfile",
        ),
        workflow_file="case-10-java-to-kotlin.json",
    ),
    CaseExpectation(
        slug="12-python-to-rag",
        case_id="12",
        origin_language="python",
        origin_entrypoint="origin/bot.py",
        destination_language="python",
        destination_files=(
            "dest/main.py",
            "dest/index.html",
            "dest/Dockerfile",
            "dest/requirements.txt",
        ),
        workflow_file="case-12-python-to-rag.json",
    ),
    CaseExpectation(
        slug="18-zig-to-crystal",
        case_id="18",
        origin_language="zig",
        origin_entrypoint="origin/src/main.zig",
        destination_language="crystal",
        destination_files=(
            "dest/src/app.cr",
            "dest/shard.yml",
            "dest/public/index.html",
            "dest/Dockerfile",
        ),
        workflow_file="case-18-zig-to-crystal.json",
    ),
    CaseExpectation(
        slug="15-grpc-go-to-python",
        case_id="15",
        origin_language="go",
        origin_entrypoint="origin/server.go",
        destination_language="python",
        destination_files=(
            "dest/main.py",
            "dest/requirements.txt",
            "dest/index.html",
            "dest/Dockerfile",
        ),
        workflow_file="case-15-grpc-go-to-python.json",
    ),
    CaseExpectation(
        slug="20-swift-to-dart",
        case_id="20",
        origin_language="swift",
        origin_entrypoint="origin/Sources/Publisher/main.swift",
        destination_language="dart",
        destination_files=(
            "dest/bin/server.dart",
            "dest/pubspec.yaml",
            "dest/public/index.html",
            "dest/Dockerfile",
        ),
        workflow_file="case-20-swift-to-dart.json",
    ),
    CaseExpectation(
        slug="13-node-to-go-kafka",
        case_id="13",
        origin_language="node",
        origin_entrypoint="origin/producer.js",
        destination_language="go",
        destination_files=(
            "dest/main.go",
            "dest/go.mod",
            "dest/index.html",
            "dest/Dockerfile",
        ),
        workflow_file="case-13-node-to-go-kafka.json",
    ),
    CaseExpectation(
        slug="14-nextjs-to-supabase",
        case_id="14",
        origin_language="node",
        origin_entrypoint="origin/app/api/emit/route.js",
        destination_language="node",
        destination_files=(
            "dest/index.js",
            "dest/package.json",
            "dest/index.html",
            "dest/Dockerfile",
        ),
        workflow_file="case-14-nextjs-to-supabase.json",
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


def is_planned_case(case_dir: Path) -> bool:
    manifest_path = case_dir / "app.manifest.yml"
    if not manifest_path.exists():
        return False
    try:
        manifest = load_manifest(case_dir)
    except OSError:
        return False
    return manifest.get("status") == "planned"


def main() -> int:
    errors: list[str] = []

    all_case_dirs = sorted(
        path for path in CASES_DIR.iterdir() if path.is_dir()
    )
    implemented_case_dirs = sorted(
        path.name for path in all_case_dirs if not is_planned_case(path)
    )
    planned_case_dirs = sorted(
        path.name for path in all_case_dirs if is_planned_case(path)
    )
    expected_case_dirs = sorted(case.slug for case in EXPECTED_CASES)

    if implemented_case_dirs != expected_case_dirs:
        errors.append(
            "cases/: implemented matrix does not match expected directories "
            f"(expected={expected_case_dirs}, actual_implemented={implemented_case_dirs})"
        )

    for case in EXPECTED_CASES:
        errors.extend(validate_case(case))

    if errors:
        print("Matrix validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Matrix validation passed for cases 01-09.")
    if planned_case_dirs:
        print(f"Skipped {len(planned_case_dirs)} planned cases: {', '.join(planned_case_dirs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# fmt: on
