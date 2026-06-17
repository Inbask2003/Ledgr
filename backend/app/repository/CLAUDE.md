# repository layer

Data access only — no business rules. One class per aggregate, constructed with
an `AsyncSession`.

Files: `merchant`, `payment`, `refund`, `ledger`.

## Rules

- Mutating methods `flush`, never `commit`. The service decides when to commit,
  so multi-repository writes in one request stay in a single transaction.
  `PaymentRepository` exposes `commit`/`rollback`/`refresh` as the unit-of-work
  handle for the service to drive.
- Scope every read and write by `merchant_id` — this enforces tenant isolation.
- Return models (or `(items, total)` for lists); let the router/service map to
  schemas.
