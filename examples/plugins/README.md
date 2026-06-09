# External plugins example

Demonstrates adding a capability **outside** `velaris-core` and `velaris-contracts`.

## Layout

```text
examples/plugins/
├── velaris.toml           # binds clock → fixed provider
├── velaris_plugins.py     # manual registration hook
├── clock/
│   ├── contract.py      # clock@0.1 Protocol (local, not in velaris-contracts)
│   └── provider.py      # FixedClock provider factory
└── tests/
    └── test_clock.py
```

## Run

**Must run from this directory** — `velaris_plugins.py` is loaded from the current working directory only.

```bash
cd examples/plugins
velaris run tests/
```

Expected output (default stdout):

```text
✓ test_fixed_time

Passed: 1
Failed: 0
Duration: 0.00s
```

Use `--debug` to see `RESOLVE clock(fixed)` and `clock.now` capability observations.

## Registration flow

1. Author contract + provider using `velaris_core.sdk`.
2. Expose `register(registry)` in `velaris_plugins.py` at the project root.
3. Bind the capability in `velaris.toml`.
4. Declare `@test("clock")` and use the injected parameter name (`clock`).

No changes to runner, resolver, or reporting are required.

See [Plugin author guide](/guide/plugin-author) on the docs site.
