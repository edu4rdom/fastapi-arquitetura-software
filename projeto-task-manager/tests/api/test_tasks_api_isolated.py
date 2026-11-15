"""A camada de API testada sem banco: troca-se o repositório via dependency_overrides."""

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_task_repository
from app.config import Settings
from app.main import create_app
from tests.fakes import FakeTaskRepository


@pytest.fixture
def isolated_client():
    app = create_app(Settings(database_path=":memory:"))
    repository = FakeTaskRepository()
    app.dependency_overrides[get_task_repository] = lambda: repository
    with TestClient(app) as client:
        yield client


def test_crud_flow_works_with_a_fake_repository(isolated_client):
    created = isolated_client.post("/tasks", json={"title": "Estudar"})
    assert created.status_code == 201

    updated = isolated_client.patch("/tasks/1", json={"priority": "low"})
    assert updated.json()["priority"] == "low"

    assert isolated_client.delete("/tasks/1").status_code == 204
    assert isolated_client.get("/tasks").json() == []


def test_domain_errors_are_translated_to_http_status(isolated_client):
    isolated_client.post("/tasks", json={"title": "Estudar"})

    assert isolated_client.post("/tasks", json={"title": "estudar"}).status_code == 409
    assert isolated_client.get("/tasks/77").status_code == 404


def test_invalid_task_error_is_translated_to_422():
    from app.api.dependencies import get_task_service
    from app.domain.exceptions import InvalidTaskError

    class BrokenService:
        def create_task(self, **kwargs):
            raise InvalidTaskError("regra violada")

    app = create_app(Settings(database_path=":memory:"))
    app.dependency_overrides[get_task_service] = lambda: BrokenService()

    with TestClient(app) as client:
        response = client.post("/tasks", json={"title": "Estudar"})

    assert response.status_code == 422
    assert response.json() == {"detail": "regra violada"}
