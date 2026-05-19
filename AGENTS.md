# Repository Guidelines

## Project Structure & Module Organization
This repo is a small Google ADK + A2A trip-planning demo. Source code lives in:

- `agents/driver/` for orchestration and routing
- `agents/hotel/`, `agents/flight/`, `agents/activities/` for specialist agents
- `common/` for shared config, prompts, and A2A helpers
- `scripts/` for local smoke tests and end-to-end checks

Keep each agent folder parallel: `agent.py` defines the agent, `serve.py` exposes the service.

## Build, Test, and Development Commands
Use `uv` from the repo root:

- `uv sync` creates/refreshes `.venv` from `pyproject.toml` and `uv.lock`
- `uv run python scripts/smoke_services.py` checks all four A2A cards and verifies driver sub-agent resolution
- `uv run python scripts/test_driver_trip.py` runs the end-to-end Barcelona trip prompt through the driver
- `uv run python -m agents.hotel.serve` starts one specialist service; swap `hotel` for `flight`, `activities`, or `driver`

## Coding Style & Naming Conventions
Target Python 3.13. Use 4-space indentation, `snake_case` for functions/modules, and `PascalCase` only for classes. Keep prompts short and explicit. Prefer small, readable helpers in `common/` over duplicating logic across agents. There is no formatter or linter configured yet, so keep edits consistent with existing style.

## Testing Guidelines
There is no formal test framework yet. Use the smoke scripts as the baseline verification:

- `scripts/smoke_services.py` for service/card wiring
- `scripts/test_driver_trip.py` for a real driver invocation

When adding behavior, update or add a script that exercises the new path.

## Commit & Pull Request Guidelines
This repository has no prior commit history, so use clear imperative commit messages such as `Add hotel agent smoke test`. For pull requests, include:

- a short description of the change
- commands used to verify it
- notes about required environment variables or ports

## Security & Configuration Tips
Do not commit `.env`. Copy from `.env.example` and keep API keys local. The default ports are `8000`-`8003`; update `*_PORT` only if those ports are already in use.
