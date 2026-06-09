# Velaris Documentation

Public documentation for Velaris v0.1.0-alpha, built with [VitePress](https://vitepress.dev/).

## Development

```bash
npm install
npm run docs:dev
```

Open `http://localhost:5173`.

## Build

```bash
npm run docs:build
npm run docs:preview
```

Output: `docs/.vitepress/dist/`

## Site structure

| Section | Path |
|---------|------|
| Homepage | `/` |
| Getting Started | `/getting-started/` |
| Concepts | `/concepts/` |
| Architecture | `/architecture/` |
| Guides | `/guide/` |
| Examples | `/examples/` |
| Milestone deep-dives | See below |

## Milestone reports (also in VitePress nav)

| Topic | Path |
|-------|------|
| Authoring adapters | [authoring-styles.md](authoring-styles.md) |
| Executable YAML | [executable-yaml.md](executable-yaml.md) |
| BDD adapter | [bdd-adapter.md](bdd-adapter.md) |
| CLI UX | [cli-ux-redesign.md](cli-ux-redesign.md) |
| HTML report | [html-report.md](html-report.md) |
| Roadmap | [roadmap.md](roadmap.md) |
| Alpha readiness sprint | [alpha-readiness-report.md](alpha-readiness-report.md) |

## Legacy markdown

These files remain in `docs/` for reference but are outside the main nav:

- [plugin-author-guide.md](plugin-author-guide.md) — superseded by `/guide/plugin-author`
- [architecture-stability-report.md](architecture-stability-report.md)
- [rfc/](rfc/) — design references
- [archive/](archive/) — superseded planning docs

## Keeping docs current

After each milestone, update:

1. Root `README.md` — status, test count, first-run path
2. `alpha-scope.md` — stable vs deferred
3. `index.md` — homepage claims
4. `examples/index.md` — example table
5. Pages that show CLI output — match default ✓ format
6. This file if new user-facing pages are added
