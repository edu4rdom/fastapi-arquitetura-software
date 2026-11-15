"""Exceções de domínio. A camada de API as traduz para códigos HTTP."""


class DomainError(Exception):
    """Base de todos os erros de regra de negócio."""


class TaskNotFoundError(DomainError):
    def __init__(self, task_id: int) -> None:
        super().__init__(f"Tarefa {task_id} não encontrada.")
        self.task_id = task_id


class InvalidTaskError(DomainError):
    """Dados que violam um invariante do domínio."""


class DuplicateTaskTitleError(DomainError):
    def __init__(self, title: str) -> None:
        super().__init__(f"Já existe uma tarefa ativa com o título '{title}'.")
        self.title = title
