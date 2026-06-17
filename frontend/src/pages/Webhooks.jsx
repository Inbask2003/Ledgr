import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { formatDateTime, webhookStatusClasses } from "../lib/format";
import { Button, Card, Input, Alert, EmptyState, PageHeader } from "../components/ui";
import { CopyIcon } from "../components/icons";
import { CenteredSpinner } from "./Dashboard";

export default function Webhooks() {
  const [endpoint, setEndpoint] = useState(undefined);
  const [events, setEvents] = useState([]);
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    Promise.all([
      api.getWebhookEndpoint().catch(() => null),
      api.listWebhookEvents("?limit=50"),
    ])
      .then(([ep, page]) => {
        if (!active) return;
        setEndpoint(ep);
        setUrl(ep?.url || "");
        setEvents(page.items);
      })
      .catch((err) => active && setError(err.message));
    return () => {
      active = false;
    };
  }, [reloadKey]);

  const save = async (e) => {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await api.setWebhookEndpoint({ url });
      setReloadKey((k) => k + 1);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const remove = async () => {
    setError("");
    try {
      await api.deleteWebhookEndpoint();
      setReloadKey((k) => k + 1);
    } catch (err) {
      setError(err.message);
    }
  };

  const replay = async (id) => {
    setError("");
    try {
      await api.replayWebhookEvent(id);
      setReloadKey((k) => k + 1);
    } catch (err) {
      setError(err.message);
    }
  };

  const copySecret = async () => {
    await navigator.clipboard.writeText(endpoint.secret);
    setCopied(true);
  };

  if (endpoint === undefined) return <CenteredSpinner />;

  return (
    <div>
      <PageHeader
        title="Webhooks"
        subtitle="Get notified when a payment changes state, instead of polling."
      />

      <Alert>{error}</Alert>

      <Card className="mb-6">
        <form onSubmit={save} className="flex flex-col gap-4">
          <Input
            id="webhook_url"
            label="Endpoint URL"
            type="url"
            required
            placeholder="https://api.yourapp.com/ledgr/webhook"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <div className="flex gap-2">
            <Button type="submit" loading={saving}>
              {endpoint ? "Update endpoint" : "Save endpoint"}
            </Button>
            {endpoint && (
              <Button type="button" variant="danger" onClick={remove}>
                Delete
              </Button>
            )}
          </div>
        </form>

        {endpoint && (
          <div className="mt-5 border-t border-border pt-4">
            <p className="text-sm font-medium text-foreground">Signing secret</p>
            <p className="mb-2 text-xs text-muted">
              Verify the <code className="font-mono">Ledgr-Signature</code> header with this secret.
            </p>
            <div className="flex items-center gap-2 rounded-lg border border-border bg-secondary px-3 py-2">
              <code className="flex-1 break-all font-mono text-xs text-foreground">
                {endpoint.secret}
              </code>
              <button onClick={copySecret} className="shrink-0 text-muted hover:text-foreground">
                <CopyIcon className="h-4 w-4" />
              </button>
            </div>
            {copied && <p className="mt-1 text-xs text-emerald-600">Copied to clipboard</p>}
          </div>
        )}
      </Card>

      <h2 className="mb-3 text-lg font-semibold text-foreground">Delivery log</h2>
      <Card padding="p-0">
        {events.length === 0 ? (
          <EmptyState
            title="No deliveries yet"
            hint="Confirm or refund a payment to trigger an event."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
                  <th className="px-5 py-3 font-medium">Event</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3 font-medium">Attempts</th>
                  <th className="px-5 py-3 font-medium">Created</th>
                  <th className="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {events.map((ev) => (
                  <tr key={ev.id}>
                    <td className="px-5 py-3">
                      <span className="font-mono text-xs text-foreground">{ev.event_type}</span>
                      {ev.last_error && (
                        <span className="block max-w-xs truncate text-xs text-red-600">
                          {ev.last_error}
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${webhookStatusClasses(ev.status)}`}
                      >
                        {ev.status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-muted">{ev.attempts}</td>
                    <td className="px-5 py-3 text-muted">{formatDateTime(ev.created_at)}</td>
                    <td className="px-5 py-3 text-right">
                      {ev.status !== "succeeded" && (
                        <button
                          onClick={() => replay(ev.id)}
                          className="text-sm font-medium text-primary hover:text-primary-hover"
                        >
                          Replay
                        </button>
                      )}
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
