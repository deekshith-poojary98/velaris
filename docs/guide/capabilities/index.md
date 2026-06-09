# Built-in Capabilities

Velaris ships four contracts in `velaris-contracts`. Three are commonly used in tests; `target_environment` supports config composition.

| Capability | Version | Providers | Guide |
|------------|---------|-----------|-------|
| `api` | 0.1 | `requests` | [api@0.1](/guide/capabilities/api) |
| `secrets` | 0.1 | `env`, `static` | [secrets@0.1](/guide/capabilities/secrets) |
| `browser` | 0.1 | `fake`, `verbose` | [browser@0.1](/guide/capabilities/browser) |
| `target_environment` | 0.1 | `static` | [target_environment@0.1](/guide/capabilities/target-environment) |

## Quick reference

```python
@test("api")
def test_api(api): ...

@test("secrets")
def test_secrets(secrets): ...

@test("browser")
def test_browser(browser): ...

@test("api", "secrets")
def test_multi(api, secrets): ...
```

## External capabilities

Built-in capabilities live in `velaris-contracts`. Custom capabilities live in your project — see [Plugin Author Guide](/guide/plugin-author).

Examples in the repository:

| Capability | Location |
|------------|----------|
| `clock` | `examples/plugins/` |
| `database`, `filesystem`, `random` | `examples/stress-test/` |
