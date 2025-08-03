"""
Integration tests for the hockey diagram MCP server with two-stage parser.
Tests the complete pipeline from natural language to diagram generation.
"""

import pytest
import asyncio
import os
import json
from pathlib import Path
from typing import Dict, Any

# Ensure imports work
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from servers.hockey_diagram_mcp.server import generate_hockey_diagram
from servers.hockey_diagram_mcp.two_stage_parser import TwoStageHockeyParser

# Skip tests if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)


class TestTwoStageParserIntegration:
    """Test the two-stage parser integration in the MCP server."""
    
    @pytest.fixture
    def parser(self):
        """Create a parser instance."""
        return TwoStageHockeyParser()
    
    @pytest.mark.asyncio
    async def test_forecheck_formation(self):
        """Test 2-1-2 forecheck formation generation."""
        result = await generate_hockey_diagram(
            prompt="2-1-2 forecheck with F1 pressuring behind net",
            diagram_type="tactical",
            view="full"
        )
        
        assert result['success'] is True
        assert 'diagram_path' in result
        assert 'diagram_spec' in result
        
        spec = result['diagram_spec']
        assert len(spec['players']) == 5
        assert spec['diagram_type'] in ['formation', 'system']
        
        # Check F1 is behind net
        f1_player = next((p for p in spec['players'] if p['position'] in ['C', 'F1']), None)
        assert f1_player is not None
        assert f1_player['x'] > 85  # Behind net area
    
    @pytest.mark.asyncio
    async def test_passing_drill(self):
        """Test passing drill generation."""
        result = await generate_hockey_diagram(
            prompt="Pass from center to left wing in slot",
            diagram_type="drill",
            view="full"
        )
        
        assert result['success'] is True
        spec = result['diagram_spec']
        
        assert len(spec['players']) >= 2
        assert len(spec['movements']) >= 1
        
        # Check movement is a pass
        movement = spec['movements'][0]
        assert movement['movement_type'] == 'pass'
    
    @pytest.mark.asyncio
    async def test_penalty_kill_formation(self):
        """Test box penalty kill formation."""
        result = await generate_hockey_diagram(
            prompt="Box penalty kill formation in defensive zone",
            diagram_type="tactical",
            view="defensive"
        )
        
        assert result['success'] is True
        spec = result['diagram_spec']
        
        # Box PK typically has 4 skaters + goalie
        assert len(spec['players']) >= 4
        assert spec['view'] == 'defensive'
        
        # Check players are in defensive zone
        for player in spec['players']:
            if player['position'] != 'G':
                assert player['x'] < 0  # Defensive zone
    
    @pytest.mark.asyncio
    async def test_power_play_with_movement(self):
        """Test power play formation with movement."""
        result = await generate_hockey_diagram(
            prompt="Power play umbrella with movement from half-wall to slot",
            diagram_type="tactical",
            view="offensive"
        )
        
        assert result['success'] is True
        spec = result['diagram_spec']
        
        # Power play should have 5 skaters + goalie
        assert len(spec['players']) >= 5
        assert len(spec['movements']) >= 1
        
        # Check movement involves slot area
        has_slot_movement = any(
            'slot' in str(m.get('to_position', '')) or 
            (isinstance(m.get('to_position'), list) and 
             60 <= m['to_position'][0] <= 89 and 
             -15 <= m['to_position'][1] <= 15)
            for m in spec['movements']
        )
        assert has_slot_movement
    
    @pytest.mark.asyncio
    async def test_complex_drill_sequence(self):
        """Test complex drill with multiple steps."""
        result = await generate_hockey_diagram(
            prompt="3v2 rush drill starting from neutral zone with D-to-D pass",
            diagram_type="drill",
            view="full"
        )
        
        assert result['success'] is True
        spec = result['diagram_spec']
        
        # Should have at least 5 players (3 forwards, 2 defense)
        assert len(spec['players']) >= 5
        assert spec['diagram_type'] in ['drill', 'play']
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid prompts."""
        result = await generate_hockey_diagram(
            prompt="",  # Empty prompt
            diagram_type="tactical"
        )
        
        # Should either fail gracefully or use fallback
        assert 'success' in result
        if not result['success']:
            assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_view_preferences(self):
        """Test that view preferences are respected."""
        views = ['full', 'offensive', 'defensive', 'neutral']
        
        for view in views:
            result = await generate_hockey_diagram(
                prompt="Basic 5v5 formation",
                diagram_type="tactical",
                view=view
            )
            
            assert result['success'] is True
            assert result['diagram_spec']['view'] == view
    
    @pytest.mark.asyncio
    async def test_parser_definitions(self, parser):
        """Test that parser has all required definitions."""
        definitions = parser.get_definitions()
        
        required_categories = [
            'movement_types', 'player_roles', 'locations',
            'zone_purposes', 'team_designations', 'view_types',
            'diagram_categories'
        ]
        
        for category in required_categories:
            assert category in definitions
            assert len(definitions[category]) > 0
    
    @pytest.mark.asyncio
    async def test_parser_validation(self, parser):
        """Test parser validation methods."""
        # Test valid values
        assert parser.validate_pick_list_value('movement_types', 'pass') is True
        assert parser.validate_pick_list_value('player_roles', 'C') is True
        
        # Test invalid values
        assert parser.validate_pick_list_value('movement_types', 'invalid') is False
        assert parser.validate_pick_list_value('player_roles', 'QB') is False
    
    @pytest.mark.asyncio
    async def test_formation_presets(self):
        """Test that preset formations work correctly."""
        formations = [
            ("1-3-1 power play", 5, 'offensive'),
            ("2-3 forecheck", 5, 'offensive'),
            ("Diamond penalty kill", 4, 'defensive'),
            ("Breakout play", 5, 'defensive')
        ]
        
        for prompt, expected_players, expected_zone in formations:
            result = await generate_hockey_diagram(
                prompt=prompt,
                diagram_type="tactical"
            )
            
            assert result['success'] is True
            spec = result['diagram_spec']
            
            # Allow for goalie to be included or not
            assert expected_players <= len(spec['players']) <= expected_players + 1


class TestDiagramGeneration:
    """Test the actual diagram generation and file output."""
    
    @pytest.mark.asyncio
    async def test_png_generation(self):
        """Test PNG file generation."""
        result = await generate_hockey_diagram(
            prompt="Simple 2-1-2 formation",
            output_format="png"
        )
        
        assert result['success'] is True
        assert 'diagram_path' in result
        assert result['diagram_path'].endswith('.png')
        
        # Check file exists
        assert Path(result['diagram_path']).exists()
    
    @pytest.mark.asyncio
    async def test_base64_output(self):
        """Test base64 image output for small diagrams."""
        result = await generate_hockey_diagram(
            prompt="Two players passing",
            output_format="png"
        )
        
        assert result['success'] is True
        
        # Small diagrams should include base64
        if not result.get('file_output', False):
            assert 'base64_image' in result
            assert result['base64_image'].startswith('iVBOR')  # PNG header
    
    @pytest.mark.asyncio 
    async def test_generation_time_tracking(self):
        """Test that generation time is tracked."""
        result = await generate_hockey_diagram(
            prompt="Quick formation test"
        )
        
        assert result['success'] is True
        assert 'generation_time' in result
        assert isinstance(result['generation_time'], (int, float))
        assert result['generation_time'] > 0


if __name__ == "__main__":
    # Run tests with pytest if available
    try:
        pytest.main([__file__, "-v", "-s"])
    except:
        print("pytest not available, run with: pytest test_integration_full.py -v")