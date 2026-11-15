

import pytest

from app.domain.exceptions import (
    DuplicateTaskTitleError,
    InvalidTaskError,
    TaskNotFoundError,
)
from app.domain.task import TaskPriority, TaskStatus


def test_create_task_sets_defaults_and_timestamps(fake_service):
    task = fake_service.create_task(title="Estudar")

    assert task.id == 1
    assert task.status is TaskStatus.PENDING
    assert task.priority is TaskPriority.MEDIUM
    assert task.created_at == task.updated_at
    assert task.completed_at is None


def test_create_task_trims_title(fake_service):
    assert fake_service.create_task(title="  Estudar  ").title == "Estudar"


def test_create_task_rejects_blank_title(fake_service):
    with pytest.raises(InvalidTaskError):
        fake_service.create_task(title="   ")


def test_create_task_rejects_duplicate_active_title_ignoring_case(fake_service):
    fake_service.create_task(title="Estudar")
    with pytest.raises(DuplicateTaskTitleError):
        fake_service.create_task(title="ESTUDAR")


def test_title_can_be_reused_after_task_is_done(fake_service):
    first = fake_service.create_task(title="Estudar")
    fake_service.update_task(first.id, {"status": TaskStatus.DONE})

    assert fake_service.create_task(title="Estudar").id == 2


def test_get_task_raises_when_missing(fake_service):
    with pytest.raises(TaskNotFoundError):
        fake_service.get_task(99)


def test_completing_a_task_sets_completed_at_and_reopening_clears_it(fake_service):
    task = fake_service.create_task(title="Estudar")

    done = fake_service.update_task(task.id, {"status": TaskStatus.DONE})
    assert done.completed_at == done.updated_at

    reopened = fake_service.update_task(task.id, {"status": TaskStatus.IN_PROGRESS})
    assert reopened.completed_at is None


def test_update_is_partial(fake_service):
    task = fake_service.create_task(title="Estudar", description="Capítulo 1")

    updated = fake_service.update_task(task.id, {"priority": TaskPriority.HIGH})

    assert updated.priority is TaskPriority.HIGH
    assert updated.title == "Estudar"
    assert updated.description == "Capítulo 1"
    assert updated.updated_at > task.updated_at


def test_update_rejects_unknown_fields(fake_service):
    task = fake_service.create_task(title="Estudar")
    with pytest.raises(InvalidTaskError):
        fake_service.update_task(task.id, {"id": 10})


def test_reopening_a_task_conflicts_with_an_active_task_of_same_title(fake_service):
    old = fake_service.create_task(title="Estudar")
    fake_service.update_task(old.id, {"status": TaskStatus.DONE})
    fake_service.create_task(title="Estudar")

    with pytest.raises(DuplicateTaskTitleError):
        fake_service.update_task(old.id, {"status": TaskStatus.PENDING})


def test_list_filters_by_status_and_paginates(fake_service):
    for name in ("A", "B", "C"):
        fake_service.create_task(title=name)
    fake_service.update_task(2, {"status": TaskStatus.DONE})

    done = fake_service.list_tasks(status=TaskStatus.DONE)
    page = fake_service.list_tasks(limit=2, offset=1)

    assert [t.title for t in done] == ["B"]
    assert [t.title for t in page] == ["B", "C"]


def test_delete_task_removes_it_and_fails_when_missing(fake_service):
    task = fake_service.create_task(title="Estudar")
    fake_service.delete_task(task.id)

    with pytest.raises(TaskNotFoundError):
        fake_service.get_task(task.id)
    with pytest.raises(TaskNotFoundError):
        fake_service.delete_task(task.id)


def test_update_title_is_trimmed_and_cannot_be_blank(fake_service):
    task = fake_service.create_task(title="Estudar")

    assert fake_service.update_task(task.id, {"title": "  Revisar  "}).title == "Revisar"
    with pytest.raises(InvalidTaskError):
        fake_service.update_task(task.id, {"title": "   "})
