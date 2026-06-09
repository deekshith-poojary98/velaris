# api@0.1

Minimal synchronous HTTP client for integration tests.

## Contract

```python
from velaris_contracts.api.v0_1 import ApiClient, Response
```

| Method | Description |
|--------|-------------|
| `get(path, *, headers, params)` | HTTP GET |
| `post(path, *, headers, json, data)` | HTTP POST |
| `put(path, *, headers, json, data)` | HTTP PUT |
| `patch(path, *, headers, json, data)` | HTTP PATCH |
| `delete(path, *, headers)` | HTTP DELETE |

`Response` exposes `status_code`, `headers`, `body`, `text`, `json()`, `raise_for_status()`.

## Providers

### `requests`

Uses the `requests` library. Requires `base_url` in config unless paths are absolute URLs.

```toml
[capabilities.api]
provider = "requests"

[capabilities.api.options]
base_url = "http://testserver"
```

## Test example

```python
from velaris_core.decorators import test

@test("api")
def test_users(api):
    response = api.get("/users")
    assert response.status_code == 200
```

## Events

| Action | When |
|--------|------|
| `request.started` | Before HTTP call |
| `request.completed` | After response received |

Stdout:

```text
api request started GET /users
api request completed GET /users 200
```

## HTTP mocking

Alpha HTTP examples expect mocked endpoints. Use `responses` or similar in test setup, or point `base_url` at a reachable server.

::: tip Alpha note
`examples/minimal` HTTP tests require `API_TOKEN` and HTTP mocking. See [Browser example](/examples/browser) for a zero-setup alternative.
:::

## With secrets

```python
@test("api", "secrets")
def test_checkout(api, secrets):
    token = secrets.get("API_TOKEN")
    response = api.get("/orders", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
```
