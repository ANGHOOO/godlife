# Repository Guidelines

## Project Structure & Module Organization
This repository is intentionally lightweight and currently contains:
- `main.py` — application entry point (`main()` prints the startup message).
- `pyproject.toml` — package metadata and Python version requirements.
- `README.md` — overview and future notes.
- (No dedicated test or asset directories yet.)

Keep source changes centered in `main.py` for now. If you add modules, place reusable code under a package directory (for example `godlife/`) and keep scripts/experiments in clearly named files outside package modules.

## Build, Test, and Development Commands
- `python main.py`
  Runs the current app directly.
- `python -m venv .venv && source .venv/bin/activate`
  Creates/uses an isolated environment.
- `pip install -e .` (after activating venv)
  Installs this package in editable mode for local development.
- `python -m pip install pytest ruff` *(optional local tooling)*
  Installs recommended test/lint tools.

## Coding Style & Naming Conventions
- Always use Context7 MCP when I need library/API documentation, code generation, setup or configuration steps without me having to explicitly ask.
- Use 4-space indentation and UTF-8 encoding.
- Prefer explicit function names and docstrings for new public functions.
- Naming: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE` for constants.
- Keep modules small and focused; avoid large monolithic functions in `main.py`.
- If adding formatting/linting, standardize on `ruff` for lint/format and `black`-style formatting (line length 88 unless project needs otherwise).

## Testing Guidelines
There is no formal test suite yet. New behavior should be covered with `pytest` tests:
- Test files: `tests/test_*.py`
- Test functions: `def test_*():`
- Run: `pytest -q`
- Add tests for edge cases and I/O behavior around new CLI logic.

## Commit & Pull Request Guidelines
No commit history is available in this repository, so use a consistent convention:
- `feat:`, `fix:`, `chore:`, `refactor:` + short scope (Conventional Commits).
- One logical change per commit.
- PRs should include:
  - Summary of user-visible changes
  - Validation steps (commands run)
  - Any config/build impacts
  - Issue/goal reference if applicable

## Security & Configuration Tips
Use a virtual environment for all local work. Avoid committing credentials, API keys, or environment files. Since this project currently has no external dependencies, prefer dependency updates in `pyproject.toml` only when needed and keep them minimal.
