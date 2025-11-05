"""
Customer Support Agent with Session Management.
Demonstrates how to create a stateful AI agent that maintains customer context and
conversation history across multiple interactions using ADK sessions.
"""

# Enables asynchronous programming for non-blocking operations (sessions, API calls)
import asyncio

# Generates unique session IDs to identify individual conversations
import uuid

# Loads environment variables from .env file (API keys, config)
from dotenv import load_dotenv

# Core agent class for creating AI agents with conversation capabilities
from google.adk.agents import Agent

# Manages conversation flow and session state for multi-turn interactions
from google.adk.runners import Runner

# Stores session data and conversation state in memory
from google.adk.sessions import InMemorySessionService

# Provides structured message types (Content, Part) for agent communication
from google.genai import types

# Loads API keys and configuration from .env file into environment variables
load_dotenv()

# Specifies which language model the agent will use for responses
AGENT_MODEL = "gemini-2.5-flash"


async def main():
    # Create session service to store customer data
    session_service = InMemorySessionService()

    # Simple customer profile
    customer_data = {
        "customer_name": "Nir Gluzman",
        "favorite_category": "Technology",
        "recent_order": "iPhone 15 Pro - Order #12345 - Shipped",
        "loyalty_points": 1000,
    }

    # Customer support agent
    support_agent = Agent(
        name="CustomerSupport",
        model=AGENT_MODEL,
        instruction="""
      You are a friendly customer agent for TechStore.
      Respond in plain text without any formatting like ** or * or #.
      Use simple, clear language without markdown formatting.

      Customer: {customer_name}
      Favorite Category: {favorite_category}
      Recent Order: {recent_order}
      Loyalty Points: {loyalty_points}
      """,
    )

    # Create session
    APP_NAME = "TechStore"
    CUSTOMER_ID = "nirgluzman"
    SESSION_ID = str(uuid.uuid4())

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=CUSTOMER_ID,
        session_id=SESSION_ID,
        state=customer_data,
    )

    print(f"Customer: {customer_data['customer_name']}")
    print(f"Favorite Category: {customer_data['favorite_category']}")
    print(f"Recent Order: {customer_data['recent_order']}")
    print(f"Loyalty Points: {customer_data['loyalty_points']}")

    # Create runner (for for conversation continuity and state management)
    runner = Runner(
        agent=support_agent,
        session_service=session_service,
        app_name=APP_NAME,
    )

    # Customer asks a question
    customer_message = types.Content(
        role="user",
        parts=[types.Part(text="Hey, can you check my recent order status?")],
    )

    print(f"Customer_message: {customer_message}")

    # Get response from agent
    # Agent knows our customer data
    async for event in runner.run_async(
        user_id=CUSTOMER_ID, session_id=SESSION_ID, new_message=customer_message
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Agent: {event.content.parts[0].text}")

    # Show final session state
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=CUSTOMER_ID, session_id=SESSION_ID
    )

    print("\nSession Data:")
    if session and hasattr(session, "state"):
        for key, value in session.state.items():
            print(f"{key}: {value}")
    else:
        print("No session data found")


if __name__ == "__main__":
    asyncio.run(main())
