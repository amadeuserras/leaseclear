# LeaseClear — Agent Instructions

Production RAG for residential lease Q&A: cited answers, honest refusals, published eval metrics.

Progress and build guide, start here: **[PROGRESS.md](./PROGRESS.md)**

## Commit style

Use Conventional Commits when creating commits (only when the user asks).

**Format:**

```
<type>(<optional scope>): <short description>
```

- **Subject line:** imperative mood, lowercase, no trailing period, ≤72 characters.
- **Body:** don't write a body unless specified
- **Breaking changes:** add `!` after type/scope (e.g. `feat(api)!: …`)

**Types:**

| Type | Use for |
|------|---------|
| `feat` | New behavior or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Tests only |
| `chore` | Tooling, deps, config, housekeeping |
| `build` | Build system or packaging |
| `ci` | CI/CD workflows |

**Scopes** (optional but preferred when the change is localized):

`corpus`, `ingest`, `retrieval`, `cli`, `eval`, `api`, `deps`, `ci`

**Examples:**

```
feat(ingest): chunk leases by section heading
fix(retrieval): return empty list when index is missing
docs: add commit style guide to agents.md
chore(deps): pin chromadb to 0.4.x
```

