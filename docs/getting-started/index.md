# Introduction

Velaris is a **capability-driven testing framework**. Tests say what they need; configuration picks how those needs are satisfied.

## The problem Velaris explores

Traditional test setup scatters concerns:

- Fixtures hide dependencies
- Environment setup lives in conftest.py
- Swapping implementations (mock vs real HTTP) requires test changes

Velaris inverts this:

1. **Tests declare capabilities** — `@test("api", "secrets")`
2. **Config binds providers** — `velaris.toml` selects `requests` vs a mock
3. **Runner resolves per test** — fresh instances, explicit teardown

## Core idea

```python
@test("api", "secrets")
def test_checkout(api, secrets):
    token = secrets.get("API_TOKEN")
    response = api.get("/orders", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
```

The test never constructs an HTTP client or reads environment variables directly. It receives **capabilities** — typed interfaces backed by provider factories.

## When to use Velaris (alpha)

Good fit:

- Exploring capability-driven test architecture
- Prototyping provider swap patterns (env vs static secrets, fake vs verbose browser)
- Building custom capabilities with the plugin SDK

Not yet a fit:

- Drop-in pytest replacement
- Production CI without clone-based install
- Large teams needing plugin marketplace or governance

## Next steps

Start here, in order:

1. **[Quickstart](/getting-started/quickstart)** — install, scaffold, and run a passing test
2. [What Velaris Can Do Today](/what-velaris-can-do-today) — the complete feature list
3. [Why Not pytest?](/concepts/why-not-pytest) — when Velaris is the right tool
4. [Examples](/examples/) — runnable sample projects

Once you're comfortable, dig into [Concepts](/concepts/) and the [Advanced](/architecture/) section for architecture and internals.
