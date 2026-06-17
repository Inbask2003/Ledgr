# schema layer

Pydantic request/response models — the API contract.

Convention: `*Create` is request input, `*Out` is a response
(`ConfigDict(from_attributes=True)`), `*Page` wraps a paginated list.

Files: `auth`, `merchant`, `payment`, `refund`, `ledger`.

## Rules

- Never expose secrets — e.g. `MerchantOut` omits `password_hash`.
- Amounts are `int` paise; currency is `Literal["INR"]`.
- Validate at the edge (field constraints) so services can trust their inputs.
