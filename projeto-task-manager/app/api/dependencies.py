"""Fiação da injeção de dependências: Settings -> conexão -> repositório -> serviço."""

import sqlite3
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request

from app.config import Settings
from app.database import connect
from app.repositories.base import TaskRepository
from app.repositories.sqlite_task_repository import SQLiteTaskRepository
from app.services.task_service import TaskService


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_db(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Iterator[sqlite3.Connection]:
    """Uma conexão por requisição, sempre fechada ao final (dependência com yield)."""
    connection = connect(settings.database_path)
    try:
        yield connection
    finally:
        connection.close()


def get_task_repository(
    connection: Annotated[sqlite3.Connection, Depends(get_db)],
) -> TaskRepository:
    return SQLiteTaskRepository(connection)


def get_task_service(
    repository: Annotated[TaskRepository, Depends(get_task_repository)],
) -> TaskService:
    return TaskService(repository)
