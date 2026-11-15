# Task Manager API

API acadêmica de gerenciamento de tarefas (FastAPI + Pydantic + SQLite + Pytest),
organizada em camadas. Projeto da disciplina de Arquitetura de Software.

## Executar

Recomendado: Python 3.11 ou superior (testado em 3.12; o código usa a sintaxe `X | None`, que exige 3.10+,
e as versões mais recentes do FastAPI deixaram de suportar o 3.10).

```bash
python -m venv .venv && source .venv/bin/activate  
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Documentação interativa: http://127.0.0.1:8000/docs
Banco: arquivo `tasks.db` (altere com a variável `TASKS_DB_PATH`).

## Testar

```bash
pytest                   
pytest --cov=app --cov-report=term-missing
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | `/tasks` | Cadastra tarefa (201) |
| GET | `/tasks?status=&limit=&offset=` | Lista com filtro e paginação |
| GET | `/tasks/{id}` | Consulta uma tarefa |
| PATCH | `/tasks/{id}` | Atualiza campos enviados |
| DELETE | `/tasks/{id}` | Exclui (204) |
| GET | `/health` | Verificação de saúde |

## Camadas (dependências apontam sempre para baixo)

`api` → `services` → `repositories` (contrato) ← `SQLite` · `domain` é usado por todas.
