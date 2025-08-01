"""
LLM-based parser to convert natural language hockey instructions to structured diagram specifications.
Uses OpenAI GPT-4 to understand coaching terminology and generate precise diagram data.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class PlayerPosition(BaseModel):
    """Structured player position data."""
    position: str = Field(..., description="Player position (C, RW, LW, LD, RD, G for home; X1-X5, XG for away)")
    x: float = Field(..., description="X coordinate on rink (-100 to 100)")
    y: float = Field(..., description="Y coordinate on rink (-42.5 to 42.5)")
    team: str = Field(..., description="Team: 'home' or 'away'")
    has_puck: bool = Field(False, description="Whether this player has the puck")

class MovementSpec(BaseModel):
    """Structured movement/pass data."""
    from_position: str = Field(..., description="Starting position (player position label)")
    to_position: str | List[float] = Field(..., description="End position (player label or [x, y] coordinates)")
    movement_type: str = Field(..., description="Type: 'skating', 'pass', 'shot', or 'forecheck'")

class ZoneSpec(BaseModel):
    """Structured zone coverage data."""
    zone_type: str = Field(..., description="Zone type: 'coverage', 'pressure', or 'neutral'")
    area: str | List[float] = Field(..., description="Named area ('slot', 'point', etc.) or [x, y, width, height]")
    team: str = Field(..., description="Team controlling zone: 'home' or 'away'")

class DiagramSpec(BaseModel):
    """Complete diagram specification."""
    players: List[PlayerPosition]
    movements: Optional[List[MovementSpec]] = []
    zones: Optional[List[ZoneSpec]] = []
    view: str = Field("full", description="View: 'full', 'offensive', 'defensive', or 'neutral'")
    title: Optional[str] = None

class HockeyPromptParser:
    """Parses natural language hockey instructions into structured diagram specifications."""
    
    SYSTEM_PROMPT = """You are a hockey tactics parser that converts natural language coaching instructions into structured JSON for diagram generation.

IMPORTANT RULES:
1. Use standard hockey positions for home team: C (Center), RW (Right Wing), LW (Left Wing), LD (Left Defense), RD (Right Defense), G (Goaltender)
2. Use X1-X5 for opposing players, XG for opposing goaltender
3. Rink coordinates: X axis is -100 (defensive end) to 100 (offensive end), Y axis is -42.5 (left) to 42.5 (right)
4. Common positions on rink:
   - Center ice: (0, 0)
   - Defensive zone faceoff dots: (-69, �22.5)
   - Offensive zone faceoff dots: (69, �22.5)
   - Goal line: x = �89
   - Blue lines: x = �25
   - Slot area: x between -20 and 20, y between -8 and 8
   - Points: approximately (�30, �20)

Output must be valid JSON matching this structure:
{
    "players": [
        {"position": "C", "x": 0, "y": 0, "team": "home", "has_puck": false}
    ],
    "movements": [
        {"from_position": "C", "to_position": [20, 10], "movement_type": "skating"}
    ],
    "zones": [
        {"zone_type": "coverage", "area": "slot", "team": "home"}
    ],
    "view": "full",
    "title": "Diagram Title"
}

Common hockey terms to understand:
- Forecheck: Pressure in offensive zone (2-1-2, 1-2-2, etc.)
- Backcheck: Defensive tracking back
- Cycle: Puck movement along boards in offensive zone
- Breakout: Moving puck out of defensive zone
- Power play: Man advantage formations (umbrella, 1-3-1, overload)
- Penalty kill: Short-handed formations (box, diamond)
- Neutral zone trap: Defensive system in neutral zone
- Slot: High-danger area in front of net
- Point: Position at blue line in offensive zone
- Half-wall: Position halfway between goal line and blue line along boards"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize parser with OpenAI client."""
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def parse_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> DiagramSpec:
        """
        Parse natural language prompt into structured diagram specification.
        
        Args:
            prompt: Natural language description of the hockey play/formation
            context: Optional context (e.g., age group, skill level)
            
        Returns:
            DiagramSpec object with structured data
        """
        # Enhance prompt with context if provided
        enhanced_prompt = prompt
        if context:
            if "age_group" in context:
                enhanced_prompt += f"\n(Context: {context['age_group']} level players)"
            if "diagram_type" in context:
                enhanced_prompt += f"\n(Diagram type: {context['diagram_type']})"
                
        try:
            # Call GPT-4 to parse the prompt
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.2,  # Low temperature for consistent parsing
                max_tokens=1000
            )
            
            # Extract and parse JSON response
            content = response.choices[0].message.content
            
            # Try to extract JSON from the response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
            else:
                json_str = content
                
            # Parse JSON and validate with Pydantic
            data = json.loads(json_str)
            diagram_spec = DiagramSpec(**data)
            
            # Add default title if not provided
            if not diagram_spec.title:
                diagram_spec.title = self._generate_title(prompt)
                
            logger.info(f"Successfully parsed prompt: {prompt[:50]}...")
            return diagram_spec
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            # Return a basic formation as fallback
            return self._get_fallback_diagram(prompt)
            
        except Exception as e:
            logger.error(f"Error parsing prompt: {e}")
            return self._get_fallback_diagram(prompt)
            
    def _generate_title(self, prompt: str) -> str:
        """Generate a title from the prompt."""
        # Simple title generation - take first 50 chars or until period
        title = prompt.split(".")[0][:50]
        if len(title) == 50 and title[-1] != " ":
            # Find last space to avoid cutting words
            last_space = title.rfind(" ")
            if last_space > 30:
                title = title[:last_space]
        return title.strip()
        
    def _get_fallback_diagram(self, prompt: str) -> DiagramSpec:
        """Return a basic diagram when parsing fails."""
        # Basic 2-1-2 formation as fallback
        return DiagramSpec(
            players=[
                PlayerPosition(position="C", x=0, y=0, team="home", has_puck=True),
                PlayerPosition(position="RW", x=10, y=20, team="home"),
                PlayerPosition(position="LW", x=10, y=-20, team="home"),
                PlayerPosition(position="LD", x=-30, y=-15, team="home"),
                PlayerPosition(position="RD", x=-30, y=15, team="home"),
                PlayerPosition(position="G", x=-89, y=0, team="home"),
                # Opposing team
                PlayerPosition(position="X1", x=40, y=0, team="away"),
                PlayerPosition(position="X2", x=50, y=15, team="away"),
                PlayerPosition(position="X3", x=50, y=-15, team="away"),
            ],
            movements=[
                MovementSpec(from_position="C", to_position=[20, 0], movement_type="skating")
            ],
            view="full",
            title=self._generate_title(prompt)
        )
        
    async def parse_with_presets(self, prompt: str, presets: Dict[str, Any]) -> DiagramSpec:
        """
        Parse prompt with access to preset formations.
        
        Args:
            prompt: Natural language prompt
            presets: Dictionary of preset formations
            
        Returns:
            DiagramSpec, possibly based on a preset
        """
        # Check if prompt mentions a known preset
        prompt_lower = prompt.lower()
        for preset_name, preset_data in presets.items():
            if preset_name.lower() in prompt_lower:
                logger.info(f"Using preset: {preset_name}")
                # Start with preset and modify based on additional instructions
                base_spec = DiagramSpec(**preset_data)
                
                # If prompt has additional instructions beyond preset name
                if len(prompt) > len(preset_name) + 10:
                    # Parse modifications
                    modifications = await self.parse_prompt(
                        prompt.replace(preset_name, "").strip()
                    )
                    # Merge modifications with preset
                    if modifications.movements:
                        base_spec.movements.extend(modifications.movements)
                    if modifications.zones:
                        base_spec.zones.extend(modifications.zones)
                        
                return base_spec
                
        # No preset found, parse normally
        return await self.parse_prompt(prompt)