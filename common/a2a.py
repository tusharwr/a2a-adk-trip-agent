from __future__ import annotations

import os

from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from .config import agent_card_url


def build_remote_agent(agent_name: str, description: str, env_var: str, default_port: int) -> RemoteA2aAgent:
    card_url = os.getenv(env_var, agent_card_url(agent_name, default_port)).strip()
    return RemoteA2aAgent(
        name=agent_name,
        description=description,
        agent_card=card_url,
        use_legacy=False,
    )
