# Ledgr roadmap

## Goal

A developer-first payments API that does the boring 80% correctly: track payment
state, never double-charge on retries, notify merchants of events, and keep a
ledger that always balances. V1 is a sandbox (mock processor, INR only, no KYC).

## What we have

- Merchant signup + JWT login, per-merchant isolation.
- Payments: create (idempotent), confirm via mock processor, cancel, list with
  filters + pagination, get by id.
- Refunds: full and partial.
- Append-only double-entry ledger with a balance + CSV export.
- Typed error envelope, clean logging, Alembic migrations.
- React dashboard (overview, payments, payment detail, ledger).

## What we are missing

- **Webhooks** — no event delivery, signing, or retries. Biggest gap.
- **API-key auth** — only JWT today; server-to-server integrations need keys.
- **Reconciliation job** — nothing proves `debits == credits` on a schedule.
- **Payment expiry** — `created` payments never time out.
- **Audit log** — only stdout logs, nothing queryable.
- **Tests** — thin; no API/integration tests, no concurrent-idempotency test.
- **Ops** — shallow health check, no metrics, no app Dockerfile/CI.

## What the user (merchant developer) needs

1. Secret API keys to call us from their backend.
2. Webhooks so they don't have to poll for payment state changes.
3. Confidence the numbers are always right (reconciliation).
4. Visibility: see keys, webhook deliveries, and audit trail in the dashboard.

## Plan (build one by one)

### Phase 1 — make it integrable
1. **API keys** — ✅ done. `sk_` keys hashed at rest and shown once, accepted as
   bearer auth alongside JWT, managed via API + dashboard.
2. **Webhooks** — ✅ done. Register an endpoint, HMAC-signed events on state
   change, an in-process dispatcher with backoff retries, delivery log, replay.

### Phase 2 — correctness & ops ✅ done
3. ✅ Integration tests, including concurrent idempotency.
4. ✅ Reconciliation job + a health check that pings the DB.
5. ✅ Payment expiry for stale `created` payments.
6. ✅ Queryable audit log (middleware + endpoint + dashboard).

### Phase 3 — hardening (next)
7. Rate limiting, app Dockerfile + CI, refresh tokens / lockout.

### Phase 4 — frontend depth
8. Toasts, API-key + webhook-log screens, dark-mode toggle, error boundary.

Status is tracked as we go; each item ships as its own vertical slice.
