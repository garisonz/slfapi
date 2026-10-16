import { useAuth } from "../auth/AuthContext";

export default function AccountPage() {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <section aria-labelledby="account-heading">
      <h1 id="account-heading">Your account</h1>
      <p>Your profile details are available while you are signed in.</p>
      <dl className="account-details">
        <div>
          <dt>Email</dt>
          <dd>{user.email}</dd>
        </div>
        <div>
          <dt>Account ID</dt>
          <dd>{user.id}</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>
            <time dateTime={user.created_at}>
              {new Date(user.created_at).toLocaleDateString(undefined, {
                year: "numeric", month: "long", day: "numeric",
              })}
            </time>
          </dd>
        </div>
      </dl>
    </section>
  );
}
