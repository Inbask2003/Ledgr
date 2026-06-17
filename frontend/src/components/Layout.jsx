import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  HomeIcon,
  CardIcon,
  LedgerIcon,
  KeyIcon,
  WebhookIcon,
  ActivityIcon,
  LogoutIcon,
} from "./icons";

const NAV = [
  { to: "/", label: "Overview", end: true, Icon: HomeIcon },
  { to: "/payments", label: "Payments", Icon: CardIcon },
  { to: "/ledger", label: "Ledger", Icon: LedgerIcon },
  { to: "/api-keys", label: "API keys", Icon: KeyIcon },
  { to: "/webhooks", label: "Webhooks", Icon: WebhookIcon },
  { to: "/activity", label: "Activity", Icon: ActivityIcon },
];

function navClass({ isActive }) {
  return `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
    isActive
      ? "bg-primary text-white shadow-card"
      : "text-muted hover:bg-secondary hover:text-foreground"
  }`;
}

export default function Layout() {
  const { merchant, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const initials = (merchant?.business_name || "?")
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-border bg-card px-4 py-6 md:flex">
        <div className="mb-8 flex items-center gap-2.5 px-2">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-lg font-bold text-white shadow-card">
            L
          </span>
          <span className="text-lg font-semibold tracking-tight text-foreground">Ledgr</span>
        </div>

        <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted">Menu</p>
        <nav className="flex flex-col gap-1">
          {NAV.map(({ to, label, end, Icon }) => (
            <NavLink key={to} to={to} end={end} className={navClass}>
              <Icon className="h-[18px] w-[18px]" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto">
          <div className="flex items-center gap-3 rounded-lg border border-border bg-secondary px-3 py-2.5">
            <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary/15 text-xs font-semibold text-primary">
              {initials}
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-foreground">
                {merchant?.business_name}
              </p>
              <p className="truncate text-xs text-muted">{merchant?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="mt-2 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted transition hover:bg-secondary hover:text-foreground"
          >
            <LogoutIcon className="h-[18px] w-[18px]" />
            Sign out
          </button>
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border bg-card px-4 py-3 md:hidden">
          <span className="flex items-center gap-2 font-semibold">
            <span className="grid h-7 w-7 place-items-center rounded-lg bg-primary text-sm font-bold text-white">
              L
            </span>
            Ledgr
          </span>
          <button onClick={handleLogout} className="text-sm text-muted">
            Sign out
          </button>
        </header>

        <nav className="flex gap-1 border-b border-border bg-card px-4 py-2 md:hidden">
          {NAV.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `rounded-lg px-3 py-1.5 text-sm font-medium ${
                  isActive ? "bg-primary text-white" : "text-muted"
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 md:px-10">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
