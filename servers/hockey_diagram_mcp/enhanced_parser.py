"""
Enhanced Hockey Diagram Parser with improved accuracy and systematic coaching patterns.

This parser addresses the accuracy issues identified between preset formations 
and LLM-parsed instructions by providing:
1. More precise NHL coordinate mapping
2. Better drill sequence understanding  
3. Enhanced position area recognition
4. Systematic play pattern templates
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import os

logger = logging.getLogger(__name__)

class PlayerPosition(BaseModel):
    """Structured player position data with NHL accuracy."""
    position: str = Field(..., description="Player position (C, RW, LW, LD, RD, G for home; X1-X5, XG for away)")
    x: float = Field(..., description="X coordinate on rink (-100 to 100)")
    y: float = Field(..., description="Y coordinate on rink (-42.5 to 42.5)")
    team: str = Field(..., description="Team: 'home' or 'away'")
    has_puck: bool = Field(False, description="Whether this player has the puck")
    step: Optional[int] = Field(None, description="Sequence step for drills (1, 2, 3, etc.)")

class MovementSpec(BaseModel):
    """Enhanced movement specification for drills and plays."""
    from_position: str = Field(..., description="Starting position (player position label)")
    to_position: Union[str, List[float]] = Field(..., description="End position (player label or [x, y] coordinates)")
    movement_type: str = Field(..., description="Type: 'skating', 'pass', 'shot', 'check', 'support'")
    sequence: Optional[int] = Field(None, description="Step number in drill sequence")
    arrow_style: str = Field("solid", description="Arrow style: 'solid', 'dashed', 'dotted'")

class ZoneSpec(BaseModel):
    """Enhanced zone specification with NHL positioning accuracy."""
    zone_type: str = Field(..., description="Zone type: 'coverage', 'pressure', 'neutral', 'position_area'")
    area: Union[str, List[float]] = Field(..., description="Named area or [x, y, width, height]")
    team: str = Field(..., description="Team controlling zone: 'home' or 'away'")
    opacity: float = Field(0.3, description="Zone shading opacity (0.1 to 0.5)")

class DiagramSpec(BaseModel):
    """Complete enhanced diagram specification."""
    players: List[PlayerPosition]
    movements: Optional[List[MovementSpec]] = []
    zones: Optional[List[ZoneSpec]] = []
    view: str = Field("full", description="View: 'full', 'offensive', 'defensive', 'neutral'")
    title: Optional[str] = None
    diagram_type: str = Field("formation", description="Type: 'formation', 'drill', 'faceoff', 'play'")

class EnhancedHockeyParser:
    """Enhanced parser with systematic accuracy improvements."""
    
    # NHL-accurate coordinate templates
    NHL_COORDINATES = {
        # Standard positions
        "center_ice": (0, 0),
        "goal_line_home": -89,
        "goal_line_away": 89,
        "blue_line_defensive": -25,
        "blue_line_offensive": 25,
        
        # Faceoff dots (exact NHL positions)
        "defensive_dot_left": (-69, -22.5),
        "defensive_dot_right": (-69, 22.5),
        "defensive_dot_center": (-69, 0),
        "offensive_dot_left": (69, -22.5),
        "offensive_dot_right": (69, 22.5),
        "offensive_dot_center": (69, 0),
        "neutral_dot_left": (-20.5, -22.5),
        "neutral_dot_right": (-20.5, 22.5),
        "neutral_dot_left_away": (20.5, -22.5),
        "neutral_dot_right_away": (20.5, 22.5),
        
        # Common tactical positions
        "slot": (75, 0),
        "high_slot": (50, 0),
        "left_point": (25, -30),
        "right_point": (25, 30),
        "left_half_wall": (60, -35),
        "right_half_wall": (60, 35),
        "left_corner": (85, -35),
        "right_corner": (85, 35),
        "behind_net": (95, 0),
        "goal_crease": (89, 0),
    }
    
    # Zone area definitions [x, y, width, height]
    ZONE_AREAS = {
        "slot": [60, -15, 29, 30],
        "high_slot": [40, -20, 40, 40],
        "left_point": [20, -40, 10, 20],
        "right_point": [20, 20, 10, 20],
        "left_corner": [75, -42.5, 25, 20],
        "right_corner": [75, 22.5, 25, 20],
        "behind_net": [89, -10, 11, 20],
        "neutral_zone": [-25, -42.5, 50, 85],
        "defensive_zone": [-100, -42.5, 75, 85],
        "offensive_zone": [25, -42.5, 75, 85],
        "left_side": [-100, -42.5, 200, 20],
        "right_side": [-100, 22.5, 200, 20],
    }
    
    SYSTEM_PROMPT = """You are an expert hockey tactics parser specializing in NHL-accurate diagram generation.

CRITICAL ACCURACY REQUIREMENTS:
1. Use EXACT NHL regulation coordinates - never approximate
2. Recognize diagram types: formation, drill, faceoff, play
3. For DRILLS: Include sequence numbers and multiple movement steps
4. For FORMATIONS: Focus on static positioning with minimal movement
5. For PLAYS: Show tactical flow with numbered sequences
6. For FACEOFFS: Show exact dot positioning and coverage responsibilities

NHL RINK COORDINATES (Use EXACTLY):
- Rink: X = -100 (defensive) to 100 (offensive), Y = -42.5 (left) to 42.5 (right)
- Goal lines: X = ±89
- Blue lines: X = ±25  
- Center: (0, 0)
- Faceoff dots: Defensive (-69, ±22.5), Offensive (69, ±22.5), Neutral (±20.5, ±22.5)

STANDARD FORMATIONS:
- 2-1-2 Forecheck: F1(80,-15), F2(80,15), F3(40,0), D1(10,-15), D2(10,15), G(-89,0)
- 1-3-1 Powerplay: F1(60,0), F2(40,-30), F3(40,30), D1(25,-25), D2(25,25), G(-89,0)
- Box Penalty Kill: F1(50,-15), F2(50,15), D1(20,-15), D2(20,15), G(-89,0)

DRILL PARSING RULES:
- Identify sequence steps (Step 1, Step 2, etc.)
- Use "sequence" field for movements
- Show player progression through drill
- Include support players and flow patterns

PLAY PARSING RULES:
- Breakouts: Start defensive zone, show progression
- Zone entries: Show neutral to offensive zone flow
- Forechecks: Show pressure patterns and coverage
- Power plays: Show formation and movement options

Output valid JSON matching this structure:
{
    "players": [{"position": "C", "x": 0, "y": 0, "team": "home", "has_puck": false, "step": 1}],
    "movements": [{"from_position": "C", "to_position": [20, 10], "movement_type": "skating", "sequence": 1, "arrow_style": "solid"}],
    "zones": [{"zone_type": "coverage", "area": "slot", "team": "home", "opacity": 0.3}],
    "view": "full",
    "title": "Diagram Title",
    "diagram_type": "drill"
}"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize enhanced parser."""
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def parse_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> DiagramSpec:
        """
        Parse natural language with enhanced accuracy.
        
        Args:
            prompt: Natural language description 
            context: Additional context (age_group, diagram_type, etc.)
            
        Returns:
            Enhanced DiagramSpec with improved accuracy
        """
        # Detect diagram type from prompt
        diagram_type = self._detect_diagram_type(prompt)
        
        # Enhance prompt with type-specific instructions
        enhanced_prompt = self._enhance_prompt_by_type(prompt, diagram_type, context)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.1,  # Very low for consistency
                max_tokens=1500
            )
            
            # Parse and validate response
            json_text = response.choices[0].message.content.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:-3]
            elif json_text.startswith("```"):
                json_text = json_text[3:-3]
                
            parsed_data = json.loads(json_text)
            
            # Post-process for accuracy
            parsed_data = self._post_process_coordinates(parsed_data, diagram_type)
            
            return DiagramSpec(**parsed_data)
            
        except Exception as e:
            logger.error(f"Enhanced parsing failed: {e}")
            # Fallback to basic formation
            return self._create_fallback_diagram(prompt, diagram_type)
    
    def _detect_diagram_type(self, prompt: str) -> str:
        """Detect the type of diagram from prompt keywords."""
        prompt_lower = prompt.lower()
        
        drill_keywords = ["drill", "exercise", "practice", "step", "sequence", "progression"]
        faceoff_keywords = ["faceoff", "face-off", "draw", "dot", "circle"]
        play_keywords = ["breakout", "entry", "zone entry", "rush", "cycle", "regroup"]
        formation_keywords = ["formation", "system", "forecheck", "backcheck", "powerplay", "penalty kill"]
        
        if any(keyword in prompt_lower for keyword in drill_keywords):
            return "drill"
        elif any(keyword in prompt_lower for keyword in faceoff_keywords):
            return "faceoff"  
        elif any(keyword in prompt_lower for keyword in play_keywords):
            return "play"
        else:
            return "formation"
    
    def _enhance_prompt_by_type(self, prompt: str, diagram_type: str, context: Optional[Dict] = None) -> str:
        """Enhance prompt based on diagram type."""
        enhanced = prompt
        
        if diagram_type == "drill":
            enhanced += "\n\nFOCUS: This is a DRILL. Show step-by-step sequence with numbered movements. Include all players involved and their progression through the drill."
        elif diagram_type == "faceoff":
            enhanced += "\n\nFOCUS: This is a FACEOFF setup. Position players exactly at faceoff dots and show coverage responsibilities."
        elif diagram_type == "play":
            enhanced += "\n\nFOCUS: This is a tactical PLAY. Show the flow and progression from start to finish with sequential movements."
        elif diagram_type == "formation":
            enhanced += "\n\nFOCUS: This is a FORMATION. Show static positioning with minimal movement, emphasizing tactical setup."
            
        if context:
            if "age_group" in context:
                enhanced += f"\n(Age group: {context['age_group']} - adjust complexity accordingly)"
                
        return enhanced
    
    def _post_process_coordinates(self, data: Dict, diagram_type: str) -> Dict:
        """Post-process coordinates for NHL accuracy."""
        # Validate and correct player positions
        if "players" in data:
            for player in data["players"]:
                # Ensure coordinates are within rink bounds
                player["x"] = max(-100, min(100, player["x"]))
                player["y"] = max(-42.5, min(42.5, player["y"]))
                
                # Apply position-specific corrections
                if player["position"] == "G":
                    # Goalies should be near goal line
                    if player["team"] == "home":
                        player["x"] = max(-95, min(-85, player["x"]))
                    else:
                        player["x"] = max(85, min(95, player["x"]))
        
        # Validate zone areas
        if "zones" in data:
            for zone in data["zones"]:
                if isinstance(zone["area"], str) and zone["area"] in self.ZONE_AREAS:
                    zone["area"] = self.ZONE_AREAS[zone["area"]]
        
        return data
    
    def _create_fallback_diagram(self, prompt: str, diagram_type: str) -> DiagramSpec:
        """Create fallback diagram with correct hockey positioning if parsing fails."""
        # Center ice faceoff formation (defensive zone on left, offensive on right)
        # LW on right side (+Y), RW on left side (-Y) when viewed from defensive zone
        basic_players = [
            {"position": "C", "x": 0, "y": 0, "team": "home", "has_puck": False},          # Center at faceoff
            {"position": "LW", "x": -5, "y": 20, "team": "home", "has_puck": False},      # Left wing on right side
            {"position": "RW", "x": -5, "y": -20, "team": "home", "has_puck": False},     # Right wing on left side
            {"position": "LD", "x": -25, "y": 20, "team": "home", "has_puck": False},     # Left defense on right side
            {"position": "RD", "x": -25, "y": -20, "team": "home", "has_puck": False},    # Right defense on left side
            {"position": "G", "x": -89, "y": 0, "team": "home", "has_puck": False}        # Goalie in net
        ]
        
        return DiagramSpec(
            players=basic_players,
            movements=[],
            zones=[],
            view="full",
            title=f"Basic {diagram_type} - Fallback",
            diagram_type=diagram_type
        )