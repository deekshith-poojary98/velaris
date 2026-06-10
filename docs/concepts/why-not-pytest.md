# Why Not pytest?

An honest answer, without marketing.

Velaris is **not** trying to replace pytest. If you already know pytest, this page tells you when to keep using it and when Velaris might be interesting.

## When pytest is the better choice

Use pytest (and you probably should, for most real work today):

- You need a mature, production-ready test runner — pytest is battle-tested, Velaris is alpha.
- You rely on the plugin ecosystem (`pytest-xdist`, `pytest-cov`, `pytest-asyncio`, etc.).
- You want parallel execution, rich parametrization, or fixtures with complex scopes.
- You need to `pip install` your test tool and run it in CI today.
- Your team already knows pytest and you have no reason to change.

pytest fixtures already let you inject dependencies and swap implementations. For many projects that is enough.

## When Velaris is interesting

Velaris explores a different idea: tests declare **capabilities**, and configuration — not code — decides **which implementation** satisfies them.

It may be worth a look if:

- You want to swap implementations (mock vs real HTTP, fake vs verbose browser) **without editing test code** — only `velaris.toml` changes.
- You want Python, YAML, and BDD tests to run on **one engine** with one set of results.
- You're interested in capability-driven test architecture as a design exercise.
- You want to build custom capabilities with a small, explicit plugin SDK.

The headline difference: in pytest you change a fixture or a parameter to swap a dependency; in Velaris you change a config file and the test is untouched.

## Current limitations

Be clear-eyed about the alpha:

- **No PyPI package** — install from source only.
- **No real browser** — the `browser` capability is an in-memory fake, not Playwright or Selenium.
- **No parallel execution.**
- **Minimal BDD** — basic Gherkin only, not full Cucumber/Behave.
- **No plugin marketplace or auto-discovery** — plugins are wired manually via `velaris_plugins.py`.
- **Alpha stability** — the execution engine is stable, but packaging and ecosystem are experimental.

## Can I use both?

Yes. Velaris is not a drop-in pytest replacement and doesn't try to be one. Many users will keep pytest for their main suite and try Velaris to explore capability-driven patterns on the side.

## See also

- [What Velaris Can Do Today](/what-velaris-can-do-today)
- [How Velaris Is Different](/concepts/how-velaris-is-different)
- [Quickstart](/getting-started/quickstart)
