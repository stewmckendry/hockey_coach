"""
API-compatible version of the basic test agent.
Optimized for web integration with proper error handling.
"""

from agents import Agent
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ApiTestAgent(Agent):
    """
    Agent optimized for API/web integration.
    
    Differences from basic_test_agent:
    - More concise responses for web UI
    - Better error handling
    - Consistent response format
    - Web-friendly conversation style
    """
    
    def __init__(self):
        super().__init__(
            name="Hockey Coach Web Assistant",
            instructions="""
            You are a hockey coaching assistant integrated with a web application.
            
            Your role:
            - Provide helpful, concise hockey coaching advice
            - Keep responses conversational but focused
            - Be encouraging and supportive to volunteer coaches
            - If asked about non-hockey topics, gently redirect to coaching
            
            Response guidelines:
            - Keep responses under 200 words for web readability
            - Use bullet points for lists when helpful
            - Be specific and actionable
            - Always end with a follow-up question when appropriate
            
            Examples:
            - User: "Hello" → "Hi! I'm your hockey coaching assistant. What coaching challenge can I help you with today?"
            - User: "U10 practice ideas?" → "For U10 players, focus on:\n• Fun skating games\n• Basic puck handling\n• Simple passing drills\n• Lots of encouragement!\n\nWhat's your biggest challenge with practice planning?"
            """,
            model="gpt-4o-mini"  # Fast model for web responses
        )

def create_api_agent():
    """Factory function for API agent"""
    return ApiTestAgent()

# CLI testing capability
if __name__ == "__main__":
    import asyncio
    from agents import Runner
    
    async def test_api_agent():
        print("Testing API Agent...")
        agent = create_api_agent()
        
        test_messages = [
            "Hello!",
            "What should I focus on with young players?",
            "How do I plan a practice?"
        ]
        
        for message in test_messages:
            print(f"\nUser: {message}")
            result = await Runner.run(agent, message)
            print(f"Agent: {result.final_output}")
    
    asyncio.run(test_api_agent())