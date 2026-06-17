# LeaseClear — Agent Instructions

Production RAG for residential lease Q&A: cited answers, honest refusals, published eval metrics.

## Start here

Before planning or writing code, read both files in full:

1. **[spec.md](./SPEC.md)** — Architecture, scope, week-by-week plan, metrics targets, and out-of-scope items. This is the blueprint.
2. **[progress.md](./PROGRESS.md)** — Personal checklist: what's done, what's next, scratchpad notes. Update this as you complete items.

## Current phase

- **Warm-up (Days 1–3):** complete
- **Next:** Week 1 — The Spine (repo scaffold, corpus, ingestion, CLI retrieval)

## How to work

1. Open `PROGRESS.md` and find the **first unchecked item** in the current phase.
2. Cross-check against `SPEC.md` for requirements and exit criteria.
3. Implement the smallest change that satisfies that item.
4. Mark the item done in `PROGRESS.md` when verified.
5. Move to the next unchecked item. Do not skip ahead unless the user asks.

## Commit style

Use [Conventional Commits](https://www.conventionalcommits.org/) when creating commits (only when the user asks).

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

