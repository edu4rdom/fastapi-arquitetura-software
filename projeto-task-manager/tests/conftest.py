from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.database import connect, init_db
from app.main import create_app
from app.repositories.sqlite_task_repository import SQLiteTaskRepository
from app.services.task_service import TaskService
from tests.fakes import FakeTaskRepository


class FakeClock:

    def __init__(self) -> None:
        self._now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        current = self._now
        self._now += timedelta(minutes=1)
        return current


@pytest.fixture
def fake_service() -> TaskService:
    return TaskService(FakeTaskRepository(), clock=FakeClock())


@pytest.fixture
def db_path(tmp_path) -> str:
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


@pytest.fixture
def sqlite_repository(db_path):
    connection = connect(db_path)
    yield SQLiteTaskRepository(connection)
    connection.close()


@pytest.fixture
def client(tmp_path):
    settings = Settings(database_path=str(tmp_path / "api.db"))
    with TestClient(create_app(settings)) as test_client:
        yield test_client
