# api@0.1 Capability Contract

| Field | Value |
|-------|-------|
| Status | Draft (Pilot) |
| Created | 2026-06-02 |
| Capability ID | `api` |
| Contract Version | `0.1` |
| Package | `velaris-contract-api` |

## Purpose

`api@0.1` is the **first capability contract pilot** for Velaris Phase 0–2. It was chosen over `browser@0.1` because:

- Smaller interface surface (fewer bikesheds)
- Two mature provider candidates (`httpx`, `requests`)
- No browser/process lifecycle complexity
- Directly validates config-driven provider swap thesis

This contract defines the minimal HTTP client interface integration tests need. It is intentionally narrow.

## Design principles

1. **HTTP semantics, not client semantics** — Methods map to HTTP verbs, not library-specific APIs
2. **Synchronous first** — Async support deferred to `api@1.0`
3. **Response abstraction** — Tests inspect status, headers, body via a Velaris `Response` type, not raw library objects
4. **Configuration over construction** — Base URL, timeouts, auth come from capability options, not test code

## Contract interface

### Python Protocol

```python
# velaris_contract_api/v0_1.py
from typing import Any, Mapping, Protocol, runtime_checkable

CAPABILITY_ID = "api"
CONTRACT_VERSION = "0.1"


@runtime_checkable
class Response(Protocol):
    """HTTP response abstraction."""

    @property
    def status_code(self) -> int: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def body(self) -> bytes: ...

    def json(self) -> Any: ...

    @property
    def text(self) -> str: ...


@runtime_checkable
class ApiClient(Protocol):
    """Minimal synchronous HTTP client for integration tests."""

    def get(self, path: str, **kwargs: Any) -> Response:
        """HTTP GET. path is relative to configured base_url unless absolute URL."""
        ...

    def post(self, path: str, **kwargs: Any) -> Response:
        """HTTP POST. kwargs may include json, data, headers."""
        ...

    def put(self, path: str, **kwargs: Any) -> Response:
        """HTTP PUT."""
        ...

    def patch(self, path: str, **kwargs: Any) -> Response:
        """HTTP PATCH."""
        ...

    def delete(self, path: str, **kwargs: Any) -> Response:
        """HTTP DELETE."""
        ...
```

**Method count:** 5 HTTP methods on `ApiClient` + 5 properties/methods on `Response` = 10 total surface points. Core client methods: **5** (within 5–7 target when counting only `ApiClient`).

### Method semantics

| Method | Behavior | Required kwargs support |
|--------|----------|-------------------------|
| `get` | GET request | `headers`, `params` |
| `post` | POST request | `json`, `data`, `headers` |
| `put` | PUT request | `json`, `data`, `headers` |
| `patch` | PATCH request | `json`, `data`, `headers` |
| `delete` | DELETE request | `headers` |

Providers may accept additional kwargs but must not require them for basic usage.

### Path resolution

- If `path` starts with `http://` or `https://` → absolute URL, `base_url` ignored
- Otherwise → `{base_url}/{path}` with slash normalization

### Response requirements

| Property/Method | Requirement |
|-----------------|-------------|
| `status_code` | Integer HTTP status |
| `headers` | Case-insensitive access recommended; keys as strings |
| `body` | Raw bytes |
| `text` | Decoded string (UTF-8 default) |
| `json()` | Parse JSON body; raise on invalid JSON |

## Configuration options

Providers must support these options via `velaris.toml`:

```toml
[capabilities.api]
provider = "httpx"
contract = "0.1"

[capabilities.api.options]
base_url = "https://api.example.com"
timeout = 30.0
verify_ssl = true
default_headers = { "Accept" = "application/json" }
auth = { type = "bearer", token_env = "API_TOKEN" }
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `base_url` | string | `""` | Base URL for relative paths |
| `timeout` | float | `30.0` | Request timeout in seconds |
| `verify_ssl` | bool | `true` | TLS certificate verification |
| `default_headers` | map | `{}` | Headers sent with every request |
| `auth` | object | null | Auth config (provider interprets) |

Auth is intentionally minimal in v0.1. Providers document supported `auth.type` values (`bearer`, `basic`, `none`).

## Provider requirements

### Registration

```python
ctx.capabilities.register(
    capability_id="api",
    contract="api@0.1",
    provider="httpx",
    factory=HttpxApiFactory,
    scopes=["test", "session"],
    requires=["network"],
)
```

### Factory contract

```python
class ApiFactory(Protocol):
    def create(
        self,
        options: dict,
        sub_capabilities: dict,
    ) -> tuple[ApiClient, Callable[[], None]]:
        """Returns (client, teardown). teardown closes connections."""
        ...
```

### Compliance checklist

Providers implementing `api@0.1` must:

- [ ] Implement all 5 HTTP methods
- [ ] Return objects satisfying `Response` Protocol
- [ ] Honor `base_url`, `timeout`, `verify_ssl`, `default_headers`
- [ ] Close connections in teardown
- [ ] Pass contract compliance test suite (shipped with `velaris-contract-api`)

## Reference providers (Phase 2)

| Provider | Package | Notes |
|----------|---------|-------|
| `httpx` | `velaris-plugin-httpx` | Preferred; modern API |
| `requests` | `velaris-plugin-requests` | Legacy compatibility |

## Example test usage

```python
from velaris_contract_api.v0_1 import ApiClient


def test_list_users(api: ApiClient) -> None:
    response = api.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)


def test_create_user(api: ApiClient) -> None:
    response = api.post("/users", json={"name": "Ada"})
    assert response.status_code == 201
    assert response.json()["name"] == "Ada"
```

Same test file with different config:

```toml
# velaris.toml — staging with httpx
[capabilities.api]
provider = "httpx"
[capabilities.api.options]
base_url = "https://staging.example.com"
```

```toml
# velaris.toml — legacy env with requests
[capabilities.api]
provider = "requests"
[capabilities.api.options]
base_url = "https://legacy.example.com"
verify_ssl = false
```

## Compliance test suite

Shipped as `velaris_contract_api/testing.py`:

```python
def assert_api_client_compliant(client_factory: Callable[[], ApiClient]) -> None:
    """Run against a mock HTTP server or recorded fixtures."""
    client = client_factory()
    # GET returns Response with status_code
    # POST with json sends body
    # Response.json() parses JSON
    # Response.text returns str
    # teardown closes resources
```

All official providers must pass before release.

## Explicit non-goals (v0.1)

| Excluded | Rationale | Target version |
|----------|-----------|----------------|
| Async methods (`aget`, etc.) | Complexity | `api@1.0` |
| WebSocket | Different capability (`websocket@1.0`) | Future |
| GraphQL client | Domain-specific | `graphql@1.0` |
| Retry/backoff | Provider-specific option, not contract | Provider docs |
| Cookie jar management | Provider option | Provider docs |
| Request recording/vcr | Separate capability | `vcr@1.0` |

## Relationship to `network` capability

`api@0.1` declares `requires: ["network"]`. The `network` capability (Phase 2 trivial contract) provides:

- DNS resolution availability check (optional)
- Proxy configuration (optional)
- TLS context customization hook (optional)

For Phase 2, `network` may be a no-op stub satisfying the dependency graph.

## Versioning path to api@1.0

Planned additions for `1.0` (not in 0.1):

- Async client protocol (`AsyncApiClient`)
- Explicit `headers` parameter typing
- `raise_for_status()` on Response
- Formal auth schema in contract RFC

Breaking changes require RFC and dual-provider support during transition.

## Governance

| Role | Responsibility |
|------|----------------|
| Velaris core team | Maintains `velaris-contract-api` package |
| Provider authors | Implement compliance suite |
| Platform teams | Propose extensions via RFC |

Changes to `api@0.1` after Phase 2 exit are **patch only** (docs, type hints). Behavioral changes require `0.2` or `1.0`.

## Exit criteria (pilot)

- [ ] Protocol reviewed by 2 platform engineers
- [ ] httpx and requests implementations feasible without adapter hacks
- [ ] Compliance test suite spec complete
- [ ] Included in RFC-001 and RFC-002 examples

## References

- [RFC-001: Capability Model](../rfc/RFC-001-capability-model.md)
- [RFC-002: TestSpec IR](../rfc/RFC-002-testspec-ir.md)
- [RFC-006: pytest Coexistence](../archive/rfc/RFC-006-pytest-coexistence.md)
