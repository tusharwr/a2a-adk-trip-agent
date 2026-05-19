from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH


load_dotenv()

DEFAULT_MODEL = "openai/gpt-5.4-nano"
DEFAULT_HOST = "127.0.0.1"


def model_name() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL).strip()


def trip_host() -> str:
    return os.getenv("TRIP_AGENT_HOST", DEFAULT_HOST).strip()


def service_port(agent_name: str, default: int) -> int:
    return int(os.getenv(f"{agent_name.upper()}_PORT", str(default)))


def agent_card_url(agent_name: str, port: int, host: str | None = None) -> str:
    resolved_host = (host or trip_host()).strip()
    return f"http://{resolved_host}:{port}{AGENT_CARD_WELL_KNOWN_PATH}"
