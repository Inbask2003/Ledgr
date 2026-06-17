# lib

Framework-agnostic helpers (no React).

- `api.js` — fetch wrapper. Attaches the bearer token from `localStorage`,
  unwraps the JSON envelope, and throws `ApiError` carrying the backend's
  `code`. Add new endpoints as methods on the `api` object; don't call `fetch`
  from components.
- `format.js` — `formatINR` (paise → ₹), date and payment-status helpers.

## Rules

- The API speaks integer paise. Convert to rupees only for display, via
  `formatINR`.
