from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from common.a2a import build_remote_agent
from common.config import model_name
from common.prompts import DRIVER_INSTRUCTION


hotel_agent = build_remote_agent(
    agent_name="hotel_agent",
    description="Finds hotel suggestions for a destination.",
    env_var="HOTEL_AGENT_CARD_URL",
    default_port=8001,
)

flight_agent = build_remote_agent(
    agent_name="flight_agent",
    description="Finds flight suggestions for a destination.",
    env_var="FLIGHT_AGENT_CARD_URL",
    default_port=8002,
)

activities_agent = build_remote_agent(
    agent_name="activities_agent",
    description="Finds activity suggestions for a destination.",
    env_var="ACTIVITIES_AGENT_CARD_URL",
    default_port=8003,
)


root_agent = Agent(
    name="driver_agent",
    description="Routes a trip request to specialist travel agents and combines the result.",
    model=LiteLlm(model=model_name()),
    instruction=DRIVER_INSTRUCTION,
    sub_agents=[hotel_agent, flight_agent, activities_agent],
)
