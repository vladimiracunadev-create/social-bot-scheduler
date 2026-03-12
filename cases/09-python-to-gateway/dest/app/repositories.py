from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain import IntegrationRequest, ProviderCall, RepoSnapshot


class IntegrationRequestRepository(ABC):
    @abstractmethod
    def save(self, request: IntegrationRequest) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, fingerprint: str, status: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_fingerprint(self, fingerprint: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def latest_requests(self, limit: int = 20) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def latest_errors(self, limit: int = 20) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def stats(self) -> dict:
        raise NotImplementedError


class ProviderCallRepository(ABC):
    @abstractmethod
    def save_call(self, provider_call: ProviderCall) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_snapshots(self, snapshots: list[RepoSnapshot]) -> None:
        raise NotImplementedError

    @abstractmethod
    def top_repos(self, limit: int = 10) -> list[dict]:
        raise NotImplementedError
