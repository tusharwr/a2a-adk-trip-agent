from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from common.config import model_name
from common.prompts import HOTEL_INSTRUCTION


root_agent = Agent(
    name="hotel_agent",
    description="Suggests simple hotel ideas for a destination trip.",
    model=LiteLlm(model=model_name()),
    instruction=HOTEL_INSTRUCTION,
)
