from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


OWNER_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


class Channel(Enum):
    EXTERNAL_API = "external-api"


class Action(Enum):
    GITHUB_REPOS_LIST = "github.repos.list"


class ProviderMode(Enum):
    PUBLIC = "public"
    REAL = "real"


@dataclass(frozen=True)
class RequestId:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("request_id must be a non-empty string")


@dataclass(frozen=True)
class Owner:
    value: str

    def __post_init__(self) -> None:
        if not OWNER_PATTERN.fullmatch(self.value):
            raise ValueError("owner must match a safe GitHub owner pattern")


@dataclass(frozen=True)
class Limit:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1 or self.value > 50:
            raise ValueError("limit must be between 1 and 50")


@dataclass(frozen=True)
class Fingerprint:
    value: str

    @classmethod
    def from_parts(cls, request_id: RequestId, channel: Channel) -> "Fingerprint":
        return cls(f"{request_id.value}_{channel.value}")


@dataclass(frozen=True)
class ApiKeyId:
    prefix: str
    hash_value: str

    @classmethod
    def from_plaintext(cls, api_key: str) -> "ApiKeyId":
        if not api_key or not api_key.strip():
            raise ValueError("api key must be present")
        trimmed = api_key.strip()
        return cls(prefix=trimmed[:8], hash_value=hashlib.sha256(trimmed.encode("utf-8")).hexdigest())


@dataclass(frozen=True)
class HttpStatus:
    value: int

    def __post_init__(self) -> None:
        if self.value < 100 or self.value > 599:
            raise ValueError("http_status must be between 100 and 599")


@dataclass(frozen=True)
class LatencyMs:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("latency_ms must be >= 0")


@dataclass(frozen=True)
class RepoSnapshot:
    request_id: str
    repo: str
    stars: int
    language: str | None
    url: str


@dataclass(frozen=True)
class ProviderCall:
    call_id: str
    request_id: str
    provider: str
    mode: ProviderMode
    endpoint: str
    http_status: HttpStatus
    latency_ms: LatencyMs
    rate_limit_remaining: str | None
    error_code: str | None
    error_message: str | None


@dataclass
class IntegrationRequest:
    request_id: RequestId
    fingerprint: Fingerprint
    channel: Channel
    action: Action
    owner: Owner
    limit: Limit
    status: str
    api_key_prefix: str
    api_key_hash: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def mark_failed(self) -> None:
        self.status = "FAILED"

    def mark_succeeded(self) -> None:
        self.status = "SUCCEEDED"
