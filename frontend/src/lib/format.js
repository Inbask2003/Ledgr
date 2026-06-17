export function formatINR(paise) {
  const rupees = (paise ?? 0) / 100;
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
  }).format(rupees);
}

export function formatDateTime(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function shortId(id) {
  return id ? id.slice(0, 8) : "";
}

const STATUS_STYLES = {
  created: "bg-slate-100 text-slate-700",
  captured: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
  cancelled: "bg-slate-100 text-slate-500",
  expired: "bg-slate-100 text-slate-500",
  partially_refunded: "bg-amber-100 text-amber-700",
  refunded: "bg-violet-100 text-violet-700",
};

export function statusClasses(status) {
  return STATUS_STYLES[status] || "bg-slate-100 text-slate-700";
}

export function statusLabel(status) {
  return (status || "").replace(/_/g, " ");
}

const WEBHOOK_STATUS_STYLES = {
  pending: "bg-amber-100 text-amber-700",
  succeeded: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
};

export function webhookStatusClasses(status) {
  return WEBHOOK_STATUS_STYLES[status] || "bg-slate-100 text-slate-700";
}
