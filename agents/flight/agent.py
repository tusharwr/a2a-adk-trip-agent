from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from common.config import model_name
from common.prompts import FLIGHT_INSTRUCTION


root_agent = Agent(
    name="flight_agent",
    description="Suggests simple flight ideas for a destination trip.",
    model=LiteLlm(model=model_name()),
    instruction=FLIGHT_INSTRUCTION,
)
