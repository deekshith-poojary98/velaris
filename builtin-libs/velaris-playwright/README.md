# velaris-playwright

Playwright-based browser capability provider for the Velaris testing framework.

## Installation

```bash
pip install -e .
playwright install chromium
```

## Configuration

Reference the provider in your `velaris.toml` configuration:

```toml
[capabilities.browser]
provider = "playwright"

[capabilities.browser.options]
browser_type = "chromium" # chromium, firefox, or webkit
headless = true
```

## Running Examples

```bash
velaris run examples/tests/ --config examples/velaris.toml --debug
```

---

# SDK Sufficiency Report

### Most Important Question
Can a real Playwright browser capability be implemented entirely through the existing public Velaris SDK and contracts without modifying Velaris core?
**No** (when running via the `velaris run` CLI).

### Public APIs Used
- `velaris_core.sdk.Registry`
- `velaris_core.sdk.ProviderFactory`
- `velaris_core.sdk.pop_emit`
- `velaris_core.sdk.capability_observed`
- `velaris_core.sdk.Teardown`
- `velaris_contracts.Browser`

### APIs That Felt Missing
- A way to register new provider names dynamically with the config loader, or a deferred validation mechanism that queries the fully populated `Registry` instead of a hardcoded map.

### Awkward Areas
- Custom provider validation happens inside `load_config` (which checks a hardcoded module-level list `KNOWN_PROVIDERS` in `velaris_core/config.py`). Since config loading occurs before `register_builtin_providers` runs to load custom plugins, `velaris run` crashes on config parsing before our plugin registration hook (`velaris_plugins.py`) can execute.

### Core Changes Required?
Yes.

### Required Changes Outside `velaris-playwright/`

1. **Required file**: [config.py](file:///Users/deekshithpoojari/Desktop/Projects/velaris/packages/velaris-core/velaris_core/config.py)
   - **Reason**: The module-level hardcoded dictionary `KNOWN_PROVIDERS` is used during config loading to throw `UnknownProviderError` if a provider (like `playwright`) isn't listed.
   - **Suggested SDK improvement**: Either defer validation of capability/provider bindings until the resolver queries the registry, or populate `KNOWN_PROVIDERS` dynamically by loading plugins before configuration validation.
