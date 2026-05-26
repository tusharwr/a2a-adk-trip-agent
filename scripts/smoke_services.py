from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.driver.agent import activities_agent, flight_agent, hotel_agent


AGENT_CARDS = {
    "hotel": ("http://127.0.0.1:8001/.well-known/agent-card.json", hotel_agent),
    "flight": ("http://127.0.0.1:8002/.well-known/agent-card.json", flight_agent),
    "activities": ("http://127.0.0.1:8003/.well-known/agent-card.json", activities_agent),
}
ALL_URLS = {
    "hotel": "http://127.0.0.1:8001/.well-known/agent-card.json",
    "flight": "http://127.0.0.1:8002/.well-known/agent-card.json",
    "activities": "http://127.0.0.1:8003/.well-known/agent-card.json",
    "driver": "http://127.0.0.1:8000/.well-known/agent-card.json",
}


async def check_cards() -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        for name, url in ALL_URLS.items():
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            assert data["name"] == f"{name}_agent", (
                f"Expected {name}_agent, got {data['name']}"
            )
            print(f"{name}: {response.status_code} {data['name']}")


async def check_driver_subagents() -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        for name, (url, agent) in AGENT_CARDS.items():
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            assert data["name"] == agent.name, (
                f"Expected {agent.name}, got {data['name']}"
            )
            print(f"{agent.name}: {data['name']} -> {url}")


async def main() -> None:
    await check_cards()
    await check_driver_subagents()


if __name__ == "__main__":
    asyncio.run(main())
