# Composition Example

Three styles of combining `api`, `secrets`, and `target_environment` under Model A.

**Location:** `examples/composition/`

## Styles

| Test file | Config | Composition layer |
|-----------|--------|-------------------|
| `test_compose_in_test.py` | `velaris.test-code.toml` | Test code |
| `test_compose_in_config.py` | `velaris.config.toml` | Configuration |
| `test_compose_in_bootstrap.py` | `velaris.bootstrap.toml` | Bootstrap merge |

## Run

```bash
cd examples/composition

velaris run tests/test_compose_in_test.py --config velaris.test-code.toml
velaris run tests/test_compose_in_bootstrap.py --config velaris.bootstrap.toml
```

::: warning
HTTP tests require mocked endpoints or a reachable `base_url`. Use `responses` in test setup.
:::

## Test code style

```python
@test("api", "secrets", "target_environment")
def test_compose_in_test(api, secrets, target_environment):
    root = target_environment.endpoint("api").rstrip("/")
    response = api.get(f"{root}/orders", ...)
```

## Bootstrap style

Test declares only `@test("api", "secrets")`. URL merged from `target_environment` by `compose.py`.

```toml
# velaris.bootstrap.toml — target_environment holds the URL
[capabilities.target_environment.options.endpoints]
api = "http://testserver"
```

## Learn

- [Model A Composition](/architecture/model-a)
- [target_environment@0.1](/guide/capabilities/target-environment)
