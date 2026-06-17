# Ledgr

Developer-facing payments API with a merchant dashboard. V1 is a sandbox: it
mirrors production payment patterns but runs against a mock processor instead of
moving real money. Currency is INR only and all amounts are integer paise.

## Layout

```
backend/             FastAPI + PostgreSQL API (the product)
frontend/            Vite + React dashboard that consumes the API
docker-compose.yaml  Local Postgres (host port 5433)
```

Each app has its own `CLAUDE.md` with the details that matter when working in it.

## Running locally

1. `docker compose up -d` — starts Postgres on `localhost:5433`.
2. Backend: see `backend/CLAUDE.md`. Runs on `http://localhost:8000`.
3. Frontend: see `frontend/CLAUDE.md`. Runs on `http://localhost:5173` and
   talks to the backend at `/api/v1`.

If host port 8000 is in use, run the backend on another port and set
`VITE_API_BASE_URL` in `frontend/.env` to match.

## Conventions

- Keep code self-explanatory; do not add narrating comments.
- Money is always integer paise end to end. Convert to rupees only for display.
- Treat the ledger as the source of truth for balances; payment status is a view.
