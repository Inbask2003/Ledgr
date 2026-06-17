import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api, getToken, setToken } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [merchant, setMerchant] = useState(null);
  const [loading, setLoading] = useState(() => !!getToken());

  useEffect(() => {
    if (!getToken()) return;

    let active = true;
    (async () => {
      try {
        const me = await api.me();
        if (active) setMerchant(me);
      } catch {
        setToken(null);
        if (active) setMerchant(null);
      } finally {
        if (active) setLoading(false);
      }
    })();

    return () => {
      active = false;
    };
  }, []);

  const login = useCallback(async (email, password) => {
    const { access_token } = await api.login({ email, password });
    setToken(access_token);
    setMerchant(await api.me());
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setMerchant(null);
  }, []);

  const value = { merchant, loading, login, logout, isAuthenticated: !!merchant };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside an AuthProvider");
  return ctx;
}
