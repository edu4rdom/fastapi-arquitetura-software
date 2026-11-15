"""Testes de arquitetura: garantem a regra de dependência entre camadas.

Lêem os imports de cada arquivo (via AST) e falham se uma camada importar
algo que não deveria conhecer.
"""

import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parent.parent / "app"

# camada -> prefixos de módulo que ela NÃO pode importar
FORBIDDEN = {
    "domain": ["fastapi", "starlette", "pydantic", "sqlite3", "app.api",
               "app.services", "app.repositories", "app.database", "app.config"],
    "services": ["fastapi", "starlette", "pydantic", "sqlite3", "app.api",
                 "app.database", "app.repositories.sqlite_task_repository"],
    "repositories": ["fastapi", "starlette", "pydantic", "app.api", "app.services"],
}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def is_forbidden(module: str, prefixes: list[str]) -> bool:
    return any(module == p or module.startswith(p + ".") for p in prefixes)


@pytest.mark.parametrize("layer", FORBIDDEN)
def test_layer_does_not_import_forbidden_modules(layer):
    files = sorted((APP / layer).rglob("*.py"))
    assert files, f"nenhum arquivo encontrado em app/{layer}"

    violations = [
        f"{file.relative_to(APP)} importa {module}"
        for file in files
        for module in imported_modules(file)
        if is_forbidden(module, FORBIDDEN[layer])
    ]

    assert violations == []
