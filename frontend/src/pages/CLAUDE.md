# pages

Route-level components, wired up in `App.jsx`.

`Login`, `Signup`, `Dashboard`, `Payments`, `PaymentDetail`, `Ledger`,
`ApiKeys`, `Webhooks`, `Activity`, `NotFound`. Authed pages render inside
`components/Layout`.

## Data-fetching pattern

Fetch in a `useEffect` that uses an `active` flag and only calls `setState`
inside the async callbacks (never synchronously in the effect body) — this keeps
the `react-hooks` lint rule happy and avoids cascading renders. To refetch after
a mutation, bump a `reloadKey` that the effect depends on. List pages keep
`draft` filter state separate from `applied` and query only on submit.

## Rules

- Call the `api` object from `lib/api`, never `fetch` directly.
- Reuse the primitives in `components/ui`; `CenteredSpinner` is exported from
  `Dashboard`.
