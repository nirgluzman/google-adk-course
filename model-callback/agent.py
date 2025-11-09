"""
Model Callbacks Example - Content Filtering and Response Modification

Demonstrates how to use before_model_callback and after_model_callback to:
- Filter and block inappropriate content before it reaches the model
- Modify or enhance responses after the model generates them
- Implement content guardrails and safety measures
- Add custom processing to model inputs and outputs

Model callbacks intercept the actual LLM communication, unlike agent callbacks.
"""

# For type hints indicating a value can be None or a specific type
from typing import Optional

# Main LLM agent class that supports callbacks for monitoring and control
from google.adk.agents import LlmAgent

# Context object passed to callback functions
from google.adk.agents.callback_context import CallbackContext

# Classes for handling model requests and responses in callbacks
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

# Content types for agent responses
from google.genai import types

# Specify which language model the agent will use for responses
AGENT_MODEL = "gemini-2.5-flash"


def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Called BEFORE sending the request to the AI model.
    Perfect for: content filtering, request logging, blocking inappropriate content
    """
    # Get the user's message from the request
    user_message = ""
    if llm_request.contents:
        for content in llm_request.contents:
            if content.role == "user" and content.parts:
                user_message = content.parts[0].text
                break

    print(f"📤 Sending to model: '{user_message}'")

    # Block math questions (as an example filter)
    math_keywords = [
        "math",
        "calculate",
        "+",
        "-",
        "*",
        "/",
        "=",
        "plus",
        "minus",
        "times",
        "divided",
    ]

    if user_message and any(
        keyword in user_message.lower() for keyword in math_keywords
    ):
        print("🚫 Blocking math-related content!")

        # Return a custom response instead of calling the model
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text="Sorry, I'm not allowed to help with math problems right now. "
                        "Try asking about something else!"
                    )
                ],
            )
        )

    print("✅ Request approved - sending to model")
    return None  # Continue to model


def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    Called AFTER getting response from the AI model.
    Perfect for: response filtering, adding disclaimers, logging responses
    """
    # Get the model's response text
    response_text = ""
    if llm_response.content and llm_response.content.parts:
        text_part = llm_response.content.parts[0].text
        response_text = text_part if text_part else ""

    print(f"📥 Model responded: '{response_text[:50]}...'")

    # Add a fun emoji to every response
    if response_text:
        modified_text = response_text + " 🤖"
        print("✨ Added robot emoji to response!")

        # Return the modified response
        return LlmResponse(
            content=types.Content(role="model", parts=[types.Part(text=modified_text)])
        )

    return None  # Use original response


# Create a simple chatbot with model callbacks
root_agent = LlmAgent(
    name="filtered_chatbot",
    model=AGENT_MODEL,
    description="A chatbot that filters math questions and adds emojis",
    instruction="""
    You are a friendly chatbot.
    - Be helpful and conversational
    - Keep responses short and friendly
    - Answer questions about various topics
    """,
    before_model_callback=before_model_callback,  # Intercept requests to filter content
    after_model_callback=after_model_callback,  # Modify responses before returning to user
)

# Example usage (uncomment to test):
# if __name__ == "__main__":
#     print("Filtered Chatbot Demo")
#     print("Try asking: 'What's the weather like?' or 'What's 2+2?'")
#
#     # Test normal question
#     response1 = chatbot.send_message("Hello, how are you?")
#     print(f"Response 1: {response1.text}\n")
#
#     # Test blocked content
#     response2 = chatbot.send_message("Can you help me calculate 15 + 25?")
#     print(f"Response 2: {response2.text}\n")
