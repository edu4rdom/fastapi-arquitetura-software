

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT NOT NULL,
    description  TEXT NOT NULL DEFAULT '',
    status       TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'done')),
    priority     TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high')),
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);

-- Rede de segurança da regra RN1: no máximo uma tarefa NÃO concluída por título.
CREATE UNIQUE INDEX IF NOT EXISTS uq_tasks_active_title
    ON tasks (lower(title)) WHERE status <> 'done';
"""


def connect(db_path: str) -> sqlite3.Connection:

    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: str) -> None:
    connection = connect(db_path)
    try:
        connection.executescript(SCHEMA)
        connection.commit()
    finally:
        connection.close()
