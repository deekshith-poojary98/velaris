# Configuration

Velaris reads capability bindings from `velaris.toml` in the working directory (or a path passed to `--config`).

## Basic structure

```toml
[capabilities.api]
provider = "requests"

[capabilities.api.options]
base_url = "http://testserver"

[capabilities.secrets]
provider = "env"
```

Each capability section has:

| Key | Required | Description |
|-----|----------|-------------|
| `provider` | Yes | Provider name registered in the registry |
| `options` | No | Provider-specific configuration table |

## Built-in capabilities

| Capability | Providers | Common options |
|------------|-----------|----------------|
| `api` | `requests` | `base_url` |
| `secrets` | `env`, `static` | `values` (static), `required` (env) |
| `browser` | `fake`, `verbose` | — |
| `target_environment` | `static` | `environment`, `endpoints` |

See [Capability Guide](/guide/capabilities/) for details.

## Static secrets example

```toml
[capabilities.secrets]
provider = "static"

[capabilities.secrets.options.values]
API_TOKEN = "demo-token"
```

## Environment override

Set a provider via environment variable without editing TOML:

```bash
export VELARIS__CAPABILITIES__SECRETS__PROVIDER=static
```

Pattern: `VELARIS__CAPABILITIES__<CAPABILITY>__PROVIDER`

## Nested options

External plugins can use nested tables:

```toml
[capabilities.database.options.seed.users.alice]
name = "Alice"
role = "admin"
```

## Config file location

```bash
# Default: ./velaris.toml
velaris run tests/

# Explicit path
velaris run tests/ --config path/to/velaris.toml
```

## Validation

Built-in capabilities validate provider names at config load time. External capabilities (from plugins) validate at resolution time — typos surface as `UnknownProviderError` when the test runs.

## Bootstrap merge (optional)

If `api.options.base_url` is unset and `target_environment.endpoints.api` exists, `compose.py` copies the URL before resolution. See [Model A Composition](/architecture/model-a).
