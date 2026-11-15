"""Repositório em memória que satisfaz o contrato TaskRepository."""

from dataclasses import replace

from app.domain.exceptions import TaskNotFoundError
from app.domain.task import NewTask, Task, TaskStatus


class FakeTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def add(self, new_task: NewTask) -> Task:
        task = Task(id=self._next_id, **vars(new_task))
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def find_all(
        self, *, status: TaskStatus | None, limit: int, offset: int
    ) -> list[Task]:
        items = [t for t in self._tasks.values() if status is None or t.status is status]
        return items[offset : offset + limit]

    def update(self, task: Task) -> Task:
        if task.id not in self._tasks:
            raise TaskNotFoundError(task.id)
        self._tasks[task.id] = replace(task)
        return task

    def delete(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None

    def exists_active_title(self, title: str, *, exclude_id: int | None = None) -> bool:
        return any(
            t.title.lower() == title.lower()
            and t.status is not TaskStatus.DONE
            and t.id != exclude_id
            for t in self._tasks.values()
        )
