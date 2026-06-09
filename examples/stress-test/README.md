# Architecture stress test

Three **external** capabilities built with the plugin SDK to surface architectural friction — not production usefulness.

## Capabilities

| Capability | Provider | Contract surface | Events |
|------------|----------|------------------|--------|
| `database@0.1` | `memory` | `get_row`, `insert_row` | `get_row`, `insert_row` |
| `filesystem@0.1` | `memory` | `read_text`, `write_text` | `read_text`, `write_text` |
| `random@0.1` | `seeded` | `number(minimum, maximum)` | `number` |

Each lives under this directory (not in `velaris-contracts` or `velaris-core`). The implementation folder for `random` is named `rng/` to avoid shadowing Python's stdlib `random` module.

## Run

**Must run from this directory** — `velaris_plugins.py` is loaded from the current working directory only.

```bash
cd examples/stress-test
velaris run tests/
```

Expected output (default stdout):

```text
✓ test_independent_capabilities_composed
✓ test_insert_row
... (7 tests)

Passed: 7
Failed: 0
```

Use `--debug` to see `RESOLVE` lines and `capability.action` observation lines.

## Findings

See [Architecture Stability Report](../../docs/architecture-stability-report.md) (historical M8 notes; authoring adapters shipped in M9–12).

## Layout

```text
examples/stress-test/
├── velaris.toml
├── velaris_plugins.py
├── database/   contract.py + provider.py
├── filesystem/ contract.py + provider.py
├── rng/        contract.py + provider.py
└── tests/
```
