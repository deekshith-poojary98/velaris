# Browser example

Stress-tests a **stateful, event-heavy** capability without Playwright or Selenium.

## Run

```bash
cd examples/browser
velaris run tests/ --config velaris.fake.toml
```

Expected output (default stdout):

```text
✓ test_login

Passed: 1
Failed: 0
Duration: 0.00s
```

There is no default `velaris.toml` in this directory — always pass `--config velaris.fake.toml` (or `velaris.verbose.toml`).

## Provider swap

```bash
velaris run tests/ --config velaris.verbose.toml
```

Same test; the `verbose` provider emits richer payloads in `--debug` mode and in JSON logs.

## JSON log and HTML report

```bash
velaris run tests/ --config velaris.fake.toml --json-log events.jsonl
velaris run tests/ --config velaris.fake.toml --html-report
open report.html
```

See [events.jsonl.example](events.jsonl.example) for sample structured output (`CapabilityObserved` format).
