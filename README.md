# A2A ADK Trip Agent

A multi-agent trip planner built with Google ADK and the A2A protocol. A **routing harness**
ensures the driver uses only the specialist agents a query actually needs, and asks for
clarification when the intent is unclear.

## Agents

| Agent | Port | Role |
|-------|------|------|
| `driver` | 8000 | Orchestrator — routes queries and synthesizes responses |
| `hotel` | 8001 | Hotel and accommodation recommendations |
| `flight` | 8002 | Flight and airport guidance |
| `activities` | 8003 | Sights, food, and local experiences |

## How routing works

The driver does **not** call all specialists for every query. It runs three focused steps:

1. **Router LLM call** — classifies the query and returns only the needed domains
   (e.g. `["hotel"]` for "best hotels near La Rambla").
2. **Parallel HTTP pipeline** — calls only those specialist A2A services.
3. **Synthesis LLM call** — combines the specialist reports into a readable response.

Unclear queries ("Hello", missing destination) receive a clarification question — no specialists
are called.

```
"Plan a trip to Barcelona"  →  router → ["hotel","flight","activities"] → 3 parallel calls → synthesis
"Best hotels in Tokyo?"     →  router → ["hotel"]                       → 1 call          → direct output
"Hello"                     →  router → []                              → clarification message
```

## Repo layout

```
a2a-adk-trip-agent/
  agents/
    driver/
      agent.py           ← wires TripPipelineAgent as root_agent
      pipeline_agent.py  ← harness orchestrator (BaseAgent subclass)
    hotel/
    flight/
    activities/
  common/
    config.py            ← env-var helpers
    prompts.py           ← all LLM prompt constants
    router.py            ← LLM-based intent classifier
    pipeline.py          ← parallel A2A HTTP caller
    a2a.py               ← RemoteA2aAgent builder
  scripts/
    smoke_services.py    ← validates all four A2A card endpoints
    test_driver_trip.py  ← E2E full-trip + hotel-only assertions
    test_router.py       ← 6-case router unit test
    test_pipeline.py     ← pipeline + agent instantiation tests
  docs/
    harness-architecture.md  ← deep-dive on the harness design
  CHANGELOG.md
  pyproject.toml
  .env.example
```

## Quick start

```powershell
uv sync
cp .env.example .env   # configure OPENAI_MODEL and OPENAI_API_KEY
```

Start in four terminals:

```powershell
uv run python -m agents.hotel.serve
uv run python -m agents.flight.serve
uv run python -m agents.activities.serve
$env:PYTHONPATH="."; uv run adk web agents --port 8000
```

Open `http://127.0.0.1:8000`, select `driver`, and try:

- `"Plan a 3-day trip to Barcelona"` → full plan (hotel + flight + activities)
- `"Best hotels near La Rambla?"` → hotel section only
- `"Hello"` → clarification question

## Model configuration

All agents use LiteLLM, so `OPENAI_MODEL` accepts any provider prefix:

| Provider | `OPENAI_MODEL` | `OPENAI_API_KEY` |
|----------|----------------|-----------------|
| Ollama (local) | `ollama/qwen2.5:1.5b` | `ollama` (literal) |
| OpenAI | `openai/gpt-4o-mini` | real key |
| Anthropic | `anthropic/claude-haiku-4-5-20251001` | real key |

Default is `ollama/qwen2.5:1.5b`. For Ollama, install from [ollama.com](https://ollama.com) then
`ollama pull qwen2.5:1.5b`.

## Testing

```powershell
uv run python scripts/smoke_services.py       # agent card health check (needs all 4 services)
uv run python scripts/test_router.py          # router unit tests (needs Ollama)
uv run python scripts/test_pipeline.py        # pipeline tests (needs specialist services)
uv run python scripts/test_driver_trip.py     # E2E full-trip + hotel-only (needs all 4 services)
```

## Documentation

- [`docs/harness-architecture.md`](docs/harness-architecture.md) — design, request flow diagram,
  trade-offs, and how to add a new specialist agent.
- [`CHANGELOG.md`](CHANGELOG.md) — version history.

## Notes

- Not connected to any live booking APIs — outputs are illustrative.
- Never commit your `.env` file or API keys.
