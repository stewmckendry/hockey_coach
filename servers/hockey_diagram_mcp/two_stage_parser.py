"""
Two-Stage Hockey Diagram Parser with comprehensive pick list definitions.

This parser improves accuracy by using a two-stage approach:
1. Stage 1: Extract general structure and identify key elements
2. Stage 2: Make specific choices from clearly defined pick lists

Every value in pick lists includes clear definitions so the LLM knows exactly when to use each option.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import os
from coordinate_mapper import coordinate_mapper, Zone
from agents.tracing import custom_span, generation_span

logger = logging.getLogger(__name__)

# Define pick list types with comprehensive definitions
MovementType = Literal[
    "pass", "skating", "skating_with_puck", "shot", "check", "support", 
    "forechecking", "backchecking", "clearing", "screening"
]

PlayerRole = Literal[
    "C", "RW", "LW", "LD", "RD", "G",  # Home team
    "F1", "F2", "F3", "D1", "D2",     # Tactical roles
    "X1", "X2", "X3", "X4", "X5", "XG"  # Away team
]

LocationName = Literal[
    "slot", "high_slot", "low_slot", "left_point", "right_point", 
    "left_half_wall", "right_half_wall", "left_corner", "right_corner",
    "behind_net", "goal_crease", "left_circle", "right_circle",
    "neutral_zone", "center_ice", "left_boards", "right_boards"
]

ZonePurpose = Literal[
    "pressure", "coverage", "support", "screening", "neutral_trap",
    "power_play_setup", "penalty_kill_box", "faceoff_alignment"
]

TeamDesignation = Literal["home", "away", "practicing"]

ViewType = Literal["full", "offensive", "defensive", "neutral"]

DiagramCategory = Literal["formation", "drill", "faceoff", "play", "system"]

class PlayerAction(BaseModel):
    """A player's action in a specific step."""
    player_role: str = Field(..., description="Role identifier (e.g., 'defender', 'forward', 'center')")
    location: str = Field(..., description="Named location (e.g., 'left_circle', 'high_slot')")
    action: str = Field(..., description="What the player does (e.g., 'pass', 'receive', 'skate')")
    has_puck: bool = Field(False, description="Whether player has puck at this moment")

class StepBreakdown(BaseModel):
    """Detailed breakdown of a single step in a drill or play."""
    step_number: int = Field(..., description="Sequential step number")
    description: str = Field(..., description="Brief description of what happens")
    player_actions: List[PlayerAction] = Field(..., description="What each player does")
    movements: List[str] = Field(default_factory=list, description="Movement descriptions")

class StructureAnalysis(BaseModel):
    """Stage 1: Enhanced structure analysis with procedural breakdown."""
    diagram_category: DiagramCategory = Field(..., description="Primary category of this diagram")
    primary_focus: str = Field(..., description="Main focus or objective")
    
    # For static formations
    formation_positions: Optional[Dict[str, str]] = Field(None, description="Static positions by role")
    
    # For drills and plays - procedural breakdown
    steps: Optional[List[StepBreakdown]] = Field(None, description="Sequential steps for drills/plays")
    
    # For coverage systems
    coverage_zones: Optional[Union[List[Dict[str, str]], Dict[str, str]]] = Field(None, description="Zone assignments")
    
    # General info
    total_players: int = Field(..., description="Total unique players involved")
    teams_involved: List[str] = Field(..., description="Teams: ['practicing'], ['home', 'away'], etc.")

class PlayerPosition(BaseModel):
    """Structured player position with role definitions."""
    position: PlayerRole = Field(..., description="Player position/role")
    zone: Optional[str] = Field(None, description="Named zone location (e.g., 'slot', 'left_circle')")
    x: Optional[float] = Field(None, description="X coordinate on rink (-100 to 100)")
    y: Optional[float] = Field(None, description="Y coordinate on rink (-42.5 to 42.5)")
    team: TeamDesignation = Field(..., description="Team designation")
    has_puck: bool = Field(False, description="Whether this player has the puck")
    step: Optional[int] = Field(None, description="Sequence step for drills (1, 2, 3, etc.)")

class MovementSpec(BaseModel):
    """Movement specification with clear type definitions."""
    from_position: PlayerRole = Field(..., description="Starting position (player role)")
    to_position: Union[PlayerRole, List[float]] = Field(..., description="End position (player role or [x, y] coordinates)")
    movement_type: MovementType = Field(..., description="Type of movement")
    sequence: Optional[int] = Field(None, description="Step number in sequence")
    arrow_style: Literal["solid", "dashed", "dotted", "thick"] = Field("solid", description="Arrow visualization style")

class ZoneSpec(BaseModel):
    """Zone specification with purpose definitions."""
    zone_type: ZonePurpose = Field(..., description="Purpose of this zone")
    area: Union[LocationName, List[float]] = Field(..., description="Named area or [x, y, width, height]")
    team: TeamDesignation = Field(..., description="Team controlling zone")
    opacity: float = Field(0.2, description="Zone shading opacity (0.1 to 0.5)")

class DiagramSpec(BaseModel):
    """Complete two-stage diagram specification."""
    players: List[PlayerPosition]
    movements: Optional[List[MovementSpec]] = []
    zones: Optional[List[ZoneSpec]] = []
    view: ViewType = Field("full", description="Diagram view type")
    title: Optional[str] = None
    diagram_type: DiagramCategory = Field("formation", description="Category of diagram")

class TwoStageHockeyParser:
    """Two-stage parser with comprehensive pick list definitions."""
    
    def _get_zone_aware_locations(self, context_zone: str = "full") -> Dict[str, str]:
        """
        Generate zone-aware location definitions using coordinate_mapper.
        
        Args:
            context_zone: The zone context (defensive, offensive, neutral, full)
            
        Returns:
            Dictionary of location names to coordinate descriptions
        """
        locations = {}
        
        # Determine which coordinate set to use based on context
        if context_zone == "defensive":
            # Use defensive zone coordinates (negative X)
            locations.update({
                "slot": "High-danger defensive area directly in front of own net (-75, 0)",
                "high_slot": "Area between faceoff circles in defensive zone (-50, 0)", 
                "low_slot": "Area between goal line and bottom of circles in defensive zone (-80, 0)",
                "left_point": "Blue line position on left side for defenseman (-25, -30)",
                "right_point": "Blue line position on right side for defenseman (-25, 30)",
                "left_half_wall": "Halfway between goal line and blue line on left boards (-60, -35)",
                "right_half_wall": "Halfway between goal line and blue line on right boards (-60, 35)",
                "left_corner": "Corner area behind goal line on left side (-85, -35)",
                "right_corner": "Corner area behind goal line on right side (-85, 35)",
                "behind_net": "Area directly behind own goal (-95, 0)",
                "goal_crease": "Protected area in front of own goal (-89, 0)",
                "left_circle": "Faceoff circle on left side in defensive zone (-69, -22.5)",
                "right_circle": "Faceoff circle on right side in defensive zone (-69, 22.5)",
            })
        elif context_zone == "offensive":
            # Use offensive zone coordinates (positive X)
            locations.update({
                "slot": "High-danger scoring area directly in front of opponent net (75, 0)",
                "high_slot": "Area between faceoff circles at top of circles in offensive zone (50, 0)", 
                "low_slot": "Area between goal line and bottom of circles in offensive zone (85, 0)",
                "left_point": "Blue line position on left side for defenseman (25, -30)",
                "right_point": "Blue line position on right side for defenseman (25, 30)",
                "left_half_wall": "Halfway between goal line and blue line on left boards (60, -35)",
                "right_half_wall": "Halfway between goal line and blue line on right boards (60, 35)",
                "left_corner": "Corner area behind goal line on left side (85, -35)",
                "right_corner": "Corner area behind goal line on right side (85, 35)",
                "behind_net": "Area directly behind opponent goal (95, 0)",
                "goal_crease": "Protected area in front of opponent goal (89, 0)",
                "left_circle": "Faceoff circle on left side in offensive zone (69, -22.5)",
                "right_circle": "Faceoff circle on right side in offensive zone (69, 22.5)",
            })
        else:
            # Use neutral or generic locations
            locations.update({
                "slot": "High-danger area in front of goal (defensive: -75, offensive: 75)",
                "high_slot": "Area between faceoff circles (defensive: -50, offensive: 50)", 
                "low_slot": "Area between goal line and circles (defensive: -80, offensive: 85)",
                "left_point": "Blue line position on left side (defensive: -25, offensive: 25, Y: -30)",
                "right_point": "Blue line position on right side (defensive: -25, offensive: 25, Y: 30)",
                "left_half_wall": "Halfway between goal line and blue line on left boards (Y: -35)",
                "right_half_wall": "Halfway between goal line and blue line on right boards (Y: 35)",
                "left_corner": "Corner area behind goal line on left side (X: ±85, Y: -35)",
                "right_corner": "Corner area behind goal line on right side (X: ±85, Y: 35)",
                "behind_net": "Area directly behind the goal (X: ±95, Y: 0)",
                "goal_crease": "Protected area in front of goal (X: ±89, Y: 0)",
                "left_circle": "Faceoff circle on left side (X: ±69, Y: -22.5)",
                "right_circle": "Faceoff circle on right side (X: ±69, Y: 22.5)",
            })
        
        # Add zone-neutral locations
        locations.update({
            "neutral_zone": "Area between the two blue lines (-25 to 25)",
            "center_ice": "Center of rink where game starts (0, 0)",
            "left_boards": "Along the left side boards (-42.5 Y coordinate)",
            "right_boards": "Along the right side boards (42.5 Y coordinate)"
        })
        
        return locations
    
    # Comprehensive definitions for all pick list values
    DEFINITIONS = {
        "movement_types": {
            "pass": "When the puck is sent from one player to another (dashed arrow)",
            "skating": "When a player moves to a new position without the puck (solid arrow)",
            "skating_with_puck": "When a player carries the puck to a new position (solid arrow with puck indicator)",
            "shot": "When a player shoots at the goal (thick arrow)",
            "check": "When a player moves to body-check an opponent (curved arrow)",
            "support": "When a player moves to provide passing option (dotted arrow)",
            "forechecking": "Aggressive pressure in opponent's defensive zone",
            "backchecking": "Defensive tracking back towards own zone",
            "clearing": "Moving puck out of dangerous area",
            "screening": "Positioning to block goalie's view"
        },
        
        "player_roles": {
            "C": "Center - primary playmaker, takes faceoffs",
            "RW": "Right Wing - right side forward",
            "LW": "Left Wing - left side forward", 
            "LD": "Left Defense - left side defenseman",
            "RD": "Right Defense - right side defenseman",
            "G": "Goaltender - goalie in net",
            "F1": "First Forward - first forechecker, applies pressure",
            "F2": "Second Forward - support forechecker, covers pass lanes",
            "F3": "Third Forward - high forward, covers middle",
            "D1": "First Defense - usually left side defenseman",
            "D2": "Second Defense - usually right side defenseman",
            "X1": "Opposing Player 1 - first opponent",
            "X2": "Opposing Player 2 - second opponent",
            "X3": "Opposing Player 3 - third opponent", 
            "X4": "Opposing Player 4 - fourth opponent",
            "X5": "Opposing Player 5 - fifth opponent",
            "XG": "Opposing Goaltender - opponent's goalie"
        },
        
        # Note: locations will be dynamically generated based on context zone
        
        "zone_purposes": {
            "pressure": "Aggressive pressure to force turnovers or poor decisions",
            "coverage": "Defensive positioning to cover dangerous areas",
            "support": "Positioning to provide passing or shooting options",
            "screening": "Blocking opponent's view or movement",
            "neutral_trap": "Defensive system to force turnovers in neutral zone",
            "power_play_setup": "Formation to create scoring chances with man advantage",
            "penalty_kill_box": "Defensive formation when short-handed",
            "faceoff_alignment": "Positioning for faceoff situations"
        },
        
        "team_designations": {
            "home": "Main team being coached (usually in colored jerseys)",
            "away": "Opposing team (usually marked with X's)",
            "practicing": "Team in practice/drill situation (all same team)"
        },
        
        "view_types": {
            "full": "Complete rink view showing all zones",
            "offensive": "Focus on offensive zone (25 to 100 X coordinates)",
            "defensive": "Focus on defensive zone (-100 to -25 X coordinates)", 
            "neutral": "Focus on neutral zone (-25 to 25 X coordinates)"
        },
        
        "diagram_categories": {
            "formation": "Static positioning showing tactical setup",
            "drill": "Practice exercise with step-by-step progression",
            "faceoff": "Specific faceoff positioning and responsibilities",
            "play": "Tactical sequence from start to finish",
            "system": "Overall team system or strategy"
        }
    }
    
    STAGE_1_PROMPT = """You are analyzing a hockey coaching instruction to create a structured breakdown.

Your job is to extract the PROCEDURAL CONTENT, not just metadata. Break down the instruction into:
- WHO is involved (players/roles)
- WHAT they do (actions)
- WHERE they are positioned (using hockey location names)
- WHEN it happens (sequence/steps for drills)

DIAGRAM CATEGORIES:
- "formation": Static positioning (use formation_positions)
- "drill": Practice with steps (use steps array)
- "play": Tactical sequence (use steps array)
- "system": Coverage system (use coverage_zones)
- "faceoff": Faceoff setup (use formation_positions)

LOCATION NAMES (use these exact terms):
- Zones: slot, high_slot, low_slot, left_point, right_point
- Circles: left_circle, right_circle, center_ice
- Boards: left_boards, right_boards, left_corner, right_corner
- Special: behind_net, goal_crease, neutral_zone
- Hash marks: left_hash, right_hash

For DRILLS, create detailed steps:
{
    "diagram_category": "drill",
    "primary_focus": "1v1 defensive technique",
    "steps": [
        {
            "step_number": 1,
            "description": "Initial pass",
            "player_actions": [
                {"player_role": "defender", "location": "left_circle", "action": "pass", "has_puck": true},
                {"player_role": "forward", "location": "left_hash", "action": "receive", "has_puck": false}
            ],
            "movements": ["Pass from defender to forward"]
        }
    ],
    "total_players": 2,
    "teams_involved": ["practicing"]
}

For FORMATIONS, use positions:
{
    "diagram_category": "formation",
    "primary_focus": "2-1-2 forecheck pressure",
    "formation_positions": {
        "F1": "behind_net",
        "F2": "left_boards",
        "F3": "right_boards",
        "D1": "left_point",
        "D2": "right_point"
    },
    "total_players": 5,
    "teams_involved": ["home"]
}

Output complete JSON with the appropriate structure for the diagram type."""

    STAGE_2_PROMPT = """You are translating a structured hockey analysis into diagram specifications.

Your ONLY job is to:
1. Map player roles to position codes
2. Assign movement types from the pick list
3. Specify zones using standard names
4. Maintain step sequences for drills

PLAYER POSITION MAPPING:
- "defender/defense" → D1, D2
- "forward/attacker" → F1, F2, F3
- "center" → C
- "right wing" → RW
- "left wing" → LW
- "left defense" → LD
- "right defense" → RD
- "goalie/goaltender" → G
- "opponent/opposing" → X1, X2, X3, X4, X5, XG

MOVEMENT TYPE MAPPING:
- "pass/passes/passing" → "pass"
- "skate/skates/skating" → "skating" (without puck) or "skating_with_puck" (with puck)
- "shoot/shot/shooting" → "shot"
- "check/hit/body contact" → "check"
- "support/help" → "support"
- "pressure/forecheck" → "forechecking"
- "backcheck/track back" → "backchecking"

ZONE NAMES (use exactly):
slot, high_slot, low_slot, left_point, right_point, left_half_wall, right_half_wall,
left_corner, right_corner, behind_net, goal_crease, left_circle, right_circle,
neutral_zone, center_ice, left_boards, right_boards, left_hash, right_hash

TEAM ASSIGNMENTS:
- For drills: everyone is "practicing"
- For formations: use "home" for main team
- For systems: use "home" and "away" as needed

ZONE PURPOSES (for coverage systems):
- "pressure", "coverage", "support", "screening"
- "neutral_trap", "power_play_setup", "penalty_kill_box", "faceoff_alignment"

OUTPUT FORMAT:
For each player, specify:
- "position": mapped position code (D1, F1, etc.)
- "zone": named zone location (slot, left_circle, etc.)
- "team": appropriate team designation
- "has_puck": true/false
- "step": step number for drills

For movements:
- "from_position": starting player code (D1, F1, etc.)
- "to_position": ending player code (D1, F1, etc.) - NOT zone names
- "movement_type": from pick list
- "sequence": step number

IMPORTANT: Movement arrows go between PLAYERS, not to zones.
If a player moves to a zone, show their starting and ending POSITIONS.

Example output:
{
    "players": [
        {"position": "D1", "zone": "left_circle", "team": "practicing", "has_puck": true, "step": 1},
        {"position": "F1", "zone": "left_hash", "team": "practicing", "has_puck": false, "step": 1}
    ],
    "movements": [
        {"from_position": "D1", "to_position": "F1", "movement_type": "pass", "sequence": 1}
    ],
    "view": "defensive",
    "title": "1v1 Defensive Drill",
    "diagram_type": "drill"
}"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize two-stage parser."""
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def parse_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> DiagramSpec:
        """
        Parse using two-stage approach with comprehensive definitions.
        
        Args:
            prompt: Natural language hockey instruction
            context: Additional context (age_group, etc.)
            
        Returns:
            DiagramSpec with accurate, well-defined choices
        """
        try:
            # Stage 1: Analyze structure
            structure = await self._stage_1_analysis(prompt, context)
            logger.info(f"Stage 1 analysis: {structure.diagram_category}, {structure.total_players} players")
            
            # Stage 2: Create precise diagram with definitions
            diagram_spec = await self._stage_2_creation(prompt, structure, context)
            logger.info(f"Stage 2 creation: {diagram_spec.title}")
            
            # Post-process to convert zones to coordinates
            diagram_spec = self._apply_coordinate_mapping(diagram_spec)
            
            # Add trace information to diagram spec as a custom attribute
            diagram_spec._traces = {
                "stage_1": {
                    "category": structure.diagram_category,
                    "total_players": structure.total_players,
                    "teams": structure.teams_involved,
                    "focus": structure.primary_focus,
                    "has_steps": bool(structure.steps),
                    "step_count": len(structure.steps) if structure.steps else 0
                },
                "stage_2": {
                    "title": diagram_spec.title,
                    "player_count": len(diagram_spec.players),
                    "movement_count": len(diagram_spec.movements) if diagram_spec.movements else 0,
                    "zone_count": len(diagram_spec.zones) if diagram_spec.zones else 0,
                    "view": diagram_spec.view
                },
                "coordinate_mapping": {
                    "players_mapped": len(diagram_spec.players),
                    "movements_mapped": len(diagram_spec.movements) if diagram_spec.movements else 0
                }
            }
            
            return diagram_spec
            
        except Exception as e:
            logger.error(f"Two-stage parsing failed: {e}")
            return self._create_fallback_diagram(prompt)
    
    async def _stage_1_analysis(self, prompt: str, context: Optional[Dict] = None) -> StructureAnalysis:
        """Stage 1: Analyze the structure and requirements."""
        with custom_span("stage_1_analysis", data={"prompt_length": len(prompt)}):
            enhanced_prompt = prompt
            if context:
                enhanced_prompt += f"\n\nContext: {context}"
            
            # Use generation_span for LLM call
            messages = [
                {"role": "system", "content": self.STAGE_1_PROMPT},
                {"role": "user", "content": enhanced_prompt}
            ]
            
            with generation_span(
                input=messages,
                model="gpt-4",
                model_config={"temperature": 0.1, "max_tokens": 1500}
            ) as gen_span:
                response = await self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=1500  # Increased to handle detailed procedural breakdowns
                )
                
                # Update generation span with usage
                if response.usage:
                    gen_span.span_data.usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
            
            json_text = self._extract_json(response.choices[0].message.content)
            data = json.loads(json_text)
            
            # Store structured trace data
            self._stage_1_trace = {
                "category": data.get("diagram_category"),
                "total_players": data.get("total_players"),
                "has_steps": bool(data.get("steps")),
                "step_count": len(data.get("steps", [])),
                "teams": data.get("teams_involved", [])
            }
            
            return StructureAnalysis(**data)
    
    async def _stage_2_creation(self, prompt: str, structure: StructureAnalysis, context: Optional[Dict] = None) -> DiagramSpec:
        """Stage 2: Create precise diagram with defined pick lists."""
        with custom_span("stage_2_creation", data={
            "category": structure.diagram_category,
            "total_players": structure.total_players
        }):
            # Determine zone context for location definitions
            context_zone = "full"
            if context and "requested_view" in context:
                context_zone = context["requested_view"]
            elif "defensive" in prompt.lower() or "penalty kill" in prompt.lower() or "box formation" in prompt.lower():
                context_zone = "defensive"
            elif "offensive" in prompt.lower() or "power play" in prompt.lower() or "cycle" in prompt.lower():
                context_zone = "offensive"
            elif "neutral" in prompt.lower() or "trap" in prompt.lower():
                context_zone = "neutral"
        
        # Build enhanced prompt based on diagram category
        enhanced_prompt = f"""
Original instruction: {prompt}

Structure analysis:
- Category: {structure.diagram_category}
- Focus: {structure.primary_focus}
- Total players: {structure.total_players}
- Teams: {', '.join(structure.teams_involved)}
"""
        
        # Add specific content based on diagram type
        if structure.diagram_category == "drill" and structure.steps:
            # Handle drill with procedural steps
            enhanced_prompt += f"\n\nDrill Steps ({len(structure.steps)} total):\n"
            for step in structure.steps:
                enhanced_prompt += f"\nStep {step.step_number}: {step.description}\n"
                enhanced_prompt += "  Player Actions:\n"
                for action in step.player_actions:
                    enhanced_prompt += f"    - {action.player_role} at {action.location}: {action.action}"
                    if action.has_puck:
                        enhanced_prompt += " (has puck)"
                    enhanced_prompt += "\n"
                if step.movements:
                    enhanced_prompt += f"  Movements: {', '.join(step.movements)}\n"
        
        elif structure.diagram_category == "formation" and structure.formation_positions:
            # Handle static formation
            enhanced_prompt += f"\n\nFormation Positions:\n"
            for role, position in structure.formation_positions.items():
                enhanced_prompt += f"  - {role}: {position}\n"
        
        elif structure.diagram_category == "system" and structure.coverage_zones:
            # Handle coverage system
            enhanced_prompt += f"\n\nCoverage Zones:\n"
            if isinstance(structure.coverage_zones, dict):
                # Handle dict format
                for role, zone in structure.coverage_zones.items():
                    enhanced_prompt += f"  - {role}: {zone}\n"
            else:
                # Handle list format
                for zone_info in structure.coverage_zones:
                    enhanced_prompt += f"  - {zone_info}\n"
        
        elif structure.diagram_category == "play":
            # Handle play/system
            if structure.steps:
                enhanced_prompt += f"\n\nPlay Sequence ({len(structure.steps)} steps):\n"
                for step in structure.steps:
                    enhanced_prompt += f"\nStep {step.step_number}: {step.description}\n"
            else:
                enhanced_prompt += f"\n\nPlay/System Description:\n"
                enhanced_prompt += f"  Primary focus: {structure.primary_focus}\n"
        
        if context:
            enhanced_prompt += f"\n\nAdditional context: {context}"
            
        enhanced_prompt += f"""

Based on the structured analysis above, create a diagram specification.

For drills with multiple steps:
- Show the MOST IMPORTANT step (usually the final competitive phase)
- Use movements to show key transitions
- Focus on the main learning objective

Use zone names from the pick list below, NOT coordinates.
"""
            
        # Use generation_span for Stage 2 LLM call
        messages = [
            {"role": "system", "content": self.STAGE_2_PROMPT},
            {"role": "user", "content": enhanced_prompt}
        ]
        
        with generation_span(
            input=messages,
            model="gpt-4",
            model_config={"temperature": 0.1, "max_tokens": 2000}
        ) as gen_span:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            # Update generation span with usage
            if response.usage:
                gen_span.span_data.usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            json_text = self._extract_json(response.choices[0].message.content)
            data = json.loads(json_text)
            
            # Post-process for accuracy
            data = self._validate_and_correct(data, structure, context_zone)
            
            # Store Stage 2 trace data
            self._stage_2_trace = {
                "title": data.get("title"),
                "player_count": len(data.get("players", [])),
                "movement_count": len(data.get("movements", [])),
                "view": data.get("view", "full")
            }
            
            return DiagramSpec(**data)
    
    def _apply_coordinate_mapping(self, diagram_spec: DiagramSpec) -> DiagramSpec:
        """Apply coordinate mapping to convert zone names to x,y coordinates."""
        # Convert zone names to coordinates for all players
        for player in diagram_spec.players:
            if player.zone and not (player.x and player.y):
                # Try to get area coordinate first
                try:
                    x, y = coordinate_mapper.get_area_coordinate(player.zone)
                    player.x = x
                    player.y = y
                    logger.debug(f"Mapped {player.position} zone '{player.zone}' to ({player.x}, {player.y})")
                except (KeyError, ValueError):
                    # If area lookup fails, use default position
                    logger.warning(f"Zone '{player.zone}' not found, using default position")
                    player.x = 0
                    player.y = 0
        
        return diagram_spec
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from response text."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        
        # Find JSON boundaries
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return text[start:end]
        return text
    
    def _validate_and_correct(self, data: Dict, structure: StructureAnalysis, context_zone: str = "full") -> Dict:
        """Validate and correct data against pick list definitions."""
        # Ensure diagram_type matches structure analysis
        data["diagram_type"] = structure.diagram_category
        
        # Validate player positions
        if "players" in data:
            for player in data["players"]:
                # Ensure coordinates are in bounds
                player["x"] = max(-100, min(100, player.get("x", 0)))
                player["y"] = max(-42.5, min(42.5, player.get("y", 0)))
                
                # Validate position against pick list
                if player.get("position") not in self.DEFINITIONS["player_roles"]:
                    logger.warning(f"Invalid position: {player.get('position')}, defaulting to C")
                    player["position"] = "C"
                
                # Validate team designation
                if player.get("team") not in ["home", "away", "practicing"]:
                    player["team"] = "home"
                    
            # Apply team separation logic to prevent player overlap
            self._apply_team_separation(data["players"])
        
        # Validate movements
        if "movements" in data:
            valid_movements = []
            player_positions = {p["position"]: (p["x"], p["y"]) for p in data.get("players", [])}
            
            for movement in data["movements"]:
                # Validate movement type
                if movement.get("movement_type") not in self.DEFINITIONS["movement_types"]:
                    # Check if it's a zone purpose being used as movement
                    if movement.get("movement_type") in self.DEFINITIONS["zone_purposes"]:
                        # Convert zone purpose to appropriate movement
                        zone_to_movement = {
                            "coverage": "skating",
                            "pressure": "forechecking",
                            "support": "support",
                            "screening": "screening"
                        }
                        new_type = zone_to_movement.get(movement["movement_type"], "skating")
                        logger.warning(f"Converting zone purpose '{movement.get('movement_type')}' to movement type '{new_type}'")
                        movement["movement_type"] = new_type
                    else:
                        logger.warning(f"Invalid movement type: {movement.get('movement_type')}, defaulting to skating")
                        movement["movement_type"] = "skating"
                
                # Handle zone names in to_position
                to_pos = movement.get("to_position")
                if to_pos and isinstance(to_pos, str) and to_pos not in self.DEFINITIONS["player_roles"]:
                    # It's a zone name, not a player position
                    # For now, remove these movements as they need different handling
                    logger.info(f"Removing zone-based movement: {movement.get('from_position')} → {to_pos}")
                    continue
                
                # Validate movement shows actual position change
                if self._is_valid_movement(movement, player_positions):
                    valid_movements.append(movement)
                else:
                    logger.info(f"Filtered out redundant movement: {movement.get('from_position')} → {movement.get('to_position')}")
            
            data["movements"] = valid_movements
        
        # Validate zones
        if "zones" in data:
            for zone in data["zones"]:
                # Validate zone type
                if zone.get("zone_type") not in self.DEFINITIONS["zone_purposes"]:
                    logger.warning(f"Invalid zone type: {zone.get('zone_type')}, defaulting to coverage")
                    zone["zone_type"] = "coverage"
                
                # Validate area if it's a named location
                # Note: locations are dynamically generated, so we'll skip validation here
                # The coordinate mapper will handle invalid locations
                pass
        
        # Set title if not provided
        if not data.get("title"):
            data["title"] = f"{structure.diagram_category.title()}: {structure.primary_focus}"
        
        # Apply coordinate mapping corrections
        data = self._apply_coordinate_mapping_dict(data, context_zone)
        
        return data
    
    def _apply_coordinate_mapping_dict(self, data: Dict, context_zone: str) -> Dict:
        """
        Apply coordinate mapper corrections for zone-aware positioning.
        
        Args:
            data: Diagram data dictionary
            context_zone: Zone context (defensive, offensive, neutral, full)
            
        Returns:
            Corrected data with accurate coordinates
        """
        if "players" not in data:
            return data
        
        # Map zone context to coordinate mapper Zone enum
        zone_map = {
            "defensive": Zone.DEFENSIVE,
            "offensive": Zone.OFFENSIVE, 
            "neutral": Zone.NEUTRAL,
            "full": Zone.NEUTRAL  # Default to neutral for full view
        }
        
        target_zone = zone_map.get(context_zone, Zone.NEUTRAL)
        
        for player in data["players"]:
            position = player.get("position", "C")
            
            # If player coordinates seem wrong for the zone, correct them
            current_x = player.get("x", 0)
            
            # Check if coordinates are in wrong zone
            zone_mismatch = False
            if context_zone == "defensive" and current_x > -25:
                zone_mismatch = True
            elif context_zone == "offensive" and current_x < 25:
                zone_mismatch = True
            
            if zone_mismatch or abs(current_x) < 5:  # Also fix players too close to center
                # Get correct coordinates from coordinate mapper
                try:
                    role = "primary"
                    # Try to determine role from position or context
                    if "penalty kill" in data.get("title", "").lower():
                        if position in ["LW", "RW"]:
                            role = "coverage"
                        elif position in ["LD", "RD"]:
                            role = "net_front"
                    elif "forecheck" in data.get("title", "").lower():
                        if position == "C":
                            role = "primary"
                        elif position in ["LW", "RW"]:
                            role = "corner" if target_zone == Zone.OFFENSIVE else "coverage"
                    
                    new_x, new_y = coordinate_mapper.get_player_coordinate(
                        position, target_zone, role
                    )
                    
                    logger.info(f"Coordinate correction: {position} from ({current_x:.1f}, {player.get('y', 0):.1f}) to ({new_x:.1f}, {new_y:.1f}) for {context_zone} zone")
                    
                    player["x"] = new_x
                    player["y"] = new_y
                    
                except Exception as e:
                    logger.warning(f"Could not map coordinates for {position} in {context_zone} zone: {e}")
                    # Fallback: use basic zone correction
                    if context_zone == "defensive" and current_x > -25:
                        player["x"] = -60  # Basic defensive position
                    elif context_zone == "offensive" and current_x < 25:
                        player["x"] = 60   # Basic offensive position
        
        return data
    
    def _apply_team_separation(self, players: List[Dict]) -> None:
        """
        Apply team separation logic to prevent player overlap.
        Away team players get X-axis offset of +5 units to prevent both teams at same coordinates.
        """
        # Group players by position to detect overlaps
        position_map = {}
        for player in players:
            pos_key = (round(player.get("x", 0), 1), round(player.get("y", 0), 1))  # Round to avoid floating point issues
            if pos_key not in position_map:
                position_map[pos_key] = []
            position_map[pos_key].append(player)
        
        # Apply separation where multiple teams occupy same position
        for position, players_at_pos in position_map.items():
            if len(players_at_pos) > 1:
                # Check if we have both home and away teams at same position
                home_players = [p for p in players_at_pos if p.get("team") == "home"]
                away_players = [p for p in players_at_pos if p.get("team") == "away"]
                
                if home_players and away_players:
                    # Apply X-axis offset to away team players
                    for away_player in away_players:
                        original_x = away_player["x"]
                        away_player["x"] = min(100, away_player["x"] + 5)
                        logger.info(f"Applied team separation: moved {away_player.get('position')} from ({original_x}, {away_player.get('y')}) to ({away_player['x']}, {away_player.get('y')})")
                        
        # Also apply preemptive separation for center positions (common overlap at 0,0)
        center_players = [p for p in players if abs(p.get("x", 0)) < 1 and abs(p.get("y", 0)) < 1]
        if len(center_players) > 1:
            home_centers = [p for p in center_players if p.get("team") == "home"]
            away_centers = [p for p in center_players if p.get("team") == "away"]
            
            if home_centers and away_centers:
                # Move away team centers to avoid center ice overlap
                for away_center in away_centers:
                    away_center["x"] = 5  # Move to slightly offensive position
                    logger.info(f"Applied preemptive center separation: moved {away_center.get('position')} to (5, 0)")
    
    def _is_valid_movement(self, movement: Dict, player_positions: Dict) -> bool:
        """
        Check if movement represents an actual position change.
        Returns False if from_position and to_position are the same location.
        """
        from_pos = movement.get("from_position")
        to_pos = movement.get("to_position")
        
        if not from_pos or not to_pos:
            return False
        
        # Get starting position
        if from_pos in player_positions:
            start_x, start_y = player_positions[from_pos]
        else:
            return True  # Can't validate, allow movement
        
        # Get ending position
        if isinstance(to_pos, list) and len(to_pos) >= 2:
            end_x, end_y = to_pos[0], to_pos[1]
        elif isinstance(to_pos, str) and to_pos in player_positions:
            end_x, end_y = player_positions[to_pos]
        else:
            return True  # Can't validate, allow movement
        
        # Check if positions are significantly different (tolerance of 2 units)
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        if distance < 2.0:
            return False  # Too close, redundant movement
            
        return True
    
    def _create_fallback_diagram(self, prompt: str) -> DiagramSpec:
        """Create fallback diagram when parsing fails."""
        # Determine context zone from prompt
        context_zone = "full"
        if "defensive" in prompt.lower() or "penalty kill" in prompt.lower() or "box formation" in prompt.lower():
            context_zone = "defensive"
        elif "offensive" in prompt.lower() or "power play" in prompt.lower() or "cycle" in prompt.lower():
            context_zone = "offensive"
        elif "neutral" in prompt.lower() or "trap" in prompt.lower():
            context_zone = "neutral"
        
        # Create basic fallback positions - using coordinate mapper for accuracy
        players = []
        
        try:
            # Map zone context to coordinate mapper Zone enum
            zone_map = {
                "defensive": Zone.DEFENSIVE,
                "offensive": Zone.OFFENSIVE, 
                "neutral": Zone.NEUTRAL,
                "full": Zone.NEUTRAL  # Default to neutral for full view
            }
            
            target_zone = zone_map.get(context_zone, Zone.NEUTRAL)
            
            # Get appropriate coordinates from coordinate mapper
            positions = [
                ("C", "primary"),
                ("RW", "primary"),
                ("LW", "primary"),
                ("LD", "primary"),
                ("RD", "primary"),
                ("G", "primary"),
            ]
            
            for position, role in positions:
                x, y = coordinate_mapper.get_player_coordinate(position, target_zone, role)
                has_puck = (position == "C")  # Give puck to center
                players.append(PlayerPosition(position=position, x=x, y=y, team="home", has_puck=has_puck))
                
        except Exception as e:
            logger.warning(f"Error creating fallback with coordinate mapper: {e}")
            # Ultra-basic fallback if coordinate mapper fails
            players = [
                PlayerPosition(position="C", x=-60 if context_zone == "defensive" else 0, y=0, team="home", has_puck=True),
                PlayerPosition(position="RW", x=-60 if context_zone == "defensive" else 10, y=20, team="home"),
                PlayerPosition(position="LW", x=-60 if context_zone == "defensive" else 10, y=-20, team="home"),
                PlayerPosition(position="LD", x=-70 if context_zone == "defensive" else -30, y=-15, team="home"),
                PlayerPosition(position="RD", x=-70 if context_zone == "defensive" else -30, y=15, team="home"),
                PlayerPosition(position="G", x=-89, y=0, team="home"),
            ]
        
        fallback_spec = DiagramSpec(
            players=players,
            movements=[],
            zones=[],
            view=context_zone if context_zone != "full" else "full",
            title=f"Basic Formation - Fallback ({context_zone})",
            diagram_type="formation"
        )
        
        # Apply coordinate mapping corrections to ensure accuracy
        fallback_data = fallback_spec.dict()
        fallback_data = self._apply_coordinate_mapping(fallback_data, context_zone)
        
        return DiagramSpec(**fallback_data)
    
    def get_definitions(self) -> Dict[str, Dict[str, str]]:
        """Return all pick list definitions for reference."""
        return self.DEFINITIONS.copy()
    
    def validate_pick_list_value(self, category: str, value: str) -> bool:
        """Validate if a value exists in a pick list category."""
        return value in self.DEFINITIONS.get(category, {})
    
    def get_category_options(self, category: str) -> List[str]:
        """Get all valid options for a pick list category."""
        return list(self.DEFINITIONS.get(category, {}).keys())
    
    def get_value_definition(self, category: str, value: str) -> Optional[str]:
        """Get the definition for a specific pick list value."""
        return self.DEFINITIONS.get(category, {}).get(value)