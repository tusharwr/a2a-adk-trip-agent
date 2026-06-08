# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```powershell
uv sync                    # create/refresh .venv from pyproject.toml + uv.lock
cp .env.example .env       # then configure OPENAI_API_KEY and OPENAI_MODEL
```

## Running the system

Start the three specialist services first, then the driver (each in a separate terminal):

```powershell
uv run python -m agents.hotel.serve       # port 8001
uv run python -m agents.flight.serve      # port 8002
uv run python -m agents.activities.serve  # port 8003
$env:PYTHONPATH="."; uv run adk web agents --port 8000   # ADK Web UI + driver
```

## Testing

No formal test framework — use the smoke scripts:

```powershell
uv run python scripts/smoke_services.py      # validates all four A2A card endpoints
uv run python scripts/test_router.py         # 6-case router unit test (needs Ollama)
uv run python scripts/test_pipeline.py       # pipeline + agent instantiation (needs specialist services)
uv run python scripts/test_driver_trip.py    # E2E full-trip + hotel-only routing (needs all 4 services)
```

All scripts exit non-zero on failure. Run after any structural change.

## Architecture

This is a Google ADK multi-agent system using the A2A protocol. Routing and specialist calls are
handled by a **Python harness** — not by LLM tool-calling — so the system works reliably with
small local models (1.5B parameters).

**Agent roles:**
- `driver_agent` (port 8000) — `TripPipelineAgent` (BaseAgent subclass); routes query, calls
  selected specialists via HTTP, synthesizes results
- `hotel_agent` (port 8001), `flight_agent` (port 8002), `activities_agent` (port 8003) —
  specialists with focused prompts; each response must start with its domain heading

**Harness flow (inside `TripPipelineAgent._run_async_impl`):**
1. `common/router.py:route_query()` — one LiteLLM call at `temperature=0` returns
   `{"domains": [...]}` → empty list triggers clarification
2. `common/pipeline.py:gather_specialist_reports()` — `asyncio.gather` over selected domains,
   parallel HTTP POST to each specialist A2A endpoint
3. Synthesis — second LiteLLM call combines reports; skipped for single-domain queries

**Two-file agent pattern (specialist agents only):**
- `agents/<name>/agent.py` — ADK `Agent` with `LiteLlm` model + system prompt from `common/prompts.py`
- `agents/<name>/serve.py` — wraps agent in FastAPI A2A server via `to_a2a()`, exposes `/.well-known/agent-card.json`

**Driver is different — three files:**
- `agents/driver/agent.py` — wires `TripPipelineAgent` as `root_agent`; keeps `hotel_agent`,
  `flight_agent`, `activities_agent` as module-level names for `smoke_services.py` compatibility
- `agents/driver/pipeline_agent.py` — `TripPipelineAgent(BaseAgent)` implementation

**Shared utilities in `common/`:**
- `config.py` — reads `OPENAI_MODEL`, `TRIP_AGENT_HOST`, and `*_PORT` env vars with sensible defaults
- `prompts.py` — `ROUTER_PROMPT`, `DRIVER_INSTRUCTION`, and specialist prompt constants
- `router.py` — `route_query(query) -> list[str]` using `litellm.acompletion`
- `pipeline.py` — `gather_specialist_reports(query, domains) -> str` parallel HTTP caller
- `a2a.py` — `build_remote_agent()` helper; still used in `driver/agent.py` for smoke_services

**A2A endpoint:** The A2A message endpoint is at the service root (e.g. `http://127.0.0.1:8001`),
not `/message/send`. Response text is at `result.artifacts[0].parts[0].text`.

## Model configuration

All agents use LiteLLM, so `OPENAI_MODEL` accepts any LiteLLM provider prefix:

| Provider | `OPENAI_MODEL` value | `OPENAI_API_KEY` |
|----------|----------------------|------------------|
| Ollama (local) | `ollama/qwen2.5:1.5b` | `ollama` (literal) |
| OpenAI | `openai/gpt-4o-mini` | real key |
| Anthropic | `anthropic/claude-haiku-4-5-20251001` | real key |

Default is `ollama/qwen2.5:1.5b`. For Ollama, run `ollama pull <model>` first.

## Adding a new specialist agent

1. Create `agents/<name>/agent.py` and `agents/<name>/serve.py` following the existing pattern.
2. Add `<NAME>_PORT` and `<NAME>_AGENT_CARD_URL` to `.env.example`.
3. Add `"<name>"` to `_VALID_DOMAINS` in `common/router.py`.
4. Add port to `_SPECIALIST_PORTS` and heading to `_HEADINGS` in `common/pipeline.py`.
5. Add the domain to `ROUTER_PROMPT` in `common/prompts.py`; add the specialist prompt constant.
6. Update `scripts/smoke_services.py` to validate the new card endpoint.
