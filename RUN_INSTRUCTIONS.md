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

Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY`.

The default model is:

```text
openai/gpt-5.4-nano
```

If that is not available for your account, switch `OPENAI_MODEL` to `openai/gpt-4o-mini`.

## 4. Start the specialist agents

Open three terminals from the repo root.

Hotel agent:

```powershell
uv run python -m agents.hotel.serve
```

Flight agent:

```powershell
uv run python -m agents.flight.serve
```

Activities agent:

```powershell
uv run python -m agents.activities.serve
```

Each service exposes an A2A card on its configured port.

## 5. Start the ADK Web UI

In a fourth terminal:

```powershell
uv run adk web agents --port 8000
```

Open the browser URL shown by ADK, then select the `driver` agent.

## 6. Test a trip request

Try:

```text
Plan a trip to Barcelona
```

Expected behavior:

- the driver calls hotel, flight, and activities
- the final answer merges all three specialist responses

## 7. Smoke test the services

With the four services already running, run:

```powershell
uv run python scripts/smoke_services.py
```

This checks all four agent-card endpoints and verifies the driver can resolve the three specialist remote agents.

## 8. Optional: run the driver A2A server

If you want to expose the driver as a remote A2A service too:

```powershell
uv run python -m agents.driver.serve
```

## Troubleshooting

- If ADK cannot find the model, check `OPENAI_MODEL`.
- If A2A calls fail, verify the specialist ports and card URLs in `.env`.
- If the UI does not load, confirm the specialist services are already running.
