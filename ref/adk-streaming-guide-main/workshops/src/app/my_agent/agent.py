"""Agent definition for the bidi-workshop."""

from google.adk.agents import Agent
from google.adk.tools import google_search

# Define the agent
agent = Agent(
    name="workshop_agent",
    model="gemini-live-2.5-flash-native-audio",
    instruction="""You are a helpful AI assistant.

    You can use Google Search to find current information.
    Keep your responses concise and friendly.
    """,
    tools=[google_search],
)
