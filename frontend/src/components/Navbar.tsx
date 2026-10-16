import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router";
import { useAuth } from "../auth/AuthContext";
import Button from "./Button";

export default function Navbar() {
  const { user, logout } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function signOut() {
    setError("");
    setBusy(true);
    try {
      await logout();
      void navigate("/login", { replace: true });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to sign out. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <header className="app-header">
      <nav className="navbar" aria-label="Main navigation">
        <Link className="brand" to={user ? "/dashboard" : "/login"}>SELF API</Link>
        <div className="nav-links">
          {user ? (
            <>
              <NavLink to="/dashboard">Dashboard</NavLink>
              <NavLink to="/account">Account</NavLink>
              <Button onClick={signOut} disabled={busy} aria-busy={busy}>
                {busy ? "Signing out…" : "Sign out"}
              </Button>
            </>
          ) : (
            <>
              <NavLink to="/login">Sign in</NavLink>
              <NavLink to="/signup">Create account</NavLink>
            </>
          )}
        </div>
      </nav>
      {error && <p className="nav-error" role="alert">{error}</p>}
    </header>
  );
}
