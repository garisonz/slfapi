const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export type User = { id: string; email: string; created_at: string };
export type Credentials = { email: string; password: string };
export type Token = {
  access_token: string;
  token_type: "bearer";
  expires_at: string;
};

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}/api/v1/auth${path}`, options);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(
      typeof body?.detail === "string"
        ? body.detail
        : "Check your email and password and try again.",
      response.status,
    );
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

function credentialsRequest(credentials: Credentials): RequestInit {
  return {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  };
}

export const authApi = {
  signup: (credentials: Credentials) => request<User>("/signup", credentialsRequest(credentials)),
  login: (credentials: Credentials) => request<Token>("/login", credentialsRequest(credentials)),
  me: (token: string) => request<User>("/me", {
    headers: { Authorization: `Bearer ${token}` },
  }),
  logout: (token: string) => request<void>("/logout", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  }),
};
