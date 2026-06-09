# Reporting Example

Generate a JSON event log during a run, then build a static HTML report.

**Location:** `examples/reporting/`

## One command

```bash
cd examples/browser
velaris run tests/ --config velaris.fake.toml --html-report
open report.html
```

## Two-step flow

```bash
velaris run tests/ --json-log run.jsonl
velaris report run.jsonl
open report.html
```

## Pre-generated example

Open `examples/reporting/report.example.html` in a browser — a multi-test report from the authoring example (Python + YAML + BDD).

Regenerate:

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

No server, no database — one `report.html` file.

## Learn

- [HTML Report](/html-report)
- [Events & Reporting](/concepts/events)
- [CLI Reference](/getting-started/cli)
