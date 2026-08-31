from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fastapi_do_zero.app import app
from fastapi_do_zero.database import start_database
from fastapi_do_zero.models import User, table_registry
from fastapi_do_zero.security import get_pwd_hash
from fastapi_do_zero.settings import Settings


@pytest.fixture
def client(session: AsyncSession):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[start_database] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def mock_user(session: AsyncSession):
    pwd = "test123"
    user = User(
        username="Test", email="test@test.com", password=get_pwd_hash(pwd)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_pwd = pwd

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


@pytest.fixture
def token(client, mock_user):
    response = client.post(
        "/auth/token",
        data={"username": mock_user.email, "password": mock_user.clean_pwd},
    )

    return response.json()["access_token"]


@pytest.fixture
def settings():
    return Settings()
