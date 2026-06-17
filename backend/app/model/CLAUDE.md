# model layer

SQLAlchemy 2.0 models and the shared enums.

Files: `merchant`, `payment`, `refund`, `ledger`, `enums`
(`PaymentStatus`, `LedgerDirection`, `LedgerAccount`).

## Rules

- Amounts are `BigInteger` paise.
- `ledger_entries` is append-only: nothing updates or deletes a row, and there
  is deliberately no `updated_at`.
- Idempotency is a unique `(merchant_id, idempotency_key)` on `payments`.
- Register every model in `__init__.py` so Alembic autogenerate picks it up,
  then `alembic revision --autogenerate` + `alembic upgrade head`.
