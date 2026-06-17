import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import { formatINR, formatDateTime } from "../lib/format";
import { Button, Card, Input, Alert, PageHeader } from "../components/ui";
import StatusBadge from "../components/StatusBadge";
import { ArrowLeftIcon } from "../components/icons";
import { CenteredSpinner } from "./Dashboard";

const REFUNDABLE = new Set(["captured", "partially_refunded"]);

export default function PaymentDetail() {
  const { id } = useParams();
  const [payment, setPayment] = useState(null);
  const [refunds, setRefunds] = useState([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const [showRefund, setShowRefund] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.all([api.getPayment(id), api.listRefunds(id)])
      .then(([p, r]) => {
        if (active) {
          setPayment(p);
          setRefunds(r);
        }
      })
      .catch((err) => active && setError(err.message))
      .finally(() => active && setLoaded(true));

    return () => {
      active = false;
    };
  }, [id, reloadKey]);

  const runAction = async (fn) => {
    setBusy(true);
    setError("");
    try {
      await fn();
      setReloadKey((k) => k + 1);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  if (!loaded) return <CenteredSpinner />;
  if (!payment) return <Alert>{error || "Payment not found"}</Alert>;

  const refundable = payment.amount - payment.amount_refunded;

  return (
    <div>
      <Link
        to="/payments"
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted transition hover:text-foreground"
      >
        <ArrowLeftIcon className="h-4 w-4" />
        Back to payments
      </Link>

      <PageHeader
        title={payment.description || "Payment"}
        subtitle={payment.id}
        action={<StatusBadge status={payment.status} />}
      />

      <Alert>{error}</Alert>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <p className="text-sm text-muted">Amount</p>
          <p className="mt-1 text-2xl font-semibold text-foreground">{formatINR(payment.amount)}</p>
        </Card>
        <Card>
          <p className="text-sm text-muted">Refunded</p>
          <p className="mt-1 text-2xl font-semibold text-foreground">
            {formatINR(payment.amount_refunded)}
          </p>
        </Card>
        <Card>
          <p className="text-sm text-muted">Currency</p>
          <p className="mt-1 text-2xl font-semibold text-foreground">{payment.currency}</p>
        </Card>
      </div>

      {payment.failure_reason && (
        <div className="mt-4">
          <Alert>Failure reason: {payment.failure_reason.replace(/_/g, " ")}</Alert>
        </div>
      )}

      <Card className="mt-4">
        <dl className="grid grid-cols-2 gap-y-3 text-sm">
          <Detail label="Created" value={formatDateTime(payment.created_at)} />
          <Detail label="Captured" value={formatDateTime(payment.captured_at)} />
        </dl>
      </Card>

      <div className="mt-6 flex flex-wrap gap-2">
        {payment.status === "created" && (
          <>
            <Button loading={busy} onClick={() => runAction(() => api.confirmPayment(id))}>
              Confirm payment
            </Button>
            <Button
              variant="secondary"
              loading={busy}
              onClick={() => runAction(() => api.cancelPayment(id))}
            >
              Cancel
            </Button>
          </>
        )}
        {REFUNDABLE.has(payment.status) && (
          <Button variant="danger" onClick={() => setShowRefund(true)}>
            Refund
          </Button>
        )}
      </div>

      <h2 className="mb-3 mt-8 text-lg font-semibold text-foreground">Refunds</h2>
      <Card padding="p-0">
        {refunds.length === 0 ? (
          <p className="px-5 py-6 text-sm text-muted">No refunds on this payment.</p>
        ) : (
          <ul className="divide-y divide-border">
            {refunds.map((r) => (
              <li key={r.id} className="flex items-center justify-between px-5 py-3 text-sm">
                <div>
                  <p className="font-medium text-foreground">{formatINR(r.amount)}</p>
                  <p className="text-xs text-muted">
                    {r.reason || "No reason"} · {formatDateTime(r.created_at)}
                  </p>
                </div>
                <span className="font-mono text-xs text-muted">{r.id.slice(0, 8)}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      {showRefund && (
        <RefundModal
          paymentId={id}
          maxAmount={refundable}
          onClose={() => setShowRefund(false)}
          onDone={() => {
            setShowRefund(false);
            setReloadKey((k) => k + 1);
          }}
        />
      )}
    </div>
  );
}

function Detail({ label, value }) {
  return (
    <>
      <dt className="text-muted">{label}</dt>
      <dd className="text-right font-medium text-foreground">{value}</dd>
    </>
  );
}

function RefundModal({ paymentId, maxAmount, onClose, onDone }) {
  const [amount, setAmount] = useState("");
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await api.refundPayment(paymentId, {
        amount: amount ? Math.round(Number(amount) * 100) : null,
        reason: reason || null,
      });
      onDone();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" onClick={onClose}>
      <div
        className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-elevated"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-semibold text-foreground">Issue refund</h2>
        <p className="mb-4 mt-1 text-sm text-muted">
          Up to {formatINR(maxAmount)} is refundable. Leave the amount blank for a full refund.
        </p>
        <form onSubmit={submit} className="flex flex-col gap-4">
          <Alert>{error}</Alert>
          <Input
            id="refund_amount"
            label="Amount (₹)"
            type="number"
            min="0.01"
            step="0.01"
            max={maxAmount / 100}
            placeholder={`${(maxAmount / 100).toFixed(2)} (full)`}
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          <Input
            id="refund_reason"
            label="Reason (optional)"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
          <div className="mt-2 flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="danger" loading={submitting}>
              Refund
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
