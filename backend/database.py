from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    # Each request gets its own session; closing rolls back uncommitted work.
    with SessionLocal() as session:
        yield session


# Put `db: Db` in a route signature to receive the request's database session.
Db = Annotated[Session, Depends(get_db)]
