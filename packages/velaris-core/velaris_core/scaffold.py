"""Project scaffolding for ``velaris init``."""

from __future__ import annotations

from pathlib import Path

from velaris_core.errors import VelarisError

VELARIS_TOML = """[capabilities.browser]
provider = "fake"
"""

TEST_LOGIN = '''from velaris_core.decorators import test


@test("browser")
def test_login(browser):
    browser.open("/login")
    browser.type("#username", "demo")
    browser.click("#submit")
'''

DOCS_URL = "https://github.com/deekshith-poojary98/velaris"


class ScaffoldError(VelarisError):
    """Project scaffolding failed."""


def _readme(project_name: str) -> str:
    return f"""# {project_name}

A [Velaris]({DOCS_URL}) test project.

Velaris is a capability-driven test runner. Tests declare what they need
(`browser`, `api`, `secrets`, …); `velaris.toml` selects provider
implementations; the runner handles collection, resolution, injection,
and teardown.

## Run tests

From this directory:

```bash
velaris run
```

Expected output:

```text
✓ test_login

Passed: 1
Failed: 0
```

## HTML report

```bash
velaris run --html-report
open report.html
```

## Project layout

```text
{project_name}/
├── velaris.toml      # capability → provider bindings
├── tests/
│   └── test_login.py
└── README.md
```

## Learn more

- [Velaris repository]({DOCS_URL})
- [Getting started]({DOCS_URL}/tree/main/docs/getting-started)
- [What Velaris can do today]({DOCS_URL}/blob/main/docs/what-velaris-can-do-today.md)
"""


def init_project(project_name: str) -> Path:
    """Create a runnable Velaris project at ``project_name``.

    Creates parent directories when needed (e.g. ``projects/demo``).
    Raises :class:`ScaffoldError` when the name is empty or the path exists.
    """
    name = project_name.strip()
    if not name:
        raise ScaffoldError("Project name must not be empty.")

    root = Path(name)
    if root.exists():
        raise ScaffoldError(f"Directory already exists: {root}")

    root.mkdir(parents=True)
    tests_dir = root / "tests"
    tests_dir.mkdir()
    (root / "velaris.toml").write_text(VELARIS_TOML, encoding="utf-8")
    (tests_dir / "test_login.py").write_text(TEST_LOGIN, encoding="utf-8")
    display_name = root.name or name
    (root / "README.md").write_text(_readme(display_name), encoding="utf-8")
    return root.resolve()


def format_success_message(project_name: str) -> str:
    """Human-readable instructions after ``velaris init`` succeeds."""
    return (
        f"Created project: {Path(project_name).name}\n"
        "\n"
        "Next steps:\n"
        "\n"
        f"cd {project_name}\n"
        "velaris run\n"
    )
