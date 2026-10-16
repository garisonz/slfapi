import { Navigate, useLocation } from "react-router";
import { useAuth } from "../auth/AuthContext";
import { getReturnPath } from "../auth/returnPath";
import AuthForm from "../components/AuthForm";

export default function SignupPage() {
  const { user, signup } = useAuth();
  const location = useLocation();
  if (user) return <Navigate to={getReturnPath(location.state)} replace />;

  return (
    <section className="auth-page" aria-labelledby="signup-heading">
      <h1 id="signup-heading">Create an account</h1>
      <p>Sign up to get your own private account.</p>
      <AuthForm mode="signup" authenticate={signup} />
    </section>
  );
}
