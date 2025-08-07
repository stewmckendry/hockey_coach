"""
Hockey Diagram Expert Agent using OpenAI Agents SDK.

This agent orchestrates hockey diagram generation by intelligently choosing between:
1. Direct parsing (for known formations)
2. Research-enhanced generation (for unknown concepts)
3. Iterative refinement (for coach feedback)
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

from agent_instructions import EXPERT_INSTRUCTIONS

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HockeyDiagramExpert:
    """
    Single agent that orchestrates all hockey diagram generation.
    
    Uses OpenAI Agents SDK to intelligently decide when and how to use:
    - Direct parsing for known formations (fast path)
    - Research tools for unknown concepts
    - Iterative refinement for coach feedback
    """
    
    def __init__(self):
        self.agent = None
        self.mcp_servers = []
        self.conversation_history = []
        
    async def initialize(self):
        """Initialize the agent with all tools and MCP servers."""
        try:
            logger.info("🚀 Initializing Hockey Diagram Expert Agent...")
            
            # Connect to MCP servers using correct params format with increased timeout
            # NOTE: Removed self-reference to hockey-diagram server to prevent recursive loop
            # The agent should not connect to its own MCP server
            self.mcp_servers = []
            
            # Only try to connect to hockey MCP if it's not already being used by the parent
            if os.environ.get("HOCKEY_DIAGRAM_AGENT_MODE") != "nested":
                try:
                    logger.info("Attempting to connect to hockey MCP server...")
                    from agents.mcp import create_static_tool_filter
                    
                    hockey_mcp = MCPServerStdio(
                        params={
                            "command": "/Users/liammckendry/thunder_playbook/servers/start_hockey_mcp.sh",
                            "args": [],
                            "env": {}
                        },
                        client_session_timeout_seconds=30.0,  # Increased from default 5s
                        # Only allow specific research tools from hockey MCP
                        tool_filter=create_static_tool_filter(
                            allowed_tool_names=["search_hockey_tactics", "search_hockey_drills", "search_hockey_videos"]
                        )
                    )
                    self.mcp_servers.append(hockey_mcp)
                except Exception as e:
                    logger.warning(f"Could not add hockey MCP server: {e}")
            else:
                logger.info("Running in nested mode - skipping hockey MCP connection")
            
            # Connect all MCP servers
            for i, server in enumerate(self.mcp_servers):
                try:
                    await server.connect()
                    logger.info(f"✅ Connected MCP server {i+1}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to connect MCP server {i+1}: {e}")
                    # Remove failed server from list
                    self.mcp_servers.remove(server)
            
            # Add web research if Exa key available
            if os.getenv("EXA_API_KEY"):
                exa_server = MCPServerStdio(
                    params={
                        "command": "npx",
                        "args": ["-y", "exa-mcp-server"],
                        "env": {"EXA_API_KEY": os.getenv("EXA_API_KEY")}
                    },
                    client_session_timeout_seconds=60.0,  # Longer timeout for web research
                    # Only allow web search tool from Exa
                    tool_filter=create_static_tool_filter(
                        allowed_tool_names=["web_search_exa"]
                    )
                )
                try:
                    await exa_server.connect()
                    self.mcp_servers.append(exa_server)
                    logger.info("✅ Exa web search connected")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to connect Exa server: {e}")
            else:
                logger.info("ℹ️ Exa web search not available (no API key)")
            
            # Import properly decorated function tools
            from hockey_tools import (
                parse_hockey_formation,
                generate_diagram_from_spec,
                list_hockey_formations
            )
            
            # Import subagents
            from hockey_subagents import get_synthesis_agent, get_zone_mapping_agent
            
            # Get subagent tools
            subagent_tools = []
            synthesis_agent = get_synthesis_agent()
            zone_mapping_agent = get_zone_mapping_agent()
            
            if synthesis_agent.agent:
                synthesis_tool = synthesis_agent.agent.as_tool(
                    tool_name="synthesize_research_to_formation",
                    tool_description="Synthesize raw research results into structured hockey formation data. Takes research findings and formation name, returns structured formation specification."
                )
                subagent_tools.append(synthesis_tool)
                logger.info("✅ FormationSynthesisAgent added as direct tool")
            
            if zone_mapping_agent.agent:
                zone_mapping_tool = zone_mapping_agent.agent.as_tool(
                    tool_name="map_formation_to_zones",
                    tool_description="Map structured formation data to precise zone-based diagram specification. Takes formation data and options, returns complete diagram specification with all entities."
                )
                subagent_tools.append(zone_mapping_tool)
                logger.info("✅ ZoneMappingAgent added as direct tool")
            
            # Combine native function tools with subagent tools
            all_tools = [
                parse_hockey_formation,
                generate_diagram_from_spec,
                list_hockey_formations
            ] + subagent_tools
            
            logger.info(f"📋 Total tools available: {len(all_tools)} (3 native + {len(subagent_tools)} subagents)")
            
            # Create agent with comprehensive instructions and all tools
            self.agent = Agent(
                name="Hockey Diagram Expert",
                instructions=EXPERT_INSTRUCTIONS,
                mcp_servers=self.mcp_servers,
                tools=all_tools,  # Native functions + subagents
                model="gpt-4o-mini"  # Use cost-effective model
            )
            
            logger.info("✅ Hockey Diagram Expert Agent initialized successfully")
            logger.info(f"📋 Connected MCP servers: {len(self.mcp_servers)} servers connected")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            raise
    
    async def generate_diagram(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a hockey diagram from natural language request.
        
        Args:
            request: Natural language description of the formation/play/drill
            context: Optional context including conversation history, preferences, etc.
            
        Returns:
            Dictionary containing:
            - response: Agent's formatted response
            - diagram_path: Path to generated diagram (if successful)
            - success: Boolean indicating success
            - processing_time: Time taken
            - tools_used: List of tools the agent used
        """
        if not self.agent:
            await self.initialize()
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"🎯 Processing diagram request: {request[:50]}...")
            
            # Add context to request if provided
            enhanced_request = request
            if context:
                if context.get("previous_diagram"):
                    enhanced_request = f"Previous diagram context: {context['previous_diagram']}\n\nNew request: {request}"
                if context.get("coach_preferences"):
                    enhanced_request += f"\n\nCoach preferences: {context['coach_preferences']}"
            
            # Run agent with the enhanced request using static method
            logger.info(f"🔧 Sending request to agent: {enhanced_request[:100]}...")
            result = await Runner.run(self.agent, enhanced_request)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"⏱️ Agent processing completed in {processing_time:.2f}s")
            
            # Extract tools used from result with detailed logging
            tools_used = []
            tool_calls_detail = []
            parser_traces = {}  # To store parser stage traces
            
            # First check direct attributes of result
            logger.info(f"📋 Result type: {type(result).__name__}")
            if hasattr(result, '__dict__'):
                logger.info(f"📋 Result attributes: {list(result.__dict__.keys())}")
            
            # Try the direct tool_calls attribute approach
            if hasattr(result, 'tool_calls') and result.tool_calls:
                logger.info(f"📋 Found tool_calls directly on result: {len(result.tool_calls)} calls")
                for call in result.tool_calls:
                    if hasattr(call, 'name'):
                        tools_used.append(call.name)
                        logger.info(f"    🛠️ Tool: {call.name}")
            
            if hasattr(result, 'new_items') and result.new_items:
                logger.info(f"📋 Inspecting {len(result.new_items)} result items...")
                
                for i, item in enumerate(result.new_items):
                    logger.info(f"  📄 Item {i+1}: {type(item).__name__}")
                    
                    # Debug: Log all item attributes
                    if hasattr(item, '__dict__'):
                        logger.debug(f"    Item attributes: {list(item.__dict__.keys())}")
                    if hasattr(item, 'type'):
                        logger.info(f"    Item type: {item.type}")
                    
                    # Check for ToolCallItem
                    if hasattr(item, 'type') and item.type == "tool_call_item":
                        # Extract tool call details - check different possible structures
                        raw_item = getattr(item, 'raw_item', None)
                        if raw_item:
                            logger.debug(f"    Raw item type: {type(raw_item).__name__}")
                            if hasattr(raw_item, '__dict__'):
                                logger.debug(f"    Raw item attrs: {list(raw_item.__dict__.keys())}")
                            
                            function_name = None
                            function_args = None
                            
                            # Try different attribute paths for function details
                            if hasattr(raw_item, 'function'):
                                # ResponseFunctionToolCall structure
                                function_name = raw_item.function.name
                                function_args = raw_item.function.arguments
                            elif hasattr(raw_item, 'name'):
                                # Direct attributes
                                function_name = raw_item.name
                                function_args = getattr(raw_item, 'arguments', None)
                            elif isinstance(raw_item, dict):
                                # Dictionary structure
                                if 'function' in raw_item:
                                    function_name = raw_item['function'].get('name')
                                    function_args = raw_item['function'].get('arguments')
                                elif 'name' in raw_item:
                                    function_name = raw_item['name']
                                    function_args = raw_item.get('arguments')
                            
                            if function_name:
                                tools_used.append(function_name)
                                tool_call_detail = {
                                    "name": function_name,
                                    "arguments": function_args,
                                    "order": len(tools_used),
                                    "output": None  # Will be filled by ToolCallOutputItem
                                }
                                tool_calls_detail.append(tool_call_detail)
                                
                                logger.info(f"    🛠️ Tool call: {function_name}")
                                logger.info(f"    📝 Args: {str(function_args)[:200]}...")
                            else:
                                logger.warning(f"    ⚠️ Could not extract function name from raw_item")
                    
                    # Check for ToolCallOutputItem
                    elif hasattr(item, 'type') and item.type == "tool_call_output_item":
                        # Get the actual output
                        output = item.output
                        logger.info(f"    📊 Tool output type: {type(output).__name__}")
                        
                        # Match this output to the corresponding tool call
                        if tool_calls_detail and len(tool_calls_detail) > 0:
                            # Find the last tool call without output
                            for i in range(len(tool_calls_detail) - 1, -1, -1):
                                if tool_calls_detail[i]["output"] is None:
                                    tool_calls_detail[i]["output"] = str(output)[:500] + "..." if len(str(output)) > 500 else str(output)
                                    
                                    # Try to extract parser traces from parse_hockey_formation output
                                    if tool_calls_detail[i]["name"] == "parse_hockey_formation":
                                        try:
                                            if isinstance(output, str):
                                                import json
                                                result_data = json.loads(output)
                                                if result_data.get('success') and 'parsed_data' in result_data:
                                                    parser_traces = {
                                                        "parser_used": result_data.get('parser_used', 'unknown'),
                                                        "parsed_data": {
                                                            "title": result_data['parsed_data'].get('title'),
                                                            "player_count": len(result_data['parsed_data'].get('players', [])),
                                                            "movement_count": len(result_data['parsed_data'].get('movements', [])),
                                                            "view": result_data['parsed_data'].get('view')
                                                        }
                                                    }
                                                    logger.info(f"    🔍 Parser traces extracted: {parser_traces}")
                                        except (json.JSONDecodeError, TypeError) as e:
                                            logger.error(f"    ❌ Failed to parse tool output: {e}")
                                    break
                    
                    # Check for MessageOutputItem
                    elif hasattr(item, 'type') and item.type == "message_output_item":
                        if hasattr(item, 'content'):
                            content_preview = str(item.content)[:150]
                            logger.info(f"    💬 Message: {content_preview}...")
            else:
                logger.warning("⚠️ Result has no new_items or empty")
            
            # Log final agent response
            response_text = str(result)
            logger.info(f"📝 Agent response length: {len(response_text)} characters")
            logger.info(f"🎭 Agent response preview: {response_text[:200]}...")
            
            # Log tools summary
            if tools_used:
                logger.info(f"🛠️ Tools used in order: {' → '.join(tools_used)}")
                logger.info(f"🔢 Total tool calls: {len(tool_calls_detail)}")
            else:
                logger.info("🚫 No tool calls detected in agent response")
            
            # Extract diagram path from response if present
            diagram_path = None
            response_text = str(result)
            if "Diagram:" in response_text:
                # Look for file path pattern, handling both plain paths and Markdown links
                import re
                # Try Markdown link format first: [text](path)
                path_match = re.search(r'📁 Diagram: \[([^\]]+)\]\(([^\)]+\.png)\)', response_text)
                if path_match:
                    diagram_path = path_match.group(2)  # Get the URL part
                else:
                    # Try plain path format
                    path_match = re.search(r'📁 Diagram: ([^\n\[]+\.png)', response_text)
                    if path_match:
                        diagram_path = path_match.group(1).strip()
            
            # Store conversation history
            self.conversation_history.append({
                "request": request,
                "response": str(result),
                "diagram_path": diagram_path,
                "tools_used": tools_used,
                "timestamp": start_time
            })
            
            logger.info(f"✅ Diagram request completed in {processing_time:.2f}s")
            logger.info(f"🛠️ Tools used: {tools_used}")
            
            return {
                "response": str(result),
                "diagram_path": diagram_path,
                "success": True,
                "processing_time": processing_time,
                "tools_used": tools_used,
                "tool_calls_detail": tool_calls_detail,
                "conversation_id": len(self.conversation_history),
                "trace": {
                    "steps": tool_calls_detail,
                    "total_steps": len(tool_calls_detail),
                    "tools_sequence": " → ".join(tools_used) if tools_used else "No tools used",
                    "execution_time": processing_time
                },
                "parser_traces": parser_traces  # Include detailed parser stage traces
            }
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"❌ Error processing diagram request: {e}")
            
            return {
                "response": f"❌ Error generating diagram: {str(e)}",
                "diagram_path": None,
                "success": False,
                "processing_time": processing_time,
                "tools_used": [],
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def continue_conversation(self, follow_up: str) -> Dict[str, Any]:
        """
        Continue the conversation with follow-up requests or feedback.
        
        Args:
            follow_up: Follow-up request or feedback
            
        Returns:
            Dictionary with same structure as generate_diagram
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        logger.info(f"💬 Processing follow-up: {follow_up[:50]}...")
        
        # Use static method to maintain conversation context
        result = await Runner.run(self.agent, follow_up)
        
        # Extract diagram path if present
        diagram_path = None
        response_text = str(result)
        if "Diagram:" in response_text:
            import re
            path_match = re.search(r'📁 Diagram: ([^\n]+\.png)', response_text)
            if path_match:
                diagram_path = path_match.group(1)
        
        return {
            "response": str(result),
            "diagram_path": diagram_path,
            "success": True
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the full conversation history."""
        return self.conversation_history.copy()
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("🧹 Conversation history cleared")
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get information about agent capabilities and available tools."""
        if not self.agent:
            await self.initialize()
        
        capabilities = {
            "agent_name": "Hockey Diagram Expert",
            "model": "gpt-4o",
            "mcp_servers": f"{len(self.mcp_servers)} MCP servers connected",
            "core_capabilities": [
                "Parse known hockey formations instantly",
                "Research unknown tactical concepts",
                "Generate NHL-regulation diagrams",
                "Handle iterative coach feedback",
                "Maintain conversation context"
            ],
            "supported_requests": [
                "Standard formations (2-1-2 forecheck, 1-3-1 powerplay, etc.)",
                "Custom drills and plays",
                "International tactical variations",
                "Position adjustments and refinements",
                "Multi-step drill sequences"
            ]
        }
        
        return capabilities

# Global agent instance for reuse
_agent_instance = None

async def get_agent() -> HockeyDiagramExpert:
    """Get or create the global agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = HockeyDiagramExpert()
        await _agent_instance.initialize()
    return _agent_instance

# Convenience functions for direct usage
async def generate_hockey_diagram_with_agent(request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate a hockey diagram using the expert agent."""
    agent = await get_agent()
    return await agent.generate_diagram(request, context)

async def continue_hockey_conversation(follow_up: str) -> Dict[str, Any]:
    """Continue conversation with the expert agent."""
    agent = await get_agent()
    return await agent.continue_conversation(follow_up)

# Test function
async def test_agent():
    """Test the agent with a simple request."""
    print("🧪 Testing Hockey Diagram Expert Agent...")
    
    agent = HockeyDiagramExpert()
    await agent.initialize()
    
    # Test known formation
    result = await agent.generate_diagram("Show me a 2-1-2 forecheck")
    print(f"✅ Test result: {result['success']}")
    print(f"📝 Response: {result['response'][:200]}...")
    
    # Test follow-up
    follow_up = await agent.continue_conversation("Make F1 more aggressive")
    print(f"💬 Follow-up: {follow_up['success']}")

if __name__ == "__main__":
    asyncio.run(test_agent())