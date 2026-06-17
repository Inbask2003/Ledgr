# Ledgr backend

FastAPI service for the Ledgr payments API. Async throughout (SQLAlchemy 2.0 +
asyncpg).

## Setup

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Docs at `http://localhost:8000/docs`. Tests: `pytest -q`.

## Layered structure

```
app/
  api/v1/      Routers. Thin: parse input, call a service, return a schema.
  service/     Business rules. Owns the transaction boundary (commit/rollback).
  repository/  Data access. Methods flush, never commit (the service decides).
  model/       SQLAlchemy models + enums.
  schema/      Pydantic request/response models.
  core/        config, logging, security, token, dependencies, exceptions.
  db/          Engine + session factory.
```

Request flow: router → service → repository → model. The domain layers never
import FastAPI; routers never contain business logic.

## Transactions

All repositories in one request share a single `AsyncSession` (every repo
provider depends on the same `get_db`). Repositories `flush` so constraint
violations surface early; the **service** calls `commit`. This is what keeps a
payment capture and its ledger entries atomic.

## Auth

Two credential types, both passed as `Authorization: Bearer <token>`:
- **JWT** from `/auth/login` — for the dashboard. `sub` is the merchant email.
- **API key** (`sk_...`) — for server-to-server. Stored hashed (sha256), shown
  once at creation, looked up by prefix then constant-time compared.

`get_current_merchant` (in `core/dependencies.py`) accepts either (an `sk_`
prefix routes to API-key resolution, otherwise JWT), resolves to the live
merchant row, and is the dependency that enforces per-merchant scoping — every
query filters by `merchant.id`, so cross-merchant access returns 404.

## Payments

- Lifecycle: `created → captured` (mock processor authorises + captures in one
  step) or `created → failed`; `created` can also be `cancelled`. Captured
  payments go to `partially_refunded` / `refunded`. Transitions only move
  forward and are guarded by `InvalidStateError`.
- Idempotency: unique `(merchant_id, idempotency_key)`. A repeat returns the
  original payment; a concurrent duplicate is caught on the constraint and the
  loser re-reads the winner's row.
- The mock processor (`service/processor.py`) succeeds at
  `PROCESSOR_SUCCESS_RATE` (default 0.9) and otherwise returns a decline reason.

## Ledger

Append-only double-entry. All writes go through `service/ledger.py:post`, which
refuses an unbalanced batch (debits must equal credits). Capture debits
`payments_clearing` / credits `merchant_balance`; refund reverses it. Balance =
credits minus debits on `merchant_balance`.

## Webhooks

On capture/fail/refund, the payment/refund service enqueues a `WebhookEvent` in
the same transaction as the state change (so an event exists iff the change
committed). An in-process dispatcher loop (started in `main.lifespan`,
`service/webhook.run_dispatcher`) polls every 5s, POSTs due events to the
merchant's endpoint signed with HMAC-SHA256 (`Ledgr-Signature`), and on failure
reschedules with backoff `[1m, 5m, 30m, 2h, 12h]` up to 5 attempts before
marking the event failed. `replay` resets an event to pending. The dispatcher
uses its own session via `AsyncSessionLocal`, not a request session.

## Errors

Raise subclasses of `LedgrError` (`core/exceptions.py`) from services. The
registered handler renders them as `{"error": {"code", "message"}}` with the
right status. Don't raise `HTTPException` from the domain.

## Background jobs & audit

- `app/jobs/` holds reconciliation (ledger `debits == credits` per merchant) and
  payment expiry (stale `created` → `expired`). Both run as periodic in-process
  loops started in `main.lifespan` and as standalone `python -m app.jobs.*` jobs.
- Every `/api/v1` request is recorded by an audit middleware (`main`) into
  `audit_logs` (method, path, status, merchant) — toggle with `AUDIT_ENABLED`.
  The merchant is read from `request.state.merchant_id`, set by
  `get_current_merchant`.
- `/healthz` pings the database and returns 503 if it's down.

## Migrations

`alembic.ini` uses a sync psycopg2 URL; the app uses asyncpg. After changing a
model: `alembic revision --autogenerate -m "..."` then `alembic upgrade head`.

## Conventions

- Amounts are integer paise; currency is INR only.
- No narrating comments — keep names and structure expressive instead.
