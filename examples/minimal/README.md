# Minimal Example (HTTP + secrets)

Demonstrates `api` + `secrets` capabilities, provider swap, and multi-capability tests.

**Not a first-run example.** Start with [browser](../browser/) or [authoring](../authoring/) if you are new to Velaris.

## Prerequisites

- `API_TOKEN` in the environment (for checkout-style tests)
- HTTP reachable at `base_url` in `velaris.toml`, **or** mock HTTP in tests (see below)

```bash
export API_TOKEN=demo-token
```

## Run

```bash
cd examples/minimal
velaris run tests/
```

**Expect failures on a fresh clone:** four tests are collected; `test_missing_secret.py` is an **intentional failure** demo (missing secret key).

Run only the passing subset:

```bash
velaris run tests/test_users.py tests/test_token.py tests/test_checkout.py
```

(Still needs HTTP mock or a reachable server for API tests.)

## Provider swap

```bash
API_TOKEN=swap-demo-token velaris run tests/test_token.py --config velaris.env-secrets.toml
velaris run tests/test_token.py --config velaris.static-secrets.toml
```

## HTTP mocking

The framework test suite mocks `http://testserver` with `responses`. This example does not include mocks by default. Either:

- Point `base_url` at a real test server, or
- Add `responses` decorators in your own tests (see [docs/examples/minimal.md](../../docs/examples/minimal.md))

## Config files

| File | Purpose |
|------|---------|
| `velaris.toml` | Default: `api` → requests, `secrets` → env |
| `velaris.env-secrets.toml` | Secrets from environment |
| `velaris.static-secrets.toml` | Secrets from TOML `values` table |

## Learn

- [api@0.1](../../docs/guide/capabilities/api.md)
- [secrets@0.1](../../docs/guide/capabilities/secrets.md)
