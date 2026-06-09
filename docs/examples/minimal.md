# Minimal Example

Basic `api` + `secrets` tests. Demonstrates provider swap and multi-capability resolution.

**Location:** `examples/minimal/`

::: warning Setup required
These tests **fail on first run** without environment variables and HTTP mocking. Start with [Browser](/examples/browser) instead.
:::

## Prerequisites

```bash
export API_TOKEN=demo-token
# Mock HTTP or point base_url at a reachable server
```

## Run

```bash
cd examples/minimal
velaris run tests/
```

## Provider swap

```bash
API_TOKEN=swap-demo-token velaris run tests/test_token.py --config velaris.env-secrets.toml
velaris run tests/test_token.py --config velaris.static-secrets.toml
```

## Tests

```python
@test("api")
def test_users(api):
    response = api.get("/users")
    assert response.status_code == 200

@test("api", "secrets")
def test_checkout(api, secrets):
    token = secrets.get("API_TOKEN")
    response = api.get("/orders", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
```

## Config

```toml
[capabilities.api]
provider = "requests"

[capabilities.api.options]
base_url = "http://testserver"

[capabilities.secrets]
provider = "env"
```

## HTTP mocking with responses

Framework tests use `responses` to mock `http://testserver`. Apply the same pattern in your tests or CI:

```python
import responses

@responses.activate
def test_with_mock():
    responses.add(responses.GET, "http://testserver/users", status=200)
    ...
```

## Learn

- [api@0.1](/guide/capabilities/api)
- [secrets@0.1](/guide/capabilities/secrets)
