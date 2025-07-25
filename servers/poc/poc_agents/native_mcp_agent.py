"""
Hockey coaching agent using native OpenAI Agents SDK MCP integration.

This approach uses the built-in MCP support rather than custom bridging code.
"""

from agents import Agent
from agents.mcp import MCPServerStreamableHttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NativeMCPHockeyAgent(Agent):
    """
    Hockey coaching agent with native MCP server integration using Streamable HTTP transport.
    
    Uses OpenAI Agents SDK built-in MCP support:
    - Automatic tool discovery via list_tools()
    - Native tool calling via call_tool()
    - Streamable HTTP transport (preferred by OpenAI)
    - No custom bridging code needed
    """
    
    def __init__(self, mcp_servers=None):
        # Default MCP servers if none provided
        if mcp_servers is None:
            mcp_servers = self._create_default_mcp_servers()
            
        super().__init__(
            name="Hockey Coach MCP Assistant",
            instructions="""
            You are an expert hockey coaching assistant with access to a comprehensive hockey knowledge base via MCP tools.
            
            Your capabilities:
            - Access to hockey knowledge base with search_hockey_knowledge tool
            - Practice planning with create_practice_plan tool  
            - Coaching recommendations with get_coaching_recommendations tool
            - Player development with analyze_player_development tool
            - Age-specific coaching guidance (U8 through U18+)
            - Evidence-based coaching techniques from expert sources
            
            When users ask hockey-related questions:
            1. Use available MCP tools to search for relevant information
            2. Synthesize results into helpful, actionable advice
            3. Always specify age-appropriate recommendations when relevant
            4. Provide specific drill names and techniques when available
            5. Keep responses concise and web-friendly (under 250 words)
            
            Tool usage guidelines:
            - Use search_hockey_knowledge for specific hockey topics (drills, skills, tactics)
            - Use create_practice_plan when coaches ask for practice planning help
            - Use get_coaching_recommendations for personalized coaching advice
            - Search when users mention age groups (U8, U10, U12, etc.)
            - Reference specific content from search results
            - Always provide actionable, practical advice
            
            Example responses:
            "For U10 skating development, I found these proven approaches:
            
            • **Balance Games**: Use stationary balance challenges before movement
            • **Red Light/Green Light**: Teaches stopping and listening skills  
            • **Follow the Leader**: Develops edge work and agility
            
            What specific skating challenges are your players facing?"
            
            Remember: Always use MCP tools when users ask about specific hockey topics!
            """,
            model="gpt-4o-mini",
            mcp_servers=mcp_servers
        )
    
    def _create_default_mcp_servers(self):
        """
        Create default MCP server connections using Streamable HTTP transport.
        
        Based on your hockey_mcp.py configuration:
        - Uses Streamable HTTP transport (streamable_http_app)
        - Connects to localhost:8000 
        - Enables tool caching for performance
        """
        servers = []
        
        try:
            # Connect to your hockey MCP server using Streamable HTTP transport
            # This aligns with your hockey_mcp.py configuration
            from agents.mcp import MCPServerStreamableHttpParams
            
            params = MCPServerStreamableHttpParams(
                url="http://localhost:8000/mcp",  # Streamable HTTP endpoint
                headers={},  # No special headers needed
                timeout=30.0,  # HTTP request timeout
                sse_read_timeout=60.0,  # Server-sent events read timeout
                terminate_on_close=False  # Don't terminate on connection close
            )
            
            hockey_server = MCPServerStreamableHttp(
                params=params,
                name="Hockey Knowledge Server",
                cache_tools_list=True  # Cache tools for performance
            )
            servers.append(hockey_server)
            print("✅ Connected to hockey MCP server via Streamable HTTP")
            
        except Exception as e:
            print(f"⚠️  Could not connect to hockey MCP server: {e}")
            print("   Make sure your hockey_mcp.py server is running on port 8000")
            print("   Agent will work but without hockey knowledge tools")
        
        return servers

def create_native_mcp_agent():
    """Factory function for native MCP agent"""
    return NativeMCPHockeyAgent()

# CLI testing capability
if __name__ == "__main__":
    import asyncio
    from agents import Runner
    
    async def test_native_mcp_agent():
        print("Testing Native MCP Hockey Agent...")
        print("=" * 50)
        
        try:
            # Create MCP server with proper connection
            from agents.mcp import MCPServerStreamableHttpParams
            
            params = MCPServerStreamableHttpParams(
                url="http://localhost:8000/mcp",
                headers={},
                timeout=30.0,
                sse_read_timeout=60.0,
                terminate_on_close=False
            )
            
            # Use async context manager for proper connection handling
            async with MCPServerStreamableHttp(
                params=params,
                name="Hockey Knowledge Server",
                cache_tools_list=True
            ) as server:
                print("✅ MCP Server connected successfully")
                
                # Create agent with connected MCP server
                agent = Agent(
                    name="Hockey Coach MCP Assistant",
                    instructions="""
                    You are an expert hockey coaching assistant with access to a comprehensive hockey knowledge base via MCP tools.
                    
                    Your capabilities:
                    - Access to hockey knowledge base with search_hockey_knowledge tool
                    - Practice planning with create_practice_plan tool  
                    - Coaching recommendations with get_coaching_recommendations tool
                    - Player development with analyze_player_development tool
                    
                    When users ask hockey-related questions:
                    1. Use available MCP tools to search for relevant information
                    2. Synthesize results into helpful, actionable advice
                    3. Always specify age-appropriate recommendations when relevant
                    4. Provide specific drill names and techniques when available
                    
                    Remember: Always use MCP tools when users ask about specific hockey topics!
                    """,
                    model="gpt-4o-mini",
                    mcp_servers=[server]
                )
                print("✅ Agent created with MCP integration")
                
                # Test with hockey-specific questions
                test_messages = [
                    "What are some good U10 skating drills?",
                    "How should I structure a practice for beginners?", 
                    "Tell me about teaching puck handling",
                    "Hello, who are you?"  # General question
                ]
                
                for message in test_messages:
                    print(f"\n{'='*50}")
                    print(f"User: {message}")
                    print("Agent: ", end="")
                    
                    try:
                        result = await Runner.run(agent, message)
                        response = result.final_output
                        print(response)
                        
                        # Check if tools were likely used
                        if any(keyword in message.lower() for keyword in ['drill', 'u10', 'practice', 'puck']):
                            if len(response) > 200:  # Detailed response suggests tool use
                                print("   ✅ Detailed response (tools likely used)")
                            else:
                                print("   ⚠️  Short response (tools may not be available)")
                        
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        
        except Exception as e:
            print(f"❌ Failed to create agent: {e}")
    
    asyncio.run(test_native_mcp_agent())