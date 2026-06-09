# Plugins Example

External `clock@0.1` capability using the plugin SDK.

**Location:** `examples/plugins/`

## Run

```bash
cd examples/plugins
velaris run tests/
```

::: warning
Must run from `examples/plugins/` — contains `velaris_plugins.py`.
:::

## Layout

```text
examples/plugins/
├── velaris.toml
├── velaris_plugins.py
├── clock/
│   ├── contract.py
│   └── provider.py
└── tests/test_clock.py
```

## Registration

```python
# velaris_plugins.py
from velaris_core.sdk import Registry
from clock.provider import register_clock_providers

def register(registry: Registry) -> None:
    register_clock_providers(registry)
```

## Test

```python
@test("clock")
def test_fixed_time(clock):
    assert clock.now() == "2026-06-02T12:00:00Z"
```

## Config

```toml
[capabilities.clock]
provider = "fixed"

[capabilities.clock.options]
fixed_time = "2026-06-02T12:00:00Z"
```

## Learn

- [Plugin Author Guide](/guide/plugin-author)
- [Providers concept](/concepts/providers)
