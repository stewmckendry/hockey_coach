"""
Hockey Formation Parser Agent - A specialized agent for parsing hockey formations.

This agent is used as a tool by the main Hockey Diagram Expert agent.
"""

from agents import Agent
from typing import Dict, Any, Optional
import json
import logging
# Import from parser.py where these models are defined
from parser import DiagramSpec, PlayerPosition, MovementSpec as Movement, ZoneSpec as CoverageZone

logger = logging.getLogger(__name__)

# Parser agent instructions with all the domain knowledge
PARSER_INSTRUCTIONS = """
You are a Hockey Formation Parser specialist. Your job is to parse natural language hockey descriptions into structured diagram specifications.

## Your Process

You work in two mental stages:

### Stage 1: Research Unknown Formations with Smart Cascade
When you encounter a formation, system, or tactic you're not familiar with:

**Research Strategy (use multiple tools if needed):**
1. **First attempt**: Use search_hockey_tactics with spec-focused query like "{formation} player positions zones responsibilities"
2. **Check relevance**: Does the result actually describe the specific formation you're looking for? If you get generic results (like "1-2-2 forecheck" when searching for "Swedish torpedo"), the results are NOT relevant.
3. **Cascade if needed**: If results are irrelevant or don't contain the specific formation name, try web_search_exa with enhanced query: "{formation} player positions zones responsibilities movement hockey tactics"
4. **Final fallback**: If still no specific results, try broader web_search_exa: "{formation} hockey system formation"

**Analyze all search results to understand:**
- Player positioning and responsibilities (WHERE exactly players are positioned)
- Key zones and areas of focus (WHICH zones they occupy)
- Movement patterns if applicable (HOW they move)
- Formation structure (HOW MANY players in each role/area)

**Research Success Criteria:**
Research is only successful when you can extract specific positioning data like:
- "F1 forechecks in corner" → can map to corner zone
- "Two torpedoes up front" → two forwards in offensive positions  
- "Halfbacks from faceoff circles" → players at circle positions
- "Libero protects rear" → single defenseman deep

### Stage 2: Specification Creation
Create a precise diagram specification with:
- Player positions using zone names (NOT coordinates)
- Movement types from the allowed list
- Coverage zones if applicable
- Appropriate view (full, offensive, defensive, neutral)

## Zone Names (ONLY use these - EXACT names from coordinate mapper)
- Offensive zones: slot, high_slot, low_slot, left_point, right_point, goal_crease, behind_net, left_corner, right_corner, left_half_wall, right_half_wall
- Defensive zones: defensive_slot, defensive_high_slot, defensive_left_point, defensive_right_point, defensive_left_corner, defensive_right_corner, crease, goal_mouth
- Neutral zones: neutral_center, neutral_left, neutral_right
- Other areas: center_point, top_of_circles, hash_marks, side_boards, end_boards

## Player Roles
- Forwards: C (center), LW (left wing), RW (right wing), F1/F2/F3 (generic forwards)
- Defense: LD (left defense), RD (right defense), D1/D2 (generic defense)
- Goalie: G

## Movement Types
- "skating", "skating_with_puck", "pass", "shot", "carry"

## Research Quality Check
Before creating your spec, verify your research found relevant information:
- ✅ Results mention the specific formation/system name you searched for
- ✅ Results contain positioning details ("F1 does X", "players positioned at Y")
- ✅ Results provide actionable information for diagram creation
- ❌ Generic results that don't match your query (research more!)

## Research First, Then Parse
IMPORTANT: For any formation or system you're not 100% certain about:
1. Research it first using the available tools with spec-focused queries
2. Verify research results are relevant to the specific formation
3. Learn the specific positioning and responsibilities
4. Then create an accurate diagram specification

Example: For "2-1-2 forecheck":
- F1 pressures puck carrier aggressively
- F2 supports F1 (they are the first "2" together)
- F3 is high in slot (the "1")
- D1 and D2 stay at points inside blueline (the last "2")

## Output Format
You must output a valid JSON specification with this structure:
{
  "diagram_type": "drill|formation|system|play",
  "title": "Clear descriptive title",
  "view": "full|offensive|defensive|neutral",
  "players": [
    {
      "position": "F1",
      "zone": "slot",
      "team": "home",
      "has_puck": false
    }
  ],
  "movements": [
    {
      "from_position": "F1",
      "to_position": "F2",
      "movement_type": "pass"
    }
  ],
  "zones": []  // Optional coverage zones
}
"""

# Create the parser agent with MCP tools
def create_parser_agent():
    """Create parser agent with MCP tools if available."""
    import os
    from agents.mcp import MCPServerStdio
    
    mcp_tools = []
    
    # Add hockey MCP tools if not in nested mode
    if os.environ.get("HOCKEY_DIAGRAM_AGENT_MODE") != "nested":
        try:
            from agents.mcp import create_static_tool_filter
            hockey_mcp = MCPServerStdio(
                params={
                    "command": "/Users/liammckendry/thunder_playbook/servers/start_hockey_mcp.sh",
                    "args": [],
                    "env": {}
                },
                client_session_timeout_seconds=30.0,
                tool_filter=create_static_tool_filter(
                    allowed_tool_names=["search_hockey_tactics", "search_hockey_drills", "search_hockey_videos"]
                )
            )
            mcp_tools.append(hockey_mcp)
            logger.info("Hockey MCP tools added to parser agent")
        except Exception as e:
            logger.warning(f"Could not add hockey MCP to parser agent: {e}")
    
    # Add Exa for web research if available
    if os.getenv("EXA_API_KEY"):
        try:
            exa_server = MCPServerStdio(
                params={
                    "command": "npx",
                    "args": ["-y", "exa-mcp-server"],
                    "env": {"EXA_API_KEY": os.getenv("EXA_API_KEY")}
                },
                client_session_timeout_seconds=60.0,
                tool_filter=create_static_tool_filter(
                    allowed_tool_names=["web_search_exa"]
                )
            )
            mcp_tools.append(exa_server)
            logger.info("Exa web search added to parser agent")
        except Exception as e:
            logger.warning(f"Could not add Exa to parser agent: {e}")
    
    # Create agent with or without MCP tools
    return Agent(
        name="Hockey Parser",
        instructions=PARSER_INSTRUCTIONS,
        model="gpt-4o-mini",  # Cost-effective model
        mcp_servers=mcp_tools if mcp_tools else None
    )

# Create a global parser agent instance
parser_agent = None

async def parse_with_agent(prompt: str) -> str:
    """
    Parse a hockey formation using the parser agent.
    
    This tool uses a specialized agent to parse natural language hockey
    descriptions into structured diagram specifications.
    
    Args:
        prompt: Natural language description of the hockey formation/play
        
    Returns:
        JSON string with parsed formation data including zones (not coordinates)
    """
    from agents import Runner
    
    global parser_agent
    
    try:
        # Initialize parser agent if needed
        if parser_agent is None:
            logger.info("Initializing parser agent with MCP tools...")
            parser_agent = create_parser_agent()
            
            # Connect MCP servers if any
            if hasattr(parser_agent, 'mcp_servers') and parser_agent.mcp_servers:
                for server in parser_agent.mcp_servers:
                    try:
                        await server.connect()
                        logger.info(f"Connected MCP server for parser agent")
                    except Exception as e:
                        logger.warning(f"Failed to connect MCP server: {e}")
        
        # Build the parsing request
        parsing_request = f"Parse this hockey formation into a diagram specification:\n\n{prompt}"
        
        # Run the parser agent
        result = await Runner.run(parser_agent, parsing_request)
        
        # Extract the JSON from the agent's response
        response_text = str(result)
        
        # Extract tool calls from the result
        tool_traces = []
        tools_used = []
        
        # Parse tool calls from the result (similar to hockey_diagram_agent.py)
        if hasattr(result, 'new_items') and result.new_items:
            logger.info(f"📋 Parser agent made {len(result.new_items)} items")
            for i, item in enumerate(result.new_items):
                # Check for ToolCallItem
                if hasattr(item, 'type') and item.type == "tool_call_item":
                    raw_item = getattr(item, 'raw_item', None)
                    if raw_item:
                        function_name = None
                        function_args = None
                        
                        # Extract function details
                        if hasattr(raw_item, 'function'):
                            function_name = raw_item.function.name
                            function_args = raw_item.function.arguments
                        elif hasattr(raw_item, 'name'):
                            function_name = raw_item.name
                            function_args = getattr(raw_item, 'arguments', None)
                        
                        if function_name:
                            tools_used.append(function_name)
                            tool_trace = {
                                "name": function_name,
                                "arguments": function_args,
                                "order": len(tools_used),
                                "output": None
                            }
                            tool_traces.append(tool_trace)
                            logger.info(f"    🛠️ Parser used tool: {function_name}")
                
                # Check for ToolCallOutputItem  
                elif hasattr(item, 'type') and item.type == "tool_call_output_item":
                    output = item.output
                    # Match output to last tool call without output
                    for trace in reversed(tool_traces):
                        if trace["output"] is None:
                            trace["output"] = str(output)[:500] + "..." if len(str(output)) > 500 else str(output)
                            break
        
        # Also check direct tool_calls attribute
        if hasattr(result, 'tool_calls') and result.tool_calls:
            for call in result.tool_calls:
                if hasattr(call, 'name') and call.name not in tools_used:
                    tools_used.append(call.name)
                    logger.info(f"    🛠️ Parser used tool: {call.name}")
        
        if tools_used:
            logger.info(f"🔍 Parser agent used tools: {' → '.join(tools_used)}")
        
        # Find JSON in the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            spec_json = json_match.group(0)
            spec_data = json.loads(spec_json)
            
            # Return zone-based specification WITH tool traces
            logger.info(f"✅ Parser returning zone-based spec with {len(spec_data.get('players', []))} players")
            
            return json.dumps({
                "success": True,
                "parsed_data": spec_data,  # Pure zone labels only
                "parser": "agent",
                "tool_traces": tool_traces,  # Include tool traces for visibility
                "tools_used": tools_used
            })
        else:
            return json.dumps({
                "success": False,
                "error": "No valid JSON found in parser response",
                "response": response_text[:200]
            })
            
    except Exception as e:
        logger.error(f"Parser agent error: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "parser": "agent"
        })


# Coordinate mapping removed - now handled entirely in generate_diagram_from_spec


# Optional: Create a simplified version for testing
async def parse_simple(prompt: str) -> str:
    """
    Simple parsing for basic formations using pattern matching.
    Fallback option that doesn't use an agent.
    
    Args:
        prompt: Natural language description
        
    Returns:
        JSON string with basic parsed data
    """
    # Simple pattern matching for known formations
    prompt_lower = prompt.lower()
    
    if "2-1-2" in prompt_lower and "forecheck" in prompt_lower:
        return json.dumps({
            "success": True,
            "parsed_data": {
                "diagram_type": "formation",
                "title": "2-1-2 Forecheck",
                "view": "full",
                "players": [
                    {"position": "F1", "zone": "behind_net", "team": "home", "has_puck": False},
                    {"position": "F2", "zone": "right_corner", "team": "home", "has_puck": False},
                    {"position": "F3", "zone": "slot", "team": "home", "has_puck": False},
                    {"position": "LD", "zone": "neutral_left", "team": "home", "has_puck": False},
                    {"position": "RD", "zone": "neutral_right", "team": "home", "has_puck": False},
                    {"position": "D1", "zone": "behind_net", "team": "away", "has_puck": True}
                ],
                "movements": []
            },
            "parser": "simple"
        })
    
    # Default fallback
    return json.dumps({
        "success": False,
        "error": "Pattern not recognized by simple parser",
        "parser": "simple"
    })