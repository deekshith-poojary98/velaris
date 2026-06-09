# Velaris Examples

Runnable projects demonstrating capabilities, authoring styles, plugins, and reporting.

## Recommended order (first-time users)

| # | Directory | Passes out of the box? | Start here |
|---|-----------|------------------------|------------|
| 1 | [browser/](browser/) | **Yes** | `cd examples/browser` then `velaris run tests/ --config velaris.fake.toml` |
| 2 | [authoring/](authoring/) | **Yes** | Python + YAML + BDD → same engine |
| 3 | [stress-test/](stress-test/) | **Yes** | External capabilities (`database`, `filesystem`, `random`) |
| 4 | [plugins/](plugins/) | **Yes** | External `clock` capability via plugin SDK |
| 5 | [reporting/](reporting/) | **Yes** | Pre-built HTML sample; or run browser/authoring with `--html-report` |
| 6 | [composition/](composition/) | No | Needs HTTP mock — see that README |
| 7 | [minimal/](minimal/) | No | Needs `API_TOKEN` + HTTP mock — **not** a first-run target |

## Working directory rules

**Always `cd` into the example directory before `velaris run`.**

| Example | Why |
|---------|-----|
| `plugins/`, `stress-test/`, `authoring/` | `velaris_plugins.py` is loaded from **current working directory** only |
| `browser/` | No `velaris.toml` — use `--config velaris.fake.toml` |
| All examples | Config paths are relative to cwd |

Running from the repo root without `cd` will miss plugins or use the wrong config:

```bash
# Wrong
velaris run examples/plugins/tests/

# Right
cd examples/plugins && velaris run tests/
```

## HTML report (one command)

```bash
cd examples/browser
velaris run tests/ --config velaris.fake.toml --html-report
open report.html
```

## Doc-only

[testspec/](testspec/) explains TestSpec IR concepts — no tests to run.

## Learn more

- [Examples on the docs site](../docs/examples/)
- [Getting started](../docs/getting-started/first-test.md)
