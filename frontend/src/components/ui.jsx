export function Button({
  children,
  variant = "primary",
  className = "",
  disabled,
  loading,
  ...props
}) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-primary text-white hover:bg-primary-hover",
    secondary: "bg-secondary text-foreground border border-border hover:bg-border/40",
    danger: "bg-red-600 text-white hover:bg-red-700",
    ghost: "text-muted hover:text-foreground hover:bg-secondary",
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner className="h-4 w-4" />}
      {children}
    </button>
  );
}

export function Input({ label, id, error, className = "", ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-foreground">
          {label}
        </label>
      )}
      <input
        id={id}
        className={`rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20 ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-red-600">{error}</span>}
    </div>
  );
}

export function Select({ label, id, children, className = "", ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-foreground">
          {label}
        </label>
      )}
      <select
        id={id}
        className={`rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20 ${className}`}
        {...props}
      >
        {children}
      </select>
    </div>
  );
}

export function Card({ children, padding = "p-5", className = "" }) {
  return (
    <div className={`rounded-xl border border-border bg-card shadow-card ${padding} ${className}`}>
      {children}
    </div>
  );
}

export function Spinner({ className = "h-5 w-5" }) {
  return (
    <svg className={`animate-spin ${className}`} viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 0 1 8-8V0C5.4 0 0 5.4 0 12h4z"
      />
    </svg>
  );
}

export function Alert({ children, variant = "error" }) {
  if (!children) return null;
  const styles = {
    error: "bg-red-50 text-red-700 border-red-200",
    success: "bg-emerald-50 text-emerald-700 border-emerald-200",
    info: "bg-violet-50 text-violet-700 border-violet-200",
  };
  return (
    <div className={`rounded-lg border px-3 py-2 text-sm ${styles[variant]}`}>{children}</div>
  );
}

export function EmptyState({ title, hint }) {
  return (
    <div className="flex flex-col items-center justify-center gap-1 py-12 text-center">
      <p className="font-medium text-foreground">{title}</p>
      {hint && <p className="text-sm text-muted">{hint}</p>}
    </div>
  );
}

export function PageHeader({ title, subtitle, action }) {
  return (
    <div className="mb-6 flex items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-muted">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}
