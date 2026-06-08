# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-08

### Added
- `common/router.py` — LLM-based intent router (`route_query`) that classifies the query with a
  single `litellm.acompletion` call at `temperature=0` and returns only the domains needed
  (`hotel`, `flight`, `activities`). Returns `[]` for unclear queries so the driver asks for
  clarification instead of guessing.
- `common/pipeline.py` — parallel A2A HTTP pipeline (`gather_specialist_reports`) that calls only
  the selected specialist services via `asyncio.gather`, validates domain headings, and falls back
  to a labelled error string so heading assertions never break downstream.
- `agents/driver/pipeline_agent.py` — `TripPipelineAgent(BaseAgent)` that sequences the three
  harness steps: route → clarify or pipeline → synthesize. Synthesis is skipped for single-domain
  queries; the raw specialist report is returned directly.
- `common/prompts.py` — `ROUTER_PROMPT` constant; specialist prompts hardened with mandatory
  `HOTEL REPORT` / `FLIGHT REPORT` / `ACTIVITIES REPORT` headings and explicit NEVER rules;
  `DRIVER_INSTRUCTION` narrowed to synthesis-only.
- `scripts/test_router.py` — 6-case routing test (full-trip, hotel-only, flight-only,
  activities-only, hotel+flight, unclear→clarify).
- `scripts/test_pipeline.py` — parallel pipeline test (all-three-sections, hotel-only isolation,
  `TripPipelineAgent` instantiation).

### Changed
- `agents/driver/agent.py` — `root_agent` is now a `TripPipelineAgent` instead of an ADK
  `LlmAgent`. The three `RemoteA2aAgent` names (`hotel_agent`, `flight_agent`, `activities_agent`)
  are kept at module level so `scripts/smoke_services.py` imports continue to work.
- `scripts/test_driver_trip.py` — assertions upgraded: checks for all three specialist report
  headings on full-trip queries and verifies that flight/activities headings are absent for
  hotel-only queries.

### Fixed
- Driver no longer calls all three specialists for every query. Selective routing is now enforced
  in Python code, not left to a 1.5B-parameter LLM.
- Unclear queries ("Hello", off-topic messages) now return a clarification question instead of
  silently calling all specialists.
- Specialist agents no longer answer outside their domain (NEVER rules in prompts).

## [0.1.1] - 2026-05-20

### Changed
- Switched default model provider from OpenAI to Ollama (`ollama/qwen2.5:1.5b`).
- `OPENAI_API_KEY` defaults to the literal string `ollama` when using a local model.
- `common/config.py` updated with port resolution helpers and sensible env-var defaults.

### Added
- `docs/superpowers/specs/2026-05-20-local-ollama-migration-design.md` — design spec for the
  Ollama migration.

## [0.1.0] - 2026-05-20

### Added
- Initial multi-agent trip planner: `driver`, `hotel`, `flight`, `activities` agents.
- Google ADK 2.0 + A2A protocol for agent-to-agent communication.
- LiteLLM abstraction layer — provider switchable via `OPENAI_MODEL` env var.
- ADK Web UI integration via `adk web agents`.
- `scripts/smoke_services.py` — validates all four A2A agent-card endpoints.
- `scripts/test_driver_trip.py` — end-to-end Barcelona trip assertion.
- `.env.example` with documented environment variable reference.

[Unreleased]: https://github.com/example/a2a-adk-trip-agent/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/example/a2a-adk-trip-agent/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/example/a2a-adk-trip-agent/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/example/a2a-adk-trip-agent/releases/tag/v0.1.0
