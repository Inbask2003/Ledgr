import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { formatDateTime } from "../lib/format";
import { Button, Card, Alert, EmptyState, PageHeader } from "../components/ui";
import { CenteredSpinner } from "./Dashboard";

const PAGE_SIZE = 50;

function statusColor(code) {
  if (code >= 500) return "text-red-600";
  if (code >= 400) return "text-amber-600";
  return "text-emerald-600";
}

export default function Activity() {
  const [data, setData] = useState(null);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    api
      .listAuditLogs(`?limit=${PAGE_SIZE}&offset=${offset}`)
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
  }, [offset]);

  if (data === null) return <CenteredSpinner />;

  const { items, total } = data;
  const from = total === 0 ? 0 : offset + 1;
  const to = Math.min(offset + PAGE_SIZE, total);

  return (
    <div>
      <PageHeader title="Activity" subtitle="Every API call made on your account." />

      <Alert>{error}</Alert>

      <Card padding="p-0">
        {items.length === 0 ? (
          <EmptyState title="No activity yet" hint="API calls will show up here." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
                  <th className="px-5 py-3 font-medium">Method</th>
                  <th className="px-5 py-3 font-medium">Path</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3 font-medium">When</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {items.map((row) => (
                  <tr key={row.id}>
                    <td className="px-5 py-3 font-mono text-xs font-medium text-foreground">
                      {row.method}
                    </td>
                    <td className="px-5 py-3 font-mono text-xs text-muted">{row.path}</td>
                    <td className={`px-5 py-3 font-mono text-xs font-medium ${statusColor(row.status_code)}`}>
                      {row.status_code}
                    </td>
                    <td className="px-5 py-3 text-muted">{formatDateTime(row.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

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
            <Button variant="secondary" disabled={to >= total} onClick={() => setOffset(offset + PAGE_SIZE)}>
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
