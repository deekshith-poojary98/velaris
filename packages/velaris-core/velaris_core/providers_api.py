"""api capability providers (requests)."""

from __future__ import annotations

from typing import Any, Callable
from urllib.parse import urljoin

from velaris_contracts.api.v0_1 import ApiClient
from velaris_core.provider_context import pop_emit
from velaris_core.reporting import capability_observed
from velaris_core.types import Teardown


class _RequestsResponse:
    def __init__(self, response: Any) -> None:
        self._response = response

    @property
    def status_code(self) -> int:
        return int(self._response.status_code)

    @property
    def headers(self) -> dict[str, str]:
        return {str(k): str(v) for k, v in self._response.headers.items()}

    @property
    def body(self) -> bytes:
        return bytes(self._response.content)

    @property
    def text(self) -> str:
        return str(self._response.text)

    def json(self) -> Any:
        return self._response.json()

    def raise_for_status(self) -> None:
        self._response.raise_for_status()


class RequestsApiClient:
    def __init__(
        self,
        session: Any,
        base_url: str,
        *,
        timeout: float = 30.0,
        emit: Callable[[object], None] | None = None,
    ) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._emit = emit

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return urljoin(self._base_url + "/", path.lstrip("/"))

    def get(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> _RequestsResponse:
        if self._emit is not None:
            self._emit(
                capability_observed("api", "request.started", {"method": "GET", "path": path})
            )
        response = self._session.get(
            self._url(path),
            headers=headers,
            params=params,
            timeout=self._timeout,
        )
        wrapped = _RequestsResponse(response)
        if self._emit is not None:
            self._emit(
                capability_observed(
                    "api",
                    "request.completed",
                    {
                        "method": "GET",
                        "path": path,
                        "status_code": wrapped.status_code,
                    },
                )
            )
        return wrapped

    def post(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        json: Any | None = None,
        data: Any | None = None,
    ) -> _RequestsResponse:
        return _RequestsResponse(
            self._session.post(
                self._url(path),
                headers=headers,
                json=json,
                data=data,
                timeout=self._timeout,
            )
        )

    def put(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        json: Any | None = None,
        data: Any | None = None,
    ) -> _RequestsResponse:
        return _RequestsResponse(
            self._session.put(
                self._url(path),
                headers=headers,
                json=json,
                data=data,
                timeout=self._timeout,
            )
        )

    def patch(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        json: Any | None = None,
        data: Any | None = None,
    ) -> _RequestsResponse:
        return _RequestsResponse(
            self._session.patch(
                self._url(path),
                headers=headers,
                json=json,
                data=data,
                timeout=self._timeout,
            )
        )

    def delete(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> _RequestsResponse:
        return _RequestsResponse(
            self._session.delete(
                self._url(path),
                headers=headers,
                timeout=self._timeout,
            )
        )


def create_requests_api(options: dict[str, Any]) -> tuple[ApiClient, Teardown]:
    import requests

    options, emit = pop_emit(options)
    session = requests.Session()
    timeout = float(options.get("timeout", 30.0))
    verify = bool(options.get("verify_ssl", True))
    session.verify = verify
    default_headers = options.get("default_headers", {})
    if isinstance(default_headers, dict):
        session.headers.update({str(k): str(v) for k, v in default_headers.items()})
    base_url = str(options.get("base_url", "http://testserver"))
    client: ApiClient = RequestsApiClient(session, base_url, timeout=timeout, emit=emit)
    return client, session.close
