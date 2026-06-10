# Capability Introspection

Velaris is self-describing. Before reading any documentation, you can ask the
framework directly: *what capabilities exist, and what can each one do?*

## `velaris capabilities`

Lists every capability Velaris knows about — built-in contracts plus any plugin
capabilities registered in your project's `velaris_plugins.py`.

```bash
velaris capabilities
```

```text
Available capabilities

api
browser
secrets
target_environment
random
```

Add `--json` for tooling:

```bash
velaris capabilities --json
```

```json
[
  "api",
  "browser",
  "random",
  "secrets",
  "target_environment"
]
```

## `velaris capability <id>`

Shows the full detail for one capability: its description, the methods you can
call on it, and which providers are registered to back it.

```bash
velaris capability browser
```

```text
Capability: browser

Description:
Minimal browser automation surface for integration tests.

Methods:
  open(url)
  click(selector)
  type(selector, text)
  close()

Providers:
  fake
  verbose
```

JSON output:

```bash
velaris capability browser --json
```

```json
{
  "id": "browser",
  "description": "Minimal browser automation surface for integration tests.",
  "methods": [
    "open(url)",
    "click(selector)",
    "type(selector, text)",
    "close()"
  ],
  "providers": [
    "fake",
    "verbose"
  ]
}
```

Unknown capabilities fail clearly:

```text
Error: Unknown capability 'nope'.
  Available: api, browser, random, secrets, target_environment
```

## How metadata is discovered

Nothing here is hand-maintained. Each command composes two sources that already
exist in the framework:

| Field | Source |
|-------|--------|
| Capability list | Published contracts + capability IDs with registered providers |
| `description` | The contract's `CONTRACT_METADATA["description"]` |
| `methods` | Introspected from the contract's `Protocol` — methods become `name(args)`, read-only properties become bare `name` |
| `providers` | The provider registry (built-ins via `bootstrap`, plus manual plugins) |

Because methods come straight from the Protocol definition, the output can never
drift from the actual contract — if the interface changes, so does the listing.

### Capabilities without a contract

Plugin capabilities (like `random` above) may register a provider without
publishing a contract Protocol. They still appear in `velaris capabilities`, and
`velaris capability <id>` shows their providers with an empty method surface:

```text
Capability: random

Description:
(no description available)

Methods:
  (no contract methods published)

Providers:
  seeded
```

## What it does *not* do

Introspection is read-only. It reads contract metadata and the registry — it
never resolves a binding, constructs a provider, or runs a test. You can run it
anywhere, anytime, with no side effects.
