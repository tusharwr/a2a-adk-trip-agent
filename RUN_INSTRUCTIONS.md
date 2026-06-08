# Run Instructions

## 1. Set up `uv`

If `uv` is not installed yet:

```powershell
python -m pip install --user uv
```

## 2. Create the environment

From the repo root:

```powershell
uv sync
```

This creates `.venv` and installs the project dependencies.
If Python 3.13 is not already installed locally, `uv` will download it when syncing.

## 3. Configure environment variables

Copy `.env.example` to `.env` and set your model provider.

### Option A: Use Ollama (local, free)

1. Install [Ollama](https://ollama.com):
   - Windows: download the installer from ollama.com or `winget install Ollama.Ollama`
   - macOS/Linux: `curl -fsSL https://ollama.com/install.sh | sh`
2. Pull a model:
   ```powershell
   ollama pull qwen2.5:1.5b
   ```
3. In `.env`, set:
   ```env
   OPENAI_API_KEY=ollama
   OPENAI_MODEL=ollama/qwen2.5:1.5b
   ```

### Option B: Use OpenAI

In `.env`, set:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=openai/gpt-4o-mini
```

### Other providers

See [LiteLLM docs](https://docs.litellm.ai/docs/providers) for Anthropic, Gemini, AWS Bedrock,
and more. Just change `OPENAI_MODEL` to the `provider/model-name` format.

## 4. Start the specialist agents

Open three terminals from the repo root.

**Hotel agent:**
```powershell
uv run python -m agents.hotel.serve
```

**Flight agent:**
```powershell
uv run python -m agents.flight.serve
```

**Activities agent:**
```powershell
uv run python -m agents.activities.serve
```

Each service exposes an A2A card on its configured port (8001, 8002, 8003).

## 5. Start the ADK Web UI

In a fourth terminal:

```powershell
$env:PYTHONPATH="."; uv run adk web agents --port 8000
```

Open the browser URL shown by ADK (typically `http://127.0.0.1:8000`), then select the `driver`
agent.

## 6. Test trip queries

The driver uses a routing harness — it calls only the specialists a query actually needs.

| Query | Expected behaviour |
|-------|--------------------|
| `"Plan a 3-day trip to Barcelona for 2 people"` | Calls hotel + flight + activities; returns a combined plan |
| `"Best hotels near La Rambla?"` | Calls hotel only; no flight or activities content |
| `"Flights from London to Paris?"` | Calls flight only |
| `"Things to do in Tokyo?"` | Calls activities only |
| `"Hello"` | Returns a clarification question; no specialists called |

In the ADK event log you should see **Event 2 of 2** for every query — one user event and one
`driver_agent` response. There are no `transfer_to_agent` entries because routing is handled by
Python code, not LLM tool-calling.

## 7. Run the test suite

With the four services already running, run all validation scripts:

```powershell
# Agent card health check
uv run python scripts/smoke_services.py

# Router unit tests (6 cases; requires Ollama running)
uv run python scripts/test_router.py

# Pipeline + agent tests (requires specialist services on 8001–8003)
uv run python scripts/test_pipeline.py

# E2E: full-trip Barcelona + hotel-only routing isolation (requires all 4 services)
uv run python scripts/test_driver_trip.py
```

All scripts exit non-zero on failure.

## 8. Optional: run the driver A2A server

If you want to expose the driver as a remote A2A service:

```powershell
uv run python -m agents.driver.serve
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| ADK cannot find the model | Check `OPENAI_MODEL` in `.env` |
| A2A calls fail | Verify specialist ports and card URLs in `.env` |
| UI does not load | Confirm specialist services are already running before starting ADK web |
| Ollama connection refused | Run `ollama serve` (or ensure the Ollama app is running) |
| Router always returns `[]` | The model may not follow JSON instructions; try a larger model |
