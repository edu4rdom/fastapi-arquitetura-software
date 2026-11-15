"""Testes de integração: o repositório contra um SQLite real (arquivo temporário)."""

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from app.domain.exceptions import DuplicateTaskTitleError, TaskNotFoundError
from app.domain.task import NewTask, TaskPriority, TaskStatus

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


def make_new_task(title="Estudar", status=TaskStatus.PENDING) -> NewTask:
    return NewTask(
        title=title,
        description="",
        status=status,
        priority=TaskPriority.MEDIUM,
        created_at=NOW,
        updated_at=NOW,
    )


def test_add_and_get_roundtrip(sqlite_repository):
    created = sqlite_repository.add(make_new_task())

    assert created.id == 1
    assert sqlite_repository.get(created.id) == created
    assert created.created_at == NOW  # datas voltam com fuso e valor preservados


def test_get_returns_none_when_missing(sqlite_repository):
    assert sqlite_repository.get(42) is None


def test_find_all_filters_and_paginates(sqlite_repository):
    sqlite_repository.add(make_new_task("A"))
    sqlite_repository.add(make_new_task("B", TaskStatus.DONE))
    sqlite_repository.add(make_new_task("C"))

    pending = sqlite_repository.find_all(status=TaskStatus.PENDING, limit=10, offset=0)
    page = sqlite_repository.find_all(status=None, limit=1, offset=2)

    assert [t.title for t in pending] == ["A", "C"]
    assert [t.title for t in page] == ["C"]


def test_update_persists_changes(sqlite_repository):
    created = sqlite_repository.add(make_new_task())

    sqlite_repository.update(replace(created, status=TaskStatus.DONE, completed_at=NOW))

    stored = sqlite_repository.get(created.id)
    assert stored.status is TaskStatus.DONE
    assert stored.completed_at == NOW


def test_delete_reports_whether_a_row_was_removed(sqlite_repository):
    created = sqlite_repository.add(make_new_task())

    assert sqlite_repository.delete(created.id) is True
    assert sqlite_repository.delete(created.id) is False


def test_database_enforces_unique_active_title_as_safety_net(sqlite_repository):
    sqlite_repository.add(make_new_task("Estudar"))

    with pytest.raises(DuplicateTaskTitleError):
        sqlite_repository.add(make_new_task("estudar"))


def test_database_allows_same_title_when_existing_task_is_done(sqlite_repository):
    sqlite_repository.add(make_new_task("Estudar", TaskStatus.DONE))

    assert sqlite_repository.add(make_new_task("Estudar")).id == 2


def test_exists_active_title_can_exclude_a_task(sqlite_repository):
    created = sqlite_repository.add(make_new_task("Estudar"))

    assert sqlite_repository.exists_active_title("ESTUDAR") is True
    assert sqlite_repository.exists_active_title("Estudar", exclude_id=created.id) is False


def test_update_of_missing_task_raises_not_found(sqlite_repository):
    created = sqlite_repository.add(make_new_task())
    sqlite_repository.delete(created.id)

    with pytest.raises(TaskNotFoundError):
        sqlite_repository.update(created)


def test_update_to_duplicate_active_title_is_blocked_by_the_database(sqlite_repository):
    sqlite_repository.add(make_new_task("A"))
    second = sqlite_repository.add(make_new_task("B"))

    with pytest.raises(DuplicateTaskTitleError):
        sqlite_repository.update(replace(second, title="a"))
