from __future__ import annotations

import json
import logging
import re

import litellm

from .config import model_name
from .prompts import ROUTER_PROMPT

logger = logging.getLogger(__name__)

_VALID_DOMAINS = frozenset({"hotel", "flight", "activities"})


async def route_query(query: str) -> list[str]:
    """Return the list of specialist domains to call for a query.

    Returns a subset of ["hotel", "flight", "activities"].
    Returns [] when the query is unclear — caller should ask for clarification.
    """
    try:
        resp = await litellm.acompletion(
            model=model_name(),
            messages=[
                {"role": "system", "content": ROUTER_PROMPT},
                {"role": "user", "content": query},
            ],
            temperature=0,
        )
        content = resp.choices[0].message.content.strip()
        match = re.search(r"\{.*?\}", content, re.DOTALL)
        if not match:
            logger.warning("[router] no JSON found in: %r", content[:120])
            return []
        data = json.loads(match.group())
        domains = [d for d in data.get("domains", []) if d in _VALID_DOMAINS]
        logger.info("[router] %r → %s", query[:60], domains)
        return domains
    except Exception as exc:
        logger.error("[router] failed: %s", exc)
        return []
