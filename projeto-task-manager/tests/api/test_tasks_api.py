"""Testes de API: requisições HTTP reais ao app, com SQLite temporário."""

import pytest


def create(client, **overrides):
    payload = {"title": "Estudar arquitetura", **overrides}
    return client.post("/tasks", json=payload)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_task_returns_201_and_the_resource(client):
    response = create(client, description="Ler o capítulo 3", priority="high")

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["status"] == "pending"
    assert body["priority"] == "high"
    assert body["completed_at"] is None


@pytest.mark.parametrize(
    "payload",
    [
        {"title": ""},
        {"title": "   "},
        {"title": "x" * 121},
        {"title": "ok", "priority": "urgentissimo"},
        {"title": "ok", "campo_extra": 1},
        {},
    ],
)
def test_create_task_validates_input_with_422(client, payload):
    assert client.post("/tasks", json=payload).status_code == 422


def test_create_duplicate_active_title_returns_409(client):
    create(client)

    response = create(client, title="ESTUDAR ARQUITETURA")

    assert response.status_code == 409


def test_list_tasks_with_filter_and_pagination(client):
    for title in ("A", "B", "C"):
        create(client, title=title)
    client.patch("/tasks/2", json={"status": "done"})

    done = client.get("/tasks", params={"status": "done"}).json()
    page = client.get("/tasks", params={"limit": 2, "offset": 1}).json()

    assert [t["title"] for t in done] == ["B"]
    assert [t["title"] for t in page] == ["B", "C"]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"status": "x"}])
def test_list_tasks_validates_query_parameters(client, params):
    assert client.get("/tasks", params=params).status_code == 422


def test_get_task_by_id_and_404(client):
    create(client)

    assert client.get("/tasks/1").json()["title"] == "Estudar arquitetura"
    assert client.get("/tasks/99").status_code == 404
    assert client.get("/tasks/0").status_code == 422  # id inválido


def test_patch_updates_only_sent_fields(client):
    create(client, description="original")

    response = client.patch("/tasks/1", json={"status": "done"})

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "done"
    assert body["description"] == "original"
    assert body["completed_at"] is not None


@pytest.mark.parametrize("payload", [{}, {"title": None}, {"id": 5}, {"status": "inexistente"}])
def test_patch_rejects_invalid_bodies(client, payload):
    create(client)
    assert client.patch("/tasks/1", json=payload).status_code == 422


def test_patch_missing_task_returns_404(client):
    assert client.patch("/tasks/99", json={"status": "done"}).status_code == 404


def test_delete_returns_204_then_404(client):
    create(client)

    assert client.delete("/tasks/1").status_code == 204
    assert client.get("/tasks/1").status_code == 404
    assert client.delete("/tasks/1").status_code == 404


def test_openapi_documents_all_crud_operations(client):
    paths = client.get("/openapi.json").json()["paths"]

    assert set(paths["/tasks"]) == {"get", "post"}
    assert set(paths["/tasks/{task_id}"]) == {"get", "patch", "delete"}
