from __future__ import annotations
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def test_routing() -> None:
    from common.router import route_query

    cases = [
        ("Plan a 3-day trip to Barcelona for 2 people", {"hotel", "flight", "activities"}),
        ("Best hotels near La Rambla in Barcelona",     {"hotel"}),
        ("Flights from London to Paris next Friday",    {"flight"}),
        ("Things to do in Tokyo for a week",            {"activities"}),
        ("Cheap flights and a hotel in Rome",           {"hotel", "flight"}),
        ("Hello",                                       set()),
    ]

    for query, expected in cases:
        result = set(await route_query(query))
        assert result == expected, (
            f"Query: {query!r}\n  Expected: {expected}\n  Got: {result}"
        )
        print(f"PASS: {query!r} -> {result or '(clarify)'}")


if __name__ == "__main__":
    asyncio.run(test_routing())
    print("\nAll router tests passed.")
