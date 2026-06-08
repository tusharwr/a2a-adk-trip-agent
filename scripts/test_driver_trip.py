from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import (
    InMemoryCredentialService,
)
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.driver.agent import root_agent


QUERY = "Plan a trip to Barcelona for 5 days in May. Include hotels, flights, and activities."
HOTEL_ONLY_QUERY = "What are the best hotels near the Gothic Quarter in Barcelona?"


async def main() -> None:
    runner = Runner(
        app_name="a2a_trip_agent",
        agent=root_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
        credential_service=InMemoryCredentialService(),
        auto_create_session=True,
    )

    session = await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="smoke_user",
        session_id="smoke_trip",
    )

    message = types.Content(role="user", parts=[types.Part(text=QUERY)])
    final_texts: list[str] = []

    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=message,
    ):
        if event.partial:
            continue
        if event.content and event.content.parts:
            text = "".join(part.text or "" for part in event.content.parts).strip()
            if text:
                final_texts.append(text)

    combined = "\n".join(final_texts)
    print(combined)
    lower = combined.lower()

    assert "hotel" in lower or "stay" in lower or "accommodation" in lower, \
        "Response missing hotel content"
    assert "flight" in lower or "airport" in lower or "route" in lower, \
        "Response missing flight content"
    assert "activit" in lower or "museum" in lower or "park" in lower \
        or "beach" in lower or "tour" in lower, \
        "Response missing activities content"

    assert "hotel report" in lower, \
        "HOTEL REPORT missing -- hotel specialist was not called"
    assert "flight report" in lower, \
        "FLIGHT REPORT missing -- flight specialist was not called"
    assert "activities report" in lower, \
        "ACTIVITIES REPORT missing -- activities specialist was not called"
    print("PASS: full-trip test")


async def main_hotel_only() -> None:
    runner = Runner(
        app_name="a2a_trip_agent",
        agent=root_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
        credential_service=InMemoryCredentialService(),
        auto_create_session=True,
    )
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="smoke_user2", session_id="smoke_hotel"
    )
    message = types.Content(role="user", parts=[types.Part(text=HOTEL_ONLY_QUERY)])
    final_texts: list[str] = []
    async for event in runner.run_async(
        user_id=session.user_id, session_id=session.id, new_message=message
    ):
        if event.partial:
            continue
        if event.content and event.content.parts:
            text = "".join(p.text or "" for p in event.content.parts).strip()
            if text:
                final_texts.append(text)

    combined = "\n".join(final_texts).lower()
    assert "hotel report" in combined, "HOTEL REPORT missing for hotel-only query"
    assert "flight report" not in combined, "FLIGHT REPORT should not appear"
    assert "activities report" not in combined, "ACTIVITIES REPORT should not appear"
    print("PASS: hotel-only routing test")


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(main_hotel_only())
