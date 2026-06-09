# Reporting & HTML Report Example

Generate a JSON event log during a run, then build a static HTML report.

## Committed samples

| File | Purpose |
|------|---------|
| `run.example.jsonl` | Current event format (`CapabilityObserved`, `test` correlation) |
| `report.example.html` | Pre-built report from authoring example (Python + YAML + BDD) |

Legacy `CapabilityEvent` logs are not supported by `velaris report`.

## Quick start (browser — passes out of the box)

```bash
cd examples/browser
velaris run tests/ --config velaris.fake.toml --json-log run.jsonl
velaris report run.jsonl
open report.html
```

## Multi-style authoring report

A pre-generated example with Python, YAML, and BDD tests:

```bash
open examples/reporting/report.example.html
```

To regenerate:

```bash
cd examples/authoring
velaris run tests/ --json-log run.jsonl
velaris report run.jsonl -o ../reporting/report.example.html
```

## What you get

- Summary cards: total, passed, failed, duration
- Test list with pass/fail status
- Click a test → capability event timeline
- Failed tests show error type and message

No server, no database — one `report.html` file you can email or archive.

See [HTML Report](../../docs/html-report.md) for architecture and CLI reference.
