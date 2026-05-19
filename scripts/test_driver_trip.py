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

    print("\n".join(final_texts))


if __name__ == "__main__":
    asyncio.run(main())
