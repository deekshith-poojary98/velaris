# Architecture Stability Report

::: warning Milestone 8 snapshot (2026-06-02)
Historical friction report from the stress-test milestone. **Authoring adapters (Python, YAML, BDD) shipped in M9–12** after this report was written. Use [authoring styles](/authoring-styles) and [roadmap](/roadmap) for current capabilities.
:::

| Field | Value |
|-------|-------|
| Milestone | 8 — Architecture Stress Test |
| Date | 2026-06-02 |
| Method | Build three external capabilities; observe friction; do not change core |

Three capabilities were implemented **outside** `velaris-core` and `velaris-contracts` using the Milestone 7 plugin SDK:

- `database@0.1` — in-memory row store (`memory` provider)
- `filesystem@0.1` — in-memory files (`memory` provider)
- `random@0.1` — seeded integers (`seeded` provider)

See [examples/stress-test](../examples/stress-test/) for contracts, providers, events, and seven tests (including a three-capability composed test).

Core modules **unchanged:** `runner`, `resolver`, `reporting`, `TestSpec`.

---

## 1. What felt easy?

**Provider factory pattern.** After one capability (`clock`), the second and third followed the same shape: `pop_emit(options)` → construct instance → return `(instance, teardown)`. No surprises.

**Independent capabilities compose naturally.** The composed test declares `@test("database", "filesystem", "random")` and receives three unrelated instances. Model A holds — no dependency graph required.

**Config binding scales to nested options.** Seeding a database table and pre-populating filesystem paths via TOML nested tables worked without framework changes:

```toml
[capabilities.database.options.seed.users.alice]
name = "Alice"
role = "admin"
```

**Event emission is lightweight.** Calling `capability_observed("database", "get_row", {...})` from provider methods required no reporter changes. JSON logs capture all actions uniformly.

**Manual registration stays predictable.** One `velaris_plugins.py` registers all three providers; `velaris run` from the example directory just works.

**Multi-cap teardown order is visible and correct.** LIFO teardown (`random` → `filesystem` → `database`) matches resolution order reversal in stdout.

---

## 2. What felt awkward?

**Capability id vs Python package name.** The capability is `random@0.1`, but the implementation folder is `rng/` because a top-level `random/` package shadows Python’s stdlib `random`. Capability naming conventions do not align with import ergonomics.

**Parameter name must match capability id.** `@test("random")` requires a parameter named `random`, which shadows the stdlib module in test files if you need `import random`. Authors must use aliases or avoid importing stdlib names that match capability ids.

**Stdout reporter is capability-specific, not generic.** Built-in capabilities (`api`, `browser`) have tailored stdout formatting. External capabilities fall through to generic `capability.action` lines. Observations are structurally correct but human-readable output is uneven across capabilities.

**No shared contract packaging story.** Each external capability duplicates the Protocol + `CAPABILITY_ID` + `CONTRACT_VERSION` boilerplate locally. There is no recommended layout for publishing contracts separately from providers.

**Stateful teardown is ad hoc.** Database and filesystem providers clear internal dicts in teardown by closing over `instance._tables` / `instance._files`. There is no lifecycle interface — authors choose their own cleanup pattern.

**Config validation is asymmetric.** Built-in capabilities are listed in `KNOWN_PROVIDERS`; external ones are not. Typos in provider names fail at resolution, not at config load. Error messages for external caps are less helpful.

**cwd-based plugin loading.** Running `velaris run` from the wrong directory silently skips external registration (only built-ins run). Easy to misconfigure without an explicit error.

**Nested TOML for complex seed data gets verbose.** Fine for a hobby project; would become tedious for large fixtures without a higher-level seeding convention (out of scope for v0.1).

---

## 3. Which abstractions were reused?

| Abstraction | Reuse across all three caps |
|-------------|----------------------------|
| `velaris_core.sdk` (`Registry`, `pop_emit`, `capability_observed`, `Teardown`) | Yes — sole framework import surface |
| Provider factory `(options) -> (instance, teardown)` | Yes |
| `typing.Protocol` contracts | Yes |
| `velaris_plugins.register(registry)` | Yes |
| `[capabilities.*]` TOML binding | Yes |
| `@test("capability")` explicit declaration | Yes |
| `CapabilityObserved` event shape | Yes |
| Per-test `Resolver` scope + LIFO teardown | Yes |

The SDK surface from Milestone 7 was sufficient for all three capabilities with zero framework edits.

---

## 4. Which abstractions leaked?

| Leaked concept | Where it surfaced |
|--------------|-------------------|
| `EMIT_OPTION_KEY` / `_emit` injection | Authors must use `pop_emit`; resolver injects emit via options dict — not visible until you read SDK docs |
| `Registry` key tuple `(capability_id, provider)` | Registration API is simple but provider string must match TOML exactly |
| `KNOWN_PROVIDERS` (core-only) | External capabilities bypass config-time validation — core knowledge leaks into “why doesn’t my typo fail early?” |
| Stdout reporter action whitelist | Browser/api-specific formatters leak the idea that reporting is not fully capability-agnostic for humans |
| `__test__ = False` for pytest coexistence | Example tests need this guard when collected by pytest from monorepo root |
| Parameter name = capability id = injection key | Decorator validation is strict; renaming a param requires renaming the capability declaration |
| Bootstrap calls `register_manual_plugins` | Plugin loading is implicit via cwd, not an explicit user-facing runner option |

Nothing in runner/resolver/TestSpec leaked into provider code — good separation. Leakage is mostly at the **edges**: config validation, reporting ergonomics, and Python import naming.

---

## 5. Which parts of the framework are becoming stable?

These behaved identically across seven stress tests and required no workarounds:

- **Execution loop** — collect → config → register → resolve → invoke → teardown → report
- **TestSpec IR** — collector output consumed by runner unchanged
- **Resolver** — per-test instance cache, binding lookup, emit injection, LIFO teardown
- **Registry** — static `(capability, provider) → factory` map
- **Event envelope model** — `EventEnvelope(test, event)` + typed lifecycle events
- **Plugin SDK** — seven-symbol public surface is enough for realistic (if fake) capabilities
- **Model A composition** — independent capabilities compose in test code without framework support

These are **candidates for a v0.1 stability promise**.

---

## 6. Which parts are still changing?

| Area | Why it still feels provisional |
|------|-------------------------------|
| External contract location | No standard package; local Protocols vs `velaris-contracts` split is unsettled |
| Plugin registration discovery | cwd + `velaris_plugins.py` is manual and silent on miss |
| `KNOWN_PROVIDERS` | Core-maintained list doesn’t scale to external caps |
| Stdout reporting | Capability-specific formatters vs generic fallback — no plugin hook |
| Config schema | No validation of `options` shape per capability/provider |
| Versioning | `@test("database")` does not pin `@0.1`; version constants are documentation-only |
| Composition helpers | `compose.py` conventions exist for built-ins only |
| Error message quality | External capability failures are generic |

---

## LOC impact (Milestone 8)

| Area | Lines (approx.) |
|------|-----------------|
| Three contracts | ~55 |
| Three providers | ~165 |
| Example tests + config + registration | ~95 |
| `test_stress_capabilities.py` | ~55 |
| This report | ~200 |
| **Total new** | **~570** |

Framework core delta: **0 lines** in runner, resolver, reporting, TestSpec.

---

## If Velaris were released as v0.1 today, what would still feel experimental?

**Stable enough to ship:**

- Running Python tests with declared capabilities
- Config-driven provider binding for built-in caps
- Per-test resolution, teardown, and event stream
- Manual plugin extension via SDK + `velaris_plugins.py`

**Would still feel experimental:**

1. **External capability authoring ergonomics** — naming collisions (`random`), no contract package convention, cwd-sensitive registration.
2. **Configuration story** — asymmetric validation, no options schema, nested TOML seeds only by convention.
3. **Observability UX** — JSON logs are consistent; stdout human output favors built-in capabilities.
4. **Versioning and compatibility** — capability versions are not enforced anywhere in the execution path.
5. **Ecosystem boundaries** — unclear when to add to `velaris-contracts` vs keep contracts local; no publishing path for third-party provider wheels.
6. **Authoring formats** — Python, YAML, and minimal BDD adapters exist (M9–12); full Gherkin and advanced YAML features remain deferred.
7. **Composition beyond Model A** — no dependency graphs, no shared setup across capabilities except test code and config merge helpers.

**Bottom line:** The **execution engine and capability injection model** could ship as v0.1. The **plugin ecosystem, config validation, and reporting polish** would read as preview/beta — fine for a hobby release with clear “experimental” labeling on external capabilities and manual registration.

---

## Recommendation (informational only)

No framework changes requested for this milestone. If friction is addressed later, highest leverage in order:

1. Config-path-aware `velaris_plugins.py` loading with explicit failure when missing
2. Generic stdout formatter using `CapabilityObserved.action` + `data` (remove built-in special cases over time)
3. Documented contract package layout (without auto-discovery)

Do not pursue until a future milestone explicitly scopes them.
