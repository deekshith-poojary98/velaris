# RFC-001: Capability Model

::: info Historical design reference
Written during early planning. Describes intent; the **implementation** is in `velaris-core` and [alpha scope](/alpha-scope). For current behavior, prefer getting started and architecture docs.
:::

| Field | Value |
|-------|-------|
| Status | Draft |
| Created | 2026-06-02 |
| Authors | Velaris Core Team |
| Reviewers | TBD (platform engineers) |

## Summary

This RFC defines the Velaris Capability Model: versioned contracts, scoped dependency injection, provider registration, configuration binding, and the resolution algorithm that connects tests to plugin implementations without test code knowing which plugin is active.

Velaris capabilities are **not** renamed pytest fixtures. They are **published, versioned interfaces** with explicit governance, config-driven provider binding, and cross-plugin interchange guarantees.

## Motivation

Platform engineering teams building org-wide test infrastructure face recurring problems:

1. **Fixture sprawl** — Each team names dependencies differently (`playwright_browser`, `driver`, `selenium`).
2. **Implementation lock-in** — Swapping Playwright for Selenium requires editing test code or maintaining parallel fixture hierarchies.
3. **No interchange standard** — Internal pytest plugins are org-specific; there is no shared contract for "what is a browser in our tests."
4. **Reporting fragmentation** — Each domain plugin emits its own trace format.

The Capability Model addresses these by separating **what a test needs** (capability ID + contract version) from **how it is provided** (plugin + config).

### What capabilities do that pytest fixtures cannot

| Capability | pytest fixture equivalent | Velaris advantage |
|------------|---------------------------|-----------------|
| Contract identity | Implicit return type | Explicit `api@1.0` contract ID, semver, compatibility matrix |
| Provider binding | conftest.py hierarchy | Config/CLI: `capabilities.api.provider = httpx` |
| Cross-repo interchange | Copy conftest or internal package | Install `velaris-plugin-httpx`; same test code works |
| Governance | Team convention doc | Contract RFC process, breaking-change policy |
| Ambiguity detection | Last conftest wins (silent) | Fail fast: "two plugins provide `browser` without priority" |
| Profile switching | Multiple conftest trees or env hacks | Named profiles: `velaris run --profile ci` |

Pytest fixtures remain excellent for **local, ad-hoc** dependencies. Capabilities are for **org-wide, swappable, governed** dependencies.

## Terminology

| Term | Definition |
|------|------------|
| **Capability** | A named dependency a test declares (e.g., `browser`, `api`). |
| **Contract** | Versioned interface spec defining required behavior (e.g., `api@0.1`). Lives in separate packages. |
| **Provider** | A plugin-registered factory implementing a contract (e.g., `httpx` provider for `api@0.1`). |
| **Binding** | Config mapping from capability ID to provider name + options. |
| **Scope** | Lifetime boundary for a resolved capability instance. |
| **Resolver** | Runtime component that builds the dependency graph and manages setup/teardown. |

## Design

### Capability identity

Every capability is identified by a tuple:

```
(capability_id, contract_version)
```

Examples:
- `("api", "0.1")` → written as `api@0.1`
- `("browser", "1.0")` → written as `browser@1.0`

The **capability_id** is the injection name used in tests and IR. The **contract_version** is semver for the interface spec.

Contract packages publish:
- A Python `Protocol` (for type checkers and plugin authors)
- Metadata: capability ID, version, required methods, optional extension points
- Compatibility declaration: which Velaris core versions are supported

Core never embeds contract definitions. Core only stores contract IDs and validates that registered providers declare which contract they implement.

### Contract packages

Contracts live in installable packages separate from core:

```
velaris-contract-api/          # defines api@0.1, api@1.0
velaris-contract-browser/      # defines browser@1.0
velaris-contract-database/     # defines database@1.0
```

Package structure (conceptual):

```
velaris_contract_api/
├── __init__.py
├── v0_1.py          # ApiClient Protocol, CAPABILITY_ID, VERSION
└── metadata.json    # method list, semver, deprecation notes
```

Tests import the Protocol for typing only:

```python
from velaris_contract_api.v0_1 import ApiClient

def test_users(api: ApiClient) -> None:
    response = api.get("/users")
    assert response.status_code == 200
```

At runtime, Velaris injects the configured provider's implementation. Tests must not import provider packages directly.

### Provider registration

Plugins register providers during `register()`:

```python
class HttpxPlugin(VelarisPlugin):
    def register(self, ctx: PluginContext) -> None:
        ctx.capabilities.register(
            capability_id="api",
            contract="api@0.1",
            provider="httpx",
            factory=HttpxApiFactory,
            scopes=["test", "session"],
            requires=["network"],  # sub-capabilities
        )
```

Registration fields:

| Field | Required | Description |
|-------|----------|-------------|
| `capability_id` | Yes | Injection name |
| `contract` | Yes | Contract ID with version |
| `provider` | Yes | Unique provider name within that capability |
| `factory` | Yes | Callable returning `(instance, teardown)` or async equivalent |
| `scopes` | Yes | Supported scope levels |
| `requires` | No | Other capability IDs this provider needs injected |
| `priority` | No | Used when multiple providers match; higher wins |
| `worker_safe` | No | Whether instance can be shared across parallel workers (default: false) |

### Configuration binding

Project config (`velaris.toml`):

```toml
[capabilities.api]
provider = "httpx"
contract = "0.1"  # optional; defaults to latest compatible

[capabilities.api.options]
base_url = "https://api.example.com"
timeout = 30
verify_ssl = true
```

Binding resolution order (highest wins):

1. CLI: `--capability api=requests`
2. Environment: `VELARIS__CAPABILITIES__API__PROVIDER=requests`
3. Profile overlay: `[profiles.ci.capabilities.api]`
4. Project config: `[capabilities.api]`
5. Plugin default (if exactly one provider registered)

If zero providers match → error at session start (fail fast).
If multiple providers match without explicit binding → error listing candidates.
If bound provider does not implement required contract version → error with compatibility matrix link.

### Capability profiles

Named bundles for environment-specific binding:

```toml
[profiles.ci]
[profiles.ci.capabilities.browser]
provider = "playwright"
[profiles.ci.capabilities.browser.options]
headless = true

[profiles.local]
[profiles.local.capabilities.browser]
provider = "playwright"
[profiles.local.capabilities.browser.options]
headless = false
slow_mo = 500
```

Run with: `velaris run --profile ci`

### Scopes

Scopes define instance lifetime and caching boundaries.

| Scope | Lifetime | Cache key | Teardown |
|-------|----------|-----------|----------|
| `session` | Entire test run | `(capability_id, provider, scope)` | After all tests |
| `module` | Single test file | `(capability_id, provider, module_path)` | After module's last test |
| `test` | Single test function | `(capability_id, provider, test_id)` | After test |
| `step` | Single step (reporting) | `(capability_id, provider, step_id)` | After step |

Default scope per capability is declared by the provider. Tests may request a narrower scope via decorator:

```python
@velaris.capability_scope(api="test")
def test_isolated(api: ApiClient) -> None:
    ...
```

**Scope narrowing rule:** A test may request a scope equal to or narrower than the provider's maximum. Requesting `session` when provider only supports `test` is an error.

**Parallel execution (Phase 5):** Session-scoped capabilities are **worker-local** by default. Cross-worker sharing requires explicit `worker_safe = true` on the provider registration. Shared resources (DB pools) must document concurrency semantics in the contract RFC.

### Dependency graph

Capabilities may depend on other capabilities via `requires`:

```
browser → requires → [network, temp_workspace]
api → requires → [network]
database → requires → [network]
```

The resolver builds a directed acyclic graph (DAG). Cycles are rejected at registration time.

Resolution order: topological sort of dependencies, then requested capabilities.

Teardown order: reverse topological sort. Teardown failures are captured and reported but do not suppress other teardowns.

### Resolution algorithm

Pseudocode for resolving capabilities for a single test:

```
function resolve(test: TestSpec, scope_context: ScopeContext) -> CapabilityBag:

    # 1. Collect requirements
    required = test.required_capabilities
    for each cap in required:
        binding = config.resolve_binding(cap.id)
        provider = registry.get_provider(cap.id, binding.provider)
        validate_contract(provider, cap.contract_version)

    # 2. Build DAG
    graph = build_dependency_graph(required, registry)
    assert acyclic(graph)

    # 3. Topological sort
    order = topological_sort(graph)

    # 4. Setup in order
    instances = {}
    for node in order:
        cache_key = scope_context.cache_key(node, test)
        if cache_key in scope_context.cache:
            instances[node.id] = scope_context.cache[cache_key]
            continue

        sub_caps = {dep.id: instances[dep.id] for dep in node.dependencies}
        instance, teardown = node.factory.create(sub_caps, node.options)
        instances[node.id] = instance
        scope_context.cache[cache_key] = instance
        scope_context.register_teardown(cache_key, teardown)

    return CapabilityBag(instances)

function teardown(scope_context):
    for teardown_fn in reversed(scope_context.teardowns):
        try:
            teardown_fn()
        except Exception as e:
            emit(CapabilityTeardownFailed, error=e)
```

**Setup failure:** If any capability setup fails, subsequent capabilities are not set up. The test is marked `ERROR`. Partial teardown runs for already-set-up capabilities.

**Lazy vs eager:** Phase 2 uses eager setup (all capabilities before test body). Future: lazy setup if a parametrized skip path never touches a capability.

### Versioning

Contracts follow semver:

- **MAJOR:** Breaking change to required methods or semantics
- **MINOR:** Additive methods or optional behavior
- **PATCH:** Documentation, type hint fixes

A provider implements exactly one contract version per registration. A plugin may register multiple providers for different versions:

```python
ctx.capabilities.register(..., contract="api@0.1", provider="httpx-v0")
ctx.capabilities.register(..., contract="api@1.0", provider="httpx-v1")
```

Config selects contract version:

```toml
[capabilities.api]
provider = "httpx-v1"
contract = "1.0"
```

**Compatibility matrix** (published per plugin):

| Plugin | api@0.1 | api@1.0 | Velaris core |
|--------|---------|---------|------------|
| velaris-plugin-httpx 0.3 | yes | yes | >=0.2 |
| velaris-plugin-requests 0.2 | yes | no | >=0.2 |

**Deprecation policy:**
1. New contract version published with migration guide
2. Old contract marked deprecated for minimum 2 minor Velaris releases
3. Providers encouraged to implement both versions during transition
4. Breaking removal requires RFC approval

### Error messages

Errors must be actionable. Examples:

```
CapabilityResolutionError: No provider bound for capability 'api'.
  Registered providers: httpx, requests
  Fix: set [capabilities.api] provider = "httpx" in velaris.toml
       or run: velaris run --capability api=httpx
```

```
CapabilityAmbiguityError: Multiple providers for 'browser' without binding.
  Candidates: playwright (velaris-plugin-playwright), selenium (velaris-plugin-selenium)
  Fix: set [capabilities.browser] provider in velaris.toml
```

```
ContractMismatchError: Provider 'requests' implements api@0.1 but test requires api@1.0.
  Compatible providers for api@1.0: httpx-v1
```

### Custom capabilities

Organizations may publish private contract packages:

```
acme-contract-payment-gateway/   # payment@1.0
acme-plugin-payment-stripe/      # implements payment@1.0
```

Velaris core treats first-party and third-party contracts identically. Governance is the organization's responsibility.

## Non-goals (this RFC)

- Parallel worker capability isolation (see Phase 5 RFC)
- YAML/BDD capability declaration syntax (see RFC-002)
- pytest adapter mechanics (see RFC-006)
- Reporting events for capability setup (see RFC-005)

## Alternatives considered

### Alternative 1: Capabilities as pytest fixture aliases

Map `browser` → `@pytest.fixture def browser(): ...` under the hood.

**Rejected.** Loses fail-fast ambiguity detection, config-only binding, and contract versioning. Becomes "pytest with a config file."

### Alternative 2: Single mega-interface per domain

One `Browser` Protocol with 50 methods covering Playwright, Selenium, and Appium.

**Rejected.** Bloated; plugins implement stubs. Prefer minimal core + optional extension protocols (`BrowserExtensions`).

### Alternative 3: Capabilities without separate contract packages

Contracts defined inline in core or plugins.

**Rejected.** Core would accumulate domain knowledge; plugins would define incompatible interfaces with the same name.

## Open questions

1. Should tests pin contract version explicitly (`api: ApiClient@v0_1`) or rely on config?
   - **Proposal:** Config pins version; type hints use Protocol import. IR stores resolved version at collection time.

2. Async capabilities: first-class in Phase 2 or Phase 3?
   - **Proposal:** Phase 2 supports sync only; Phase 3 adds async factory protocol.

3. Parametrized capability binding (run same test with httpx AND requests)?
   - **Proposal:** Phase 3 via `@velaris.capability_matrix(api=["httpx", "requests"])`. Out of scope for Phase 2.

## Implementation plan

| Phase | Deliverable |
|-------|-------------|
| Phase 2 | Registry, resolver, scopes (test, session), config binding, `api@0.1` + `clock@1.0` |
| Phase 3 | Plugin SDK registration helpers, compatibility matrix tooling |
| Phase 5 | Worker-safe flags, scope isolation across processes |

## Exit criteria (RFC-001)

- [ ] Two external platform engineers review and comment
- [ ] Written answer to "capabilities vs fixtures" accepted by reviewers
- [ ] Resolution algorithm handles: missing provider, ambiguous provider, setup failure, teardown failure
- [ ] Versioning and deprecation policy agreed

## References

- [RFC-002: TestSpec IR](./RFC-002-testspec-ir.md)
- [RFC-006: pytest Coexistence](../archive/rfc/RFC-006-pytest-coexistence.md)
- [api@0.1 Contract](../contracts/api-0.1.md)
- pytest fixtures: https://docs.pytest.org/en/stable/explanation/fixtures.html
- Python Protocols: PEP 544
