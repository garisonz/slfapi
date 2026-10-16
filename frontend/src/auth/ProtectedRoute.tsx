import { Navigate, Outlet, useLocation } from "react-router";
import { useAuth } from "./AuthContext";

export function ProtectedRoute() {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" replace state={{
      from: location.pathname + location.search + location.hash,
    }} />;
  }

  return <Outlet />;
}
