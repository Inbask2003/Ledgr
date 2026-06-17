import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { formatINR, formatDateTime } from "../lib/format";
import { Button, Card, Alert, EmptyState, PageHeader } from "../components/ui";
import { DownloadIcon } from "../components/icons";
import { CenteredSpinner } from "./Dashboard";

export default function Ledger() {
  const [balance, setBalance] = useState(null);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [bal, rows] = await Promise.all([
          api.getBalance(),
          api.listLedger("?limit=100"),
        ]);
        setBalance(bal.balance);
        setEntries(rows);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleExport = async () => {
    setExporting(true);
    setError("");
    try {
      const blob = await api.exportLedger();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "ledger.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting(false);
    }
  };

  if (loading) return <CenteredSpinner />;

  return (
    <div>
      <PageHeader
        title="Ledger"
        subtitle="Every money movement, append-only and always balanced."
        action={
          <Button variant="secondary" loading={exporting} onClick={handleExport}>
            <DownloadIcon className="h-4 w-4" />
            Export CSV
          </Button>
        }
      />

      <Alert>{error}</Alert>

      <Card className="mb-6">
        <p className="text-sm text-muted">Available balance</p>
        <p className="mt-1 text-3xl font-semibold text-foreground">{formatINR(balance)}</p>
      </Card>

      <Card padding="p-0">
        {entries.length === 0 ? (
          <EmptyState title="No ledger entries yet" hint="Capture a payment to see entries here." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
                  <th className="px-5 py-3 font-medium">Date</th>
                  <th className="px-5 py-3 font-medium">Account</th>
                  <th className="px-5 py-3 font-medium">Description</th>
                  <th className="px-5 py-3 text-right font-medium">Debit</th>
                  <th className="px-5 py-3 text-right font-medium">Credit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {entries.map((e) => (
                  <tr key={e.id}>
                    <td className="whitespace-nowrap px-5 py-3 text-muted">
                      {formatDateTime(e.created_at)}
                    </td>
                    <td className="px-5 py-3 font-medium capitalize text-foreground">
                      {e.account.replace(/_/g, " ")}
                    </td>
                    <td className="px-5 py-3 text-muted">{e.description}</td>
                    <td className="px-5 py-3 text-right font-mono text-foreground">
                      {e.direction === "debit" ? formatINR(e.amount) : "—"}
                    </td>
                    <td className="px-5 py-3 text-right font-mono text-foreground">
                      {e.direction === "credit" ? formatINR(e.amount) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
