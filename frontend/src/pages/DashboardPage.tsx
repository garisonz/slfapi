import { Link } from "react-router";
import { useAuth } from "../auth/AuthContext";

export default function DashboardPage() {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <section aria-labelledby="dashboard-heading">
      <h1 id="dashboard-heading">Dashboard</h1>
      <p>Signed in as <strong className="account-email">{user.email}</strong>.</p>
      <p>Welcome to your private dashboard.</p>
      <Link to="/account">View your account details</Link>
    </section>
  );
}
