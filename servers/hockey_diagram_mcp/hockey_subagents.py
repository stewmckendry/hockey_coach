"""
Hockey Diagram Subagents using OpenAI Agents SDK.

This module implements specialized subagents for the enhanced hockey diagram flow:
- FormationSynthesisAgent: Converts raw research into structured formation data
- ZoneMappingAgent: Maps formations to precise zone-based specifications

These subagents have native LLM capabilities and can be used as tools by the main agent.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from agents import Agent
    AGENTS_SDK_AVAILABLE = True
except ImportError:
    AGENTS_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)


class FormationSynthesisAgent:
    """
    Specialized agent for synthesizing hockey formation research into structured data.
    
    This agent takes raw research results from multiple sources and creates
    a structured formation specification that can be mapped to zones.
    """
    
    def __init__(self):
        """Initialize the formation synthesis agent."""
        if not AGENTS_SDK_AVAILABLE:
            logger.warning("OpenAI Agents SDK not available. Falling back to direct OpenAI API calls.")
            self.agent = None
            return
            
        self.agent = Agent(
            name="Formation Synthesis Specialist",
            instructions="""
You are an expert hockey tactics analyst specializing in synthesizing research into structured formation data.

## Your Mission
Convert raw research findings about hockey formations into precise, structured specifications that can be mapped to tactical diagrams.

## Input Format
You receive:
- Research results from multiple sources (tactics databases, videos, coaching manuals)
- Formation name or concept being researched

## Output Requirements
Create a structured JSON formation specification with exactly these fields:

### 1. name (string)
Clear, descriptive formation name (e.g., "2-1-2 Aggressive Forecheck", "Swedish Torpedo System")

### 2. description (string)
Comprehensive tactical description in 2-3 sentences explaining the formation's purpose and execution

### 3. players_involved (array of strings)
List of positions using standard notations. **CRITICAL**: Choose ONE system per formation and be consistent:

#### Position Notation Systems:

**A. Specific Positions** (use for structured systems, set plays, special teams):
- **Home Team**: C, RW, LW, LD, RD, G
- **Away Team**: X1, X2, X3, X4, X5, XG
- **When to use**: Power play units, penalty kill boxes, face-off formations, line-based systems
- **Example**: "1-3-1 Power Play" → ["C", "RW", "LW", "LD", "RD"]

**B. Tactical Roles** (use for systems, forechecking, breakouts):
- **Home Team**: F1, F2, F3, D1, D2, G
- **Away Team**: X1, X2, X3, X4, X5, XG  
- **When to use**: Forechecking systems, breakout patterns, tactical concepts where role matters more than position
- **Example**: "2-1-2 Forecheck" → ["F1", "F2", "F3", "D1", "D2"]

#### Selection Rules:
1. **Forechecking/Backchecking**: Use F1, F2, F3 (F1 = first forechecker, F2 = support, F3 = back-pressure)
2. **Breakouts**: Use F1, F2, F3 (F1 = outlet, F2 = support, F3 = stretch pass)
3. **Power Play Units**: Use C, RW, LW, LD, RD (specific positions matter)
4. **Penalty Kill**: Use tactical roles if system-based, positions if structured
5. **Face-offs**: Use C, RW, LW, LD, RD (position-specific responsibilities)
6. **Drills with Opposition**: Include X1-X5 for defending team

### 4. steps (array of strings)
Sequential execution steps (3-5 steps maximum). Each step should be one clear action.
Examples:
- "F1 pressures puck carrier behind the net"
- "F2 positions high slot for rebound"
- "D1 pinches down the boards"

### 5. primary_zone (string)
Main area of play - MUST be one of:
- "defensive" (own end, below goal line)
- "neutral" (center ice, between blue lines)  
- "offensive" (attacking end, above blue line)

### 6. key_concepts (array of strings)
List of 3-5 tactical concepts. Choose from:
**Pressure Concepts**: "forecheck pressure", "backcheck", "neutral zone pressure", "puck pursuit"
**Support Concepts**: "back pressure", "weak side support", "point coverage", "slot coverage"
**Movement Concepts**: "quick transition", "puck movement", "player rotation", "zone reloads"
**System Concepts**: "trap", "overload", "cycling", "screening", "net front presence"

## Hockey Expertise Standards
- Use proper hockey terminology and notation
- Consider standard NHL positioning and responsibilities
- Account for tactical principles (pressure, support, coverage)
- Ensure formations are tactically sound and executable
- Reference standard hockey systems when applicable

## Example Output
```json
{
  "name": "2-1-2 Aggressive Forecheck",
  "description": "High-pressure forechecking system with two forwards attacking the puck carrier while the third forward provides back-pressure support. Creates quick puck recovery opportunities in the offensive zone.",
  "players_involved": ["F1", "F2", "F3", "D1", "D2"],
  "steps": [
    "F1 pressures puck carrier behind the net",
    "F2 covers strong-side boards and support",
    "F3 provides back-pressure at blue line",
    "D1 and D2 maintain gap control at blue line"
  ],
  "primary_zone": "offensive",
  "key_concepts": ["forecheck pressure", "back pressure", "quick transition", "puck pursuit"]
}
```

## Additional Examples by Formation Type:

**Power Play (use specific positions):**
```json
{
  "name": "1-3-1 Umbrella Power Play",
  "players_involved": ["C", "RW", "LW", "LD", "RD"],
  "primary_zone": "offensive"
}
```

**Breakout (use tactical roles):**
```json
{
  "name": "D-to-D Breakout",
  "players_involved": ["F1", "F2", "F3", "D1", "D2"],
  "primary_zone": "defensive"
}
```

## Quality Requirements
- Be concise but comprehensive
- Focus on tactical essentials, not excessive detail
- Ensure all players have clear roles and responsibilities
- Validate that formation is practically executable
- Use consistent terminology throughout
- ALWAYS output valid JSON matching the exact structure above

Always format your response as valid JSON matching the exact structure specified above.
            """,
            model="gpt-4o"
        )
    
    async def synthesize_formation(
        self, 
        research_results: List[Dict[str, Any]], 
        formation_name: str
    ) -> Dict[str, Any]:
        """
        Synthesize research results into structured formation data.
        
        Args:
            research_results: List of research findings from search tools
            formation_name: Name of the formation being synthesized
            
        Returns:
            Dictionary containing structured formation data or error information
        """
        start_time = datetime.now()
        logger.info(f"SYNTHESIS SUBAGENT - Formation: {formation_name}")
        logger.info(f"SYNTHESIS SUBAGENT - Research sources: {len(research_results)}")
        
        try:
            if not self.agent:
                # Fallback to direct OpenAI API call
                return await self._fallback_synthesis(research_results, formation_name)
            
            # Prepare research context for the agent
            research_context = self._format_research_context(research_results, formation_name)
            
            # Use the subagent
            from agents import Runner
            
            result = await Runner.run(
                agent=self.agent,
                input=research_context,
                max_turns=3  # Limit turns for efficiency
            )
            
            # Parse the agent's response
            formation_data = json.loads(result.final_output)
            
            # Log synthesis output
            logger.info(f"SYNTHESIS SUBAGENT OUTPUT - Formation: {formation_data.get('name', 'Unknown')}")
            logger.info(f"SYNTHESIS SUBAGENT OUTPUT - Players: {formation_data.get('players_involved', [])}")
            logger.info(f"SYNTHESIS SUBAGENT OUTPUT - Primary zone: {formation_data.get('primary_zone', 'Unknown')}")
            
            generation_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"SYNTHESIS SUBAGENT PERFORMANCE - Time: {generation_time:.3f}s")
            
            return {
                "success": True,
                "formation_data": formation_data,
                "source_count": len(research_results),
                "generation_time": generation_time,
                "agent_type": "subagent",
                "next_tool": "map_formation_to_zones"
            }
            
        except Exception as e:
            logger.error(f"SYNTHESIS SUBAGENT ERROR: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "agent_type": "subagent"
            }
    
    def _format_research_context(self, research_results: List[Dict[str, Any]], formation_name: str) -> str:
        """Format research results into context for the agent."""
        research_text = "\n\n".join([
            f"Source: {r.get('source', 'Unknown')}\n{r.get('content', '')}"
            for r in research_results
        ])
        
        return f"""Please synthesize research about '{formation_name}' into structured formation data.

Research findings:
{research_text}

Create a JSON specification with: name, description, players_involved, steps, primary_zone, key_concepts"""
    
    async def _fallback_synthesis(self, research_results: List[Dict[str, Any]], formation_name: str) -> Dict[str, Any]:
        """Fallback to direct OpenAI API if Agents SDK not available."""
        from openai import OpenAI
        
        client = OpenAI()
        research_text = self._format_research_context(research_results, formation_name)
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a hockey tactics expert. Create structured formation data from research."},
                {"role": "user", "content": research_text}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        formation_data = json.loads(response.choices[0].message.content)
        
        return {
            "success": True,
            "formation_data": formation_data,
            "source_count": len(research_results),
            "agent_type": "fallback"
        }


class ZoneMappingAgent:
    """
    Specialized agent for mapping formations to zone-based diagram specifications.
    
    This agent converts high-level formation descriptions into precise zone
    mappings with all required entities for diagram generation.
    """
    
    def __init__(self):
        """Initialize the zone mapping agent."""
        if not AGENTS_SDK_AVAILABLE:
            logger.warning("OpenAI Agents SDK not available. Falling back to direct OpenAI API calls.")
            self.agent = None
            return
            
        self.agent = Agent(
            name="Zone Mapping Specialist", 
            instructions="""
You are an expert hockey zone mapping specialist who converts formation descriptions into precise zone-based diagram specifications using hockey-friendly zone labels.

## Your Mission
Transform structured formation data into complete zone-based diagram specifications with all entities mapped to NHL rink zones using descriptive labels (NOT numeric coordinates).

## Input Format
You receive structured formation data containing:
- Formation name and description
- List of players involved
- Sequential execution steps
- Primary zone of play
- Key tactical concepts

## Zone System Knowledge - Complete 32-Zone List
You work with a 32-zone NHL rink grid system. ONLY use these exact zone names:

**Defensive Zones (16 zones)**:
d-corner-left-high, d-circle-left-high, d-circle-right-high, d-corner-right-high,
d-behind-net-left, d-circle-left-center, d-circle-right-center, d-behind-net-right,
d-behind-net-left, d-circle-left-low, d-circle-right-low, d-behind-net-right,
d-corner-left-low, d-circle-left-boards, d-circle-right-boards, d-corner-right-low

**Neutral Zones (8 zones)**:
neutral-left-wing-high, neutral-right-wing-high, neutral-left-center-high, neutral-right-center-high,
neutral-left-center-low, neutral-right-center-low, neutral-left-wing-low, neutral-right-wing-low

**Offensive Zones (8 zones)**:
o-corner-left-high, o-point-left, o-high-slot-high, o-corner-right-high,
o-behind-net-left, o-point-center-left, o-slot-high, o-behind-net-right,
o-behind-net-left, o-point-center-right, o-slot-low, o-behind-net-right,
o-corner-left-low, o-point-right, o-low-slot, o-corner-right-low

## Output Requirements
Create a complete JSON diagram specification with exactly these fields:

### 1. PLAYERS Array (required)
For each player position, specify:
- **role**: Choose from position notation systems below. **CRITICAL**: Stay consistent with the formation_data input:

#### Position Notation Systems (match the input formation):

**A. Specific Positions** (for structured systems, set plays, special teams):
- **Home Team**: C, RW, LW, LD, RD, G
- **Away Team**: X1, X2, X3, X4, X5, XG
- **Use when**: Formation uses positional roles (power play, penalty kill, face-offs)

**B. Tactical Roles** (for systems, forechecking, breakouts):  
- **Home Team**: F1, F2, F3, D1, D2, G
- **Away Team**: X1, X2, X3, X4, X5, XG
- **Use when**: Formation uses tactical roles (forechecking, breakouts, systems)

**Selection Rule**: Use the SAME notation system as the input formation_data.players_involved

- **zone**: MUST be one of the 32 zone names listed above
- **offset**: Position adjustment within zone using DESCRIPTIVE terms:
  - **description**: MUST be one of: "center", "deep", "high", "near boards", "slot-side", "point-side", "wall-side", "net-front", "between-circles"
- **team**: MUST be "home", "away", or "practicing"
- **has_puck**: MUST be true or false
- **sequence**: Integer 1, 2, 3... for multi-step plays

### 2. MOVEMENTS Array (if include_movements=true)
For each movement, specify:
- **from**: Player role (e.g., "F1") or zone name
- **to**: Player role (e.g., "F2") or zone name
- **type**: MUST be one of: "pass", "skating", "skating_with_puck", "shot", "check", "support", "forechecking", "backchecking"
- **sequence**: Integer order of execution (1, 2, 3...)
- **style**: MUST be "dashed" (pass), "solid" (skating), "thick" (shot)

### 3. ZONES Array (if include_coverage=true)
For coverage areas, specify:
- **purpose**: MUST be one of: "pressure", "coverage", "support", "screening", "neutral_trap", "defensive_box", "offensive_overload"
- **areas**: Array of zone names from the 32-zone list
- **team**: MUST be "home" or "away"
- **opacity**: MUST be number between 0.1 and 0.5

### 4. METADATA (required)
- **category**: MUST be one of: "formation", "drill", "faceoff", "play", "system"
- **view**: MUST be one of: "full", "offensive", "defensive", "neutral"
- **title**: Clear descriptive title (string)
- **focus**: Primary tactical objective (string)

## Example Output

**Example 1: Tactical Roles (Forechecking System)**
```json
{
  "players": [
    {
      "role": "F1",
      "zone": "o-behind-net-left",
      "offset": {"description": "tight-to-net"},
      "team": "home",
      "has_puck": false,
      "sequence": 1
    },
    {
      "role": "F2", 
      "zone": "o-slot-high",
      "offset": {"description": "net-front"},
      "team": "home",
      "has_puck": false,
      "sequence": 1
    }
  ],
  "movements": [
    {
      "from": "F1",
      "to": "F2",
      "type": "pass",
      "sequence": 1,
      "style": "dashed"
    }
  ],
  "zones": [
    {
      "purpose": "pressure",
      "areas": ["o-behind-net-left", "o-corner-left-high"],
      "team": "home",
      "opacity": 0.3
    }
  ],
  "metadata": {
    "category": "formation",
    "view": "offensive",
    "title": "2-1-2 Forecheck",
    "focus": "High pressure puck recovery"
  }
}
```

**Example 2: Specific Positions (Power Play)**
```json
{
  "players": [
    {
      "role": "C",
      "zone": "o-low-slot",
      "offset": {"description": "net-front"},
      "team": "home",
      "has_puck": false,
      "sequence": 1
    },
    {
      "role": "RW",
      "zone": "o-corner-right-low",
      "offset": {"description": "boards-side"},
      "team": "home", 
      "has_puck": true,
      "sequence": 1
    }
  ],
  "metadata": {
    "category": "formation",
    "view": "offensive", 
    "title": "1-3-1 Umbrella Power Play",
    "focus": "Power play positioning"
  }
}
```

## Hockey Expertise Standards
- Use proper NHL positioning principles
- Ensure tactical soundness and execution flow
- Consider player spacing and support angles
- Account for puck movement and pressure concepts
- Validate zone selections make tactical sense
- Use only descriptive positioning terms, never numeric coordinates

## Quality Requirements
- All player positions must use valid zone names from the 32-zone list
- Movement arrows must connect logically between players/zones
- Coverage zones should support tactical objective
- Offset descriptions must be hockey-appropriate descriptive terms
- Ensure diagram will be visually clear and instructive
- NEVER use numeric coordinates - only zone labels and descriptive offsets

Always format your response as valid JSON matching the exact structure specified above.
            """,
            model="gpt-4o"
        )
    
    async def map_to_zones(
        self, 
        formation_data: Dict[str, Any],
        include_movements: bool = True,
        include_coverage: bool = True
    ) -> Dict[str, Any]:
        """
        Map structured formation data to zone-based diagram specification.
        
        Args:
            formation_data: Structured formation from synthesis agent
            include_movements: Whether to generate movement arrows
            include_coverage: Whether to generate coverage zones
            
        Returns:
            Complete diagram specification with all entities mapped
        """
        start_time = datetime.now()
        logger.info(f"ZONE MAPPING SUBAGENT - Formation: {formation_data.get('name', 'Unknown')}")
        logger.info(f"ZONE MAPPING SUBAGENT - Include movements: {include_movements}")
        logger.info(f"ZONE MAPPING SUBAGENT - Include coverage: {include_coverage}")
        
        try:
            if not self.agent:
                # Fallback to direct OpenAI API call
                return await self._fallback_zone_mapping(formation_data, include_movements, include_coverage)
            
            # Prepare formation context for the agent
            mapping_context = self._format_mapping_context(formation_data, include_movements, include_coverage)
            
            # Use the subagent
            from agents import Runner
            
            result = await Runner.run(
                agent=self.agent,
                input=mapping_context,
                max_turns=3  # Limit turns for efficiency
            )
            
            # Parse the agent's response
            diagram_spec = json.loads(result.final_output)
            
            # Log zone mapping output
            players = diagram_spec.get('players', [])
            movements = diagram_spec.get('movements', [])
            zones = diagram_spec.get('zones', [])
            
            logger.info(f"ZONE MAPPING SUBAGENT OUTPUT - Players mapped: {len(players)}")
            logger.info(f"ZONE MAPPING SUBAGENT OUTPUT - Movements: {len(movements)}")
            logger.info(f"ZONE MAPPING SUBAGENT OUTPUT - Coverage zones: {len(zones)}")
            
            generation_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"ZONE MAPPING SUBAGENT PERFORMANCE - Time: {generation_time:.3f}s")
            
            return {
                "success": True,
                "diagram_spec": diagram_spec,
                "player_count": len(players),
                "movement_count": len(movements),
                "zone_count": len(zones),
                "generation_time": generation_time,
                "agent_type": "subagent",
                "next_tool": "generate_diagram_from_spec"
            }
            
        except Exception as e:
            logger.error(f"ZONE MAPPING SUBAGENT ERROR: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "agent_type": "subagent"
            }
    
    def _format_mapping_context(self, formation_data: Dict[str, Any], include_movements: bool, include_coverage: bool) -> str:
        """Format formation data into context for the agent."""
        from zone_grid_hockey_names import HOCKEY_ZONES
        
        # Get available zones
        zone_list = "\n".join([f"- {name}: {desc}" for name, desc in HOCKEY_ZONES.items()])
        
        return f"""Please map this formation to precise zone-based diagram specification.

Formation Data:
- Name: {formation_data.get('name')}
- Description: {formation_data.get('description')}
- Players: {', '.join(formation_data.get('players_involved', []))}
- Steps: {json.dumps(formation_data.get('steps', []), indent=2)}
- Primary Zone: {formation_data.get('primary_zone')}
- Key Concepts: {formation_data.get('key_concepts', [])}

Include Movements: {include_movements}
Include Coverage Zones: {include_coverage}

Available zones to choose from:
{zone_list}

Create a complete JSON diagram specification with players, movements (if requested), zones (if requested), and metadata."""
    
    async def _fallback_zone_mapping(self, formation_data: Dict[str, Any], include_movements: bool, include_coverage: bool) -> Dict[str, Any]:
        """Fallback to direct OpenAI API if Agents SDK not available."""
        from openai import OpenAI
        
        client = OpenAI()
        mapping_context = self._format_mapping_context(formation_data, include_movements, include_coverage)
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a hockey zone mapping expert. Create precise zone-based specifications."},
                {"role": "user", "content": mapping_context}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        diagram_spec = json.loads(response.choices[0].message.content)
        
        return {
            "success": True,
            "diagram_spec": diagram_spec,
            "agent_type": "fallback"
        }


# Global instances
formation_synthesis_agent = FormationSynthesisAgent()
zone_mapping_agent = ZoneMappingAgent()


def get_synthesis_agent() -> FormationSynthesisAgent:
    """Get the formation synthesis agent instance."""
    return formation_synthesis_agent


def get_zone_mapping_agent() -> ZoneMappingAgent:
    """Get the zone mapping agent instance."""  
    return zone_mapping_agent


def create_subagent_tools():
    """
    Create subagent tools for the main hockey diagram agent.
    
    Returns:
        List of agent tools that can be used by the main agent
    """
    if not AGENTS_SDK_AVAILABLE:
        logger.warning("OpenAI Agents SDK not available. Cannot create subagent tools.")
        return []
    
    tools = []
    
    # Add synthesis agent as tool
    if formation_synthesis_agent.agent:
        synthesis_tool = formation_synthesis_agent.agent.as_tool(
            tool_name="synthesize_research_to_formation",
            tool_description="Synthesize raw research results into structured hockey formation data. Takes research findings and formation name, returns structured formation specification.",
        )
        tools.append(synthesis_tool)
    
    # Add zone mapping agent as tool  
    if zone_mapping_agent.agent:
        zone_mapping_tool = zone_mapping_agent.agent.as_tool(
            tool_name="map_formation_to_zones", 
            tool_description="Map structured formation data to precise zone-based diagram specification. Takes formation data and options, returns complete diagram specification with all entities.",
        )
        tools.append(zone_mapping_tool)
    
    return tools


# Export for backward compatibility
__all__ = [
    'FormationSynthesisAgent',
    'ZoneMappingAgent', 
    'formation_synthesis_agent',
    'zone_mapping_agent',
    'get_synthesis_agent',
    'get_zone_mapping_agent',
    'create_subagent_tools',
    'AGENTS_SDK_AVAILABLE'
]