# Examples

Runnable projects in the repository. Each demonstrates a different aspect of Velaris.

See `examples/README.md` in the repository for the recommended order and cwd rules.

| Example | Passes out of box | Demonstrates |
|---------|-------------------|--------------|
| [Browser](/examples/browser) | Yes | Stateful capability, provider swap |
| [Authoring](/examples/authoring) | Yes | Python + YAML + BDD → same TestSpec |
| [Stress test](/examples/stress-test) | Yes | External capabilities, multi-cap |
| [Plugins](/examples/plugins) | Yes (from example dir) | Plugin SDK, clock capability |
| [Reporting](/examples/reporting) | Yes | JSON log + HTML report |
| [Composition](/examples/composition) | Needs HTTP mock | Model A composition styles |
| [Minimal](/examples/minimal) | Needs env + HTTP | api + secrets basics |

## Recommended path

1. [Browser](/examples/browser) — first run, no setup
2. [Authoring](/examples/authoring) — three authoring styles, one engine
3. [Stress test](/examples/stress-test) — external capabilities
4. [Plugins](/examples/plugins) — write a capability
5. [Reporting](/examples/reporting) — HTML report from event log
6. [Composition](/examples/composition) — config patterns
7. [Minimal](/examples/minimal) — HTTP + secrets (advanced)

## Run any example

```bash
cd examples/<name>
velaris run tests/ [--config <file>]
```

Generate an HTML report:

```bash
velaris run tests/ --html-report
open report.html
```

::: warning Working directory
Examples with `velaris_plugins.py` must run from their own directory.
:::
