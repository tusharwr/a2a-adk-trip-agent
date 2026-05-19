from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from common.config import model_name
from common.prompts import ACTIVITIES_INSTRUCTION


root_agent = Agent(
    name="activities_agent",
    description="Suggests simple activities for a destination trip.",
    model=LiteLlm(model=model_name()),
    instruction=ACTIVITIES_INSTRUCTION,
)
