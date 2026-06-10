# Examples

Runnable projects in the repository, each demonstrating a different aspect of Velaris.

::: tip New to Velaris?
Start with the [Quickstart](/getting-started/quickstart) and `velaris init` instead of the examples. The examples are best **after** your first passing test.
:::

::: warning Working directory matters
Always `cd` into an example's own directory before running it. Examples that contain a `velaris_plugins.py` are cwd-sensitive and will fail if run from the repo root.
:::

## Recommended first examples

Both pass out of the box with no extra setup.

### Browser

- **Purpose:** Stateful capability and provider swapping (fake vs verbose).
- **Difficulty:** Beginner
- **Requirements:** None
- **Passes out of the box:** Yes

```bash
cd examples/browser
velaris run tests/ --config velaris.fake.toml
```

### Authoring

- **Purpose:** Python + YAML + BDD all compiling to one engine.
- **Difficulty:** Beginner
- **Requirements:** None
- **Passes out of the box:** Yes

```bash
cd examples/authoring
velaris run tests/
```

## More examples

| Example | Purpose | Difficulty | Requirements | Passes out of box |
|---------|---------|------------|--------------|-------------------|
| [Stress test](/examples/stress-test) | External + multi-capability tests | Intermediate | None | Yes |
| [Plugins](/examples/plugins) | Plugin SDK, custom `clock` capability | Intermediate | Run from example dir | Yes |
| [Reporting](/examples/reporting) | JSON log → static HTML report | Intermediate | None | Yes |

## Advanced examples

These need extra setup and are **not** good first runs.

| Example | Purpose | Difficulty | Requirements | Passes out of box |
|---------|---------|------------|--------------|-------------------|
| [Composition](/examples/composition) | Model A composition styles | Advanced | HTTP mock | No — needs setup |
| [Minimal](/examples/minimal) | `api` + `secrets` basics over HTTP | Advanced | `API_TOKEN` env + HTTP mock | No — needs setup |

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
