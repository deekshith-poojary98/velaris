# Capability Composition Examples

Three ways to combine `api`, `secrets`, and `target_environment` under **Model A** (independent capabilities). The resolver does not know about relationships between capabilities.

**Not a first-run example.** Tests call a real HTTP API — mock HTTP or point `base_url` at a reachable server. Start with [browser](../browser/) if you are new.

```bash
cd examples/composition
```

## 1. Test code (`test_compose_in_test.py`)

The test declares all three capabilities and wires them in Python.

```python
@test("api", "secrets", "target_environment")
def test_compose_in_test(api, secrets, target_environment):
    root = target_environment.endpoint("api").rstrip("/")
    response = api.get(f"{root}/orders", ...)
```

**Config:** `velaris.test-code.toml` — no `api.options.base_url`.

| Pros | Cons |
|------|------|
| Fully explicit; easy to debug | Verbose; wiring repeats across tests |
| No hidden framework behavior | Authors must understand all three contracts |

```bash
velaris run tests/test_compose_in_test.py --config velaris.test-code.toml
```

## 2. Configuration (`test_compose_in_config.py`)

`base_url` is set directly under `[capabilities.api.options]`. `target_environment` documents the environment but the test only needs `api` + `secrets`.

**Config:** `velaris.config.toml` — `base_url` duplicates `endpoints.api`.

| Pros | Cons |
|------|------|
| Simple tests | Duplication between `api.options` and `target_environment.endpoints` |
| No bootstrap magic | Changing environment URL requires editing multiple config keys |

```bash
velaris run tests/test_compose_in_config.py --config velaris.config.toml
```

## 3. Bootstrap convention (`test_compose_in_bootstrap.py`)

`target_environment` appears in config only. `compose.apply_bootstrap_conventions()` copies `endpoints.api` into `api.options.base_url` before resolution if `base_url` is unset.

The test declares only `@test("api", "secrets")`.

| Pros | Cons |
|------|------|
| Single source of truth for URL in config | Convention is implicit — must read docs |
| Test stays short | `target_environment` resolved only if test injects it; here it is config-only |

```bash
velaris run tests/test_compose_in_bootstrap.py --config velaris.bootstrap.toml
```

## Where composition belongs

| Layer | Responsibility |
|-------|----------------|
| **Test code** | Ad-hoc wiring, assertions, headers, paths |
| **Configuration** | Static binding values per capability |
| **Bootstrap conventions** | Documented, optional config merges before resolve |
| **Resolver** | Independent `resolve(id)` only — unchanged |

None of these introduce capability-to-capability dependencies.
