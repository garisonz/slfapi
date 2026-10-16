## Local Docker setup

Run `docker compose up --build -d` from the repository root. Services:

- `db`: PostgreSQL 17 with a persistent `db-data` volume, bound to localhost:5432.
- `migrate`: applies `alembic upgrade head` once the database is healthy.
- `app`: FastAPI on localhost:8000, started after migrations succeed.

Open http://localhost:8000/docs to try the account API. Run the React frontend
separately with `cd frontend && npm install && npm run dev`.

Optional settings are documented in `.env.example`. To change the host database
port, set `POSTGRES_PORT`; local backend connections must use the matching port.

Inspect services with `docker compose ps -a`, view logs with
`docker compose logs app migrate`, and stop with `docker compose down`. Stopping
preserves accounts. The `-v` flag also deletes the database volume and its accounts.

See [README.md](README.md) for API examples, local development, and migrations.
