# Ollama Local LLM Migration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Switch the trip agent from OpenAI API models to locally-run Ollama models

**Architecture:** Configuration-only change — LiteLLM already supports `ollama/` provider prefix. All four agents (`driver`, `hotel`, `flight`, `activities`) read `OPENAI_MODEL` from `.env` and route through `LiteLlm(model=model_name())`. No Python code changes needed.

**Tech Stack:** Ollama, LiteLLM, Google ADK, Python 3.13

**Note:** Config file edits (`.env`, `.env.example`, `common/config.py`, `README.md`, `RUN_INSTRUCTIONS.md`) have already been applied. This plan covers verification, documentation organization, and environment setup.

---

### Task 1: Move spec document to correct location

**Files:**
- Modify: move `.opencode/plans/2026-05-20-local-ollama-migration-design.md` → `docs/superpowers/specs/`
- Create: `docs/superpowers/specs/` if needed

- [ ] **Step 1: Create specs directory and move file**

```bash
mkdir -p docs/superpowers/specs
mv .opencode/plans/2026-05-20-local-ollama-migration-design.md docs/superpowers/specs/
```

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/specs/2026-05-20-local-ollama-migration-design.md
git add .opencode/plans/2026-05-20-local-ollama-migration-plan.md
git commit -m "docs: add Ollama migration spec and plan"
```

---

### Task 2: Install Ollama and pull a model

- [ ] **Step 1: Install Ollama**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

- [ ] **Step 2: Pull the model**

```bash
ollama pull qwen2.5:7b
```

- [ ] **Step 3: Verify Ollama is running**

```bash
ollama list
# Expected: shows "qwen2.5:7b" in the list
```

---

### Task 3: Rebuild virtual environment

- [ ] **Step 1: Sync dependencies**

```bash
uv sync
```

Expected: creates/updates `.venv` with all dependencies installed, no errors.

---

### Task 4: Verify Python imports and config work

- [ ] **Step 1: Test config module loads correctly**

```bash
uv run python -c "from common.config import model_name; print('Model:', model_name())"
```

Expected output: `Model: ollama/qwen2.5:7b`

- [ ] **Step 2: Verify all agent files parse without syntax errors**

```bash
uv run python -m py_compile agents/driver/agent.py && echo "driver OK"
uv run python -m py_compile agents/hotel/agent.py && echo "hotel OK"
uv run python -m py_compile agents/flight/agent.py && echo "flight OK"
uv run python -m py_compile agents/activities/agent.py && echo "activities OK"
uv run python -m py_compile common/config.py && echo "config OK"
```

Expected: all five files show "OK"

---

### Task 5: Run smoke tests

- [ ] **Step 1: Start the three specialist services and run the smoke test**

First terminal:
```bash
uv run python -m agents.hotel.serve
```

Second terminal:
```bash
uv run python -m agents.flight.serve
```

Third terminal:
```bash
uv run python -m agents.activities.serve
```

Fourth terminal (with services running):
```bash
uv run python scripts/smoke_services.py
```

Expected: all four A2A agent-card endpoints respond successfully.

- [ ] **Step 2: Run end-to-end driver trip test**

```bash
uv run python scripts/test_driver_trip.py
```

Expected: driver routes the Barcelona trip request to all three specialists and returns a combined plan.

---

### Task 6: Final commit

- [ ] **Step 1: Commit all remaining files**

```bash
git add .
git commit -m "feat: switch from OpenAI to Ollama for local LLM inference"
```
