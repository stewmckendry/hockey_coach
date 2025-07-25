"""
Web-optimized hockey agent with native MCP integration and native SDK tool logging.
"""

import asyncio
import logging
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebNativeMCPAgent:
    """
    Web-optimized hockey coaching agent with native MCP integration and tool logging.
    
    Uses OpenAI Agents SDK native capabilities for:
    - Tool call detection via result.new_items
    - Tool metadata extraction from raw_item
    - Automatic MCP server connection management
    """
    
    def __init__(self):
        self.server = None
        self.agent = None
    
    async def connect(self):
        """Initialize MCP server connection and create agent"""
        try:
            logger.info("🚀 Initializing web MCP agent with hockey knowledge...")
            
            # Create MCP server parameters
            params = MCPServerStreamableHttpParams(
                url="http://localhost:8000/mcp",
                headers={},
                timeout=30.0,
                sse_read_timeout=60.0,
                terminate_on_close=False
            )
            
            # Create and connect MCP server
            self.server = MCPServerStreamableHttp(
                params=params,
                name="Hockey Knowledge Server", 
                cache_tools_list=True
            )
            
            await self.server.connect()
            logger.info("✅ Hockey MCP server connected successfully")
            
            # Create agent with connected server
            self.agent = Agent(
                name="Hockey Coach Web Assistant",
                instructions="""
                You are a hockey coaching assistant with access to expert hockey knowledge via MCP tools.
                
                Your role:
                - Help volunteer coaches with practical, actionable advice
                - Use MCP tools for specific hockey questions (drills, skills, tactics)
                - Provide age-appropriate recommendations when relevant
                - Keep responses concise and web-friendly
                
                Response format for web:
                - Start with direct, actionable answer
                - Include 2-3 specific recommendations with bullet points
                - End with helpful follow-up question
                - Keep total response under 250 words
                - Use clear, simple language
                
                When to use MCP tools:
                - User asks about specific skills (skating, passing, shooting)
                - User mentions age groups (U8, U10, U12, etc.)
                - User asks about drills or practice activities
                - User asks about tactics or game situations
                
                Always use available MCP tools for hockey-specific questions!
                """,
                model="gpt-4o-mini",
                mcp_servers=[self.server]
            )
            
            logger.info("✅ Web MCP agent created with hockey knowledge tools")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create web MCP agent: {e}")
            logger.warning("   Agent will work but without hockey knowledge tools")
            return False
    
    async def cleanup(self):
        """Clean up MCP server connection"""
        if self.server:
            try:
                await self.server.cleanup()
                logger.info("🧹 MCP server connection cleaned up")
            except Exception as e:
                logger.warning(f"⚠️  Error cleaning up MCP server: {e}")
    
    def analyze_tool_usage(self, query: str, result) -> dict:
        """
        Analyze tool usage using OpenAI Agents SDK native capabilities.
        
        Returns detailed information about tool calls from result.new_items
        """
        tool_calls = []
        tool_outputs = []
        
        # Extract tool calls and outputs from result.new_items
        for item in result.new_items:
            if item.type == 'tool_call_item':
                tool_call_info = {
                    'type': 'tool_call',
                    'function_name': item.raw_item.name if hasattr(item.raw_item, 'name') else 'unknown',
                    'call_id': item.raw_item.call_id if hasattr(item.raw_item, 'call_id') else 'unknown',
                    'status': item.raw_item.status if hasattr(item.raw_item, 'status') else 'unknown'
                }
                
                # Parse arguments if available
                if hasattr(item.raw_item, 'arguments'):
                    try:
                        tool_call_info['arguments'] = json.loads(item.raw_item.arguments)
                    except:
                        tool_call_info['arguments'] = item.raw_item.arguments
                
                tool_calls.append(tool_call_info)
                
            elif item.type == 'tool_call_output_item':
                tool_output_info = {
                    'type': 'tool_output',
                    'call_id': item.raw_item.get('call_id', 'unknown') if isinstance(item.raw_item, dict) else 'unknown',
                    'output_length': len(str(item.output)) if item.output else 0
                }
                tool_outputs.append(tool_output_info)
        
        # Analysis summary
        analysis = {
            'query': query,
            'response_length': len(result.final_output),
            'tool_calls_count': len(tool_calls),
            'tool_outputs_count': len(tool_outputs),
            'tool_calls': tool_calls,
            'tool_outputs': tool_outputs,
            'tools_used': [call['function_name'] for call in tool_calls]
        }
        
        return analysis
    
    def log_tool_usage(self, analysis: dict):
        """Log tool usage information with detailed SDK metadata"""
        
        query = analysis['query']
        response_length = analysis['response_length']
        tools_used = analysis['tools_used']
        tool_calls_count = analysis['tool_calls_count']
        
        if tool_calls_count > 0:
            logger.info(f"🔧 MCP TOOLS USED - Query: '{query[:50]}...'")
            logger.info(f"   📊 Response: {response_length} chars | Tool calls: {tool_calls_count}")
            logger.info(f"   🛠️  Tools: {', '.join(tools_used)}")
            
            # Log detailed tool call information
            for i, call in enumerate(analysis['tool_calls']):
                logger.info(f"   └─ Call {i+1}: {call['function_name']} (ID: {call['call_id'][:12]}...)")
                if 'arguments' in call and isinstance(call['arguments'], dict):
                    # Log key arguments
                    if 'query' in call['arguments']:
                        logger.info(f"      Query: '{call['arguments']['query']}'")
                    if 'age_groups' in call['arguments']:
                        logger.info(f"      Age groups: {call['arguments']['age_groups']}")
                    if 'content_types' in call['arguments']:
                        logger.info(f"      Content types: {call['arguments']['content_types']}")
            
        else:
            logger.info(f"💬 NO TOOLS USED - Query: '{query[:50]}...'")
            logger.info(f"   📊 Response: {response_length} chars | Conversational response")
    
    async def run(self, message: str) -> str:
        """Run the agent with comprehensive tool usage logging"""
        if not self.agent:
            return "Agent not initialized. Please connect first."
        
        logger.info(f"📝 Processing user query: '{message[:100]}{'...' if len(message) > 100 else ''}'")
        
        try:
            # Run the agent
            logger.info("🤖 Running agent with MCP tools...")
            result = await Runner.run(self.agent, message)
            
            # Analyze tool usage using native SDK capabilities
            analysis = self.analyze_tool_usage(message, result)
            
            # Log the analysis
            self.log_tool_usage(analysis)
            
            logger.info(f"✅ Agent response generated successfully")
            return result.final_output
            
        except Exception as e:
            logger.error(f"❌ Error running web MCP agent: {e}")
            return f"I apologize, but I'm having trouble accessing my hockey knowledge right now. Please try again."

# Factory function for easy use
async def create_web_native_mcp_agent():
    """Create and connect a web native MCP agent"""
    agent = WebNativeMCPAgent()
    success = await agent.connect()
    if success:
        return agent
    else:
        raise Exception("Failed to create web MCP agent")

# API runner function
async def run_web_mcp_agent_with_logging(message: str) -> str:
    """
    Run the web MCP agent with comprehensive logging.
    
    This function handles the complete lifecycle:
    1. Create and connect agent
    2. Process query with tool logging
    3. Clean up connections
    4. Return response
    """
    agent = None
    
    try:
        # Create connected agent
        agent = await create_web_native_mcp_agent()
        
        # Run with logging
        response = await agent.run(message)
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in web MCP agent runner: {e}")
        return f"I apologize, but I'm having trouble accessing my hockey knowledge right now. Please try again."
        
    finally:
        # Clean up
        if agent:
            await agent.cleanup()

# CLI testing
if __name__ == "__main__":
    async def test_web_mcp_agent_with_native_logging():
        print("Testing Web MCP Agent with Native SDK Tool Logging...")
        print("=" * 70)
        
        test_messages = [
            "What are good U10 skating drills?",
            "How do I plan a practice for beginners?", 
            "Tell me about puck handling techniques",
            "Hello, what can you help me with?"
        ]
        
        for message in test_messages:
            print(f"\n{'='*70}")
            print(f"🏒 Testing: {message}")
            print("-" * 50)
            
            response = await run_web_mcp_agent_with_logging(message)
            
            print(f"\nResponse: {response}")
            print("-" * 50)
    
    asyncio.run(test_web_mcp_agent_with_native_logging())