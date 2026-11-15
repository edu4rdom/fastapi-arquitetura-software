"""Implementação do repositório de tarefas sobre SQLite (SQL parametrizado)."""

import sqlite3
from datetime import datetime

from app.domain.exceptions import DuplicateTaskTitleError, TaskNotFoundError
from app.domain.task import NewTask, Task, TaskPriority, TaskStatus


def _to_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _from_iso(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        status=TaskStatus(row["status"]),
        priority=TaskPriority(row["priority"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        completed_at=_from_iso(row["completed_at"]),
    )


class SQLiteTaskRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def add(self, new_task: NewTask) -> Task:
        try:
            cursor = self._conn.execute(
                "INSERT INTO tasks (title, description, status, priority, "
                "created_at, updated_at, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    new_task.title,
                    new_task.description,
                    new_task.status.value,
                    new_task.priority.value,
                    _to_iso(new_task.created_at),
                    _to_iso(new_task.updated_at),
                    _to_iso(new_task.completed_at),
                ),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as exc:
            self._conn.rollback()
            raise self._translate(exc, new_task.title) from exc
        task = self.get(cursor.lastrowid)
        assert task is not None
        return task

    def get(self, task_id: int) -> Task | None:
        row = self._conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return _row_to_task(row) if row else None

    def find_all(
        self, *, status: TaskStatus | None, limit: int, offset: int
    ) -> list[Task]:
        query = "SELECT * FROM tasks"
        params: list[object] = []
        if status is not None:
            query += " WHERE status = ?"
            params.append(status.value)
        query += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self._conn.execute(query, params).fetchall()
        return [_row_to_task(row) for row in rows]

    def update(self, task: Task) -> Task:
        try:
            cursor = self._conn.execute(
                "UPDATE tasks SET title = ?, description = ?, status = ?, "
                "priority = ?, updated_at = ?, completed_at = ? WHERE id = ?",
                (
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    _to_iso(task.updated_at),
                    _to_iso(task.completed_at),
                    task.id,
                ),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as exc:
            self._conn.rollback()
            raise self._translate(exc, task.title) from exc
        if cursor.rowcount == 0:
            raise TaskNotFoundError(task.id)
        return task

    def delete(self, task_id: int) -> bool:
        cursor = self._conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def exists_active_title(
        self, title: str, *, exclude_id: int | None = None
    ) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM tasks WHERE lower(title) = lower(?) "
            "AND status <> 'done' AND (? IS NULL OR id <> ?) LIMIT 1",
            (title, exclude_id, exclude_id),
        ).fetchone()
        return row is not None

    @staticmethod
    def _translate(exc: sqlite3.IntegrityError, title: str) -> Exception:
        """Converte erro técnico do SQLite em erro de domínio, quando possível."""
        if "UNIQUE" in str(exc):
            return DuplicateTaskTitleError(title)
        return exc
