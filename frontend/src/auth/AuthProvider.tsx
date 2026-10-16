import { useEffect, useState, type ReactNode } from "react";
import { ApiError, authApi, type User } from "../api/auth";
import { AuthContext } from "./AuthContext";

type Session = { token: string; user: User; expiresAt: number };

export function AuthProvider({ children }: { children: ReactNode }) {
  // Keep tokens in memory; reloading the app requires signing in again.
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    if (!session) return;
    const expiresAt = session.expiresAt;
    let timer: ReturnType<typeof setTimeout>;
    function checkExpiry() {
      const remaining = expiresAt - Date.now();
      if (remaining <= 0) setSession(null);
      else timer = setTimeout(checkExpiry, Math.min(remaining, 2 ** 31 - 1));
    }
    checkExpiry();
    return () => clearTimeout(timer);
  }, [session]);

  async function login(email: string, password: string) {
    const token = await authApi.login({ email, password });
    const user = await authApi.me(token.access_token);
    setSession({
      token: token.access_token,
      user,
      expiresAt: Date.parse(token.expires_at),
    });
  }

  async function signup(email: string, password: string) {
    await authApi.signup({ email, password });
    try {
      await login(email, password);
    } catch {
      throw new Error("Your account was created. Use the sign in page to try signing in again.");
    }
  }

  async function logout() {
    if (session) {
      try {
        await authApi.logout(session.token);
      } catch (error) {
        // An expired or revoked session is already signed out on the server.
        if (!(error instanceof ApiError) || error.status !== 401) throw error;
      }
    }
    setSession(null);
  }

  return (
    <AuthContext.Provider value={{ user: session?.user ?? null, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
