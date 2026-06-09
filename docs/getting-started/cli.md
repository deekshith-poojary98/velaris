# CLI Reference

## `velaris init`

Create a new project with `velaris.toml`, a passing browser test, and a README.

```bash
velaris init <project-name>
```

Examples:

```bash
velaris init demo
velaris init projects/demo
```

Output:

```text
Created project: demo

Next steps:

cd demo
velaris run
```

Fails if the target directory already exists. Creates parent directories when needed.

## `velaris run`

```bash
velaris run [paths...] [options]
```

Execute Velaris tests.

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `paths` | `tests` | Files or directories to collect |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--config` | `velaris.toml` | Path to configuration file |
| `--verbose` | — | Show lifecycle events (run, resolve, pass/fail, teardown) |
| `--debug` | — | Show all events including capability observations |
| `--json-log` | — | Write JSON-lines event log to PATH |
| `--html-report` | — | Generate HTML report after the run (default: `report.html`) |

Generate a report in one command:

```bash
velaris run tests/ --html-report
open report.html
```

Custom paths:

```bash
velaris run tests/ --html-report artifacts/report.html
# also writes artifacts/report.jsonl (unless --json-log overrides)
```

Or keep the two-step flow for re-generating reports from an existing log:

```bash
velaris run tests/ --json-log run.jsonl
velaris report run.jsonl
```

### `velaris report`

Generate a static HTML report from a JSON event log.

```bash
velaris report run.jsonl [-o report.html]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `json_log` | (required) | Path to JSON-lines file from `velaris run --json-log` |
| `-o`, `--output` | `report.html` | Output HTML path |

Typical workflow:

```bash
velaris run tests/ --json-log run.jsonl
velaris report run.jsonl
```

See [HTML Report](/html-report) for architecture and examples.

### Examples

```bash
# Run all tests in tests/
velaris run tests/

# Single file
velaris run tests/test_login.py

# Custom config
velaris run tests/ --config velaris.fake.toml

# Structured debug log (full event detail always written to file)
velaris run tests/ --config velaris.fake.toml --json-log events.jsonl

# Framework lifecycle visibility
velaris run tests/ --verbose

# Full debug trace (pre-v0.1 default stdout behavior)
velaris run tests/ --debug
```

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | All tests passed |
| `1` | One or more tests failed |
| `2` | CLI usage error |

## Event output

Default stdout is result-focused:

```text
✓ test_login

Passed: 1
Failed: 0
Duration: 0.00s
```

Use `--verbose` for lifecycle events (`RUN`, `RESOLVE`, `PASS`/`FAIL`, `TEARDOWN`) or `--debug` for the full capability observation trace. See [CLI UX redesign](/cli-ux-redesign) for details.

JSON log entries always include full event detail regardless of stdout mode:

```json
{"type": "TestStarted", "test": "test_login", "name": "test_login"}
{"type": "CapabilityObserved", "test": "test_login", "capability": "browser", "action": "open", "data": {"path": "/login"}}
```

## Working directory

Run from the project root that contains:

- `velaris.toml` (or pass `--config`)
- `velaris_plugins.py` (if using external capabilities)

Running from the wrong directory silently skips plugin registration.
