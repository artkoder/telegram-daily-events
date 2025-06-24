from __future__ import annotations

from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine


class Admin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    is_superadmin: bool = False


engine = create_engine("sqlite:///data.db", echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
