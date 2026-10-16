"""Reusable authentication dependencies for any private API route."""

import hashlib
import secrets
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import select

from database import Db
from models import AuthSession, User

bearer = HTTPBearer(auto_error=False)
password_hasher = PasswordHash.recommended()
dummy_hash = password_hasher.hash(secrets.token_urlsafe(32))


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_session(
    db: Db,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> AuthSession:
    if credentials is None or len(credentials.credentials) > 128:
        raise unauthorized()
    session = db.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == hash_token(credentials.credentials),
            AuthSession.expires_at > datetime.now(UTC),
        )
    )
    if session is None:
        raise unauthorized()
    return session


CurrentSession = Annotated[AuthSession, Depends(get_current_session)]


def get_current_user(db: Db, session: CurrentSession) -> User:
    user = db.get(User, session.user_id)
    if user is None:
        raise unauthorized()
    return user


# Reuse this dependency on every route that reads or writes private user data.
CurrentUser = Annotated[User, Depends(get_current_user)]

