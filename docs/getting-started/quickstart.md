# Quickstart

Get a passing test in under 5 minutes (excluding install). Copy, paste, run.

## 1. Install Velaris

Velaris is alpha software and installs from source.

```bash
git clone https://github.com/deekshith-poojary98/velaris.git
cd velaris

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e packages/velaris-contracts -e "packages/velaris-core[dev]"
```

## 2. Scaffold a project

```bash
velaris init demo
cd demo
```

This creates a ready-to-run project:

```text
demo/
├── velaris.toml
├── README.md
└── tests/
    └── test_login.py
```

## 3. Run it

```bash
velaris run
```

Expected output:

```text
✓ test_login

Passed: 1
Failed: 0
```

That's it — a passing test.

## Next steps

- [What Velaris Can Do Today](/what-velaris-can-do-today) — the full feature list
- [Your First Test](/getting-started/first-test) — read and modify the generated test
- [Examples](/examples/) — runnable sample projects
- [Why Not pytest?](/concepts/why-not-pytest) — when Velaris is (and isn't) the right tool
