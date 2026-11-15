

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_path: str = "tasks.db"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(database_path=os.getenv("TASKS_DB_PATH", cls.database_path))
