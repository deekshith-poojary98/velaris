"""Contract Protocol compliance smoke tests."""

from __future__ import annotations

from velaris_contracts.api.v0_1 import ApiClient, Response
from velaris_contracts.browser.v0_1 import CONTRACT_METADATA as BROWSER_META
from velaris_contracts.browser.v0_1 import Browser
from velaris_contracts.secrets.v0_1 import CONTRACT_METADATA as SECRETS_META
from velaris_contracts.secrets.v0_1 import Secrets
from velaris_contracts.target_environment.v0_1 import CONTRACT_METADATA as TARGET_ENV_META
from velaris_contracts.target_environment.v0_1 import TargetEnvironment


class _FakeSecrets:
    def get(self, name: str) -> str:
        return f"value-of-{name}"


class _FakeTargetEnvironment:
    @property
    def environment(self) -> str:
        return "local-hermetic"

    def endpoint(self, name: str) -> str:
        endpoints = {
            "api": "https://api.example.test",
            "database_dsn": "postgresql://localhost/test",
        }
        return endpoints[name]


class _FakeResponse:
    status_code = 200
    headers = {"content-type": "application/json"}
    body = b"{}"
    text = "{}"

    def json(self) -> dict[str, str]:
        return {}

    def raise_for_status(self) -> None:
        return None


class _FakeApiClient:
    def get(self, path: str, **kwargs: object) -> _FakeResponse:
        return _FakeResponse()

    def post(self, path: str, **kwargs: object) -> _FakeResponse:
        return _FakeResponse()

    def put(self, path: str, **kwargs: object) -> _FakeResponse:
        return _FakeResponse()

    def patch(self, path: str, **kwargs: object) -> _FakeResponse:
        return _FakeResponse()

    def delete(self, path: str, **kwargs: object) -> _FakeResponse:
        return _FakeResponse()


class _FakeBrowser:
    def open(self, url: str) -> None:
        pass

    def click(self, selector: str) -> None:
        pass

    def type(self, selector: str, text: str) -> None:
        pass

    def close(self) -> None:
        pass


def test_secrets_protocol() -> None:
    assert isinstance(_FakeSecrets(), Secrets)


def test_secrets_metadata() -> None:
    assert SECRETS_META["capability_id"] == "secrets"
    assert SECRETS_META["version"] == "0.1"


def test_target_environment_protocol() -> None:
    env = _FakeTargetEnvironment()
    assert isinstance(env, TargetEnvironment)
    assert env.environment == "local-hermetic"
    assert env.endpoint("api") == "https://api.example.test"
    assert env.endpoint("database_dsn").startswith("postgresql://")


def test_target_environment_metadata() -> None:
    assert TARGET_ENV_META["capability_id"] == "target_environment"


def test_api_protocol() -> None:
    client = _FakeApiClient()
    assert isinstance(client, ApiClient)
    response = client.get("/users")
    assert isinstance(response, Response)


def test_browser_protocol() -> None:
    assert isinstance(_FakeBrowser(), Browser)


def test_browser_metadata() -> None:
    assert BROWSER_META["capability_id"] == "browser"
    assert BROWSER_META["version"] == "0.1"
