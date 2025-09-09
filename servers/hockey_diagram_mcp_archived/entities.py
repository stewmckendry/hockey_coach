"""
Entity model definitions for the two-stage hockey diagram parser system.

This module defines Pydantic models for extracting semantic entities from natural language
hockey instructions without requiring coordinate knowledge from the LLM. The entities are
then mapped to coordinates by a separate coordinate mapping system.
"""

from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field


class PlayerEntity(BaseModel):
    """
    Represents a player entity extracted from natural language.
    
    The LLM identifies player roles and responsibilities without needing to know
    exact coordinates. Coordinate mapping happens in a separate stage.
    """
    position: str = Field(
        ..., 
        description="Player position role (C, RW, LW, LD, RD, G for home; X1-X5, XG for away)"
    )
    team: Literal["home", "away"] = Field(
        ..., 
        description="Team designation"
    )
    named_location: Optional[str] = Field(
        None, 
        description="Named location on rink (e.g., 'slot', 'point', 'behind_net', 'center_ice')"
    )
    tactical_role: Optional[str] = Field(
        None, 
        description="Tactical responsibility (e.g., 'puck_carrier', 'support', 'pressure', 'coverage')"
    )
    has_puck: bool = Field(
        False, 
        description="Whether this player currently has puck possession"
    )
    step: Optional[int] = Field(
        None, 
        description="Sequence step for drill progressions (1, 2, 3, etc.)"
    )
    formation_role: Optional[str] = Field(
        None, 
        description="Role in formation (e.g., 'F1', 'F2', 'F3', 'weak_side', 'strong_side')"
    )


class MovementEntity(BaseModel):
    """
    Represents a movement or action entity extracted from natural language.
    
    Describes intent and purpose without requiring coordinate knowledge.
    """
    from_player: str = Field(
        ..., 
        description="Starting player position identifier"
    )
    to_location: Union[str, None] = Field(
        None, 
        description="Target location name (e.g., 'slot', 'behind_net') or target player"
    )
    movement_type: Literal[
        "skating", "pass", "shot", "check", "support", "forecheck", "backcheck", "pressure"
    ] = Field(
        ..., 
        description="Type of movement or action"
    )
    purpose: Optional[str] = Field(
        None, 
        description="Tactical purpose (e.g., 'create_space', 'apply_pressure', 'support_puck')"
    )
    sequence: Optional[int] = Field(
        None, 
        description="Order in sequence for multi-step plays"
    )
    timing: Optional[str] = Field(
        None, 
        description="When movement occurs (e.g., 'simultaneous', 'after_pass', 'on_puck_drop')"
    )
    arrow_style: Optional[Literal["solid", "dashed", "dotted", "thick"]] = Field(
        "solid", 
        description="Visual style for movement arrow"
    )


class ZoneEntity(BaseModel):
    """
    Represents a zone or area entity with tactical meaning.
    
    Describes coverage areas and responsibilities without coordinate specifics.
    """
    zone_name: str = Field(
        ..., 
        description="Named zone or area (e.g., 'slot', 'neutral_zone', 'left_point')"
    )
    zone_type: Literal["coverage", "pressure", "neutral", "position_area", "responsibility"] = Field(
        ..., 
        description="Type of zone marking"
    )
    team: Literal["home", "away"] = Field(
        ..., 
        description="Team responsible for or controlling this zone"
    )
    intensity: Optional[Literal["light", "medium", "heavy"]] = Field(
        "medium", 
        description="Visual intensity of zone marking"
    )
    purpose: Optional[str] = Field(
        None, 
        description="Tactical purpose (e.g., 'defensive_coverage', 'pressure_area', 'support_zone')"
    )


class FormationEntity(BaseModel):
    """
    Represents a recognized hockey formation or system.
    
    Identifies standard formations without needing coordinate knowledge.
    """
    formation_name: str = Field(
        ..., 
        description="Standard formation name (e.g., '2-1-2_forecheck', '1-3-1_powerplay')"
    )
    formation_type: Literal[
        "forecheck", "backcheck", "powerplay", "penalty_kill", "neutral_zone", "faceoff", "breakout"
    ] = Field(
        ..., 
        description="Category of formation"
    )
    variation: Optional[str] = Field(
        None, 
        description="Formation variation (e.g., 'umbrella', 'overload', 'left_side')"
    )
    zone_focus: Literal["offensive", "defensive", "neutral", "full"] = Field(
        "full", 
        description="Primary zone of focus for the formation"
    )


class DrillEntity(BaseModel):
    """
    Represents a drill structure with steps and objectives.
    
    Identifies drill components without coordinate requirements.
    """
    drill_name: Optional[str] = Field(
        None, 
        description="Name or type of drill"
    )
    drill_category: Literal[
        "passing", "shooting", "skating", "forechecking", "breakout", "transition", "faceoff"
    ] = Field(
        ..., 
        description="Category of drill"
    )
    steps: List[str] = Field(
        default_factory=list, 
        description="Sequential steps in the drill"
    )
    objectives: List[str] = Field(
        default_factory=list, 
        description="Learning objectives or skills practiced"
    )
    players_involved: List[str] = Field(
        default_factory=list, 
        description="Player positions involved in the drill"
    )


class ExtractedEntities(BaseModel):
    """
    Complete collection of entities extracted from natural language input.
    
    This is the output of the first stage of the two-stage parser, containing
    semantic understanding without coordinate specifics.
    """
    # Core entities
    players: List[PlayerEntity] = Field(
        default_factory=list, 
        description="Player entities identified in the instruction"
    )
    movements: List[MovementEntity] = Field(
        default_factory=list, 
        description="Movement and action entities identified"
    )
    zones: List[ZoneEntity] = Field(
        default_factory=list, 
        description="Zone and area entities identified"
    )
    
    # Context entities
    formation: Optional[FormationEntity] = Field(
        None, 
        description="Formation entity if a standard formation is identified"
    )
    drill: Optional[DrillEntity] = Field(
        None, 
        description="Drill entity if drill structure is identified"
    )
    
    # Metadata
    diagram_type: Literal["formation", "drill", "play", "faceoff"] = Field(
        "formation", 
        description="Type of diagram being described"
    )
    primary_focus: Optional[str] = Field(
        None, 
        description="Main focus or objective of the instruction"
    )
    age_group_context: Optional[str] = Field(
        None, 
        description="Age group context if mentioned (U8, U10, U12, etc.)"
    )
    view_preference: Literal["full", "offensive", "defensive", "neutral"] = Field(
        "full", 
        description="Preferred view based on content focus"
    )
    title: Optional[str] = Field(
        None, 
        description="Generated title for the diagram"
    )
    
    # Validation and quality
    confidence_score: Optional[float] = Field(
        None, 
        description="Parser confidence in entity extraction (0.0 to 1.0)"
    )
    missing_elements: List[str] = Field(
        default_factory=list, 
        description="Elements that may be missing or unclear"
    )
    assumptions_made: List[str] = Field(
        default_factory=list, 
        description="Assumptions made during parsing"
    )


class CoordinateMappingResult(BaseModel):
    """
    Result of mapping entities to specific coordinates.
    
    This is the output of the second stage, where semantic entities
    are converted to precise diagram specifications.
    """
    diagram_spec: dict = Field(
        ..., 
        description="Complete diagram specification with coordinates"
    )
    mapping_notes: List[str] = Field(
        default_factory=list, 
        description="Notes about coordinate mapping decisions"
    )
    coordinate_adjustments: List[str] = Field(
        default_factory=list, 
        description="Adjustments made during coordinate mapping"
    )
    validation_warnings: List[str] = Field(
        default_factory=list, 
        description="Warnings about potential coordinate issues"
    )


class ParsingContext(BaseModel):
    """
    Context information for parsing customization.
    
    Provides additional context to guide entity extraction.
    """
    age_group: Optional[str] = Field(
        None, 
        description="Target age group (U8, U10, U12, U14, etc.)"
    )
    skill_level: Optional[str] = Field(
        None, 
        description="Skill level (beginner, intermediate, advanced)"
    )
    session_type: Optional[str] = Field(
        None, 
        description="Type of session (practice, game, drill, tutorial)"
    )
    emphasis: Optional[str] = Field(
        None, 
        description="What to emphasize in the diagram"
    )
    simplification_level: Optional[str] = Field(
        None, 
        description="How much to simplify (full, simplified, minimal)"
    )
    preferred_view: Optional[str] = Field(
        None, 
        description="Preferred diagram view"
    )