"""
Agent Callbacks Example - Monitoring Agent Execution

Demonstrates how to use before_agent_callback and after_agent_callback to:
- Log user inputs and execution timing
- Track agent performance and response generation
- Store temporary data in session state during processing

Agent callbacks hook into the agent's execution flow, not the model calls.
"""

# For tracking execution time and logging timestamps
from datetime import datetime

# For type hints indicating a value can be None or a specific type
from typing import Optional

# Main LLM agent class that supports callbacks for monitoring and control
from google.adk.agents import LlmAgent

# Context object passed to callback functions
from google.adk.agents.callback_context import CallbackContext

# Content types for agent responses
from google.genai import types

# Specify which language model the agent will use for responses
AGENT_MODEL = "gemini-2.5-flash"


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Called BEFORE the agent processes the user's message.
    Great for: logging, authentication, input validation
    """
    print(f"🚀 Starting to process: '{callback_context.user_content}'")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")

    # Store start time in session state
    callback_context.state["start_time"] = datetime.now()

    return None  # Continue normal processing


def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Called AFTER the agent generates a response.
    Great for: logging responses, analytics, post-processing
    """
    # Calculate how long it took
    if "start_time" in callback_context.state:
        duration = datetime.now() - callback_context.state["start_time"]
        print(f"⚡ Response generated in {duration.total_seconds():.1f} seconds")

    print(f"✅ Agent responded: '{callback_context.state.to_dict()}...'")

    return None  # Don't modify the response


root_agent = LlmAgent(
    name="math_tutor",
    model=AGENT_MODEL,
    description="A friendly math tutor for students",
    instruction="""
    You are a helpful math tutor.
    - Give clear, step-by-step explanations
    - Be encouraging and patient
    - Keep answers concise but complete
    """,
    before_agent_callback=before_agent_callback,  # Hook for pre-processing monitoring
    after_agent_callback=after_agent_callback,    # Hook for post-processing analytics
)
