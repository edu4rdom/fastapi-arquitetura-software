

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.error_handlers import register_error_handlers
from app.api.routes import tasks
from app.config import Settings
from app.database import init_db


def create_app(settings: Settings | None = None) -> FastAPI:

    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        init_db(settings.database_path)  
        yield

    app = FastAPI(
        title="Task Manager API",
        description="API acadêmica de gerenciamento de tarefas em camadas.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = settings
    register_error_handlers(app)
    app.include_router(tasks.router)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
