# core layer

Cross-cutting infrastructure used everywhere.

Files:
- `config` — settings loaded from env / `.env`.
- `logging` — `setup_logging()`; quiets `uvicorn.access` and the passlib bcrypt
  warning. Called first in `app.main` before other imports so import-time logs
  are formatted too.
- `security` — bcrypt hashing.
- `token` — JWT encode/decode (plain sync functions).
- `dependencies` — repo providers + `get_current_merchant` (resolves the token
  to the live merchant; the basis of tenant scoping).
- `exceptions` — `LedgrError` hierarchy and the handler that renders
  `{"error": {"code", "message"}}`.

## Rules

- This layer must not import from `api`/`service`/`repository`.
