# Alpha Readiness Sprint Report

| Field | Value |
|-------|-------|
| Sprint | Alpha Readiness (post M13 approval) |
| Date | 2026-06-02 |
| Scope | Documentation, examples, repository hygiene — **no framework features** |

---

## 1. Files changed

### P0 — Documentation accuracy & example UX

| File | Change |
|------|--------|
| `examples/README.md` | **New** — recommended order, cwd rules, HTML report quick start |
| `examples/minimal/README.md` | **New** — prerequisites, intentional failure, not first-run |
| `examples/plugins/README.md` | Default ✓ stdout; `--debug` for trace |
| `examples/stress-test/README.md` | Same + cwd requirement |
| `examples/browser/README.md` | Default output; `--config` required |
| `examples/authoring/README.md` | cwd + run instructions |
| `examples/composition/README.md` | Not first-run; `cd` required |
| `examples/reporting/README.md` | Sample file table; legacy format note |
| `docs/guide/capabilities/browser.md` | Events table → `--debug` only |
| `docs/concepts/providers.md` | Stdout vs JSON clarification |
| `docs/architecture/execution-pipeline.md` | RESOLVE visible with `--verbose`/`--debug` |
| `docs/concepts/how-velaris-is-different.md` | RESOLVE visibility clarified |
| `docs/examples/stress-test.md` | cwd warning + default stdout |
| `docs/examples/index.md` | Points to `examples/README.md` |
| `examples/reporting/events.jsonl.example` | **Removed** (legacy `CapabilityEvent`) |

### P1 — Hygiene & doc fixes

| File | Change |
|------|--------|
| `.gitignore` | `**/__pycache__/`, `*.pyc` |
| `examples/**/__pycache__/*` | **Untracked** from git |
| `examples/authoring/run.jsonl` | **Untracked** from git |
| `packages/velaris-core/velaris_core/errors.py` | Removed unused `ReportError` |
| `packages/velaris-core/velaris_core/providers_browser.py` | Removed unused `CapabilityObserved` import |
| `packages/velaris-core/tests/test_runner.py` | Removed unused `OutputMode` import |
| `docs/roadmap.md` | TestSpec YAML/BDD; browser deferred wording; event names |
| `docs/rfc/RFC-001-*.md`, `RFC-002-*.md` | RFC-006 links → archive; historical banners |
| `docs/contracts/api-0.1.md` | RFC-006 link fix |
| `docs/architecture-stability-report.md` | M8 banner; authoring formats corrected |
| `docs/alpha-scope.md` | `[dev]` install extras |
| `docs/html-report.md` | ReportError LOC removed; legacy log note |
| `README.md` | `examples/README.md` in layout |

### P2 — Historical labeling

| File | Change |
|------|--------|
| `docs/rfc/RFC-001`, `RFC-002` | Historical design reference banners |
| `docs/archive/rfc/RFC-006` | Archived enterprise pivot banner |
| `docs/authoring-styles.md`, `executable-yaml.md`, `bdd-adapter.md`, `cli-ux-redesign.md`, `html-report.md` | Milestone report banners |
| `docs/plugin-author-guide.md` | Superseded banner → `/guide/plugin-author` |
| `docs/archive/README.md` | Roadmap description fix |

---

## 2. Docs consistency report

| Topic | Before | After |
|-------|--------|-------|
| Default stdout | Some example READMEs showed `RUN`/`RESOLVE`/observations | All aligned to ✓/✗ + `--debug` for trace |
| Plugin cwd | Mentioned in some guides | `examples/README.md`, example READMEs, docs examples pages |
| Legacy JSONL | `events.jsonl.example` with `CapabilityEvent` | Removed; `run.example.jsonl` + browser `events.jsonl.example` |
| Roadmap TestSpec | “Python only” implied | Python + YAML + BDD |
| Roadmap browser | “Out of scope” (wrong) | Fake providers shipped; real drivers deferred |
| Stability report §6 | “Python-only; no YAML adapter” | Corrected + M8 historical banner |
| RFC-006 links | Broken `docs/rfc/RFC-006` | `docs/archive/rfc/RFC-006-pytest-coexistence.md` |
| Plugin author | Duplicate `plugin-author-guide.md` | Superseded banner on legacy file |

---

## 3. Dead code removed

| Item | Location |
|------|----------|
| `ReportError` class (unused) | `velaris_core/errors.py` |
| Unused `CapabilityObserved` import | `providers_browser.py` |
| Unused `OutputMode` import | `tests/test_runner.py` |

---

## 4. Example usability improvements

- **Central index:** `examples/README.md` with ordered path and cwd table
- **Minimal:** README explains failures, env vars, and subset run command
- **Every runnable example:** README states whether it passes out of the box and required `cd`
- **Reporting:** Committed samples documented; legacy format explicitly unsupported

---

## 5. Remaining known issues before alpha

| Issue | Severity | Notes |
|-------|----------|-------|
| `velaris_plugins.py` cwd-only loading | Medium | Silent skip if run from wrong directory — documented, not fixed |
| No PyPI packages | Medium | Clone + editable install only |
| `examples/minimal` fails by design | Low | Documented; not first-run |
| `examples/composition` needs HTTP | Low | Documented |
| Config validation for external caps | Low | Typos fail at resolve time |
| Archive docs still link `rfc/` internally | Low | Archive-only; active docs fixed |
| VitePress `ignoreDeadLinks: true` | Low | May hide broken links in CI |

---

## 6. First clone path — will it succeed?

**Recommended path (succeeds without confusion):**

```bash
git clone <repo-url> velaris && cd velaris
python -m venv .venv && source .venv/bin/activate
pip install -e packages/velaris-contracts -e "packages/velaris-core[dev]"
cd examples/browser
velaris run tests/ --config velaris.fake.toml
```

Expected:

```text
✓ test_login

Passed: 1
Failed: 0
Duration: 0.00s
```

**Optional HTML report:**

```bash
velaris run tests/ --config velaris.fake.toml --html-report
open report.html
```

**Next steps (still pass out of the box):**

1. `cd examples/authoring && velaris run tests/`
2. `cd examples/stress-test && velaris run tests/`
3. `cd examples/plugins && velaris run tests/`

**Avoid on day one:** `examples/minimal`, `examples/composition` (HTTP/env), running plugin examples without `cd`.

---

## 7. Verification

- `pytest` — run after sprint (expected: 108 passing)
- `npm run docs:build` — optional VitePress build

---

**Status: Ready for review.** No framework features, adapters, or runner/resolver changes were made beyond dead-code cleanup.
