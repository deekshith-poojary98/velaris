# velaris-core

Execution engine for Velaris: collection, configuration, registry, resolver, runner, events, authoring adapters, and reporting.

## Install

Install with contracts:

```bash
pip install -e ../velaris-contracts -e ".[dev]"
```

The `velaris` CLI entry point is defined in this package.

## Commands

```bash
velaris run tests/ [--config velaris.toml] [--html-report] [--json-log PATH]
velaris report run.jsonl [-o report.html]
```

## Run tests

```bash
pytest
```

## Modules

| Module | Role |
|--------|------|
| `adapters/` | Python, YAML, BDD → TestSpec |
| `compose.py` | Optional config merge conventions before resolve |
| `bootstrap.py` | Central provider registration |
| `cli.py` | `velaris run`, `velaris report` |
| `collector.py` | Adapter dispatcher |
| `runner.py` | Execution loop |
| `testspec.py` | Minimal TestSpec IR |
| `decorators.py` | `@test` marker |
| `resolver.py` | Per-test capability resolution |
| `registry.py` | Provider factory registry |
| `config.py` | `velaris.toml` loading |
| `events.py` | Lifecycle + capability + session events |
| `reporting.py` | `Reporter` Protocol, event multiplex |
| `stdout_reporter.py` | Terminal output (default / verbose / debug) |
| `json_reporter.py` | JSON-lines reporting |
| `report_loader.py` | Load JSONL → report model |
| `html_report.py` | Static HTML report generator |
| `provider_context.py` | Internal `_emit` option helper |
| `providers.py` | secrets, target_environment providers |
| `providers_api.py` | api (requests) provider |
| `providers_browser.py` | browser (fake) providers |
