import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { Button, Input, Alert } from "../components/ui";
import { AuthShell } from "./Login";

export default function Signup() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ business_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await api.signup(form);
      await login(form.email, form.password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthShell title="Create your account" subtitle="Start accepting test payments in minutes">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Alert>{error}</Alert>
        <Input
          id="business_name"
          label="Business name"
          required
          minLength={5}
          placeholder="Acme Pvt Ltd"
          value={form.business_name}
          onChange={update("business_name")}
        />
        <Input
          id="email"
          label="Email"
          type="email"
          autoComplete="email"
          required
          value={form.email}
          onChange={update("email")}
        />
        <Input
          id="password"
          label="Password"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={form.password}
          onChange={update("password")}
        />
        <p className="-mt-2 text-xs text-muted">At least 8 characters.</p>
        <Button type="submit" loading={submitting} className="mt-1 w-full">
          Create account
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-muted">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-primary hover:text-primary-hover">
          Sign in
        </Link>
      </p>
    </AuthShell>
  );
}
