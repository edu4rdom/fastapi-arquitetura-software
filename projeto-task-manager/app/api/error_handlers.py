"""Tradução de erros de domínio para respostas HTTP, em um único lugar."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    DuplicateTaskTitleError,
    InvalidTaskError,
    TaskNotFoundError,
)


def _json(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": message})


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(TaskNotFoundError)
    async def _not_found(request: Request, exc: TaskNotFoundError) -> JSONResponse:
        return _json(status.HTTP_404_NOT_FOUND, str(exc))

    @app.exception_handler(DuplicateTaskTitleError)
    async def _conflict(request: Request, exc: DuplicateTaskTitleError) -> JSONResponse:
        return _json(status.HTTP_409_CONFLICT, str(exc))

    @app.exception_handler(InvalidTaskError)
    async def _invalid(request: Request, exc: InvalidTaskError) -> JSONResponse:
        return _json(422, str(exc))
