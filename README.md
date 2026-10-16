# slfapi
A service to other's pursuing truth, reflection, discipline, and completion. Ultimately, with aim in helping improve the world around me, by promoting others fulfill their destiny.

## Run locally

From the repository root:

```sh
docker compose up --build -d
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 to create an account and sign in. The API and interactive
Swagger docs run at http://localhost:8000/docs. Compose starts PostgreSQL 17,
waits for it to be healthy, applies Alembic migrations, and starts FastAPI.
PostgreSQL data persists in the `db-data` Docker volume.

## Frontend pages

The frontend uses [React Router](https://reactrouter.com/start/declarative/routing)
to give each screen its own URL:

| URL | Page component | Access |
| --- | --- | --- |
| `/login` | `LoginPage.tsx` | Public |
| `/signup` | `SignupPage.tsx` | Public |
| `/dashboard` | `DashboardPage.tsx` | Signed in |
| `/account` | `AccountPage.tsx` | Signed in |

Create new screens in `frontend/src/pages/` and add their routes in
`frontend/src/App.tsx`. Put private routes inside the existing `ProtectedRoute`
group. Shared UI such as `Navbar`, `Button`, and `AuthForm` lives in
`frontend/src/components/`. Auth state lives in `frontend/src/auth/`, and account
API calls live in `frontend/src/api/auth.ts`.

Signed-out users visiting a private page are sent to `/login`, then returned to
that page after signing in. `/` opens the dashboard when signed in and the login
page otherwise. Unknown URLs show a page-not-found message. Sessions remain in
memory, so reloading a private page requires signing in again. Backend
authentication still enforces access to private data.

When hosting the built frontend, configure the web server to serve `index.html`
for client-side routes such as `/account`; Vite's development server handles
this automatically.

## Account API

| Method | Route | Request / behavior |
| --- | --- | --- |
| POST | `/api/v1/auth/signup` | JSON `email`, `password`; returns the new user (201) |
| POST | `/api/v1/auth/login` | JSON `email`, `password`; returns a bearer token and expiry |
| GET | `/api/v1/auth/me` | Returns only the authenticated user's account |
| POST | `/api/v1/auth/logout` | Revokes the current session (204) |

Signup requires a valid email and a password of 12–128 characters. Emails are
trimmed and lowercased; duplicates return 409. Invalid input returns 422. Missing,
invalid, expired, and revoked credentials return 401. Passwords are hashed with
Argon2 and never included in user responses. Random session tokens expire after
24 hours by default; only their SHA-256 digests are stored in PostgreSQL.

Example (use the same credentials for signup and login):

```sh
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"a-long-example-password"}'

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"a-long-example-password"}'

# Replace TOKEN with access_token from the login response.
curl http://localhost:8000/api/v1/auth/me -H 'Authorization: Bearer TOKEN'
curl -X POST http://localhost:8000/api/v1/auth/logout -H 'Authorization: Bearer TOKEN'
```

The React form keeps the token in memory: refreshing the page requires signing
in again. Logout revokes that login only; other devices remain signed in. In
Swagger, use **Authorize** to paste the token returned by `/login`.

## Backend development

To run FastAPI outside Docker (requires Python 3.12+ and `uv`):

```sh
docker compose up db -d
cd backend
uv sync --group dev
uv run alembic upgrade head
uv run uvicorn main:app --reload
```

Defaults use `postgresql+psycopg://slfapi:slfapi@localhost:5432/slfapi`.
See `.env.example` for settings. Compose reads the root `.env`; a local backend
reads `backend/.env`. `SESSION_HOURS` controls expiry and `CORS_ORIGINS` is a JSON
array of allowed frontend origins. Set `VITE_API_URL` in `frontend/.env` to change
the frontend's API base URL. The checked-in database credentials and HTTP setup
are for local development. Use a URL-safe database password in Compose; when
writing `DATABASE_URL` directly, URL-encode any special password characters.

Create a migration after changing SQLAlchemy models:

```sh
cd backend
uv run alembic revision --autogenerate -m "describe the schema change"
# Review the generated migration before applying it.
uv run alembic upgrade head
```

Tests use an isolated in-memory SQLite database by default:

```sh
cd backend
uv run pytest -q
# Optional: run API tests against a disposable, migrated PostgreSQL database.
TEST_DATABASE_URL=postgresql+psycopg://user:password@localhost/test_db uv run pytest -q
```

## Protecting future data

Start with the [backend guide](backend/README.md) for a file map, request flow,
and a complete example of private CRUD that you can adapt for your own data.

Use the `CurrentUser` dependency from `backend/auth.py` on private routes. For
user-owned records, add a non-null `user_id` foreign key and scope every read,
update, and delete to the authenticated user's ID. Never trust a caller-provided
user ID for authorization. For example, a route declared as
`def list_entries(user: CurrentUser, db: Db)` should query with
`select(Entry).where(Entry.user_id == user.id)`; set `user_id=user.id` on creation.
Import `Db` from `backend/database.py` and create feature routes in
`backend/routes/`. Account endpoints live in `backend/routes/auth.py`.
The public `/api/v1/hello` endpoint remains available.

This starter covers accounts and sessions. Email verification, password recovery,
login throttling, and production HTTPS configuration are separate follow-up work.
