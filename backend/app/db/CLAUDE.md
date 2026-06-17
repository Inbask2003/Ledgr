# db layer

Database engine and session wiring.

Files:
- `base` — the Declarative `Base` all models inherit from.
- `session` — async engine + `async_sessionmaker`, and `get_db`, which yields one
  session per request and rolls back on error.

## Rules

- Every repo provider depends on `get_db`, so all repositories in a single
  request share the same session — that's what makes cross-repository commits
  atomic. Don't create sessions elsewhere.
- The app uses the asyncpg URL; Alembic uses the sync psycopg2 URL in
  `alembic.ini`.
