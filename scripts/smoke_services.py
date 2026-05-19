from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.driver.agent import activities_agent, flight_agent, hotel_agent


URLS = {
    "hotel": "http://127.0.0.1:8001/.well-known/agent-card.json",
    "flight": "http://127.0.0.1:8002/.well-known/agent-card.json",
    "activities": "http://127.0.0.1:8003/.well-known/agent-card.json",
    "driver": "http://127.0.0.1:8000/.well-known/agent-card.json",
}


async def check_cards() -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        for name, url in URLS.items():
            response = await client.get(url)
            response.raise_for_status()
            print(f"{name}: {response.status_code} {response.json()['name']}")


async def check_driver_subagents() -> None:
    for agent in [hotel_agent, flight_agent, activities_agent]:
        await agent._ensure_resolved()
        print(f"{agent.name}: {agent._agent_card.name} -> {agent._agent_card.url}")


async def main() -> None:
    await check_cards()
    await check_driver_subagents()


if __name__ == "__main__":
    asyncio.run(main())
