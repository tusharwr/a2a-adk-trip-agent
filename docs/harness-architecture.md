# Harness Architecture

## Problem

`qwen2.5:1.5b` (and similarly small local models) cannot reliably orchestrate multi-agent
workflows when given a single overloaded prompt. Two failures were observed:

1. **Routing failure** — the driver called only one specialist (`hotel_agent`) for a full-trip
   query, leaving flight and activities answers missing.
2. **Domain leakage** — a specialist answered questions outside its role (e.g. the hotel agent
   providing activity suggestions) because prompts lacked hard constraints.

The harness fixes both without upgrading the model.

## Design Principle

Move reliability-critical logic into Python code. Leave the LLM only two focused, well-bounded
jobs:

| Step | Who does it | What it does |
|------|-------------|--------------|
| 1. Route | LLM (`temperature=0`) | Classify query → `{"domains": [...]}` |
| 2. Call | Python (`asyncio.gather`) | HTTP POST to selected specialists only |
| 3. Synthesize | LLM | Reformat combined reports into readable output |

## Components

### `common/router.py` — Intent classifier

```
query → litellm.acompletion(ROUTER_PROMPT, temperature=0) → {"domains": [...]} → list[str]
```

- Returns a subset of `["hotel", "flight", "activities"]`.
- Returns `[]` for unclear queries — the driver asks for clarification instead of guessing.
- Regex-extracts the JSON from the model output, tolerating prose wrappers.
- Falls back to `[]` on any exception (parse failure, network error, timeout).

### `common/pipeline.py` — Parallel A2A caller

```
(query, domains) → asyncio.gather(*[POST /message/send for each domain]) → combined text
```

- Calls **only** the domains the router selected.
- A2A endpoint is the root URL of each specialist service (e.g. `http://127.0.0.1:8001`).
- Extracts text from `result.artifacts[0].parts[0].text` in the JSON-RPC response.
- Prepends the domain heading (`HOTEL REPORT`, etc.) if the specialist omitted it — ensures
  heading assertions never fail due to model non-compliance.
- Returns a `---`-separated string of all specialist reports.

### `agents/driver/pipeline_agent.py` — Orchestrator

`TripPipelineAgent(BaseAgent)` sequences the three steps:

```
user_text
  → route_query(user_text)
      [] → yield clarification message
      domains → gather_specialist_reports(user_text, domains)
                  len(domains) == 1 → yield specialist report directly
                  len(domains) > 1  → litellm.acompletion(synthesis_prompt)
                                        → yield synthesis + raw reports appended
```

Single-domain queries skip synthesis — the specialist report already has the right heading and
no reformatting is needed. Multi-domain synthesis appends the raw reports after the summary so
heading assertions and downstream consumers can always find `HOTEL REPORT` etc.

### `common/prompts.py` — Prompt constants

| Constant | Purpose |
|----------|---------|
| `ROUTER_PROMPT` | System prompt for the router LLM. Defines the 3 domains, JSON format, and 6 worked examples. |
| `DRIVER_INSTRUCTION` | Synthesis-only prompt for the driver LLM. Instructs it to combine reports under `## Hotels` / `## Flights` / `## Activities` headings. |
| `HOTEL_INSTRUCTION` | Hotel specialist prompt. Mandates `HOTEL REPORT` heading on line 1, prohibits flight/activity answers. |
| `FLIGHT_INSTRUCTION` | Flight specialist prompt. Mandates `FLIGHT REPORT` heading, prohibits hotel/activity answers. |
| `ACTIVITIES_INSTRUCTION` | Activities specialist prompt. Mandates `ACTIVITIES REPORT` heading, prohibits hotel/flight answers. |

## Request Flow

```
User query
    │
    ▼
TripPipelineAgent._run_async_impl
    │
    ├─ route_query(query)          ← 1 LLM call, temperature=0
    │     ├─ [] → clarification event (no specialists called)
    │     └─ ["hotel","flight","activities"]
    │              │
    ▼              ▼
    gather_specialist_reports      ← 3 parallel HTTP calls
         │    │    │
         ▼    ▼    ▼
      hotel  flight activities    ← A2A JSON-RPC POST to each
         │    │    │
         └────┴────┘
              │
              ▼
         combined reports
              │
              ├─ len==1 → yield directly
              │
              └─ len>1  → litellm.acompletion(synthesis)   ← 1 LLM call
                               │
                               ▼
                          synthesis + raw reports
                               │
                               ▼
                          single Event to ADK
```

## Event Trace (ADK Web UI)

With the harness, the ADK event log shows **2 events** for any query:

```
#1  user          "Plan a 3-day trip to Barcelona"
#2  driver_agent  <full response>   NodePath: N/A
```

Without the harness (old LlmAgent design), a full-trip query produced **4+ events**:

```
#1  user              "Plan a 3-day trip to Barcelona"
#2  driver_agent      transfer_to_agent("hotel_agent")
#3  driver_agent      transfer_to_agent result
#4  hotel_agent       <hotel-only response>
```

The `N/A` node path on event #2 confirms no ADK sub-agent routing occurred.

## Adding a New Specialist

1. Create `agents/<name>/agent.py` and `agents/<name>/serve.py` following the existing pattern.
2. Add `<NAME>_PORT` and `<NAME>_AGENT_CARD_URL` to `.env.example`.
3. Add `"<name>"` to `_VALID_DOMAINS` in `common/router.py`.
4. Add port mapping to `_SPECIALIST_PORTS` in `common/pipeline.py`.
5. Add heading constant to `_HEADINGS` in `common/pipeline.py`.
6. Add the domain to `ROUTER_PROMPT` examples in `common/prompts.py`.
7. Add the new specialist prompt constant to `common/prompts.py`.
8. Update `scripts/smoke_services.py` to validate the new card endpoint.

## Trade-offs

| Approach | Pro | Con |
|----------|-----|-----|
| **Harness (current)** | Works with 1.5B models; routing is deterministic Python | Router LLM call adds ~2s latency; synthesis may still hallucinate |
| **Pure LLM orchestration** | No extra code | Unreliable with small models; requires GPT-4-class model |
| **Keyword router** | Zero latency | Brittle; breaks on paraphrasing; no clarification behaviour |
