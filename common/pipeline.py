from __future__ import annotations

import asyncio
import logging
import os
import uuid
from typing import NamedTuple

import httpx

from .config import trip_host

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 60.0

_SPECIALIST_PORTS: dict[str, int] = {
    "hotel":      int(os.getenv("HOTEL_PORT", "8001")),
    "flight":     int(os.getenv("FLIGHT_PORT", "8002")),
    "activities": int(os.getenv("ACTIVITIES_PORT", "8003")),
}

_HEADINGS: dict[str, str] = {
    "hotel":      "HOTEL REPORT",
    "flight":     "FLIGHT REPORT",
    "activities": "ACTIVITIES REPORT",
}


class SpecialistResult(NamedTuple):
    domain: str
    text: str
    ok: bool


def _a2a_url(port: int) -> str:
    return f"http://{trip_host()}:{port}"


def _build_request(query: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": query}],
                "messageId": str(uuid.uuid4()),
            },
            "configuration": {"acceptedOutputModes": ["text"]},
        },
    }


def _extract_text(response_json: dict) -> str:
    try:
        result = response_json.get("result", {})
        artifacts = result.get("artifacts") or []
        if artifacts:
            for part in artifacts[0].get("parts", []):
                if part.get("text"):
                    return part["text"].strip()
        parts = result.get("status", {}).get("message", {}).get("parts", [])
        if parts:
            return parts[0].get("text", "").strip()
    except Exception as exc:
        logger.warning("[pipeline] extract_text error: %s", exc)
    return ""


def _ensure_heading(result: SpecialistResult) -> SpecialistResult:
    expected = _HEADINGS[result.domain]
    if not result.text.upper().startswith(expected):
        return SpecialistResult(result.domain, f"{expected}\n{result.text}", result.ok)
    return result


async def _call_specialist(
    client: httpx.AsyncClient, domain: str, query: str
) -> SpecialistResult:
    port = _SPECIALIST_PORTS[domain]
    try:
        resp = await client.post(
            _a2a_url(port), json=_build_request(query), timeout=_DEFAULT_TIMEOUT
        )
        resp.raise_for_status()
        text = _extract_text(resp.json())
        if not text:
            return SpecialistResult(
                domain, f"{_HEADINGS[domain]}\n(empty response)", False
            )
        return SpecialistResult(domain, text, True)
    except Exception as exc:
        logger.error("[pipeline] %s failed: %s", domain, exc)
        return SpecialistResult(domain, f"{_HEADINGS[domain]}\n(error: {exc})", False)


async def gather_specialist_reports(query: str, domains: list[str]) -> str:
    """Call selected specialists in parallel and return combined labelled report string."""
    async with httpx.AsyncClient() as client:
        results: list[SpecialistResult] = list(
            await asyncio.gather(
                *[_call_specialist(client, d, query) for d in domains]
            )
        )
    validated = [_ensure_heading(r) for r in results]
    return "\n\n---\n\n".join(r.text for r in validated)
