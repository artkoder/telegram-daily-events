import sys
from pathlib import Path

# ruff: noqa: E402

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import pytest
from sqlmodel import Session, SQLModel, create_engine

from bot.services.admin import register_first_admin
from db.models import Admin


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_first_start_registers_superadmin(session):
    reply = register_first_admin(session, 123)
    assert reply == "Registered as superadmin"
    admin = session.query(Admin).first()
    assert admin is not None
    assert admin.user_id == 123
    assert admin.is_superadmin is True


def test_repeated_start_denied_for_other_user(session):
    # register first admin
    register_first_admin(session, 123)
    reply = register_first_admin(session, 456)
    assert reply == "Access restricted"
    count = session.query(Admin).count()
    assert count == 1
