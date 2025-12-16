import pytest
from unittest.mock import Mock, MagicMock
from app.storage import (
    Storage,
    EmptyUsernameError,
    EmptyPasswordError,
    UserAlreadyExistsError,
    UserNotFoundError,
    User,
    Task
)
#во всех тестах Storage создается через new, чтобы не вызывать инит и не подключаться к самому БД
def test_register_user_empty_username():
    storage = Storage.__new__(Storage)

    with pytest.raises(EmptyUsernameError):
        storage.register_user("   ", "123")


def test_register_user_empty_password():
    storage = Storage.__new__(Storage)

    with pytest.raises(EmptyPasswordError):
        storage.register_user("isf", "")

def test_search_tasks_text_found():
    storage = Storage.__new__(Storage)

    session = MagicMock()
    storage.SessionLocal = MagicMock()
    storage.SessionLocal.return_value.__enter__.return_value = session

    user = User(id=1, username="никита")
    storage._get_user = MagicMock(return_value=user)

    task = Task(description="Купить молоко", completed=False, deadline=None)

    query_mock = MagicMock()

    session.query.return_value = query_mock
    query_mock.filter.return_value = query_mock  
    query_mock.all.return_value = [task]

    result = storage.search_tasks(
        username="никита",
        text="мол",
        date_from=None,
        date_to=None
    )

    assert result == ["Купить молоко"]

def test_search_tasks_text_not_found():
    storage = Storage.__new__(Storage)

    session = MagicMock()
    storage.SessionLocal = MagicMock()
    storage.SessionLocal.return_value.__enter__.return_value = session

    user = User(id=1, username="никита")
    storage._get_user = MagicMock(return_value=user)

    query_mock = MagicMock()
    session.query.return_value = query_mock
    query_mock.filter.return_value = query_mock

    query_mock.all.return_value = []

    result = storage.search_tasks(
        username="никита",
        text="экзамен",
        date_from=None,
        date_to=None
    )

    assert result == []


def test_check_login_success():
    storage = Storage.__new__(Storage)

    password = "123"
    fake_hash = storage_hash = "$2b$12$AM9zDeq0FYB.txs4eXJzWu6rWP/ANg2iSMTnM.anYV9GvBkJSQXOS" 

    user = User(username="test", password_hash=fake_hash)

    session = MagicMock()
    storage.SessionLocal = MagicMock()
    storage.SessionLocal.return_value.__enter__.return_value = session

    session.query.return_value.filter_by.return_value.first.return_value = user

    import bcrypt
    bcrypt.checkpw = MagicMock(return_value=True)

    assert storage.check_login("123", password) is True



def test_add_task_user_not_found():
    storage = Storage.__new__(Storage)

    session = MagicMock()
    storage.SessionLocal = MagicMock()
    storage.SessionLocal.return_value.__enter__.return_value = session

    storage._get_user = MagicMock(return_value=None)

    with pytest.raises(UserNotFoundError):
        storage.add_task("ghost", "test task")


def test_get_completed_tasks_empty():
    storage = Storage.__new__(Storage)

    session = MagicMock()
    storage.SessionLocal = MagicMock()
    storage.SessionLocal.return_value.__enter__.return_value = session

    user = User(id=1, username="nikita")
    storage._get_user = MagicMock(return_value=user)

    session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

    result = storage.get_completed_tasks("nikita")

    assert result == []