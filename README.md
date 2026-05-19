# A2A ADK Trip Agent

This repo is a small learning project that shows how to build a multi-agent trip planner with:

- Google ADK
- A2A for agent-to-agent communication
- OpenAI models through LiteLLM
- ADK Web UI for testing the driver agent

The project has four agents:

- `driver`
- `hotel`
- `flight`
- `activities`

The `driver` agent routes the user request to the specialist agents and combines their responses into one trip plan.

## What it does

For a request like:

```text
Plan a trip to Barcelona
```

the driver should consult:

- the hotel agent for stay options
- the flight agent for travel suggestions
- the activities agent for things to do

## Repo layout

```text
a2a-adk-trip-agent/
  agents/
    driver/
    hotel/
    flight/
    activities/
  common/
  README.md
  RUN_INSTRUCTIONS.md
  pyproject.toml
  .env.example
```

Each agent folder has the same simple structure:

- `__init__.py`
- `agent.py`
- `serve.py`

## Runtime

This project targets Python 3.13.

## Model choice

The default model is `openai/gpt-5.4-nano` through LiteLLM. If that model is not available in your OpenAI account or provider setup, change `OPENAI_MODEL` in `.env` to a compatible small model such as `openai/gpt-4o-mini`.

## Testing

Use the ADK Web UI against the `driver` agent after starting the three specialist A2A services.

## Notes

- This is intentionally simple and not connected to any live booking APIs.
- The agent outputs are meant for learning and demo purposes.
- Never commit your `.env` file or API keys.
