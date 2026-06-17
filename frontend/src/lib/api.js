const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const TOKEN_KEY = "ledgr_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  constructor(message, { status, code } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

async function request(method, path, { body, auth = true } = {}) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";

  const token = getToken();
  if (auth && token) headers["Authorization"] = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("Can't reach the Ledgr API. Is the server running?", {
      status: 0,
    });
  }

  if (res.status === 204) return null;

  const isJson = res.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await res.json() : await res.text();

  if (!res.ok) {
    const err = payload?.error;
    throw new ApiError(err?.message || `Request failed (${res.status})`, {
      status: res.status,
      code: err?.code,
    });
  }

  return payload;
}

export const api = {
  get: (path, opts) => request("GET", path, opts),
  post: (path, body, opts) => request("POST", path, { ...opts, body }),

  signup: (data) => request("POST", "/merchants", { body: data, auth: false }),
  login: (data) => request("POST", "/auth/login", { body: data, auth: false }),
  me: () => request("GET", "/merchants/me"),

  listPayments: (query = "") => request("GET", `/payments${query}`),
  getPayment: (id) => request("GET", `/payments/${id}`),
  createPayment: (data) => request("POST", "/payments", { body: data }),
  confirmPayment: (id) => request("POST", `/payments/${id}/confirm`),
  cancelPayment: (id) => request("POST", `/payments/${id}/cancel`),
  refundPayment: (id, data) => request("POST", `/payments/${id}/refunds`, { body: data }),
  listRefunds: (id) => request("GET", `/payments/${id}/refunds`),

  listLedger: (query = "") => request("GET", `/ledger${query}`),
  getBalance: () => request("GET", "/ledger/balance"),

  listApiKeys: () => request("GET", "/api-keys"),
  createApiKey: (data) => request("POST", "/api-keys", { body: data }),
  revokeApiKey: (id) => request("DELETE", `/api-keys/${id}`),

  getWebhookEndpoint: () => request("GET", "/webhooks/endpoint"),
  setWebhookEndpoint: (data) => request("PUT", "/webhooks/endpoint", { body: data }),
  deleteWebhookEndpoint: () => request("DELETE", "/webhooks/endpoint"),
  listWebhookEvents: (query = "") => request("GET", `/webhooks/events${query}`),
  replayWebhookEvent: (id) => request("POST", `/webhooks/events/${id}/replay`),

  listAuditLogs: (query = "") => request("GET", `/audit-logs${query}`),
  exportLedger: async () => {
    const res = await fetch(`${BASE_URL}/ledger/export`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new ApiError("Could not export the ledger", { status: res.status });
    return res.blob();
  },
};

export { BASE_URL };
