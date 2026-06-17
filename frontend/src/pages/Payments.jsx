import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { formatINR, formatDateTime, shortId } from "../lib/format";
import {
  Button,
  Card,
  Input,
  Select,
  Alert,
  EmptyState,
  PageHeader,
} from "../components/ui";
import StatusBadge from "../components/StatusBadge";
import { PlusIcon } from "../components/icons";
import { CenteredSpinner } from "./Dashboard";

const PAGE_SIZE = 20;
const STATUSES = [
  "created",
  "captured",
  "failed",
  "cancelled",
  "expired",
  "partially_refunded",
  "refunded",
];

export default function Payments() {
  const [draft, setDraft] = useState({ status: "", min_amount: "", max_amount: "" });
  const [applied, setApplied] = useState(draft);
  const [offset, setOffset] = useState(0);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    let active = true;
    const params = new URLSearchParams({ limit: PAGE_SIZE, offset });
    if (applied.status) params.set("status", applied.status);
    if (applied.min_amount) params.set("min_amount", Math.round(applied.min_amount * 100));
    if (applied.max_amount) params.set("max_amount", Math.round(applied.max_amount * 100));

    api
      .listPayments(`?${params.toString()}`)
      .then((page) => {
        if (active) {
          setData(page);
          setError("");
        }
      })
      .catch((err) => {
        if (active) {
          setData({ items: [], total: 0 });
          setError(err.message);
        }
      });

    return () => {
      active = false;
    };
  }, [applied, offset, reloadKey]);

  const applyFilters = (e) => {
    e.preventDefault();
    setOffset(0);
    setApplied(draft);
  };

  const loading = data === null;
  const { items, total } = data || { items: [], total: 0 };
  const from = total === 0 ? 0 : offset + 1;
  const to = Math.min(offset + PAGE_SIZE, total);

  return (
    <div>
      <PageHeader
        title="Payments"
        subtitle="Create, track, and manage your payments."
        action={
          <Button onClick={() => setShowCreate(true)}>
            <PlusIcon className="h-4 w-4" />
            New payment
          </Button>
        }
      />

      <form onSubmit={applyFilters} className="mb-4 flex flex-wrap items-end gap-3">
        <Select
          id="status"
          label="Status"
          value={draft.status}
          onChange={(e) => setDraft({ ...draft, status: e.target.value })}
        >
          <option value="">All</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, " ")}
            </option>
          ))}
        </Select>
        <Input
          id="min_amount"
          label="Min (₹)"
          type="number"
          min="0"
          step="0.01"
          className="w-28"
          value={draft.min_amount}
          onChange={(e) => setDraft({ ...draft, min_amount: e.target.value })}
        />
        <Input
          id="max_amount"
          label="Max (₹)"
          type="number"
          min="0"
          step="0.01"
          className="w-28"
          value={draft.max_amount}
          onChange={(e) => setDraft({ ...draft, max_amount: e.target.value })}
        />
        <Button type="submit" variant="secondary">
          Apply
        </Button>
      </form>

      <Alert>{error}</Alert>

      {loading ? (
        <CenteredSpinner />
      ) : (
        <Card padding="p-0">
          {items.length === 0 ? (
            <EmptyState title="No payments found" hint="Try adjusting your filters." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
                    <th className="px-5 py-3 font-medium">Payment</th>
                    <th className="px-5 py-3 font-medium">Status</th>
                    <th className="px-5 py-3 font-medium">Created</th>
                    <th className="px-5 py-3 text-right font-medium">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {items.map((p) => (
                    <tr key={p.id} className="transition hover:bg-secondary">
                      <td className="px-5 py-3">
                        <Link to={`/payments/${p.id}`} className="block">
                          <span className="font-medium text-foreground">
                            {p.description || "Payment"}
                          </span>
                          <span className="block font-mono text-xs text-muted">
                            {shortId(p.id)}
                          </span>
                        </Link>
                      </td>
                      <td className="px-5 py-3">
                        <StatusBadge status={p.status} />
                      </td>
                      <td className="px-5 py-3 text-muted">{formatDateTime(p.created_at)}</td>
                      <td className="px-5 py-3 text-right font-medium text-foreground">
                        {formatINR(p.amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {total > 0 && (
        <div className="mt-4 flex items-center justify-between text-sm text-muted">
          <span>
            {from}–{to} of {total}
          </span>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              disabled={offset === 0}
              onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              disabled={to >= total}
              onClick={() => setOffset(offset + PAGE_SIZE)}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      {showCreate && (
        <CreatePaymentModal
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            setShowCreate(false);
            setOffset(0);
            setReloadKey((k) => k + 1);
          }}
        />
      )}
    </div>
  );
}

function CreatePaymentModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ amount: "", description: "", idempotency_key: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await api.createPayment({
        amount: Math.round(Number(form.amount) * 100),
        currency: "INR",
        description: form.description || null,
        idempotency_key: form.idempotency_key || null,
      });
      onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-elevated"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-semibold text-foreground">New payment</h2>
        <p className="mb-4 mt-1 text-sm text-muted">Amounts are in rupees.</p>
        <form onSubmit={submit} className="flex flex-col gap-4">
          <Alert>{error}</Alert>
          <Input
            id="amount"
            label="Amount (₹)"
            type="number"
            min="0.01"
            step="0.01"
            required
            placeholder="500.00"
            value={form.amount}
            onChange={(e) => setForm({ ...form, amount: e.target.value })}
          />
          <Input
            id="description"
            label="Description"
            placeholder="Order #1042"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <Input
            id="idempotency_key"
            label="Idempotency key (optional)"
            placeholder="order-1042"
            value={form.idempotency_key}
            onChange={(e) => setForm({ ...form, idempotency_key: e.target.value })}
          />
          <div className="mt-2 flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" loading={submitting}>
              Create payment
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
