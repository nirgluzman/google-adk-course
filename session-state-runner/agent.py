"""
Customer Support Agent with Session Management.
Demonstrates how to create a stateful AI agent that maintains customer context and
conversation history across multiple interactions using ADK sessions.
"""

# Enable asynchronous programming for non-blocking operations (sessions, API calls)
import asyncio

# Generate unique session IDs to identify individual conversations
import uuid

# Load environment variables from .env file (API keys, config)
from dotenv import load_dotenv

# Core agent class for creating AI agents with conversation capabilities
from google.adk.agents import Agent

# Manage conversation flow and session state for multi-turn interactions
from google.adk.runners import Runner

# Store session data and conversation state in memory
from google.adk.sessions import InMemorySessionService

# Provide structured message types (Content, Part) for agent communication
from google.genai import types

# Data validation library for creating structured data models with type checking
from pydantic import BaseModel, Field

# Load API keys and configuration from .env file into environment variables
load_dotenv()

# Specify which language model the agent will use for responses
AGENT_MODEL = "gemini-2.5-flash"


# Define customer schema using Pydantic
class CustomerProfileOutput(BaseModel):
    customer_name: str = Field(description="Full name of the customer.")
    favorite_category: str = Field(description="Customer's preferred product category")
    recent_order: str = Field(description="Details of the customer's most recent order")
    loyalty_points: int = Field(description="Current number of loyalty/reward points")


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
        # Output schema when agent replies
        output_schema=CustomerProfileOutput,
        # The key in session state to store the output of the agent
        output_key="state",
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

    # Check if session exists and if structured output exists in session state
    if session and "state" in session.state:
        structured_data = session.state["state"]
        print(structured_data)
        print("updating session state:")

        # Apply the structured updates to the main session state keys through for loop
        for key, value in structured_data.items():
            session.state[key] = value
            print(f" - {key} updated to {value}")

        # Remove the temporary output_key from the session state
        del session.state["state"]
    else:
        print("No structured output found in session state.")

    # Display remaining session data (original customer data keys persist after removing temporary "state" key)
    print("\nSession Data:")
    if session and hasattr(session, "state"):
        for key, value in session.state.items():
            print(f"{key}: {value}")
    else:
        print("No session data found")


if __name__ == "__main__":
    asyncio.run(main())
