from dataclasses import asdict

from sqlalchemy import select

from fastapi_do_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username="Test", email="test@test.com", password="test123"
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == "Test"))

    assert asdict(user) == {
        "id": 1,
        "username": "Test",
        "email": "test@test.com",
        "password": "test123",
        "created_at": time,
        "updated_at": time,
    }
