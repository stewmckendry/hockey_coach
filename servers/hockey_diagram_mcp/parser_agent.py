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
from coordinate_mapper import coordinate_mapper

logger = logging.getLogger(__name__)

# Parser agent instructions with all the domain knowledge
PARSER_INSTRUCTIONS = """
You are a Hockey Formation Parser specialist. Your job is to parse natural language hockey descriptions into structured diagram specifications.

## Your Process

You work in two mental stages:

### Stage 1: Research Unknown Formations
When you encounter a formation, system, or tactic you're not familiar with:
1. Use the search_hockey_tactics tool to find specific hockey tactics and systems
2. Use the search_hockey_drills tool if it's a drill description
3. Use the web_search_exa tool as a fallback for less common or international variations
4. Analyze the search results to understand:
   - Player positioning and responsibilities
   - Key zones and areas of focus
   - Movement patterns if applicable
   - Defensive assignments

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

## Research First, Then Parse
IMPORTANT: For any formation or system you're not 100% certain about:
1. Research it first using the available tools
2. Learn the specific positioning and responsibilities
3. Then create an accurate diagram specification

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
        model="gpt-4",
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
        
        # Find JSON in the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            spec_json = json_match.group(0)
            spec_data = json.loads(spec_json)
            
            # Apply coordinate mapping
            spec_with_coords = apply_coordinate_mapping(spec_data)
            
            # Log if research tools were used
            if hasattr(result, 'tool_calls') and result.tool_calls:
                tools_used = [call.name for call in result.tool_calls]
                if any(tool in tools_used for tool in ['search_hockey_tactics', 'search_hockey_drills', 'web_search_exa']):
                    logger.info(f"🔍 Parser agent used research tools: {tools_used}")
            
            return json.dumps({
                "success": True,
                "parsed_data": spec_with_coords,
                "parser": "agent",
                "raw_spec": spec_data  # Include original zone-based spec
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


def apply_coordinate_mapping(spec_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply coordinate mapping to convert zone names to x,y coordinates.
    
    Args:
        spec_data: Parsed specification with zone names
        
    Returns:
        Specification with both zones and coordinates
    """
    # Map player zones to coordinates
    for player in spec_data.get("players", []):
        if "zone" in player and "x" not in player:
            try:
                x, y = coordinate_mapper.get_area_coordinate(player["zone"])
                player["x"] = x
                player["y"] = y
                logger.info(f"Mapped {player['zone']} to ({x}, {y})")
            except KeyError:
                logger.warning(f"Unknown zone: {player['zone']}")
                # Fallback to center position
                player["x"] = 0
                player["y"] = 0
    
    # Map movement endpoints if they use zones
    for movement in spec_data.get("movements", []):
        if isinstance(movement.get("to_position"), str) and movement["to_position"] not in ["F1", "F2", "F3", "D1", "D2", "C", "LW", "RW", "LD", "RD", "G"]:
            # This is a zone name, not a player position
            try:
                x, y = coordinate_mapper.get_area_coordinate(movement["to_position"])
                movement["to_position"] = [x, y]
            except KeyError:
                logger.warning(f"Unknown movement zone: {movement['to_position']}")
    
    return spec_data


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
                    {"position": "F1", "zone": "behind_net", "x": 0, "y": 95, "team": "home", "has_puck": False},
                    {"position": "F2", "zone": "right_corner", "x": 35, "y": 85, "team": "home", "has_puck": False},
                    {"position": "F3", "zone": "slot", "x": 0, "y": 75, "team": "home", "has_puck": False},
                    {"position": "LD", "zone": "neutral_left", "x": -25, "y": 15, "team": "home", "has_puck": False},
                    {"position": "RD", "zone": "neutral_right", "x": 25, "y": 15, "team": "home", "has_puck": False},
                    {"position": "D1", "zone": "behind_net", "x": 5, "y": 92, "team": "away", "has_puck": True}
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