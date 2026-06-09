# Stress Test Example

Three external capabilities built to surface architectural friction — not production usefulness.

**Location:** `examples/stress-test/`

## Run

```bash
cd examples/stress-test
velaris run tests/
```

::: warning Working directory
Must run from `examples/stress-test/` — `velaris_plugins.py` is loaded from cwd only.
:::

Seven tests pass, including a three-capability composed test. Default stdout shows `✓` per test; use `--debug` for resolve and capability observation lines.

## Capabilities

| Capability | Provider | Methods |
|------------|----------|---------|
| `database@0.1` | `memory` | `get_row`, `insert_row` |
| `filesystem@0.1` | `memory` | `read_text`, `write_text` |
| `random@0.1` | `seeded` | `number(minimum, maximum)` |

Implementation folder for `random` is `rng/` to avoid shadowing Python's stdlib `random` module.

## Composed test

```python
@test("database", "filesystem", "random")
def test_independent_capabilities_composed(database, filesystem, random):
    user_id = str(random.number(minimum=1000, maximum=9999))
    database.insert_row("sessions", user_id, {"status": "active"})
    filesystem.write_text(f"/sessions/{user_id}.json", f'{{"id": "{user_id}"}}')
    ...
```

Model A: three independent capabilities, wired in test code. LIFO teardown: `random` → `filesystem` → `database`.

## Config snippet

```toml
[capabilities.database.options.seed.users.alice]
name = "Alice"
role = "admin"

[capabilities.filesystem.options.files]
"/data/input.txt" = "seed-content"

[capabilities.random.options]
seed = 42
```

## Learn

- [Architecture Stability Report](/architecture-stability-report)
- [Model A Composition](/architecture/model-a)
