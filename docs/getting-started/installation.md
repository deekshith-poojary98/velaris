# Installation

Velaris v0.1.0-alpha installs from source. Two Python packages are required.

## Requirements

- Python 3.10+
- git

## Install from clone

```bash
git clone https://github.com/velaris-framework/velaris.git
cd velaris

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e packages/velaris-contracts -e "packages/velaris-core[dev]"
```

| Package | Role |
|---------|------|
| `velaris-contracts` | Capability Protocol definitions |
| `velaris-core` | Runner, resolver, CLI (`velaris` command) |

The `[dev]` extra installs pytest and responses for running the framework test suite. For running Velaris tests only:

```bash
pip install -e packages/velaris-contracts -e packages/velaris-core
```

## Verify

```bash
velaris --help
velaris run --help
```

## Documentation site (optional)

```bash
npm install
npm run docs:dev
```

Open `http://localhost:5173`.

## PyPI

PyPI packages are **not published** in v0.1.0-alpha. Install from a git clone.

## Troubleshooting

### `velaris: command not found`

Ensure your virtual environment is activated and `velaris-core` installed:

```bash
which velaris
pip show velaris-core
```

### `No module named velaris_core`

Install both packages. `velaris-core` depends on `velaris-contracts`.

### Plugin capabilities not found

Run `velaris run` from the directory containing `velaris_plugins.py`. See [Plugin Author Guide](/guide/plugin-author).
