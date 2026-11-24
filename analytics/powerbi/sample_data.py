"""Deterministic synthetic datasets.

Purpose: let somebody open Power BI Desktop, build the model, write the DAX
measures and check the visuals **before** any case is running, and let the
regression tests work on fixed data. The generator is seeded, so the same
arguments always produce byte-identical CSVs.

These rows are synthetic and are labelled as such in the manifest. They are
never mixed with a real export: ``sample`` and ``export`` write to different
directories and the manifest records which one produced the files.
"""

from __future__ import annotations

import datetime as dt
import random
from typing import Any

SAMPLE_SEED = 20260115

CHANNELS = ("twitter", "linkedin", "mastodon")
OWNERS = ("python", "golang", "rust-lang")
PROVIDERS = ("github",)
LANGUAGES = ("Python", "Go", "Rust")


def build_sample_raw_datasets(
    reference: dt.datetime,
    days: int = 7,
    requests_per_day: int = 6,
    posts_per_day: int = 5,
) -> dict[str, list[dict[str, Any]]]:
    """Build one synthetic raw dataset per contract.

    The shape matches the real adapters exactly - same column names, same
    types, same ISO timestamp rendering - so a report built on the sample keeps
    working when it is pointed at a real export.
    """
    if days <= 0:
        raise ValueError("days must be positive")
    rng = random.Random(SAMPLE_SEED)
    start = (reference - dt.timedelta(days=days - 1)).replace(
        hour=9, minute=0, second=0, microsecond=0
    )

    requests: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    posts13: list[dict[str, Any]] = []
    posts16: list[dict[str, Any]] = []

    for day in range(days):
        base = start + dt.timedelta(days=day)

        for index in range(requests_per_day):
            moment = base + dt.timedelta(minutes=17 * index)
            request_id = f"req-{day:02d}{index:02d}"
            failed = rng.random() < 0.18
            channel = CHANNELS[(day + index) % len(CHANNELS)]
            owner = OWNERS[index % len(OWNERS)]
            requests.append(
                {
                    "request_id": request_id,
                    "channel": channel,
                    "action": "trending_repos",
                    "owner": owner,
                    "request_limit": 5 + (index % 3) * 5,
                    "status": "FAILED" if failed else "SUCCEEDED",
                    "created_at": moment.isoformat(),
                }
            )
            http_status = rng.choice((403, 500, 502)) if failed else 200
            calls.append(
                {
                    "call_id": f"call-{day:02d}{index:02d}",
                    "request_id": request_id,
                    "provider": PROVIDERS[0],
                    "mode": "public",
                    "endpoint": f"/users/{owner}/repos",
                    "http_status": http_status,
                    "latency_ms": (
                        rng.randint(900, 2600) if failed else rng.randint(120, 850)
                    ),
                    "error_code": "PROVIDER_ERROR" if failed else "",
                    "error_message": (
                        f"provider answered {http_status}" if failed else ""
                    ),
                    "created_at": (moment + dt.timedelta(seconds=2)).isoformat(),
                }
            )
            if not failed:
                for rank in range(3):
                    snapshots.append(
                        {
                            "request_id": request_id,
                            "repo": f"{owner}/sample-repo-{rank + 1}",
                            "stars": 1000 * (3 - rank) + rng.randint(0, 400),
                            "language": LANGUAGES[rank % len(LANGUAGES)],
                            "url": (
                                f"https://github.com/{owner}/sample-repo-{rank + 1}"
                            ),
                        }
                    )

        for index in range(posts_per_day):
            moment = base + dt.timedelta(minutes=11 * index + 5)
            channel = CHANNELS[(day * 2 + index) % len(CHANNELS)]
            posts13.append(
                {
                    "id": f"post-13-{day:02d}{index:02d}",
                    "channel": channel,
                    "text": f"Synthetic post {index} of day {day} (Kafka -> ClickHouse)",
                    "created_at": moment.isoformat(),
                }
            )
            posts16.append(
                {
                    "id": f"post-16-{day:02d}{index:02d}",
                    "channel": channel,
                    "text": f"Synthetic post {index} of day {day} (Hasura -> Timescale)",
                    "scheduled_at": (moment + dt.timedelta(hours=1)).isoformat(),
                    "created_at": moment.isoformat(),
                }
            )

    return {
        "case09_requests": requests,
        "case09_provider_calls": calls,
        "case09_repo_snapshots": snapshots,
        "case13_posts": posts13,
        "case16_posts": posts16,
    }
