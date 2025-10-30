# Agent class - this class provides the foundation for creating AI agents with specific capabilities
# https://google.github.io/adk-docs/get-started/python/
from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent

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
    # Functions the agent can call to perform specific tasks (e.g., API calls, data retrieval)
    tools=[get_weather, get_current_time],
)
