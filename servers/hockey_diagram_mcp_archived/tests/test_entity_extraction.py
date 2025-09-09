"""
Unit tests for entity extraction from natural language hockey descriptions.
"""

import pytest
import asyncio
from two_stage_parser import TwoStageParser
from entities import (
    ExtractedEntities, Player, Movement, Zone,
    PlayerRole, MovementType, ZoneType, ArrowType
)


class TestEntityExtraction:
    """Test entity extraction functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return TwoStageParser()
    
    def test_extract_basic_formation(self, parser):
        """Test extraction of basic formation."""
        prompt = "Show a 2-1-2 forecheck"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        assert entities.formation == "2-1-2_forecheck"
        assert entities.action == "forecheck"
        assert len(entities.players) >= 5  # Should have F1, F2, F3, D1, D2
    
    def test_extract_power_play(self, parser):
        """Test extraction of power play formation."""
        prompt = "1-3-1 power play umbrella formation with center in high slot"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        assert entities.formation == "1-3-1_powerplay"
        assert entities.situation == "power_play"
        # Check for center position
        center_players = [p for p in entities.players if p.position == "C"]
        assert len(center_players) > 0
        assert any("high slot" in (p.location or "") for p in center_players)
    
    def test_extract_penalty_kill(self, parser):
        """Test extraction of penalty kill system."""
        prompt = "Box penalty kill with tight coverage"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        assert entities.formation == "box_penalty_kill"
        assert entities.situation == "penalty_kill"
        assert entities.team_strength == "4v5"
    
    def test_extract_player_movements(self, parser):
        """Test extraction of player movements."""
        prompt = "F1 forechecks hard on the puck carrier, F2 supports from the right"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        # Check F1 attributes
        f1_players = [p for p in entities.players if p.label == "F1"]
        assert len(f1_players) > 0
        assert f1_players[0].role == PlayerRole.FORECHECKER
        
        # Check movements
        assert len(entities.movements) > 0
        f1_movements = [m for m in entities.movements if m.player == "F1"]
        assert len(f1_movements) > 0
    
    def test_extract_passing_plays(self, parser):
        """Test extraction of passing plays."""
        prompt = "D1 passes to the center who then passes to the left wing in the corner"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        # Should have multiple pass movements
        pass_movements = [m for m in entities.movements if m.movement_type == MovementType.PASS]
        assert len(pass_movements) >= 2
        
        # Check pass sequence
        assert any(m.player == "D1" and m.target_player == "C" for m in pass_movements)
        assert any(m.player == "C" and m.target_player == "LW" for m in pass_movements)
    
    def test_extract_zones(self, parser):
        """Test extraction of zone highlighting."""
        prompt = "Highlight the slot area and show defensive zone coverage"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        assert len(entities.zones) >= 2
        zone_types = [z.zone_type for z in entities.zones]
        assert ZoneType.SLOT in zone_types
        assert ZoneType.DEFENSIVE in zone_types
    
    def test_extract_drill(self, parser):
        """Test extraction of drill description."""
        prompt = "3v2 rush drill starting from the neutral zone"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        assert entities.action == "drill"
        assert "3v2" in entities.situation or "3v2" in entities.formation
        # Should have neutral zone reference
        assert any(z.zone_type == ZoneType.NEUTRAL for z in entities.zones)
    
    def test_extract_complex_scenario(self, parser):
        """Test extraction from complex tactical description."""
        prompt = """
        2-1-2 forecheck with F1 pressuring the puck carrier behind the net,
        F2 taking away the strong side boards, F3 covering the slot,
        and both defensemen holding the blue line
        """
        entities = asyncio.run(parser.extract_entities(prompt))
        
        assert entities.formation == "2-1-2_forecheck"
        
        # Check all players are identified
        player_labels = [p.label for p in entities.players]
        assert "F1" in player_labels
        assert "F2" in player_labels
        assert "F3" in player_labels
        
        # Check locations
        f1 = next(p for p in entities.players if p.label == "F1")
        assert "behind" in (f1.location or "").lower() and "net" in (f1.location or "").lower()
        
        f3 = next(p for p in entities.players if p.label == "F3")
        assert "slot" in (f3.location or "").lower()
    
    def test_extract_faceoff_setup(self, parser):
        """Test extraction of faceoff positioning."""
        prompt = "Offensive zone faceoff setup with strong side overload"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        assert entities.situation == "faceoff"
        assert any(z.zone_type == ZoneType.OFFENSIVE for z in entities.zones)
        
        # Should identify it's a special formation
        assert "overload" in (entities.formation or "").lower() or \
               "overload" in (entities.strategy or "").lower()
    
    def test_extract_breakout(self, parser):
        """Test extraction of breakout play."""
        prompt = "D to D pass for a weak side breakout with center swinging through middle"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        assert entities.action == "breakout"
        
        # Check for D to D pass
        d_to_d_passes = [
            m for m in entities.movements 
            if m.player in ["LD", "RD", "D1", "D2"] and 
               m.target_player in ["LD", "RD", "D1", "D2"]
        ]
        assert len(d_to_d_passes) > 0
        
        # Check for center movement
        center_movements = [m for m in entities.movements if m.player == "C"]
        assert len(center_movements) > 0
    
    def test_extract_cycle_play(self, parser):
        """Test extraction of offensive zone cycle."""
        prompt = "LW cycles the puck low to center, who passes back to the point"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        # Check for cycle movement
        cycle_movements = [m for m in entities.movements if m.movement_type == MovementType.CYCLE]
        assert len(cycle_movements) > 0
        
        # Check for pass to point
        point_passes = [
            m for m in entities.movements 
            if m.movement_type == MovementType.PASS and 
               "point" in (m.to_location or "").lower()
        ]
        assert len(point_passes) > 0
    
    def test_extract_defensive_coverage(self, parser):
        """Test extraction of defensive zone coverage."""
        prompt = "Man-on-man coverage with center supporting low"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        assert entities.strategy == "man-on-man"
        
        # Check center position
        centers = [p for p in entities.players if p.position == "C"]
        assert len(centers) > 0
        assert centers[0].role == PlayerRole.SUPPORT
    
    def test_extract_rush_play(self, parser):
        """Test extraction of rush play."""
        prompt = "3-man rush with LW driving wide and C trailing"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        assert entities.action == "rush"
        
        # Check for wide drive
        lw_movements = [m for m in entities.movements if m.player == "LW"]
        assert len(lw_movements) > 0
        assert any("wide" in (m.direction or "").lower() for m in lw_movements)
    
    def test_empty_prompt(self, parser):
        """Test handling of empty prompt."""
        entities = asyncio.run(parser.extract_entities(""))
        
        assert isinstance(entities, ExtractedEntities)
        assert len(entities.players) == 0
        assert len(entities.movements) == 0
    
    def test_invalid_formation(self, parser):
        """Test handling of invalid formation."""
        prompt = "Show a 7-2-5 formation"  # Invalid formation
        entities = asyncio.run(parser.extract_entities(prompt))
        
        # Should still extract some entities
        assert isinstance(entities, ExtractedEntities)
        # But formation might be None or a best guess
        assert entities.formation is None or "7-2-5" not in entities.formation
    
    def test_multiple_teams(self, parser):
        """Test extraction with multiple teams."""
        prompt = "Home team in 1-2-2 forecheck against away team's breakout"
        entities = asyncio.run(parser.extract_entities(prompt))
        
        # Should have players from both teams
        home_players = [p for p in entities.players if p.team == "home"]
        away_players = [p for p in entities.players if p.team == "away"]
        
        assert len(home_players) > 0
        assert len(away_players) > 0


if __name__ == "__main__":
    # Run tests
    parser = TwoStageParser()
    test = TestEntityExtraction()
    
    # Run a few key tests
    print("Testing basic formation extraction...")
    test.test_extract_basic_formation(parser)
    print("✓ Basic formation test passed")
    
    print("\nTesting power play extraction...")
    test.test_extract_power_play(parser)
    print("✓ Power play test passed")
    
    print("\nTesting complex scenario...")
    test.test_extract_complex_scenario(parser)
    print("✓ Complex scenario test passed")
    
    print("\nAll tests completed!")