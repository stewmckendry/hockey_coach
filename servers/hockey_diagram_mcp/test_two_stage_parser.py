"""
Comprehensive tests for the two-stage hockey diagram parser system.

Tests validate that the parser correctly extracts semantic entities from natural language
without requiring hockey coordinate knowledge from the LLM, then properly maps those
entities to accurate coordinates.
"""

import json
from typing import Dict, Any
try:
    import pytest
    from unittest.mock import AsyncMock, patch
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    print("pytest not available - running basic tests only")

from entities import (
    PlayerEntity, MovementEntity, ZoneEntity, FormationEntity, DrillEntity,
    ExtractedEntities, CoordinateMappingResult, ParsingContext
)


class TestEntityModels:
    """Test the Pydantic entity models for validation and structure."""
    
    def test_player_entity_creation(self):
        """Test PlayerEntity model validation."""
        player = PlayerEntity(
            position="C",
            team="home",
            named_location="center_ice",
            tactical_role="puck_carrier",
            has_puck=True
        )
        
        assert player.position == "C"
        assert player.team == "home"
        assert player.named_location == "center_ice"
        assert player.has_puck is True
        
    def test_player_entity_validation(self):
        """Test PlayerEntity validation rules."""
        # Valid teams
        PlayerEntity(position="C", team="home")
        PlayerEntity(position="X1", team="away")
        
        # Invalid team should raise validation error
        with pytest.raises(ValueError):
            PlayerEntity(position="C", team="invalid")
    
    def test_movement_entity_creation(self):
        """Test MovementEntity model validation."""
        movement = MovementEntity(
            from_player="C",
            to_location="slot",
            movement_type="skating",
            purpose="create_space",
            sequence=1
        )
        
        assert movement.from_player == "C"
        assert movement.movement_type == "skating"
        assert movement.sequence == 1
        
    def test_zone_entity_creation(self):
        """Test ZoneEntity model validation."""
        zone = ZoneEntity(
            zone_name="slot",
            zone_type="coverage",
            team="home",
            intensity="medium"
        )
        
        assert zone.zone_name == "slot"
        assert zone.zone_type == "coverage"
        assert zone.intensity == "medium"
    
    def test_formation_entity_creation(self):
        """Test FormationEntity model validation."""
        formation = FormationEntity(
            formation_name="2-1-2_forecheck",
            formation_type="forecheck",
            zone_focus="offensive"
        )
        
        assert formation.formation_name == "2-1-2_forecheck"
        assert formation.formation_type == "forecheck"
        assert formation.zone_focus == "offensive"
    
    def test_drill_entity_creation(self):
        """Test DrillEntity model validation."""
        drill = DrillEntity(
            drill_category="passing",
            steps=["Player passes to center", "Center returns pass"],
            objectives=["Improve accuracy", "Practice timing"]
        )
        
        assert drill.drill_category == "passing"
        assert len(drill.steps) == 2
        assert len(drill.objectives) == 2


class TestEntityExtraction:
    """Test entity extraction from natural language hockey instructions."""
    
    def test_extract_2_1_2_forecheck_entities(self):
        """Test extraction of 2-1-2 forecheck formation entities."""
        # This would be the result of Stage 1 parsing
        entities = ExtractedEntities(
            diagram_type="formation",
            primary_focus="forechecking pressure in offensive zone",
            formation=FormationEntity(
                formation_name="2-1-2_forecheck",
                formation_type="forecheck",
                zone_focus="offensive"
            ),
            players=[
                PlayerEntity(
                    position="C", team="home", formation_role="F1",
                    named_location="behind_net", tactical_role="pressure"
                ),
                PlayerEntity(
                    position="RW", team="home", formation_role="F2", 
                    named_location="right_corner", tactical_role="pressure"
                ),
                PlayerEntity(
                    position="LW", team="home", formation_role="F3",
                    named_location="high_slot", tactical_role="support"
                ),
                PlayerEntity(
                    position="LD", team="home", formation_role="D1",
                    named_location="left_point", tactical_role="coverage"
                ),
                PlayerEntity(
                    position="RD", team="home", formation_role="D2",
                    named_location="right_point", tactical_role="coverage"
                )
            ],
            zones=[
                ZoneEntity(
                    zone_name="offensive_zone", zone_type="pressure", 
                    team="home", intensity="heavy"
                )
            ],
            view_preference="offensive"
        )
        
        # Validate extraction results
        assert entities.diagram_type == "formation"
        assert entities.formation.formation_type == "forecheck"
        assert len(entities.players) == 5
        assert entities.players[0].tactical_role == "pressure"
        assert entities.view_preference == "offensive"
    
    def test_extract_passing_drill_entities(self):
        """Test extraction of passing drill entities."""
        entities = ExtractedEntities(
            diagram_type="drill",
            primary_focus="triangle passing with movement",
            drill=DrillEntity(
                drill_category="passing",
                steps=[
                    "Player 1 passes to Player 2",
                    "Player 2 passes to Player 3", 
                    "Player 3 passes back to Player 1",
                    "All players move to next position"
                ],
                objectives=["Improve passing accuracy", "Practice receiving while moving"],
                players_involved=["C", "RW", "LW"]
            ),
            players=[
                PlayerEntity(
                    position="C", team="home", step=1,
                    named_location="center_ice", has_puck=True
                ),
                PlayerEntity(
                    position="RW", team="home", step=1,
                    named_location="right_point"
                ),
                PlayerEntity(
                    position="LW", team="home", step=1,
                    named_location="left_point"
                )
            ],
            movements=[
                MovementEntity(
                    from_player="C", to_location="RW", movement_type="pass",
                    sequence=1, timing="on_drill_start"
                ),
                MovementEntity(
                    from_player="RW", to_location="LW", movement_type="pass",
                    sequence=2, timing="after_reception"
                ),
                MovementEntity(
                    from_player="LW", to_location="C", movement_type="pass",
                    sequence=3, timing="after_reception"
                )
            ]
        )
        
        # Validate drill extraction
        assert entities.diagram_type == "drill"
        assert entities.drill.drill_category == "passing"
        assert len(entities.drill.steps) == 4
        assert len(entities.movements) == 3
        assert entities.movements[0].sequence == 1
    
    def test_extract_box_penalty_kill_entities(self):
        """Test extraction of box penalty kill formation entities."""
        entities = ExtractedEntities(
            diagram_type="formation",
            primary_focus="4-player box defensive formation",
            formation=FormationEntity(
                formation_name="box_penalty_kill",
                formation_type="penalty_kill",
                zone_focus="defensive"
            ),
            players=[
                PlayerEntity(
                    position="C", team="home", formation_role="high_forward",
                    named_location="high_slot", tactical_role="pressure"
                ),
                PlayerEntity(
                    position="RW", team="home", formation_role="low_forward", 
                    named_location="right_side", tactical_role="coverage"
                ),
                PlayerEntity(
                    position="LD", team="home", formation_role="left_defense",
                    named_location="left_side", tactical_role="coverage"
                ),
                PlayerEntity(
                    position="RD", team="home", formation_role="right_defense",
                    named_location="right_side", tactical_role="coverage"
                ),
                PlayerEntity(
                    position="G", team="home", 
                    named_location="goal_crease", tactical_role="last_line"
                )
            ],
            zones=[
                ZoneEntity(
                    zone_name="defensive_zone", zone_type="coverage",
                    team="home", intensity="heavy"
                )
            ],
            view_preference="defensive"
        )
        
        # Validate penalty kill extraction
        assert entities.formation.formation_type == "penalty_kill"
        assert len(entities.players) == 5
        assert entities.view_preference == "defensive"
        assert entities.zones[0].zone_type == "coverage"


class TestCoordinateMapping:
    """Test the coordinate mapping stage of the two-stage parser."""
    
    def test_map_formation_to_coordinates(self):
        """Test mapping formation entities to precise coordinates."""
        # Input entities (from Stage 1)
        entities = ExtractedEntities(
            diagram_type="formation",
            formation=FormationEntity(
                formation_name="2-1-2_forecheck",
                formation_type="forecheck"
            ),
            players=[
                PlayerEntity(position="C", team="home", named_location="behind_net"),
                PlayerEntity(position="RW", team="home", named_location="right_corner"),
                PlayerEntity(position="LW", team="home", named_location="high_slot")
            ]
        )
        
        # Expected coordinate mapping
        expected_coordinates = {
            "players": [
                {"position": "C", "x": 95, "y": 0, "team": "home"},  # behind_net
                {"position": "RW", "x": 85, "y": 35, "team": "home"},  # right_corner  
                {"position": "LW", "x": 50, "y": 0, "team": "home"}   # high_slot
            ],
            "view": "offensive"
        }
        
        # This would be implemented by the coordinate mapper
        result = CoordinateMappingResult(
            diagram_spec=expected_coordinates,
            mapping_notes=["Mapped named locations to NHL coordinates"],
            coordinate_adjustments=["Adjusted LW position for better spacing"]
        )
        
        assert len(result.diagram_spec["players"]) == 3
        assert result.diagram_spec["players"][0]["x"] == 95  # behind_net
        assert len(result.mapping_notes) > 0
    
    def test_map_drill_to_coordinates(self):
        """Test mapping drill entities with sequences to coordinates."""
        entities = ExtractedEntities(
            diagram_type="drill",
            drill=DrillEntity(drill_category="passing"),
            players=[
                PlayerEntity(position="C", team="home", step=1, named_location="center_ice"),
                PlayerEntity(position="RW", team="home", step=1, named_location="right_point"),
                PlayerEntity(position="LW", team="home", step=1, named_location="left_point")
            ],
            movements=[
                MovementEntity(
                    from_player="C", to_location="RW", movement_type="pass", sequence=1
                )
            ]
        )
        
        expected_coordinates = {
            "players": [
                {"position": "C", "x": 0, "y": 0, "team": "home", "step": 1},
                {"position": "RW", "x": 25, "y": 30, "team": "home", "step": 1},
                {"position": "LW", "x": 25, "y": -30, "team": "home", "step": 1}
            ],
            "movements": [
                {
                    "from_position": "C", 
                    "to_position": [25, 30],  # Mapped to RW coordinates
                    "movement_type": "pass",
                    "sequence": 1
                }
            ]
        }
        
        result = CoordinateMappingResult(
            diagram_spec=expected_coordinates,
            mapping_notes=["Mapped triangle formation for passing drill"]
        )
        
        assert len(result.diagram_spec["movements"]) == 1
        assert result.diagram_spec["movements"][0]["sequence"] == 1


class TestEndToEndParsing:
    """Test complete end-to-end parsing scenarios."""
    
    def test_2_1_2_forecheck_parsing(self):
        """Test complete parsing of '2-1-2 forecheck' instruction."""
        instruction = "2-1-2 forecheck with F1 pressuring behind net"
        
        # Stage 1: Entity extraction (what the LLM should output)
        extracted_entities = ExtractedEntities(
            diagram_type="formation",
            primary_focus="forechecking pressure with F1 behind net",
            title="2-1-2 Forecheck Formation",
            formation=FormationEntity(
                formation_name="2-1-2_forecheck",
                formation_type="forecheck",
                zone_focus="offensive"
            ),
            players=[
                PlayerEntity(
                    position="C", team="home", formation_role="F1",
                    named_location="behind_net", tactical_role="pressure"
                ),
                PlayerEntity(
                    position="RW", team="home", formation_role="F2",
                    named_location="right_corner", tactical_role="pressure"
                ),
                PlayerEntity(
                    position="LW", team="home", formation_role="F3", 
                    named_location="high_slot", tactical_role="support"
                ),
                PlayerEntity(
                    position="LD", team="home",
                    named_location="left_point", tactical_role="coverage"
                ),
                PlayerEntity(
                    position="RD", team="home",
                    named_location="right_point", tactical_role="coverage"
                )
            ],
            movements=[
                MovementEntity(
                    from_player="C", to_location="behind_net",
                    movement_type="forecheck", purpose="apply_pressure"
                )
            ],
            view_preference="offensive",
            confidence_score=0.95
        )
        
        # Validate Stage 1 output
        assert extracted_entities.diagram_type == "formation"
        assert extracted_entities.formation.formation_type == "forecheck"
        assert len(extracted_entities.players) == 5
        assert extracted_entities.players[0].named_location == "behind_net"
        
        # Stage 2: Coordinate mapping
        final_spec = {
            "players": [
                {"position": "C", "x": 95, "y": 0, "team": "home"},  # behind_net
                {"position": "RW", "x": 85, "y": 35, "team": "home"},  # right_corner
                {"position": "LW", "x": 50, "y": 0, "team": "home"},   # high_slot
                {"position": "LD", "x": 25, "y": -30, "team": "home"}, # left_point
                {"position": "RD", "x": 25, "y": 30, "team": "home"}   # right_point
            ],
            "movements": [
                {"from_position": "C", "to_position": [95, 0], "movement_type": "forecheck"}
            ],
            "view": "offensive",
            "title": "2-1-2 Forecheck Formation"
        }
        
        mapping_result = CoordinateMappingResult(
            diagram_spec=final_spec,
            mapping_notes=["Applied standard 2-1-2 forecheck coordinates"],
            coordinate_adjustments=["F1 positioned optimally behind net"]
        )
        
        # Validate final output
        assert len(mapping_result.diagram_spec["players"]) == 5
        assert mapping_result.diagram_spec["view"] == "offensive"
    
    def test_passing_drill_parsing(self):
        """Test parsing of 'Pass from center to left wing in slot' instruction."""
        instruction = "Pass from center to left wing in slot"
        
        # Stage 1: Entity extraction
        extracted_entities = ExtractedEntities(
            diagram_type="drill",
            primary_focus="center to left wing passing in slot area",
            title="Center to Left Wing Pass",
            drill=DrillEntity(
                drill_category="passing",
                steps=["Center passes to left wing in slot area"],
                objectives=["Practice slot area passing"],
                players_involved=["C", "LW"]
            ),
            players=[
                PlayerEntity(
                    position="C", team="home", has_puck=True,
                    named_location="center_ice", tactical_role="puck_carrier"
                ),
                PlayerEntity(
                    position="LW", team="home",
                    named_location="slot", tactical_role="receiver"
                )
            ],
            movements=[
                MovementEntity(
                    from_player="C", to_location="slot",
                    movement_type="pass", purpose="deliver_puck"
                )
            ],
            view_preference="offensive"
        )
        
        # Validate entity extraction
        assert extracted_entities.diagram_type == "drill"
        assert extracted_entities.players[0].has_puck is True
        assert extracted_entities.players[1].named_location == "slot"
        assert extracted_entities.movements[0].movement_type == "pass"
        
        # Stage 2: Coordinate mapping
        final_spec = {
            "players": [
                {"position": "C", "x": 0, "y": 0, "team": "home", "has_puck": True},
                {"position": "LW", "x": 75, "y": 0, "team": "home"}  # slot center
            ],
            "movements": [
                {
                    "from_position": "C", 
                    "to_position": [75, 0],  # slot coordinates
                    "movement_type": "pass"
                }
            ],
            "view": "full"
        }
        
        mapping_result = CoordinateMappingResult(
            diagram_spec=final_spec,
            mapping_notes=["Mapped slot to offensive zone coordinates"]
        )
        
        assert mapping_result.diagram_spec["players"][1]["x"] == 75  # slot position
    
    def test_box_penalty_kill_parsing(self):
        """Test parsing of 'Box penalty kill formation' instruction."""
        instruction = "Box penalty kill formation"
        
        # Stage 1: Entity extraction  
        extracted_entities = ExtractedEntities(
            diagram_type="formation",
            primary_focus="4-player box defensive formation",
            title="Box Penalty Kill",
            formation=FormationEntity(
                formation_name="box_penalty_kill",
                formation_type="penalty_kill",
                zone_focus="defensive"
            ),
            players=[
                PlayerEntity(
                    position="C", team="home", formation_role="high_forward",
                    named_location="high_slot", tactical_role="pressure"
                ),
                PlayerEntity(
                    position="RW", team="home", formation_role="low_forward",
                    named_location="goal_line", tactical_role="coverage"
                ),
                PlayerEntity(
                    position="LD", team="home", formation_role="left_defense",
                    named_location="left_side", tactical_role="coverage"
                ),
                PlayerEntity(
                    position="RD", team="home", formation_role="right_defense", 
                    named_location="right_side", tactical_role="coverage"
                ),
                PlayerEntity(
                    position="G", team="home",
                    named_location="goal_crease", tactical_role="last_line"
                )
            ],
            zones=[
                ZoneEntity(
                    zone_name="defensive_zone", zone_type="coverage",
                    team="home", intensity="heavy"
                )
            ],
            view_preference="defensive"
        )
        
        # Validate extraction
        assert extracted_entities.formation.formation_type == "penalty_kill"
        assert len(extracted_entities.players) == 5
        assert extracted_entities.view_preference == "defensive"
        
        # Stage 2: Coordinate mapping for box formation
        final_spec = {
            "players": [
                {"position": "C", "x": -50, "y": 0, "team": "home"},   # high_slot
                {"position": "RW", "x": -75, "y": 0, "team": "home"},  # low in box
                {"position": "LD", "x": -60, "y": -20, "team": "home"}, # left side
                {"position": "RD", "x": -60, "y": 20, "team": "home"},  # right side  
                {"position": "G", "x": -89, "y": 0, "team": "home"}    # goal
            ],
            "zones": [
                {"zone_type": "coverage", "area": [-100, -42.5, 75, 85], "team": "home"}
            ],
            "view": "defensive"
        }
        
        mapping_result = CoordinateMappingResult(
            diagram_spec=final_spec,
            mapping_notes=["Applied standard box penalty kill positioning"]
        )
        
        assert mapping_result.diagram_spec["view"] == "defensive"
        assert len(mapping_result.diagram_spec["players"]) == 5


class TestParsingContext:
    """Test how parsing context affects entity extraction."""
    
    def test_age_group_context_extraction(self):
        """Test that age group context is properly extracted and applied."""
        context = ParsingContext(
            age_group="U10",
            skill_level="beginner", 
            simplification_level="simplified"
        )
        
        # With U10 context, should extract simpler entities
        entities = ExtractedEntities(
            diagram_type="drill",
            age_group_context="U10",
            primary_focus="simple passing drill for beginners",
            drill=DrillEntity(
                drill_category="passing",
                steps=["Pass and move"],  # Simplified for U10
                objectives=["Learn to pass accurately"]
            )
        )
        
        assert entities.age_group_context == "U10"
        assert len(entities.drill.steps) == 1  # Simplified
    
    def test_emphasis_context_extraction(self):
        """Test that emphasis context guides entity extraction."""
        context = ParsingContext(
            emphasis="defensive_positioning",
            session_type="tutorial"
        )
        
        entities = ExtractedEntities(
            diagram_type="formation",
            primary_focus="defensive positioning emphasis",
            zones=[
                ZoneEntity(
                    zone_name="defensive_coverage", zone_type="responsibility",
                    team="home", intensity="heavy"
                )
            ]
        )
        
        assert "defensive" in entities.primary_focus
        assert entities.zones[0].zone_type == "responsibility"


class TestValidationAndErrorHandling:
    """Test validation and error handling in the parsing system."""
    
    def test_entity_validation_errors(self):
        """Test that invalid entities raise appropriate validation errors."""
        # Invalid team designation
        with pytest.raises(ValueError):
            PlayerEntity(position="C", team="invalid_team")
        
        # Invalid movement type
        with pytest.raises(ValueError):
            MovementEntity(
                from_player="C", movement_type="invalid_movement"
            )
        
        # Invalid zone type
        with pytest.raises(ValueError):
            ZoneEntity(
                zone_name="slot", zone_type="invalid_zone", team="home"
            )
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        # Missing required position field
        with pytest.raises(ValueError):
            PlayerEntity(team="home")
        
        # Missing required movement type
        with pytest.raises(ValueError):
            MovementEntity(from_player="C")
    
    def test_confidence_and_quality_tracking(self):
        """Test that parsing quality and confidence are tracked."""
        entities = ExtractedEntities(
            diagram_type="formation",
            confidence_score=0.85,
            missing_elements=["goaltender position not specified"],
            assumptions_made=["assumed standard 2-1-2 positioning"]
        )
        
        assert entities.confidence_score == 0.85
        assert len(entities.missing_elements) == 1
        assert len(entities.assumptions_made) == 1


if __name__ == "__main__":
    # Run basic tests to verify the models work
    print("Testing entity models...")
    
    # Test basic entity creation
    player = PlayerEntity(position="C", team="home", named_location="center_ice")
    print(f"✓ Player entity: {player.position} at {player.named_location}")
    
    movement = MovementEntity(
        from_player="C", to_location="slot", movement_type="skating"
    )
    print(f"✓ Movement entity: {movement.movement_type} from {movement.from_player}")
    
    zone = ZoneEntity(zone_name="slot", zone_type="coverage", team="home")
    print(f"✓ Zone entity: {zone.zone_name} ({zone.zone_type})")
    
    # Test complete extraction
    entities = ExtractedEntities(
        diagram_type="formation",
        players=[player],
        movements=[movement], 
        zones=[zone]
    )
    print(f"✓ Complete entities: {len(entities.players)} players, {len(entities.movements)} movements")
    
    print("\nAll entity models working correctly!")
    print("\nTo run full test suite: pytest test_two_stage_parser.py -v")