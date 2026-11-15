"""Contrato (porta) de persistência. O serviço depende disto, não do SQLite."""

from typing import Protocol

from app.domain.task import NewTask, Task, TaskStatus


class TaskRepository(Protocol):
    def add(self, new_task: NewTask) -> Task: ...

    def get(self, task_id: int) -> Task | None: ...

    def find_all(
        self, *, status: TaskStatus | None, limit: int, offset: int
    ) -> list[Task]: ...

    def update(self, task: Task) -> Task: ...

    def delete(self, task_id: int) -> bool: ...

    def exists_active_title(self, title: str, *, exclude_id: int | None = None) -> bool: ...
