import { Navigate, useLocation } from "react-router";
import { useAuth } from "../auth/AuthContext";
import { getReturnPath } from "../auth/returnPath";
import AuthForm from "../components/AuthForm";

export default function LoginPage() {
  const { user, login } = useAuth();
  const location = useLocation();
  if (user) return <Navigate to={getReturnPath(location.state)} replace />;

  return (
    <section className="auth-page" aria-labelledby="login-heading">
      <h1 id="login-heading">Sign in</h1>
      <p>Access your private account.</p>
      <AuthForm mode="login" authenticate={login} />
    </section>
  );
}
