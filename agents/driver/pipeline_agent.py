from __future__ import annotations

import logging
from typing import AsyncGenerator

import litellm
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from pydantic import Field
from typing_extensions import override

from common.config import model_name
from common.pipeline import gather_specialist_reports
from common.prompts import DRIVER_INSTRUCTION
from common.router import route_query

logger = logging.getLogger(__name__)

_CLARIFICATION_MSG = (
    "Could you tell me more about what you need? "
    "Are you looking for hotel recommendations, flight options, "
    "activity ideas, or a full trip plan?"
)


class TripPipelineAgent(BaseAgent):
    """Harness agent: routes query -> calls only needed specialists -> synthesizes.

    Routing and specialist calls are Python code, not LLM tool-calling.
    The LLM is used only for (1) intent classification and (2) final synthesis.
    """

    model: LiteLlm = Field(default_factory=lambda: LiteLlm(model=model_name()))

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        user_text = ""
        if ctx.user_content and ctx.user_content.parts:
            user_text = " ".join(
                p.text or "" for p in ctx.user_content.parts
            ).strip()

        if not user_text:
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=_CLARIFICATION_MSG)],
                ),
            )
            return

        domains = await route_query(user_text)
        logger.info("[harness] %r -> domains=%s", user_text[:60], domains)

        if not domains:
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=_CLARIFICATION_MSG)],
                ),
            )
            return

        try:
            specialist_context = await gather_specialist_reports(user_text, domains)
        except Exception as exc:
            logger.error("[harness] pipeline error: %s", exc)
            specialist_context = "(specialist services unavailable)"

        if len(domains) == 1:
            final_text = specialist_context
        else:
            synthesis_prompt = (
                f"{DRIVER_INSTRUCTION}\n\n"
                f"--- SPECIALIST REPORTS ---\n\n"
                f"{specialist_context}"
            )
            synthesis = ""
            try:
                resp = await litellm.acompletion(
                    model=self.model.model,
                    messages=[{"role": "user", "content": synthesis_prompt}],
                )
                synthesis = (resp.choices[0].message.content or "").strip()
            except Exception as exc:
                logger.error("[harness] synthesis error: %s", exc)

            if synthesis:
                final_text = f"{synthesis}\n\n---\n\n{specialist_context}"
            else:
                final_text = specialist_context

        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=types.Content(
                role="model",
                parts=[types.Part(text=final_text.strip())],
            ),
        )

    @override
    async def _run_live_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        async for event in self._run_async_impl(ctx):
            yield event
