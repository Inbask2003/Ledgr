import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Button, Input, Alert } from "../components/ui";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthShell title="Welcome back" subtitle="Sign in to your Ledgr dashboard">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Alert>{error}</Alert>
        <Input
          id="email"
          label="Email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <Input
          id="password"
          label="Password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button type="submit" loading={submitting} className="mt-2 w-full">
          Sign in
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-muted">
        New to Ledgr?{" "}
        <Link to="/signup" className="font-medium text-primary hover:text-primary-hover">
          Create an account
        </Link>
      </p>
    </AuthShell>
  );
}

export function AuthShell({ title, subtitle, children }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-secondary px-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex items-center justify-center gap-2">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-primary text-lg font-bold text-white">
            L
          </span>
          <span className="text-2xl font-semibold text-foreground">Ledgr</span>
        </div>
        <div className="rounded-2xl border border-border bg-card p-8 shadow-card">
          <h1 className="text-xl font-semibold text-foreground">{title}</h1>
          {subtitle && <p className="mb-6 mt-1 text-sm text-muted">{subtitle}</p>}
          {children}
        </div>
      </div>
    </div>
  );
}
