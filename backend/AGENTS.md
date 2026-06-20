# Python Code Style Preferences

### General Philosophy
Prefer simple, minimal, and readable code over overly defensive or over-engineered implementations. Optimise for clarity and directness rather than exhaustive edge-case handling unless explicitly required.

If something can be done in a shorter, cleaner way without introducing risk or ambiguity, prefer the simpler version.

Avoid “clever” abstractions. Prefer explicit, boring code.

### Typing & Data Models
- Use standard Python type hints consistently.
- Prefer `dataclass` for simple data containers.
- Prefer clear, explicit types over complex generics unless truly needed.
- Keep data models lightweight and focused.

### Runtime Validation
- Use Pydantic **only at API boundaries (FastAPI request/response layer)**.
- Internal code should rely on type hints + Pyright, not runtime validation.

### Structure & Design
- Prefer small, single-responsibility functions.
- Keep logic linear and easy to follow.
- Prefer composition over abstraction unless abstraction clearly reduces complexity.

### Comments
- Comments should be rare and intentional.
- Do NOT comment obvious code.
- Only add comments for:
  - non-obvious business rules
  - external constraints or API quirks
  - non-intuitive edge cases
- Prefer self-explanatory code over explanatory comments.

### API Layer (FastAPI)
- Use Pydantic models for request/response validation.
- Keep endpoint functions thin and orchestration-focused.
- Move business logic into service layer functions/classes.

### Style Preferences
- Prefer minimal, sleek, readable code.
- Avoid over-defensive programming unless explicitly necessary.
- Do not prematurely optimise for edge cases.
- Prefer “good enough and clear” over “fully hardened and complex”.