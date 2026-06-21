# Python Code Style Preferences

### Code Style
- Use idiomatic, declarative, minimal, and readable code. 
- Do not prematurely optimise for edge cases.
- Prefer “good enough and clear” over “fully hardened and complex”.

### List Comprehensions
- Single-letter loop variables are idiomatic (brief scope, mirrors set-builder notation).
- `x` generic; `i`/`j`/`k` indices; `s`/`ch` strings; `f` files; `_` unused.

### Typing & Data Models
- Use standard Python type hints consistently.
- Prefer `dataclass` for simple data containers.
- Keep data models lightweight and focused.

### Runtime Validation
- Use Pydantic **only at API boundaries (FastAPI request/response layer)**.
- Internal code should rely on type hints + Pyright, not runtime validation.

### Comments
- Comments should be rare and intentional, never the default.
- Only add comments for:
  - non-obvious business rules
  - external constraints or API quirks
  - non-intuitive edge cases

### API Layer (FastAPI)
- Use Pydantic models for request/response validation.
- Keep endpoint functions thin and orchestration-focused.
- Move business logic into service layer functions/classes.

