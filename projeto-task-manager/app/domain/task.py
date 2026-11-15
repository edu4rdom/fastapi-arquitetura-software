"""Entidades do domínio. Não dependem de FastAPI, Pydantic nem SQLite."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class NewTask:
    """Dados de uma tarefa que ainda não foi persistida (não tem id)."""

    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


@dataclass(frozen=True)
class Task:
    """Tarefa persistida. Imutável: alterações geram uma nova instância."""

    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
