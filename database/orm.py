from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from database.conexaodb import DB_PATH, Database


with Database():
    pass

engine = create_engine(
    f"sqlite:///{DB_PATH.replace(chr(92), '/')}",
    connect_args={"check_same_thread": False},
)


class Base(DeclarativeBase):
    pass


@contextmanager
def session_scope():
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()