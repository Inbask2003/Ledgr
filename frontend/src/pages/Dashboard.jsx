import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { formatINR, formatDateTime, shortId } from "../lib/format";
import { Card, Spinner, Alert, EmptyState, PageHeader, Button } from "../components/ui";
import StatusBadge from "../components/StatusBadge";
import { WalletIcon, ReceiptIcon, PlusIcon } from "../components/icons";

export default function Dashboard() {
  const { merchant } = useAuth();
  const [balance, setBalance] = useState(null);
  const [recent, setRecent] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [bal, page] = await Promise.all([
          api.getBalance(),
          api.listPayments("?limit=5"),
        ]);
        setBalance(bal.balance);
        setRecent(page.items);
        setTotal(page.total);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <CenteredSpinner />;

  return (
    <div>
      <PageHeader
        title={`Welcome, ${merchant?.business_name?.split(" ")[0] || "there"}`}
        subtitle="Here's what's happening with your payments."
        action={
          <Link to="/payments">
            <Button>
              <PlusIcon className="h-4 w-4" />
              New payment
            </Button>
          </Link>
        }
      />

      <Alert>{error}</Alert>

      <div className="grid gap-4 sm:grid-cols-2">
        <MetricCard
          label="Available balance"
          value={formatINR(balance)}
          to="/ledger"
          linkText="View ledger"
          Icon={WalletIcon}
        />
        <MetricCard
          label="Total payments"
          value={total}
          to="/payments"
          linkText="View all"
          Icon={ReceiptIcon}
        />
      </div>

      <h2 className="mb-3 mt-8 text-lg font-semibold text-foreground">Recent payments</h2>
      <Card padding="p-0">
        {recent.length === 0 ? (
          <EmptyState title="No payments yet" hint="Create your first payment to get started." />
        ) : (
          <ul className="divide-y divide-border">
            {recent.map((p) => (
              <li key={p.id}>
                <Link
                  to={`/payments/${p.id}`}
                  className="flex items-center justify-between gap-4 px-5 py-3 transition hover:bg-secondary"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium text-foreground">
                      {p.description || "Payment"}
                    </p>
                    <p className="font-mono text-xs text-muted">
                      {shortId(p.id)} · {formatDateTime(p.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <StatusBadge status={p.status} />
                    <span className="font-medium text-foreground">{formatINR(p.amount)}</span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}

function MetricCard({ label, value, to, linkText, Icon }) {
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-tight text-foreground">{value}</p>
        </div>
        <span className="grid h-10 w-10 place-items-center rounded-xl bg-primary/10 text-primary">
          <Icon className="h-5 w-5" />
        </span>
      </div>
      <Link
        to={to}
        className="mt-3 inline-block text-sm font-medium text-primary hover:text-primary-hover"
      >
        {linkText} →
      </Link>
    </Card>
  );
}

export function CenteredSpinner() {
  return (
    <div className="flex justify-center py-20 text-primary">
      <Spinner className="h-8 w-8" />
    </div>
  );
}
