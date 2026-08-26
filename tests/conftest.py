from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, event
from sqlalchemy.orm import Session

from fastapi_do_zero.app import app
from fastapi_do_zero.database import start_database
from fastapi_do_zero.models import User, table_registry


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[start_database] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine, expire_on_commit=False) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def mock_user(session):
    user = User(username="Test", email="test@test.com", password="test123")
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@contextmanager
def _mock_db_time(model, time=datetime(2025, 5, 20)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, "created_at"):
            target.created_at = time
        if hasattr(target, "updated_at"):
            target.updated_at = time

    event.listen(model, "before_insert", fake_time_hook)

    yield time

    event.remove(model, "before_insert", fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
