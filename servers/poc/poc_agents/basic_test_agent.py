"""
Basic test agent to validate OpenAI Agents SDK functionality.

Requirements:
- Inherit from agents.Agent
- Respond conversationally to any input
- Use existing hockey knowledge when relevant
- Keep responses helpful and friendly
"""

from agents import Agent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BasicTestAgent(Agent):
    """
    Simple agent for testing OpenAI Agents SDK integration.
    
    This agent should:
    1. Respond to any user input conversationally
    2. Identify itself as a hockey coaching assistant
    3. Offer to help with hockey-related questions
    4. Keep responses concise but helpful
    """
    
    def __init__(self):
        super().__init__(
            name="Hockey Coach Test Assistant",
            instructions="""
            You are a helpful hockey coaching assistant built to test the OpenAI Agents SDK.
            
            Your role:
            - Respond conversationally to any input
            - Identify yourself as a hockey coaching assistant when greeting users
            - Offer to help with hockey coaching questions
            - Keep responses friendly, helpful, and concise
            - If asked about hockey topics, provide basic helpful information
            
            Examples of good responses:
            - User: "Hello" → "Hi! I'm your hockey coaching assistant. I'm here to help with any coaching questions you might have!"
            - User: "What should I focus on with young players?" → "For young players, focus on fun, basic skating skills, and simple puck handling. What age group are you coaching?"
            - User: "How are you?" → "I'm doing great and ready to help with your hockey coaching needs! What can I assist you with today?"
            
            Keep it simple and conversational!
            """,
            model="gpt-4o-mini"  # Use faster model for testing
        )

def create_test_agent():
    """Factory function to create the test agent"""
    return BasicTestAgent()