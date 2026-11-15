"""Rotas HTTP de tarefas. Só traduz HTTP <-> serviço; não contém regra de negócio."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.dependencies import get_task_service
from app.api.schemas import TaskCreate, TaskRead, TaskUpdate
from app.domain.task import Task, TaskStatus
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

ServiceDep = Annotated[TaskService, Depends(get_task_service)]
TaskId = Annotated[int, Path(ge=1, description="Identificador da tarefa")]


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, service: ServiceDep) -> Task:
    return service.create_task(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
    )


@router.get("", response_model=list[TaskRead])
def list_tasks(
    service: ServiceDep,
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Task]:
    return service.list_tasks(status=task_status, limit=limit, offset=offset)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: TaskId, service: ServiceDep) -> Task:
    return service.get_task(task_id)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: TaskId, payload: TaskUpdate, service: ServiceDep) -> Task:
    # exclude_unset: só o que o cliente realmente enviou chega ao serviço.
    return service.update_task(task_id, payload.model_dump(exclude_unset=True))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: TaskId, service: ServiceDep) -> None:
    service.delete_task(task_id)
