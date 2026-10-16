from http import HTTPStatus

import factory.fuzzy
import pytest

from fastapi_do_zero.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker("text")
    description = factory.Faker("text")
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            "/todos",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Test",
                "description": "Test description",
                "state": "draft",
            },
        )
        assert response.json() == {
            "id": 1,
            "title": "Test",
            "description": "Test description",
            "state": "draft",
            "created_at": time.isoformat(),
            "updated_at": time.isoformat(),
        }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(
    session, client, mock_user, token
):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=mock_user.id))
    await session.commit()

    response = client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session, client, mock_user, token
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=mock_user.id))
    await session.commit()

    response = client.get(
        "/todos/?offset=1&limit=2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    session, mock_user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=mock_user.id, title="Test todo 1")
    )
    await session.commit()

    response = client.get(
        "/todos/?title=Test todo 1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    session, mock_user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5, user_id=mock_user.id, description="description"
        )
    )
    await session.commit()

    response = client.get(
        "/todos/?description=desc",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    session, mock_user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5, user_id=mock_user.id, state=TodoState.draft
        )
    )
    await session.commit()

    response = client.get(
        "/todos/?state=draft",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_return_5_todos(
    session, mock_user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=mock_user.id,
            title="Test todo combined",
            description="combined description",
            state=TodoState.done,
        )
    )

    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=mock_user.id,
            title="Other title",
            description="other description",
            state=TodoState.todo,
        )
    )
    await session.commit()

    response = client.get(
        "/todos/?title=Test todo combined&description=combined&state=done",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_delete_todo(session, client, mock_user, token):
    todo = TodoFactory(user_id=mock_user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f"/todos/{todo.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "message": "Task has been deleted successfully."
    }


def test_delete_todo_error(client, token):
    response = client.delete(
        "/todos/50", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Task not found."}


@pytest.mark.asyncio
async def test_delete_todo_other_user(session, client, token, mock_other_user):
    todo_other_user = TodoFactory(user_id=mock_other_user.id)
    session.add(todo_other_user)
    await session.commit()

    response = client.delete(
        f"/todos/{todo_other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_patch_todo_error(client, token):
    response = client.patch(
        "/todos/10",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Task not found."}


@pytest.mark.asyncio
async def test_patch_todo(session, client, mock_user, token):
    todo = TodoFactory(user_id=mock_user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f"/todos/{todo.id}",
        json={"title": "teste!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["title"] == "teste!"


@pytest.mark.asyncio
async def test_list_todos_should_return_all_expected_fields__exercicio(
    session, client, mock_user, token, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory.create(user_id=mock_user.id)
        session.add(todo)
        await session.commit()

    await session.refresh(todo)
    response = client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.json()["todos"] == [
        {
            "description": todo.description,
            "id": todo.id,
            "state": todo.state,
            "title": todo.title,
            "created_at": time.isoformat(),
            "updated_at": time.isoformat(),
        }
    ]


def test_list_todos_filter_min_length_exercicio_06(client, token):
    tiny_string = 'a'
    response = client.get(
        f'/todos/?title={tiny_string}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_list_todos_filter_max_length_exercicio_06(client, token):
    large_string = 'a' * 22
    response = client.get(
        f'/todos/?title={large_string}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY