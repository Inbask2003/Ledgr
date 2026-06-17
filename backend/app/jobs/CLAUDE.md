# jobs

Maintenance tasks that run on a schedule, not in the request path.

- `reconcile` — asserts `debits == credits` per merchant on the ledger. Run as
  `python -m app.jobs.reconcile` (exits non-zero on imbalance); also exposes
  `run_reconcile_loop` for the in-process periodic check.
- `expire` — moves `created` payments older than 15 min to `expired`. Run as
  `python -m app.jobs.expire`; also exposes `run_expiry_loop`.

## Rules

- Each module is runnable standalone (`__main__` opens + disposes its own engine)
  and also importable as a loop that `main.lifespan` starts as a background task.
- Use `AsyncSessionLocal` for sessions; these run outside any request scope.
