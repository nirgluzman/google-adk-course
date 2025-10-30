# Agent class - this class provides the foundation for creating AI agents with specific capabilities
# https://google.github.io/adk-docs/get-started/python/
from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search

# # LiteLlm provides a unified interface to multiple LLM providers, allowing easy switching between different models
# from google.adk.models.lite_llm import LiteLlm

AGENT_MODEL = "gemini-2.5-flash"


# Mock weather tool that returns predefined weather data for demonstration purposes
def get_weather(city: str) -> dict:
    """
    Retrieves the current weather report for a specific city

    Args:
        city (str): The name of the city (e.g. "Munich", "London", Tel Aviv")

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key with error details.
    """
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    # Mock weather data for different cities
    mock_weather_data = {
        "munich": {
            "status": "success",
            "report": "The weather in Munich is rainy with temperature of 12 deg",
        },
        "london": {
            "status": "success",
            "report": "The weather in London is cloudy with temperature of 9 deg",
        },
        "telaviv": {
            "status": "success",
            "report": "The weather in Tel Aviv is sunny with temperature of 30 deg",
        },
        "rome": {
            "status": "success",
            "report": "The weather in Rome is sunny with temperature of 22 deg",
        },
    }

    if city_normalized in mock_weather_data:
        return mock_weather_data[city_normalized]
    else:
        return {
            "status": "error",
            "error_message": f"Could not find weather information for {city}",
        }


# Tool to provide current time in different cities (currently supports specific predefined cities)
def get_current_time(city: str) -> dict:
    """
    Retrieves the current time for a specific city

    Args:
        city (str): The name of the city (e.g. "Munich", "London", Tel Aviv")

    Returns:
        dict: A dictionary containing the current time information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'time' key with the current time.
              If 'error', includes an 'error_message' key with error details.
    """
    print(f"--- Tool: get_current_time called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    # City to timezone mapping
    city_timezones = {
        "munich": "Europe/Berlin",
        "london": "Europe/London",
        "telaviv": "Asia/Jerusalem",
        "rome": "Europe/Rome",
    }

    if city_normalized in city_timezones:
        tz = ZoneInfo(city_timezones[city_normalized])
        current_time = datetime.now(tz).strftime("%I:%M %p")
        return {
            "status": "success",
            "time": current_time,
        }

    return {
        "status": "error",
        "error_message": f"Could not find current time information for {city}",
    }


# --- Sequential Agent ---
# SequentialAgent is a subclass of Agent that executes a sequence of tasks.
# It is useful for creating agents that perform a series of actions in a specific order.
# -------------------------

# Destination Research Agent - Researches location information.
destination_research_agent = Agent(
    name="DestinationResearchAgent",
    model=AGENT_MODEL,
    description="An agent that researches travel destinations and gathers essential information.",
    instruction="""
    You are a travel researcher. You will be given a destination and travel preferences, and you will research:
    - Best time to visit and weather patterns
    - Top attractions and must-see locations
    - Local culture, customs, and etiquette tips
    - Transportation options within the destination
    - Safety considerations and travel requirements
    Provide comprehensive destination insights for trip planning.
    """,
    tools=[google_search],
    output_key="destination_research",  # Stores output in state["destination_research"]
)

# Itinerary Builder Agent - Creates detailed travel schedule.
itinerary_builder_agent = Agent(
    name="ItineraryBuilderAgent",
    model=AGENT_MODEL,
    description="An agent that creates structured travel itineraries with daily schedules.",
    instruction="""
    You are a professional travel planner. Using the research from "destination_research" output, create a detailed itinerary that includes:
    - Day-by-day schedule with recommended activities
    - Suggested accommodation areas or districts
    - Estimated time requirements for each activity
    - Meal recommendations and dining suggestions
    - Budget estimates for major expenses
    Structure it logically for easy following during the trip.
    """,
    output_key="travel_itinerary",
)

# Travel Optimizer Agent - Adds practical tips and optimizations
travel_optimizer_agent = Agent(
    name="TravelOptimizerAgent",
    model=AGENT_MODEL,
    description="An agent that optimizes travel plans with practical advice and alternatives",
    instruction="""
    You are a seasoned travel consultant. Using the itinerary from "travel_itinerary" output, optimize it by adding:
    - Money-saving tips and budget alternatives
    - Packing recommendations specific to the destination
    - Backup plans for weather or unexpected situations
    - Local apps, websites, or resources to download
    - Cultural do's and don'ts for respectful travel

    Format the final output as:
        ITINERARY: {travel_itinerary}
        OPTIMIZATION TIPS: [your money-saving and practical tips here]
        TRAVEL ESSENTIALS: [packing and preparation advice here]
        BACKUP PLANS: [alternative options and contingencies here]
    """,
)

# This agent orchestrates the pipeline by running the sub_agents in order.
root_agent = SequentialAgent(
    name="TravelPlannerAgent",
    # model=LiteLlm(AGENT_MODEL), # Not needed for SequentialAgent
    # model=AGENT_MODEL, # Not needed for SequentialAgent
    #
    # "What does this agent do?" (external documentation)
    # High-level summary of the agent's capabilities and purpose
    description="A comprehensive system that researches destinations, builds itineraries, and optimizes travel plans",
    # "How should LLM behave?" (internal system prompt)
    # Direct behavioral instructions given to the language model
    # instruction="You are a travel planner agent that helps users plan their trips.",
    #
    # Functions the agent can call to perform specific tasks (e.g., API calls, data retrieval)
    # tools=[get_weather, get_current_time],
    #
    # The agents will run in the order provided:.
    sub_agents=[
        destination_research_agent,
        itinerary_builder_agent,
        travel_optimizer_agent,
    ],
)
