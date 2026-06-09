# secrets@0.1

Read-only access to named secret values.

## Contract

```python
from velaris_contracts.secrets.v0_1 import Secrets
```

```python
class Secrets(Protocol):
    def get(self, name: str) -> str: ...  # raises KeyError if missing
```

## Providers

### `env`

Reads from environment variables.

```toml
[capabilities.secrets]
provider = "env"
```

Optional required list fails setup early if vars missing:

```toml
[capabilities.secrets.options]
required = ["API_TOKEN"]
```

```bash
API_TOKEN=demo velaris run tests/
```

### `static`

Reads from config values table.

```toml
[capabilities.secrets]
provider = "static"

[capabilities.secrets.options.values]
API_TOKEN = "demo-token"
```

## Test example

```python
from velaris_core.decorators import test

@test("secrets")
def test_token(secrets):
    token = secrets.get("API_TOKEN")
    assert token.startswith("demo")
```

## Provider swap

Same test, different config — no code changes:

```bash
velaris run tests/test_token.py --config velaris.env-secrets.toml
velaris run tests/test_token.py --config velaris.static-secrets.toml
```

## Events

Emits `CapabilityObserved` with action `resolved` at setup time.

## Failure behavior

Missing secret → `KeyError` during test → `TestFailed` with message `'API_TOKEN'`.

Use `required` in env provider config to fail at resolve time instead.
