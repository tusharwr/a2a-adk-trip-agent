# Switch Local LLM Provider from OpenAI to Ollama

**Date:** 2026-05-20
**Status:** Approved

## Goal

Replace OpenAI API-dependent models with locally-run Ollama models so the project
works without API credits.

## Architecture

No architectural changes. The existing LiteLLM abstraction already supports the
`ollama/` provider prefix. The change is purely configuration:

```
User prompt → Driver Agent → LiteLlm(model=ollama/...) → Ollama server (localhost:11434)
                                ↓
                         Specialist Agents (hotel/flight/activities)
                         each also using LiteLlm(model=ollama/...)
```

## Files Changed

| File | Change | Rationale |
|------|--------|-----------|
| `.env` | `OPENAI_API_KEY=ollama` + `OPENAI_MODEL=ollama/qwen2.5:1.5b` | Runtime config — points all agents to local Ollama |
| `.env.example` | Document OpenAI, Ollama, and other providers | Template for new developers |
| `common/config.py` | Default model `ollama/qwen2.5:1.5b` | Fallback if env var is unset |
| `README.md` | Model choice section covers all providers | Documentation |
| `RUN_INSTRUCTIONS.md` | Setup steps for Ollama + OpenAI | Documentation |

## Zero Python Code Changes

The `model=LiteLlm(model=model_name())` pattern in all four agent files remains
untouched. The entire switch is handled by changing environment variables.

## Provider Flexibility

To switch back to OpenAI or to another provider, only `.env` needs changing:

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=openai/gpt-4o-mini

# Ollama
OPENAI_API_KEY=ollama
OPENAI_MODEL=ollama/qwen2.5:1.5b

# Anthropic (or any LiteLLM-supported provider)
OPENAI_API_KEY=sk-ant-...
OPENAI_MODEL=anthropic/claude-sonnet-4-20250514
```

## User Steps to Complete the Switch

1. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
2. Pull the model: `ollama pull qwen2.5:1.5b`
3. Ensure Ollama is running: `ollama serve` (usually runs as a service)
4. Rebuild the venv: `uv sync`
5. Run smoke tests: `uv run python scripts/smoke_services.py`

## Verification

- `smoke_services.py` — validates all four A2A agent-card endpoints (HTTP 200, correct agent name) and verifies driver sub-agent card resolution via HTTP. Exits non-zero on failure.
- `test_driver_trip.py` — end-to-end trip prompt through the driver with content assertions (response must mention hotels, flights, and activities). Exits non-zero on failure.
- No Python syntax or import errors
