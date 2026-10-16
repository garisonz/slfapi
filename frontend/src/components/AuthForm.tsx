import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import { getReturnPath } from "../auth/returnPath";
import Button from "./Button";

type AuthFormProps = {
  mode: "login" | "signup";
  authenticate: (email: string, password: string) => Promise<void>;
};

export default function AuthForm({ mode, authenticate }: AuthFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const isSignup = mode === "signup";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      await authenticate(email, password);
      setPassword("");
      void navigate(getReturnPath(location.state), { replace: true });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to sign in. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} aria-busy={busy}>
      <label htmlFor="email">Email</label>
      <input
        id="email"
        name="email"
        type="email"
        autoComplete="email"
        required
        maxLength={320}
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        disabled={busy}
      />
      <label htmlFor="password">Password</label>
      <input
        id="password"
        name="password"
        type="password"
        required
        minLength={isSignup ? 12 : 1}
        maxLength={128}
        autoComplete={isSignup ? "new-password" : "current-password"}
        aria-describedby={isSignup ? "password-hint" : undefined}
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        disabled={busy}
      />
      {isSignup && <p id="password-hint" className="form-hint">Use at least 12 characters.</p>}
      {error && <p role="alert">{error}</p>}
      <Button type="submit" disabled={busy}>
        {busy ? "Please wait…" : isSignup ? "Create account" : "Sign in"}
      </Button>
      <p className="form-footer">
        {isSignup ? "Already have an account? " : "Need an account? "}
        <Link to={isSignup ? "/login" : "/signup"} state={location.state}>
          {isSignup ? "Sign in" : "Create an account"}
        </Link>
      </p>
    </form>
  );
}
