# Import the Agent class - this class provides the foundation for creating AI agents with specific capabilities
# https://google.github.io/adk-docs/get-started/python/
from google.adk.agents import Agent

# # LiteLlm provides a unified interface to multiple LLM providers, allowing easy switching between different models
# from google.adk.models.lite_llm import LiteLlm

AGENT_MODEL = "gemini-2.5-flash"

root_agent = Agent(
    name="travel_planner_agent",
    # model=LiteLlm(AGENT_MODEL),
    model=AGENT_MODEL,
    # "What does this agent do?" (external documentation)
    # High-level summary of the agent's capabilities and purpose
    description="AI-powered travel planner that creates personalized itineraries, suggests destinations, finds accommodations, and provides travel recommendations based on user preferences and budget",
    # "How should LLM behave?" (internal system prompt)
    # Direct behavioral instructions given to the language model
    instruction="You are a travel planner agent that helps users plan their trips.",
)
