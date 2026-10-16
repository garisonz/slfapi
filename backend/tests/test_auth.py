import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from auth import hash_token, password_hasher
from database import Base, get_db
from main import app
from models import AuthSession, User

PASSWORD = "a-long-test-password"


@pytest.fixture
def client():
    # Set TEST_DATABASE_URL only to a disposable PostgreSQL database.
    url = os.getenv("TEST_DATABASE_URL", "sqlite://")
    options = (
        {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
        if url == "sqlite://" else {}
    )
    engine = create_engine(url, **options)
    Base.metadata.create_all(engine)
    with engine.connect() as connection:
        transaction = connection.begin()

        def override_db():
            with Session(bind=connection, join_transaction_mode="create_savepoint") as db:
                yield db

        app.dependency_overrides[get_db] = override_db
        try:
            with TestClient(app) as test_client:
                yield test_client, connection
        finally:
            app.dependency_overrides.clear()
            transaction.rollback()
    engine.dispose()


def register(client, email="alice@example.com"):
    response = client.post("/api/v1/auth/signup", json={"email": email, "password": PASSWORD})
    assert response.status_code == 201, response.text
    return response.json()


def login(client, email="alice@example.com"):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    assert response.headers["cache-control"] == "no-store"
    return response.json()["access_token"]


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_signup_normalizes_email_and_keeps_password_private(client):
    api, connection = client
    user = register(api, " Alice@Example.com ")
    assert user["email"] == "alice@example.com"
    assert set(user) == {"id", "email", "created_at"}
    with Session(connection, join_transaction_mode="create_savepoint") as db:
        stored = db.scalar(select(User))
        assert stored.password_hash != PASSWORD
        assert password_hasher.verify(PASSWORD, stored.password_hash)
    duplicate = api.post("/api/v1/auth/signup", json={"email": "ALICE@example.com", "password": PASSWORD})
    assert duplicate.status_code == 409


@pytest.mark.parametrize("payload", [
    {"email": "invalid", "password": PASSWORD},
    {"email": "alice@example.com", "password": "short"},
    {"email": "alice@example.com", "password": "x" * 129},
    {"email": "alice@example.com"},
])
def test_invalid_signup(client, payload):
    assert client[0].post("/api/v1/auth/signup", json=payload).status_code == 422


def test_login_rejects_wrong_password_and_unknown_email(client):
    api, _ = client
    register(api)
    for email in ("alice@example.com", "unknown@example.com"):
        response = api.post("/api/v1/auth/login", json={"email": email, "password": "wrong"})
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("authorization", [None, "Bearer invalid", "Basic invalid"])
def test_private_routes_reject_missing_or_invalid_token(client, authorization):
    request_headers = {"Authorization": authorization} if authorization else {}
    for method, path in (("GET", "/me"), ("POST", "/logout")):
        assert client[0].request(method, "/api/v1/auth" + path, headers=request_headers).status_code == 401


def test_private_account_isolation_and_logout(client):
    api, connection = client
    alice = register(api)
    bob = register(api, "bob@example.com")
    alice_token = login(api)
    bob_token = login(api, "bob@example.com")
    for user, token in ((alice, alice_token), (bob, bob_token)):
        response = api.get("/api/v1/auth/me", headers=headers(token))
        assert response.status_code == 200
        assert response.json()["id"] == user["id"]
    # A caller-supplied user ID cannot change the account returned.
    assert api.get(f"/api/v1/auth/me?user_id={bob['id']}", headers=headers(alice_token)).json()["id"] == alice["id"]
    with Session(connection, join_transaction_mode="create_savepoint") as db:
        stored = db.get(AuthSession, hash_token(alice_token))
        assert stored is not None
        assert stored.token_hash != alice_token
    assert api.post("/api/v1/auth/logout", headers=headers(alice_token)).status_code == 204
    assert api.get("/api/v1/auth/me", headers=headers(alice_token)).status_code == 401
    assert api.post("/api/v1/auth/logout", headers=headers(alice_token)).status_code == 401
    assert api.get("/api/v1/auth/me", headers=headers(bob_token)).status_code == 200


def test_expired_session_and_independent_logins(client):
    api, connection = client
    register(api)
    first = login(api)
    second = login(api)
    with Session(connection, join_transaction_mode="create_savepoint") as db:
        db.get(AuthSession, hash_token(first)).expires_at = datetime.now(UTC) - timedelta(seconds=1)
        db.commit()
    assert api.get("/api/v1/auth/me", headers=headers(first)).status_code == 401
    assert api.get("/api/v1/auth/me", headers=headers(second)).status_code == 200


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "PATCH", "DELETE"])
def test_cors_allows_frontend_authorization(client, method):
    response = client[0].options("/api/v1/auth/login", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": method,
        "Access-Control-Request-Headers": "authorization,content-type",
    })
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_migration_round_trip(tmp_path, monkeypatch):
    from config import settings

    url = f"sqlite:///{tmp_path / 'migration.db'}"
    monkeypatch.setattr(settings, "database_url", url)
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(config, "head")
    command.check(config)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
