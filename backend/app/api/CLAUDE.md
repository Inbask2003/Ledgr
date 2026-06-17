# api layer

HTTP routers, versioned under `v1/` and mounted at `/api/v1` in `app.main`.

Files: `auth`, `merchant`, `payment`, `ledger`.

## Rules

- Keep routers thin: validate input (Pydantic), call a service, return a schema.
  No business logic and no direct DB access here.
- Get the caller with `Depends(get_current_merchant)`; get repositories from the
  `get_*_repo` providers in `core/dependencies.py`. Every authed route is scoped
  to that merchant.
- Don't raise `HTTPException`. Let services raise `LedgrError` subclasses; the
  handler registered in `app.main` turns them into the JSON error envelope.
- Declare `response_model=` with a `schema/*` class so responses are filtered.
