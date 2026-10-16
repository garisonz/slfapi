"""Account creation, signin, current account, and logout endpoints."""

import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from auth import CurrentSession, CurrentUser, dummy_hash, hash_token, password_hasher, unauthorized
from config import settings
from database import Db
from models import AuthSession, User
from schemas import ErrorResponse, LoginRequest, SignupRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
def signup(payload: SignupRequest, db: Db) -> User:
    user = User(
        email=str(payload.email),
        password_hash=password_hasher.hash(payload.password.get_secret_value()),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email is already registered") from None
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
def login(payload: LoginRequest, response: Response, db: Db) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == str(payload.email)))
    # Verify a hash even for unknown emails to reduce timing differences.
    valid = password_hasher.verify(
        payload.password.get_secret_value(), user.password_hash if user else dummy_hash
    )
    if not valid or user is None:
        raise unauthorized()

    now = datetime.now(UTC)
    db.execute(delete(AuthSession).where(
        AuthSession.user_id == user.id, AuthSession.expires_at <= now
    ))
    token = secrets.token_urlsafe(32)
    expires_at = now + timedelta(hours=settings.session_hours)
    db.add(AuthSession(token_hash=hash_token(token), user_id=user.id, expires_at=expires_at))
    db.commit()
    response.headers["Cache-Control"] = "no-store"
    return TokenResponse(access_token=token, expires_at=expires_at)


@router.get("/me", response_model=UserResponse, responses={401: {"model": ErrorResponse}})
def me(user: CurrentUser, response: Response) -> User:
    response.headers["Cache-Control"] = "no-store"
    return user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse}},
)
def logout(db: Db, session: CurrentSession) -> Response:
    db.delete(session)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
