import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Payments from "./pages/Payments";
import PaymentDetail from "./pages/PaymentDetail";
import Ledger from "./pages/Ledger";
import ApiKeys from "./pages/ApiKeys";
import Webhooks from "./pages/Webhooks";
import Activity from "./pages/Activity";
import NotFound from "./pages/NotFound";

function PublicOnly({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return null;
  return isAuthenticated ? <Navigate to="/" replace /> : children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />
      <Route path="/signup" element={<PublicOnly><Signup /></PublicOnly>} />

      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="payments" element={<Payments />} />
        <Route path="payments/:id" element={<PaymentDetail />} />
        <Route path="ledger" element={<Ledger />} />
        <Route path="api-keys" element={<ApiKeys />} />
        <Route path="webhooks" element={<Webhooks />} />
        <Route path="activity" element={<Activity />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
