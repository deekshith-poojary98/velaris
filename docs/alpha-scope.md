# Alpha scope

Velaris **v0.1.0-alpha** is a public preview of the capability-driven execution engine. Expect rough edges in onboarding and plugin ergonomics.

## Stable in alpha

These behaviors are covered by tests and intended to remain consistent:

- `velaris run` execution loop
- Multi-format collection → TestSpec → runner (Python, YAML, minimal BDD)
- Config binding via `velaris.toml`
- Per-test resolver with LIFO teardown
- Event model (`EventEnvelope`, `CapabilityObserved`, lifecycle events)
- Plugin SDK (`velaris_core.sdk`)
- Model A — independent capabilities composed in test code
- CLI output modes (default / `--verbose` / `--debug`)
- Static HTML report (`velaris report` or `velaris run --html-report`)

## Experimental in alpha

- Install path (clone + editable pip only; no PyPI packages yet)
- External capability packaging conventions
- `velaris_plugins.py` loading (cwd-sensitive)
- Config validation for external capabilities
- YAML and BDD adapters (minimal syntax — not full Gherkin/Cucumber)
- Capability version pinning (`@0.1` is documentation-only)

## Not included

| Feature | Status |
|---------|--------|
| Plugin discovery / entry points | Deferred |
| Full Gherkin (tags, outlines, tables, step defs) | Deferred |
| Parallel execution | Deferred |
| Historical report trends / databases | Deferred |
| Real browser drivers (Playwright/Selenium) | Deferred |

## Install note

Alpha requires cloning the repository and installing two editable packages:

```bash
pip install -e packages/velaris-contracts -e "packages/velaris-core[dev]"
```

## Recommended first example

Start with [Browser example](/examples/browser) — runs without network or environment variables.

Then try [Authoring styles](/examples/authoring) — same login test in Python, YAML, and BDD.
