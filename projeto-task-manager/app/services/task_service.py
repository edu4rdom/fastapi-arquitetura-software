"""Regras de negócio. Não conhece HTTP, Pydantic nem SQL."""

from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from app.domain.exceptions import (
    DuplicateTaskTitleError,
    InvalidTaskError,
    TaskNotFoundError,
)
from app.domain.task import NewTask, Task, TaskPriority, TaskStatus
from app.repositories.base import TaskRepository

# Campos que um cliente pode alterar. Tudo fora disto é rejeitado.
UPDATABLE_FIELDS = {"title", "description", "status", "priority"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._clock = clock  # injetável: permite testes determinísticos

    def create_task(
        self,
        *,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> Task:
        title = self._normalize_title(title)
        # RN1: não pode haver duas tarefas ativas com o mesmo título.
        if self._repository.exists_active_title(title):
            raise DuplicateTaskTitleError(title)
        now = self._clock()
        return self._repository.add(
            NewTask(
                title=title,
                description=description,
                status=TaskStatus.PENDING,
                priority=priority,
                created_at=now,
                updated_at=now,
            )
        )

    def get_task(self, task_id: int) -> Task:
        task = self._repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def list_tasks(
        self, *, status: TaskStatus | None = None, limit: int = 50, offset: int = 0
    ) -> list[Task]:
        return self._repository.find_all(status=status, limit=limit, offset=offset)

    def update_task(self, task_id: int, changes: Mapping[str, Any]) -> Task:
        unknown = set(changes) - UPDATABLE_FIELDS
        if unknown:
            raise InvalidTaskError(f"Campos não atualizáveis: {sorted(unknown)}")

        current = self.get_task(task_id)
        values = dict(changes)
        if "title" in values:
            values["title"] = self._normalize_title(values["title"])

        now = self._clock()
        updated = replace(current, **values, updated_at=now)

        # RN2: completed_at acompanha o status automaticamente.
        if updated.status is TaskStatus.DONE and current.status is not TaskStatus.DONE:
            updated = replace(updated, completed_at=now)
        elif updated.status is not TaskStatus.DONE:
            updated = replace(updated, completed_at=None)

        # RN1 também vale ao editar o título ou ao reabrir uma tarefa concluída.
        if updated.status is not TaskStatus.DONE and self._repository.exists_active_title(
            updated.title, exclude_id=updated.id
        ):
            raise DuplicateTaskTitleError(updated.title)

        return self._repository.update(updated)

    def delete_task(self, task_id: int) -> None:
        if not self._repository.delete(task_id):
            raise TaskNotFoundError(task_id)

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Invariante de domínio, garantido mesmo sem a validação da API."""
        title = title.strip()
        if not title:
            raise InvalidTaskError("O título não pode ser vazio.")
        return title
