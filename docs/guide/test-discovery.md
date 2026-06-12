# Test Discovery (`velaris collect`)

`velaris collect` answers a simple question: **what tests will run, and what do they need?** — without running anything.

```bash
velaris collect
# or
velaris collect tests/
```

```text
Found 3 tests

test_login
  source: tests/test_login.py
  authoring_style: python
  capabilities:
    - browser

test_login_yaml
  source: tests/test_login.yaml
  authoring_style: yaml
  capabilities:
    - browser

User logs in
  source: tests/login.feature
  authoring_style: bdd
  capabilities:
    - browser
```

## What collect does

It runs only the first half of the pipeline and then stops:

```text
Collect → TestSpec        ← velaris collect stops here
→ Resolve → Execute → Events → Report   ← only velaris run does this
```

For each discovered test, `collect` reports:

| Field | Meaning |
|-------|---------|
| name | The test's name |
| source | The file it was discovered in |
| authoring_style | Which frontend produced it — `python`, `yaml`, or `bdd` |
| capabilities | What the test declares it needs |
| tags | Optional classification labels associated with the test |

It does **not** load configuration, look up providers, create capability
instances, run the test body, or emit events.

## collect vs run

| | `velaris collect` | `velaris run` |
|--|-------------------|---------------|
| Collects tests | Yes | Yes |
| Builds TestSpec | Yes | Yes |
| Reads `velaris.toml` | No | Yes |
| Resolves providers | No | Yes |
| Executes test bodies | No | Yes |
| Produces reports | No | Yes |
| Fails on collection errors | Yes | Yes |

Both share the same collection and validation logic, so anything that breaks
collection (a duplicate test name, a test with no capabilities) fails the same
way in both:

```text
CollectionError:
Duplicate test name: 'test_login'
```

## Why it exists

The TestSpec — Velaris's internal, format-agnostic representation of a test —
is the architectural heart of the framework, but until now it was invisible.
`collect` makes it observable:

- **See the engine's view.** Python, YAML, and BDD all compile down to the same
  shape. `collect` shows that three different files produced three comparable
  tests with the same `browser` capability.
- **Debug discovery, not execution.** Confirm a test was found, in the right
  file, with the capabilities you expect — before dealing with config or
  providers.
- **Inspect without side effects.** Nothing is executed, so it is safe to run
  anywhere, anytime.

## JSON output

For tooling and CI, add `--json` for a stable, machine-readable array:

```bash
velaris collect tests/ --json
```

```json
[
  {
    "name": "test_login",
    "authoring_style": "python",
    "source": "tests/test_login.py",
    "capabilities": ["browser"],
    "tags": []
  }
]
```

This is the first public serialization of TestSpec-like information. It exposes
only discovery facts — never the underlying callable or any execution detail.

## Working directory

Like `velaris run`, `collect` resolves `source` paths relative to where you run
it. Run it from your project root (the directory containing `tests/`) for clean,
relative paths.
