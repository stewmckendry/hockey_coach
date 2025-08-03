"""
Unit tests for coordinate mapping functionality.
"""

import pytest
from coordinate_mapper import (
    HockeyCoordinateMapper, Zone, Team, CoordinateMapping,
    get_player_coordinate, get_area_coordinate, get_formation_coordinates,
    get_drill_positioning, get_zone_boundary, find_nearest_area,
    validate_coordinate, list_available_formations
)


class TestCoordinateMapping:
    """Test coordinate mapping functionality."""
    
    @pytest.fixture
    def mapper(self):
        """Create mapper instance."""
        return HockeyCoordinateMapper()
    
    def test_player_coordinates_basic(self, mapper):
        """Test basic player coordinate retrieval."""
        # Test center in offensive zone
        x, y = mapper.get_player_coordinate("C", Zone.OFFENSIVE, "primary")
        assert x == 60  # Should be in offensive zone
        assert y == 0   # Center ice laterally
        
        # Test left wing in defensive zone
        x, y = mapper.get_player_coordinate("LW", Zone.DEFENSIVE, "primary")
        assert x == -70  # Should be in defensive zone
        assert y == -25  # Left side
        
        # Test goalie position
        x, y = mapper.get_player_coordinate("G", Zone.DEFENSIVE, "primary")
        assert x == -89  # In goal
        assert y == 0    # Centered
    
    def test_formation_adjustments(self, mapper):
        """Test formation-specific coordinate adjustments."""
        # Test 2-1-2 forecheck positions
        coords = mapper.get_formation_coordinates("2-1-2_forecheck")
        
        assert "F1" in coords
        assert "F2" in coords
        assert "F3" in coords
        assert "D1" in coords
        assert "D2" in coords
        
        # F1 and F2 should be deep in offensive zone
        assert coords["F1"][0] > 50
        assert coords["F2"][0] > 50
        
        # F3 should be higher (neutral zone)
        assert coords["F3"][0] < coords["F1"][0]
    
    def test_power_play_formations(self, mapper):
        """Test power play formation coordinates."""
        # Test 1-3-1 umbrella
        coords = mapper.get_formation_coordinates("1-3-1_powerplay")
        
        assert len(coords) == 5  # 5 players on power play
        
        # Check relative positions
        assert "net_front" in coords
        assert "left_wing" in coords
        assert "right_wing" in coords
        assert "left_point" in coords
        assert "right_point" in coords
        
        # Points should be at blue line area
        assert coords["left_point"][0] < 40
        assert coords["right_point"][0] < 40
    
    def test_penalty_kill_formations(self, mapper):
        """Test penalty kill formation coordinates."""
        # Test box penalty kill
        coords = mapper.get_formation_coordinates("box_penalty_kill")
        
        assert len(coords) == 4  # 4 players on PK
        
        # Should form a box shape
        assert coords["high_left"][1] < 0  # Left side
        assert coords["high_right"][1] > 0  # Right side
        assert coords["low_left"][1] < 0   # Left side
        assert coords["low_right"][1] > 0  # Right side
        
        # High players should be further from net
        assert coords["high_left"][0] > coords["low_left"][0]
        assert coords["high_right"][0] > coords["low_right"][0]
    
    def test_area_coordinates(self, mapper):
        """Test named area coordinate retrieval."""
        # Test slot area
        x, y = mapper.get_area_coordinate("slot")
        assert x == 75
        assert y == 0
        
        # Test corner areas
        x, y = mapper.get_area_coordinate("left_corner")
        assert x == 85
        assert y == -35
        
        # Test faceoff dots
        x, y = mapper.get_area_coordinate("offensive_left")
        assert x == 69
        assert y == -22.5
    
    def test_zone_boundaries(self, mapper):
        """Test zone boundary retrieval."""
        # Test offensive zone
        boundary = mapper.get_zone_boundary("offensive_zone")
        assert boundary[0] == 25    # Starts at blue line
        assert boundary[2] == 75    # Width
        assert boundary[3] == 85    # Height (full rink width)
        
        # Test slot area
        boundary = mapper.get_zone_boundary("slot")
        assert boundary[0] == 60    # X position
        assert boundary[2] == 29    # Width
        assert boundary[3] == 30    # Height
    
    def test_relative_positioning(self, mapper):
        """Test relative position calculations."""
        base = (50, 0)
        
        # Test directional positioning
        x, y = mapper.get_relative_position(base, "north", 10)
        assert x == 50
        assert y == 10
        
        x, y = mapper.get_relative_position(base, "east", 20)
        assert x == 70
        assert y == 0
        
        # Test diagonal positioning
        x, y = mapper.get_relative_position(base, "northeast", 10)
        assert x > 50 and y > 0
    
    def test_role_to_coordinate_conversion(self, mapper):
        """Test converting role descriptions to coordinates."""
        # Test slot positioning
        x, y = mapper.convert_role_to_coordinate("C", "high slot", "offensive")
        assert 40 <= x <= 60  # High slot range
        assert -10 <= y <= 10  # Central area
        
        # Test corner positioning
        x, y = mapper.convert_role_to_coordinate("LW", "left corner", "offensive")
        assert x > 80  # Deep in zone
        assert y < -30  # Left side
        
        # Test point positioning
        x, y = mapper.convert_role_to_coordinate("LD", "left point", "offensive")
        assert 20 <= x <= 30  # Blue line area
        assert y < -15  # Left side
    
    def test_drill_positioning(self, mapper):
        """Test drill-specific positioning."""
        # Test triangle passing drill
        positions = mapper.get_drill_positioning("triangle_passing", 3)
        assert len(positions) == 3
        
        # Should form a triangle
        assert positions[0] != positions[1]
        assert positions[1] != positions[2]
        assert positions[0] != positions[2]
        
        # Test 2v1 rush drill
        positions = mapper.get_drill_positioning("2v1_rush", 4)
        assert len(positions) == 4
        
        # Should have goalie
        assert any(pos[0] == -89 for pos in positions)
    
    def test_coordinate_validation(self, mapper):
        """Test coordinate validation and clamping."""
        # Test valid coordinates
        x, y = mapper.validate_coordinate(50, 20)
        assert x == 50
        assert y == 20
        
        # Test out of bounds coordinates
        x, y = mapper.validate_coordinate(150, 60)
        assert x == 100   # Clamped to max
        assert y == 42.5  # Clamped to max
        
        x, y = mapper.validate_coordinate(-150, -60)
        assert x == -100  # Clamped to min
        assert y == -42.5  # Clamped to min
    
    def test_find_nearest_area(self, mapper):
        """Test finding nearest named area."""
        # Test near slot
        area = mapper.find_nearest_area(70, 0)
        assert area in ["slot", "low_slot"]
        
        # Test near corner
        area = mapper.find_nearest_area(85, -30)
        assert "corner" in area
        
        # Test center ice
        area = mapper.find_nearest_area(0, 0)
        assert area == "neutral_center"
    
    def test_zone_specific_coordinates(self, mapper):
        """Test getting all coordinates for a zone."""
        # Get offensive zone coordinates
        coords = mapper.get_zone_specific_coordinates(Zone.OFFENSIVE)
        
        assert "C" in coords
        assert "LW" in coords
        assert "RW" in coords
        assert "LD" in coords
        assert "RD" in coords
        
        # Check all positions have multiple roles
        for position, roles in coords.items():
            if position != "G":  # Goalie doesn't move zones
                assert len(roles) > 1
    
    def test_list_available_formations(self):
        """Test listing available formations."""
        formations = list_available_formations()
        
        # Check key formations exist
        assert "2-1-2_forecheck" in formations
        assert "1-3-1_powerplay" in formations
        assert "box_penalty_kill" in formations
        assert "neutral_zone_trap" in formations
        
        # Should have a good variety
        assert len(formations) > 15
    
    def test_custom_formation_adjustments(self, mapper):
        """Test applying formation adjustments to players."""
        # Create test players
        players = [
            {"position": "C", "x": 0, "y": 0},
            {"position": "LW", "x": 0, "y": -25},
            {"position": "RW", "x": 0, "y": 25},
            {"position": "LD", "x": -25, "y": -20},
            {"position": "RD", "x": -25, "y": 20},
        ]
        
        # Apply 2-1-2 forecheck
        adjusted = mapper.adjust_for_formation(players, "2-1-2_forecheck")
        
        # Players should have moved
        assert adjusted[0]["x"] != players[0]["x"]  # Center moved
        assert adjusted[1]["x"] != players[1]["x"]  # LW moved
        assert adjusted[2]["x"] != players[2]["x"]  # RW moved
    
    def test_nhl_regulation_dimensions(self, mapper):
        """Test NHL regulation rink dimensions."""
        # Check key dimensions
        assert mapper.NHL_RINK["rink_length"] == 200
        assert mapper.NHL_RINK["rink_width"] == 85
        assert mapper.NHL_RINK["blue_line_defensive"] == -25
        assert mapper.NHL_RINK["blue_line_offensive"] == 25
        assert mapper.NHL_RINK["goal_line_home"] == -89
        assert mapper.NHL_RINK["goal_line_away"] == 89
    
    def test_faceoff_dot_positions(self, mapper):
        """Test faceoff dot positions."""
        dots = mapper.FACEOFF_DOTS
        
        # Center ice
        assert dots["center"] == (0, 0)
        
        # Offensive zone dots
        assert dots["offensive_left"][0] == 69
        assert dots["offensive_left"][1] == -22.5
        assert dots["offensive_right"][0] == 69
        assert dots["offensive_right"][1] == 22.5
        
        # Should be symmetrical
        assert abs(dots["defensive_left"][0]) == abs(dots["offensive_left"][0])
        assert dots["defensive_left"][1] == dots["offensive_left"][1]


if __name__ == "__main__":
    # Run tests
    mapper = HockeyCoordinateMapper()
    test = TestCoordinateMapping()
    
    # Run key tests
    print("Testing player coordinates...")
    test.test_player_coordinates_basic(mapper)
    print("✓ Player coordinates test passed")
    
    print("\nTesting formation adjustments...")
    test.test_formation_adjustments(mapper)
    print("✓ Formation adjustments test passed")
    
    print("\nTesting power play formations...")
    test.test_power_play_formations(mapper)
    print("✓ Power play formations test passed")
    
    print("\nTesting penalty kill formations...")
    test.test_penalty_kill_formations(mapper)
    print("✓ Penalty kill formations test passed")
    
    print("\nTesting NHL dimensions...")
    test.test_nhl_regulation_dimensions(mapper)
    print("✓ NHL dimensions test passed")
    
    print("\nAll coordinate mapping tests completed!")