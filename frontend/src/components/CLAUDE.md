# components

Shared, presentational building blocks.

- `ui.jsx` — primitives: `Button`, `Input`, `Select`, `Card`, `Spinner`,
  `Alert`, `EmptyState`, `PageHeader`.
- `Layout.jsx` — the authed app shell (sidebar nav + mobile bar, `<Outlet/>`).
- `ProtectedRoute.jsx` — redirects to `/login` when unauthenticated.
- `StatusBadge.jsx` — payment-status pill.
- `icons.jsx` — inline stroke SVG icons.

## Rules

- Style with the design tokens from `index.css` (`bg-card`, `text-foreground`,
  `bg-primary`, `border-border`, `text-muted`, `shadow-card`).
- Set `Card` padding with its `padding` prop (e.g. `padding="p-0"` for tables) —
  don't pass conflicting `p-*` via `className`.
- Keep these dumb: no data fetching here, that lives in `pages`.
