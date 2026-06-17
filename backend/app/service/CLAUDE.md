# service layer

Business rules. This layer owns the **transaction boundary**: services call
`commit`/`rollback`; repositories only `flush`. That's what keeps a payment
change and its ledger entries atomic.

Files:
- `payment` — create (idempotent), confirm (routes through the processor, posts
  ledger on capture), cancel.
- `refund` — full/partial refunds, posts the reversing ledger entries.
- `ledger` — `post()` writes a balanced batch and refuses an unbalanced one.
- `processor` — mock card processor (success rate + decline reasons).
- `merchant` — signup, maps a duplicate email to `ConflictError`.

## Rules

- Raise `LedgrError` subclasses (`core/exceptions.py`) for expected failures.
- All money is integer paise.
- Never build `LedgerEntry` rows by hand — go through `ledger.post()`.
