# Velaris Roadmap

| Field | Value |
|-------|-------|
| Status | Active |
| Updated | 2026-06-02 |
| Scope | Hobby framework — learning and architectural clarity |

This roadmap reflects **what exists in code today** and the next steps for validating the capability model. It does not optimize for enterprise adoption.

---

## Completed

### Minimal execution engine

- `@test` collection, manual registry, resolver, runner, events, stdout reporter
- `api@0.1` with `requests` provider
- `velaris run tests/` CLI

### Multiple capability validation

- `secrets@0.1` with `env` provider
- Multi-cap tests, LIFO teardown, failure handling
- Event sequence: RUN → RESOLVE → PASS/FAIL → TEARDOWN (visible with `--verbose` / `--debug`; default stdout is ✓/✗ only)

### Repository consolidation

- Removed legacy `src/velaris` duplicate package
- Archived governance and superseded planning docs
- Single install path via `velaris-core` + `velaris-contracts`

---

### Explicit bootstrap (manual plugins)

- `bootstrap.py` — sole registration point for all built-in providers
- Runner imports only `bootstrap`, not individual provider modules
- Explicit `@test("api", "secrets")` capability declaration
- Provider swap demo: `test_token.py` with `env` vs `static` secrets configs

---

### Capability composition (Model A)

- `api` + `secrets` + `target_environment` validated via three composition styles
- `compose.py` — optional bootstrap config merge (no resolver changes)
- Examples in `examples/composition/`

---

### Reporting & observability

- `Reporter` Protocol + `multiplex()` event bus
- `JsonReporter` (JSON-lines) alongside stdout
- `CapabilityObserved` from providers; `RunFinished` session summary
- `--json-log` CLI flag

---

### TestSpec IR

- `TestSpec` — minimal format-agnostic test representation
- Python, YAML, and BDD adapters produce validated `TestSpec`
- Runner executes `TestSpec` only (not format-specific types)

---

### Browser capability (minimal)

- `browser@0.1` contract + `FakeBrowser` / `FakeBrowserVerbose` providers
- Stateful capability stress-test; no Playwright/Selenium

---

### Event model hardening

- `EventEnvelope` correlates every event with `test` (or `null` for session)
- `CapabilityObserved` replaces `CapabilityEvent` — action + `data` dict
- JSON logs partitionable via `test` field

---

### Plugin SDK (manual extension)

- `velaris_core.sdk` — public surface for capability authors (~7 symbols)
- `plugin_loader` — loads project-local `velaris_plugins.py` from cwd
- `examples/plugins/` — external `clock@0.1` with `FixedClock` provider
- Runner, resolver, and reporting unchanged

---

### Architecture stress test

- Three external capabilities: `database@0.1`, `filesystem@0.1`, `random@0.1`
- Seven example tests including three-capability composition
- [Architecture Stability Report](architecture-stability-report.md) — friction findings
- Core execution path unchanged

---

### Authoring style architecture

- `AuthoringAdapter` Protocol — `extensions` + `collect(path) -> list[TestSpec]`
- `PythonAdapter` (refactored, unchanged behavior) + minimal `YamlAdapter`
- `collector.collect` is now a dispatcher; runner/resolver/reporting unchanged
- `TestSpec.callable` defaults to a no-op body for declaration-only styles
- `examples/authoring/` — Python + YAML tests sharing one capability
- [Authoring Style Architecture](authoring-styles.md) — diagram, interface, BDD design, risks

---

### Executable YAML

- `YamlAdapter` compiles `actions` (serialized capability calls) into a callable
- `adapters/yaml_actions.py` — `ast`-based structural parser + callable generator
- Compile-time errors: syntax, shape, unknown capability, non-literal args
- Python and executable YAML emit identical event streams (verified)
- Runner / resolver / reporting / TestSpec unchanged (0 LOC)
- [Executable YAML](executable-yaml.md) — architecture, event parity, risks, A-vs-B verdict

---

### CLI UX & reporting redesign

- Default stdout: ✓/✗ per test + summary (no resolve/teardown/observations)
- `--verbose` — lifecycle events; `--debug` — full trace (legacy default)
- Failure output: scannable ✗ + exception type + message
- Event bus and JSON reporter unchanged; filtering in `StdoutReporter` only
- [CLI UX Redesign](cli-ux-redesign.md) — modes, filtering strategy, samples, risks

---

### Minimal BDD adapter

- `BddAdapter` — `.feature` files compile to TestSpec via shared `yaml_actions` compiler
- Given/When/Then are serialized capability calls (no keyword engine, no step matching)
- Capabilities inferred from steps; Python / YAML / BDD emit identical browser events
- Runner / resolver / reporting unchanged (0 LOC)
- [BDD Adapter](bdd-adapter.md) — architecture, parity proof, risks

---

### Static HTML report

- `velaris report run.jsonl` → single self-contained `report.html`
- Consumes existing `--json-log` output only; no runner/resolver/event changes
- Summary cards, test list, detail view, capability timeline
- [HTML Report](html-report.md) — architecture, CLI, risks

---

## Deferred

| Topic | Reason |
|-------|--------|
| Full Gherkin (tags, outlines, tables, And/But) | Would pull toward keyword engine / second model |
| YAML variables / data flow / conditionals | The A→B line; intentionally refused |
| IR serialization / JSON schema | Not required yet |
| Plugin discovery | Manual bootstrap works |
| pytest coexistence | Different project than hobby runner |
| Parallel execution | Needs serial correctness proven |
| Real browser drivers (Playwright/Selenium) | Deferred — fake/verbose providers only in alpha |
| Enterprise profiles / governance | Not the hobby vision |

See [archive/](archive/) for superseded enterprise roadmap and governance strategy.
