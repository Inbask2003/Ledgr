import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Spinner } from "./ui";

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-primary">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location }} />;

  return children;
}
