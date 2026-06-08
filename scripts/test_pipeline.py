from __future__ import annotations
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def test_all_three_sections() -> None:
    from common.pipeline import gather_specialist_reports

    result = await gather_specialist_reports(
        "Plan a trip to Barcelona for 2 people, 3 days.",
        domains=["hotel", "flight", "activities"],
    )
    lower = result.lower()
    assert "hotel report" in lower,      f"Missing HOTEL REPORT:\n{result}"
    assert "flight report" in lower,     f"Missing FLIGHT REPORT:\n{result}"
    assert "activities report" in lower, f"Missing ACTIVITIES REPORT:\n{result}"
    print("PASS: all three sections present")
    print(result[:400])


async def test_hotel_only() -> None:
    from common.pipeline import gather_specialist_reports

    result = await gather_specialist_reports(
        "Best hotels near the Gothic Quarter in Barcelona?",
        domains=["hotel"],
    )
    lower = result.lower()
    assert "hotel report" in lower,          f"Missing HOTEL REPORT:\n{result}"
    assert "flight report" not in lower,     "FLIGHT REPORT should not appear"
    assert "activities report" not in lower, "ACTIVITIES REPORT should not appear"
    print("PASS: hotel-only section present")


def test_agent_instantiates() -> None:
    from agents.driver.pipeline_agent import TripPipelineAgent
    from google.adk.models.lite_llm import LiteLlm
    agent = TripPipelineAgent(
        name="driver_agent",
        description="test",
        model=LiteLlm(model="ollama/qwen2.5:1.5b"),
    )
    assert agent.name == "driver_agent"
    assert agent.sub_agents == []
    print("PASS: TripPipelineAgent instantiates")


if __name__ == "__main__":
    asyncio.run(test_all_three_sections())
    asyncio.run(test_hotel_only())
    test_agent_instantiates()
    print("\nAll pipeline tests passed.")
