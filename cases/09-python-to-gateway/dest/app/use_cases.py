from __future__ import annotations

import os
import time
import uuid
from datetime import datetime, timezone

import requests

from app.domain import Action, ApiKeyId, Channel, Fingerprint, HttpStatus, IntegrationRequest, LatencyMs, Limit, Owner, ProviderCall, ProviderMode, RepoSnapshot, RequestId
from app.repositories import IntegrationRequestRepository, ProviderCallRepository


class HandleIntegrationRequest:
    def __init__(self, integration_repo: IntegrationRequestRepository, provider_repo: ProviderCallRepository, github_token: str | None) -> None:
        self.integration_repo = integration_repo
        self.provider_repo = provider_repo
        self.github_token = github_token or ""

    def execute(self, payload: dict, api_key: str) -> dict:
        request_id = RequestId(payload["id"])
        channel = Channel(payload["channel"])
        action = Action(payload["action"])
        params = payload["params"]
        owner = Owner(params["owner"])
        limit = Limit(int(params["limit"]))
        fingerprint = Fingerprint.from_parts(request_id, channel)
        api_key_id = ApiKeyId.from_plaintext(api_key)

        existing = self.integration_repo.get_by_fingerprint(fingerprint.value)
        if existing:
            return {"ok": True, "duplicate": True, "request_id": existing["request_id"], "fingerprint": existing["fingerprint"], "status": existing["status"]}

        integration_request = IntegrationRequest(
            request_id=request_id,
            fingerprint=fingerprint,
            channel=channel,
            action=action,
            owner=owner,
            limit=limit,
            status="PROCESSING",
            api_key_prefix=api_key_id.prefix,
            api_key_hash=api_key_id.hash_value,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.integration_repo.save(integration_request)

        mode = ProviderMode.REAL if self.github_token else ProviderMode.PUBLIC
        endpoint = f"https://api.github.com/users/{owner.value}/repos?per_page={limit.value}&sort=updated"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "social-bot-scheduler-case09"}
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"

        started_at = time.perf_counter()

        try:
            response = requests.get(endpoint, headers=headers, timeout=20)
            latency_ms = int((time.perf_counter() - started_at) * 1000)
            response.raise_for_status()

            self.provider_repo.save_call(
                ProviderCall(
                    call_id=str(uuid.uuid4()),
                    request_id=request_id.value,
                    provider="github",
                    mode=mode,
                    endpoint=endpoint,
                    http_status=HttpStatus(response.status_code),
                    latency_ms=LatencyMs(latency_ms),
                    rate_limit_remaining=response.headers.get("X-RateLimit-Remaining"),
                    error_code=None,
                    error_message=None,
                )
            )

            repos = response.json()
            snapshots = [
                RepoSnapshot(
                    request_id=request_id.value,
                    repo=repo["full_name"],
                    stars=int(repo.get("stargazers_count", 0)),
                    language=repo.get("language"),
                    url=repo["html_url"],
                )
                for repo in repos[: limit.value]
            ]
            self.provider_repo.save_snapshots(snapshots)
            self.integration_repo.update_status(fingerprint.value, "SUCCEEDED")

            top_repo = max(snapshots, key=lambda snapshot: snapshot.stars, default=None)
            return {
                "ok": True,
                "request_id": request_id.value,
                "fingerprint": fingerprint.value,
                "status": "SUCCEEDED",
                "mode": mode.value,
                "repo_count": len(snapshots),
                "top_repo": top_repo.repo if top_repo else None,
                "top_repo_stars": top_repo.stars if top_repo else None,
            }
        except requests.HTTPError as exc:
            latency_ms = int((time.perf_counter() - started_at) * 1000)
            self.integration_repo.update_status(fingerprint.value, "FAILED")
            self.provider_repo.save_call(
                ProviderCall(
                    call_id=str(uuid.uuid4()),
                    request_id=request_id.value,
                    provider="github",
                    mode=mode,
                    endpoint=endpoint,
                    http_status=HttpStatus(exc.response.status_code),
                    latency_ms=LatencyMs(latency_ms),
                    rate_limit_remaining=exc.response.headers.get("X-RateLimit-Remaining"),
                    error_code=f"HTTP_{exc.response.status_code}",
                    error_message=str(exc)[:255],
                )
            )
            raise


class HandleIntegrationFailure:
    def __init__(self, integration_repo: IntegrationRequestRepository, provider_repo: ProviderCallRepository) -> None:
        self.integration_repo = integration_repo
        self.provider_repo = provider_repo

    def execute(self, payload: dict) -> dict:
        body = payload.get("payload") or {}
        params = body.get("params") or {}
        request_id = RequestId(body.get("id") or f"dlq-{uuid.uuid4()}")
        channel = Channel(body.get("channel", Channel.EXTERNAL_API.value))
        action = Action(body.get("action", Action.GITHUB_REPOS_LIST.value))
        owner = Owner(params.get("owner", "fallback-owner"))
        limit = Limit(int(params.get("limit", 1)))
        fingerprint_value = payload.get("fingerprint") or f"{request_id.value}_{channel.value}"
        fingerprint = Fingerprint(fingerprint_value)

        if not self.integration_repo.get_by_fingerprint(fingerprint.value):
            self.integration_repo.save(
                IntegrationRequest(
                    request_id=request_id,
                    fingerprint=fingerprint,
                    channel=channel,
                    action=action,
                    owner=owner,
                    limit=limit,
                    status="FAILED",
                    api_key_prefix="",
                    api_key_hash="",
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
            )
        else:
            self.integration_repo.update_status(fingerprint.value, "FAILED")

        self.provider_repo.save_call(
            ProviderCall(
                call_id=str(uuid.uuid4()),
                request_id=request_id.value,
                provider="n8n-dlq",
                mode=ProviderMode.PUBLIC,
                endpoint="/errors",
                http_status=HttpStatus(500),
                latency_ms=LatencyMs(0),
                rate_limit_remaining=None,
                error_code="DLQ",
                error_message=str(payload.get("error", "Unknown error"))[:255],
            )
        )
        return {"ok": True, "status": "FAILED", "fingerprint": fingerprint.value}


def create_use_cases(integration_repo: IntegrationRequestRepository, provider_repo: ProviderCallRepository) -> tuple[HandleIntegrationRequest, HandleIntegrationFailure]:
    return (
        HandleIntegrationRequest(integration_repo=integration_repo, provider_repo=provider_repo, github_token=os.getenv("GITHUB_TOKEN", "")),
        HandleIntegrationFailure(integration_repo=integration_repo, provider_repo=provider_repo),
    )
