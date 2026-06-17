import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { formatDateTime } from "../lib/format";
import { Button, Card, Input, Alert, EmptyState, PageHeader } from "../components/ui";
import { PlusIcon, CopyIcon } from "../components/icons";
import { CenteredSpinner } from "./Dashboard";

export default function ApiKeys() {
  const [keys, setKeys] = useState(null);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    let active = true;
    api
      .listApiKeys()
      .then((rows) => {
        if (active) {
          setKeys(rows);
          setError("");
        }
      })
      .catch((err) => {
        if (active) {
          setKeys([]);
          setError(err.message);
        }
      });
    return () => {
      active = false;
    };
  }, [reloadKey]);

  const revoke = async (id) => {
    setError("");
    try {
      await api.revokeApiKey(id);
      setReloadKey((k) => k + 1);
    } catch (err) {
      setError(err.message);
    }
  };

  if (keys === null) return <CenteredSpinner />;

  return (
    <div>
      <PageHeader
        title="API keys"
        subtitle="Use a secret key to call the Ledgr API from your backend."
        action={
          <Button onClick={() => setShowCreate(true)}>
            <PlusIcon className="h-4 w-4" />
            Create key
          </Button>
        }
      />

      <Alert>{error}</Alert>

      <Card padding="p-0">
        {keys.length === 0 ? (
          <EmptyState title="No API keys yet" hint="Create one to start integrating." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted">
                  <th className="px-5 py-3 font-medium">Name</th>
                  <th className="px-5 py-3 font-medium">Key</th>
                  <th className="px-5 py-3 font-medium">Created</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {keys.map((k) => (
                  <tr key={k.id}>
                    <td className="px-5 py-3 font-medium text-foreground">{k.name}</td>
                    <td className="px-5 py-3 font-mono text-xs text-muted">
                      {k.prefix}…{k.last4}
                    </td>
                    <td className="px-5 py-3 text-muted">{formatDateTime(k.created_at)}</td>
                    <td className="px-5 py-3">
                      {k.revoked_at ? (
                        <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-500">
                          Revoked
                        </span>
                      ) : (
                        <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
                          Active
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-right">
                      {!k.revoked_at && (
                        <button
                          onClick={() => revoke(k.id)}
                          className="text-sm font-medium text-red-600 hover:text-red-700"
                        >
                          Revoke
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

      {showCreate && (
        <CreateKeyModal
          onClose={() => setShowCreate(false)}
          onDone={() => {
            setShowCreate(false);
            setReloadKey((k) => k + 1);
          }}
        />
      )}
    </div>
  );
}

function CreateKeyModal({ onClose, onDone }) {
  const [name, setName] = useState("");
  const [created, setCreated] = useState(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      setCreated(await api.createApiKey({ name }));
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const copy = async () => {
    await navigator.clipboard.writeText(created.key);
    setCopied(true);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      onClick={created ? onDone : onClose}
    >
      <div
        className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-elevated"
        onClick={(e) => e.stopPropagation()}
      >
        {created ? (
          <>
            <h2 className="text-lg font-semibold text-foreground">Copy your API key</h2>
            <p className="mb-4 mt-1 text-sm text-muted">
              This is the only time the full key is shown. Store it somewhere safe.
            </p>
            <div className="flex items-center gap-2 rounded-lg border border-border bg-secondary px-3 py-2">
              <code className="flex-1 break-all font-mono text-xs text-foreground">{created.key}</code>
              <button onClick={copy} className="shrink-0 text-muted hover:text-foreground">
                <CopyIcon className="h-4 w-4" />
              </button>
            </div>
            <div className="mt-5 flex justify-end gap-2">
              <Button onClick={onDone}>{copied ? "Copied — done" : "Done"}</Button>
            </div>
          </>
        ) : (
          <>
            <h2 className="text-lg font-semibold text-foreground">Create API key</h2>
            <p className="mb-4 mt-1 text-sm text-muted">Give it a name so you can recognise it later.</p>
            <form onSubmit={submit} className="flex flex-col gap-4">
              <Alert>{error}</Alert>
              <Input
                id="key_name"
                label="Name"
                required
                placeholder="Production server"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <div className="mt-2 flex justify-end gap-2">
                <Button type="button" variant="ghost" onClick={onClose}>
                  Cancel
                </Button>
                <Button type="submit" loading={submitting}>
                  Create key
                </Button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
