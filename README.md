# Análise arquitetural do FastAPI + Task Manager API

Trabalho da disciplina de **Arquitetura de Software** (Engenharia de Software).
Analisa o repositório [fastapi/fastapi](https://github.com/fastapi/fastapi) em cinco atividades e aplica o que foi
aprendido num projeto próprio, a **Task Manager API**.

> Autores: Eduardo de Macedo, Endrik Thibes · Professor(a): Paulo Roberto Farah · Instituição: UDESC · 2026

## O que há neste repositório

| Pasta | Conteúdo |
|---|---|
| `docs/trabalho-escrito/` | Trabalho escrito em PDF (Entrega 1) |
| `docs/apresentacao/` | Slides e roteiro de apresentação (Entrega 2) |
| `docs/diagramas/` | Código-fonte dos 6 diagramas em Mermaid (`.mmd`) |
| `docs/fontes.md` | Lista das fontes consultadas |
| `projeto-task-manager/` | Código da Task Manager API (Atividade 5), com testes |

## As cinco atividades

1. **Partes interessadas (stakeholders):** quem são, interesses, necessidades e conflitos.
2. **Pontos de vista:** o que cada grupo espera e quais aspectos arquiteturais priorizam.
3. **Atributos de qualidade com GQM:** nove atributos, com objetivos, perguntas e métricas propostas.
4. **Diagramas e padrões:** contexto, componentes, camadas, sequência; padrões com evidências.
5. **Projeto Task Manager API:** arquitetura em camadas, código e testes.

## Convenção de evidências usada no trabalho

**[C]** comprovado em fonte oficial · **[S]** fonte secundária · **[I]** interpretação dos autores.
As métricas do GQM são **propostas**, não medições do FastAPI. As únicas medições relatadas são as do projeto da
Atividade 5.

## Executar o projeto

```bash
cd projeto-task-manager
python -m venv .venv && source .venv/bin/activate   
pip install -r requirements-dev.txt
pytest                                  
uvicorn app.main:app --reload           
```

## Diagramas

Os arquivos de `docs/diagramas/*.mmd` podem ser colados em <https://mermaid.live>. O GitHub também renderiza
blocos ```` ```mermaid ```` diretamente em arquivos Markdown.

## Status dos testes

<!-- Depois de criar o repositório, troque USUARIO e REPOSITORIO e descomente: -->
<!-- ![tests](https://github.com/USUARIO/REPOSITORIO/actions/workflows/tests.yml/badge.svg) -->
