# Environment Diagnostics (`velaris doctor`)

When something is misconfigured, you shouldn't have to read a stack trace to
find out why. `velaris doctor` validates your local setup and explains common
problems in plain language — before you run anything.

```bash
velaris doctor
```

It runs **no tests**, resolves **no capabilities**, and instantiates **no
providers**. Every check reuses the same machinery a real run uses (config
loading, the plugin loader, and collection), so its diagnosis can't disagree
with what `velaris run` would do.

## A healthy project

```text
Velaris Environment Check

✓ Python 3.13
✓ velaris.toml found
✓ tests directory found
✓ 5 tests discovered
✓ browser capability configured
✓ fake provider available

Capabilities used by tests

browser ........ 5 tests

No issues detected.
```

## What it checks

| Area | Validates |
|------|-----------|
| Environment | Python version, `velaris.toml` presence |
| Collection | Tests can be discovered, no duplicate names, no collection errors |
| Capability config | Every configured capability resolves to a registered provider |
| Plugin loading | `velaris_plugins.py` loads cleanly (same path as a real run) |
| Usage audit | Which capabilities tests use, and config/usage mismatches |

## Output symbols

| Symbol | Meaning |
|--------|---------|
| `✓` | Success |
| `⚠` | Warning — non-fatal, worth a look |
| `✗` | Error — will likely break a run |

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Healthy |
| `1` | Warnings only |
| `2` | One or more errors |

This makes `velaris doctor` usable as a CI gate.

## Common failure scenarios

### Missing config

```text
✗ velaris.toml not found

Suggestion:
    velaris init demo
```

### No tests

```text
✗ No tests discovered

Suggestion:
    Create tests/ directory
    or run:
        velaris collect
```

### Unknown provider

```text
✗ Provider 'playwright' is not registered for capability 'browser'

Suggestion:
    Run:
        velaris capabilities
```

### Plugin capability missing a provider

```text
✗ Capability 'random' configured but no provider registered

Suggestion:
    Verify velaris_plugins.py
    and run from the project root
```

### Plugin fails to load

```text
✗ Failed to load velaris_plugins.py

Reason:
    ImportError: No module named 'rng'
```

## Usage audit warnings

`doctor` cross-checks the capabilities your tests declare against the ones your
config binds:

```text
⚠ Capability used by tests but not configured:
    browser

⚠ Capability configured but not used:
    target_environment
```

## JSON output

For tooling and CI, add `--json`:

```bash
velaris doctor --json
```

```json
{
  "errors": [],
  "warnings": [
    "Capability configured but not used: target_environment"
  ],
  "checks": {
    "python": "3.13",
    "config": true,
    "tests_discovered": 12,
    "plugins_loaded": true
  }
}
```
