# context

React context providers.

- `AuthContext` — holds the token + current merchant, exposes `login`/`logout`
  and `isAuthenticated`, and verifies an existing token via `/merchants/me`
  before the app renders. Consume it with the `useAuth()` hook.

## Rules

- The token lives in `localStorage` (via `lib/api`), not in component state.
- `loading` gates the initial token check — `ProtectedRoute` waits on it so the
  login screen doesn't flash for already-signed-in users.
