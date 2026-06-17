# Ledgr frontend

Merchant dashboard for the Ledgr API. Vite + React 19 + Tailwind 4 +
React Router 7.

## Setup

```
npm install
cp .env.example .env   # optional; sets VITE_API_BASE_URL
npm run dev            # http://localhost:5173
```

`npm run build`, `npm run lint`. The API base defaults to
`http://localhost:8000/api/v1`; override with `VITE_API_BASE_URL`.

## Structure

```
src/
  lib/api.js          fetch wrapper: attaches the bearer token, unwraps the
                      JSON envelope, throws ApiError with the backend's code.
  lib/format.js       formatINR (paise → ₹), date + status helpers.
  context/AuthContext token + merchant state, login/logout, initial /me check.
  components/          ui.jsx primitives, Layout (app shell), ProtectedRoute,
                      StatusBadge.
  pages/              Login, Signup, Dashboard, Payments, PaymentDetail, Ledger.
```

## Auth

The token lives in `localStorage`. On load, `AuthProvider` verifies it via
`/merchants/me` before rendering. `ProtectedRoute` gates the app shell;
`PublicOnly` (in `App.jsx`) keeps signed-in users off the auth screens.

## Data fetching pattern

Effects use an `active` flag and only call `setState` inside async callbacks
(after the `await`), never synchronously in the effect body — this satisfies the
`react-hooks` lint rule and avoids cascading renders. To refetch after a
mutation, bump a `reloadKey` that the effect depends on. List pages keep `draft`
filter state separate from `applied`, querying only on submit.

## Styling

Use the design tokens from `index.css`: `bg-background`, `text-foreground`,
`bg-primary` / `hover:bg-primary-hover`, `bg-secondary`, `border-border`,
`text-muted`. They support dark mode via the `.dark` class. Prefer the shared
primitives in `components/ui.jsx` over ad-hoc markup.

## Conventions

- API amounts are integer paise. Input fields take rupees and convert
  (`* 100`) before sending; display goes through `formatINR`.
- No narrating comments — keep components small and named clearly instead.
