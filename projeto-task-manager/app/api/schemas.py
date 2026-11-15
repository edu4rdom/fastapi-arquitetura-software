"""Contratos HTTP (Pydantic): o que entra e o que sai pela API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(min_length=1, max_length=120, examples=["Estudar arquitetura"])
    description: str = Field(default="", max_length=1000)
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskUpdate(BaseModel):
    """Atualização parcial: só os campos enviados são alterados."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None

    @model_validator(mode="after")
    def _check_sent_fields(self) -> "TaskUpdate":
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualizar.")
        for name in self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"O campo '{name}' não pode ser nulo.")
        return self


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
