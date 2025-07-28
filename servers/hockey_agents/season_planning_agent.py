"""
Season Planning Specialist Agent with minimal customization.

Extends WebNativeMCPAgent for hockey season planning through natural conversation.
Uses native SDK features: Runner.run(), MCPServerStreamableHttp, tracing, WebSearchTool.
"""

import asyncio
import logging
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from agents import Agent, Runner, trace, gen_trace_id, WebSearchTool, SQLiteSession
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
from dotenv import load_dotenv

# Import base agent
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from poc.poc_agents.web_native_mcp_agent import WebNativeMCPAgent

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SeasonPlanningAgent(WebNativeMCPAgent):
    """
    Season Planning Specialist Agent extending WebNativeMCPAgent.
    
    Minimal customization - primary intelligence comes from prompt files.
    Additional features:
    - save_season_plan() method for file output
    - Configurable prompts from files
    - WebSearchTool integration
    """
    
    def __init__(self, prompts_dir: str = "../prompts"):
        super().__init__()
        self.prompts_dir = prompts_dir
        self.web_search_tool = WebSearchTool()
        self._loaded_prompts = {}
    
    def load_prompt(self, filename: str) -> str:
        """Load a prompt from the prompts directory."""
        if filename in self._loaded_prompts:
            return self._loaded_prompts[filename]
        
        # Use absolute path relative to this file's location
        if self.prompts_dir.startswith('../'):
            base_dir = Path(__file__).resolve().parent.parent.parent
            prompt_path = base_dir / self.prompts_dir.lstrip('../') / filename
        else:
            prompt_path = Path(self.prompts_dir) / filename
        try:
            with open(prompt_path, 'r') as f:
                content = f.read()
                self._loaded_prompts[filename] = content
                logger.info(f"✅ Loaded prompt from {filename}")
                return content
        except Exception as e:
            logger.error(f"❌ Failed to load prompt {filename}: {e}")
            return ""
    
    def build_full_instructions(self) -> str:
        """Build comprehensive instructions from multiple prompt files."""
        # Load all prompt components
        main_instructions = self.load_prompt("season_planning_instructions.md")
        tool_guidelines = self.load_prompt("tool_usage_guidelines.md")
        examples = self.load_prompt("conversation_examples.md")
        completion_signals = self.load_prompt("completion_signals.md")
        
        # Combine into full instructions
        full_instructions = f"""
{main_instructions}

## Tool Usage Guidelines
{tool_guidelines}

## Conversation Examples
{examples}

## Completion Recognition
{completion_signals}
"""
        return full_instructions
    
    async def connect(self):
        """Initialize MCP server connection and create agent with enhanced tools."""
        try:
            logger.info("🚀 Initializing Season Planning Agent...")
            
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
            
            # Load comprehensive instructions from files
            full_instructions = self.build_full_instructions()
            
            # Create agent with all tools (MCP + WebSearch)
            self.agent = Agent(
                name="Hockey Season Planning Specialist",
                instructions=full_instructions,
                model="gpt-4o-mini",
                mcp_servers=[self.server],
                tools=[self.web_search_tool]
            )
            
            logger.info("✅ Season Planning Agent created with:")
            logger.info(f"   - MCP tools: 6 (4 existing + 2 new)")
            logger.info(f"   - Native tools: WebSearchTool")
            logger.info(f"   - Prompts loaded: {len(self._loaded_prompts)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create Season Planning Agent: {e}")
            return False
    
    async def run(self, message: str, group_id: str = None, session_id: str = None) -> str:
        """Run the agent with comprehensive logging and tracing."""
        if not self.agent:
            return "Agent not initialized. Please connect first."
        
        logger.info(f"📝 Processing season planning query: '{message[:100]}{'...' if len(message) > 100 else ''}'")
        
        # Create SQLiteSession for conversation persistence
        session = None
        if session_id:
            try:
                session = SQLiteSession(session_id, "season_planning_conversations.db")
                logger.info(f"📚 Using SQLiteSession for conversation persistence: {session_id}")
            except Exception as e:
                logger.warning(f"⚠️  Could not create SQLiteSession: {e}. Continuing without persistence.")
        
        # Create trace metadata
        trace_metadata = {
            "query_length": str(len(message)),
            "query_preview": message[:100],
            "agent_type": "season_planning_specialist",
            "mcp_server": "localhost:8000",
            "session_id": session_id or "none",
            "has_session_persistence": str(session is not None)
        }
        
        # Generate trace ID
        trace_id = gen_trace_id()
        
        # Use OpenAI Agents SDK trace
        with trace(
            workflow_name="Season Planning Specialist", 
            trace_id=trace_id,
            group_id=group_id,
            metadata=trace_metadata
        ):
            try:
                # Run the agent within trace context with session
                logger.info("🏒 Running season planning agent with MCP tools and WebSearch...")
                result = await Runner.run(self.agent, message, session=session)
                
                # Analyze tool usage
                analysis = self.analyze_tool_usage(message, result)
                
                # Log the analysis
                self.log_tool_usage(analysis)
                
                # Check if response contains season plan to save
                if self._should_save_plan(result.final_output):
                    saved_path = await self.save_season_plan(result.final_output)
                    if saved_path:
                        logger.info(f"💾 Season plan automatically saved to: {saved_path}")
                
                # Log trace URL
                trace_url = f"https://platform.openai.com/logs/trace?trace_id={trace_id}"
                logger.info(f"🔍 View trace in OpenAI Dashboard: {trace_url}")
                
                logger.info(f"✅ Season planning response generated successfully")
                return result.final_output
                
            except Exception as e:
                logger.error(f"❌ Error running season planning agent: {e}")
                return f"I apologize, but I'm having trouble accessing my hockey knowledge right now. Please try again."
    
    def _should_save_plan(self, response: str) -> bool:
        """Determine if the response contains a season plan to save."""
        # Look for indicators that a full season plan was generated
        indicators = [
            "## Season Plan",
            "### Monthly Breakdown",
            "### Phase 1:",
            "### Pre-Season",
            "### Regular Season",
            "### Playoffs",
            "Monthly Practice Themes",
            "Season Overview",
            "# Season Plan for",
            "## Complete Season Plan"
        ]
        
        return any(indicator in response for indicator in indicators)
    
    async def save_season_plan(self, plan_content: str) -> str:
        """Save the season plan to a timestamped file."""
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"season_plan_{timestamp}.md"
            # Save to outputs directory
            filepath = Path(__file__).resolve().parent.parent.parent / "outputs" / "season_plans" / filename
            
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the plan
            with open(filepath, 'w') as f:
                f.write(plan_content)
            
            logger.info(f"💾 Season plan saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error saving season plan: {e}")
            return None
    
    def get_session_info(self, session_id: str = None) -> dict:
        """Get session information for debugging."""
        info = {
            "session_persistence": "SQLiteSession (automatic)",
            "database_file": "season_planning_conversations.db",
            "session_id": session_id or "not_provided"
        }
        
        # Try to get conversation count from database if session_id provided
        if session_id:
            try:
                session = SQLiteSession(session_id, "season_planning_conversations.db")
                # Note: SQLiteSession doesn't expose message count directly
                # This is handled internally by the SDK
                info["status"] = "active"
            except Exception as e:
                info["status"] = f"error: {e}"
        
        return info


# Factory function for easy use
async def create_season_planning_agent() -> SeasonPlanningAgent:
    """Create and connect a season planning agent."""
    agent = SeasonPlanningAgent()
    success = await agent.connect()
    if success:
        return agent
    else:
        raise Exception("Failed to create season planning agent")


# API runner function
async def run_season_planning_agent(message: str, group_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """
    Run the season planning agent with comprehensive logging and tracing.
    
    This function handles the complete lifecycle:
    1. Create and connect agent
    2. Process query with tool logging and tracing (with session persistence if session_id provided)
    3. Save season plan if generated
    4. Clean up connections
    5. Return response
    
    Args:
        message: User query for season planning
        group_id: Optional group ID for trace linking
        session_id: Optional session ID for conversation persistence
    
    Returns:
        Season planning response with trace recorded
    """
    agent = None
    
    try:
        # Create connected agent
        agent = await create_season_planning_agent()
        
        # Run with logging and tracing (with session persistence)
        response = await agent.run(message, group_id=group_id, session_id=session_id)
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in season planning agent runner: {e}")
        return f"I apologize, but I'm having trouble with season planning right now. Please try again."
        
    finally:
        # Clean up
        if agent:
            await agent.cleanup()


# CLI testing
if __name__ == "__main__":
    async def test_season_planning_agent():
        print("Testing Season Planning Agent...")
        print("=" * 70)
        
        print("\n🏒 Starting interactive season planning session...")
        print("Type 'quit' to exit\n")
        
        agent = None
        session_id = f"cli_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Create agent once for the session
            agent = await create_season_planning_agent()
            print(f"✅ Agent created successfully")
            print(f"📝 Session ID: {session_id}")
            print(f"💾 Conversation persistence: Enabled (SQLiteSession)")
            print("-" * 50)
            
            while True:
                # Get user input
                message = input("\nCoach: ").strip()
                
                if message.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for planning your season! Good luck coaching!")
                    break
                
                if not message:
                    continue
                
                # Process message with session persistence
                print("\nAssistant: ", end="", flush=True)
                response = await agent.run(message, session_id=session_id)
                print(response)
                print("-" * 50)
                
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Thanks for using the Season Planning Agent!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            # Clean up
            if agent:
                await agent.cleanup()
    
    asyncio.run(test_season_planning_agent())