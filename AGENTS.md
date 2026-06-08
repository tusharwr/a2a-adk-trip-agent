# Repository Guidelines

## Project Structure & Module Organization

This repo is a Google ADK + A2A trip-planning demo with a routing harness that ensures the driver
calls only the specialist agents a query actually needs. Source code lives in:

- `agents/driver/` — orchestration: `pipeline_agent.py` (harness) + `agent.py` (wiring)
- `agents/hotel/`, `agents/flight/`, `agents/activities/` — specialist agents
- `common/` — shared config, prompts, router, pipeline, and A2A helpers
- `scripts/` — smoke tests and end-to-end checks
- `docs/` — design documents

Keep each specialist agent folder parallel: `agent.py` defines the agent, `serve.py` exposes
the A2A service.

### Harness files (do not skip when editing routing or agent behaviour)

| File | Purpose |
|------|---------|
| `common/router.py` | LLM intent classifier — returns selected domain list or `[]` |
| `common/pipeline.py` | Parallel HTTP caller — calls only selected specialists |
| `agents/driver/pipeline_agent.py` | `TripPipelineAgent` — sequences route → pipeline → synthesize |
| `common/prompts.py` | All LLM prompt constants including `ROUTER_PROMPT` |

## Build, Test, and Development Commands

Use `uv` from the repo root:

- `uv sync` — creates/refreshes `.venv` from `pyproject.toml` and `uv.lock`
- `uv run python scripts/smoke_services.py` — checks all four A2A cards (requires all 4 services running)
- `uv run python scripts/test_router.py` — 6-case router unit test (requires Ollama)
- `uv run python scripts/test_pipeline.py` — pipeline + agent instantiation tests (requires specialist services)
- `uv run python scripts/test_driver_trip.py` — E2E full-trip + hotel-only routing assertions (requires all 4 services)

## Coding Style & Naming Conventions

Target Python 3.13. Use 4-space indentation, `snake_case` for functions/modules, and `PascalCase`
only for classes. Keep prompts short and explicit. Prefer small, readable helpers in `common/`
over duplicating logic across agents. There is no formatter or linter configured yet; keep edits
consistent with existing style.

## Testing Guidelines

There is no formal test framework. Use the smoke scripts as the baseline verification:

- `scripts/smoke_services.py` — validates all four A2A card endpoints (HTTP 200, correct agent
  name). Exits non-zero on failure.
- `scripts/test_router.py` — validates the 6 router cases. Tests make real Ollama calls; Ollama
  must be running with the configured model pulled.
- `scripts/test_pipeline.py` — validates parallel specialist calls and `TripPipelineAgent`
  instantiation. Requires specialist services on ports 8001–8003.
- `scripts/test_driver_trip.py` — full-trip Barcelona assertion + hotel-only routing isolation.
  Requires all four services.

When adding behaviour, update or add a script that exercises the new path.

## Adding a New Specialist Agent

1. Create `agents/<name>/agent.py` and `agents/<name>/serve.py` following the existing pattern.
2. Add `<NAME>_PORT` and `<NAME>_AGENT_CARD_URL` to `.env.example`.
3. Add `"<name>"` to `_VALID_DOMAINS` in `common/router.py`.
4. Add the port to `_SPECIALIST_PORTS` and heading to `_HEADINGS` in `common/pipeline.py`.
5. Add the domain with description and examples to `ROUTER_PROMPT` in `common/prompts.py`.
6. Add the specialist prompt constant to `common/prompts.py`.
7. Update `scripts/smoke_services.py` to validate the new card endpoint.

## Commit & Pull Request Guidelines

Use clear imperative commit messages following Conventional Commits style:

- `feat(harness): add LLM-based intent router`
- `fix: correct A2A response text extraction path`
- `docs: update harness architecture doc`
- `test: add hotel-only routing assertion`

Update `CHANGELOG.md` under `[Unreleased]` for every user-visible change.

For pull requests, include:
- a short description of the change
- commands used to verify it
- notes about required environment variables or ports

## Security & Configuration Tips

Do not commit `.env`. Copy from `.env.example` and keep API keys local. The default ports are
`8000`–`8003`; update `*_PORT` only if those ports are already in use.
