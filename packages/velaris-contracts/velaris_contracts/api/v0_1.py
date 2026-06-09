"""api@0.1 capability contract (MVN resolver spike)."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable

from velaris_contracts._metadata import ContractMetadata

CAPABILITY_ID = "api"
CONTRACT_VERSION = "0.1"

CONTRACT_METADATA: ContractMetadata = {
    "capability_id": CAPABILITY_ID,
    "version": CONTRACT_VERSION,
    "description": "Minimal synchronous HTTP client for integration tests.",
}


@runtime_checkable
class Response(Protocol):
    """HTTP response abstraction."""

    @property
    def status_code(self) -> int: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def body(self) -> bytes: ...

    @property
    def text(self) -> str: ...

    def json(self) -> Any: ...

    def raise_for_status(self) -> None: ...


@runtime_checkable
class ApiClient(Protocol):
    """Minimal synchronous HTTP client for integration tests."""

    def get(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> Response: ...

    def post(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        json: Any | None = None,
        data: Any | None = None,
    ) -> Response: ...

    def put(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        json: Any | None = None,
        data: Any | None = None,
    ) -> Response: ...

    def patch(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        json: Any | None = None,
        data: Any | None = None,
    ) -> Response: ...

    def delete(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> Response: ...
