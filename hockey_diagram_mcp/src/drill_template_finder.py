"""
Drill Template Finder - Discover and reuse drill templates and components.
Helps the hockey-diagram-expert agent find matching templates or components to start from.
"""

import json
import os
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path


class DrillTemplateFinder:
    """Find and suggest drill templates based on description keywords."""
    
    def __init__(self, template_dir: str = None):
        if template_dir is None:
            # Use absolute path relative to the src directory
            self.template_dir = Path(__file__).parent.parent / "templates"
        else:
            self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Define drill pattern library with keywords
        self.drill_patterns = {
            'give_and_go': {
                'keywords': ['give and go', 'give-and-go', 'quick pass', 'one-two'],
                'template_file': 'give_and_go_base.json',
                'components': ['pivot_player', 'moving_player', 'pass_sequence'],
                'description': 'Player at stationary position exchanges passes with moving player'
            },
            'cross_ice': {
                'keywords': ['cross ice', 'cross-ice', 'opposite side', 'far side'],
                'template_file': 'cross_ice_base.json',
                'components': ['cross_movement', 'player_queue'],
                'description': 'Movement across the width of the ice (Y-axis change 40+ units)'
            },
            'breakout': {
                'keywords': ['breakout', 'break out', 'exit zone', 'd to d'],
                'template_file': 'breakout_base.json',
                'components': ['d_to_d_pass', 'wing_routes', 'center_support'],
                'description': 'Defensive zone exit pattern with multiple passing options'
            },
            'cycle': {
                'keywords': ['cycle', 'cycling', 'board play', 'corner work'],
                'template_file': 'cycle_base.json',
                'components': ['corner_movement', 'board_pass', 'net_front'],
                'description': 'Offensive zone puck movement along boards and corners'
            },
            'rush': {
                'keywords': ['rush', '2 on 1', '3 on 2', 'odd man', 'transition'],
                'template_file': 'rush_base.json',
                'components': ['lanes', 'passing_options', 'trailer'],
                'description': 'Transition play with numerical advantage'
            },
            'forecheck': {
                'keywords': ['forecheck', '2-1-2', '1-2-2', 'pressure', 'aggressive'],
                'template_file': 'forecheck_base.json',
                'components': ['f1_pressure', 'f2_support', 'defensive_positioning'],
                'description': 'Offensive zone pressure system'
            },
            'power_play': {
                'keywords': ['power play', 'powerplay', 'pp', 'umbrella', '1-3-1'],
                'template_file': 'power_play_base.json',
                'components': ['umbrella_setup', 'passing_lanes', 'net_front_presence'],
                'description': 'Special teams offensive setup'
            },
            'shooting': {
                'keywords': ['shooting', 'shot', 'one-timer', 'screen', 'tip'],
                'template_file': 'shooting_base.json',
                'components': ['shooting_lane', 'screen_position', 'rebound_coverage'],
                'description': 'Shooting drill with various release points'
            },
            'skating': {
                'keywords': ['skating', 'edges', 'crossovers', 'pivots', 'stops'],
                'template_file': 'skating_base.json',
                'components': ['skating_pattern', 'cone_layout', 'return_path'],
                'description': 'Pure skating drill focusing on technique'
            },
            'small_area': {
                'keywords': ['small area', 'small game', 'battle', '1v1', '2v2', '3v3'],
                'template_file': 'small_area_base.json',
                'components': ['zone_boundaries', 'mini_nets', 'player_matchups'],
                'description': 'Confined space competitive drill'
            }
        }
        
        # Component generators (references to utility functions)
        self.component_generators = {
            'player_queue': 'create_player_queue',
            'cone_pattern': 'create_cone_pattern', 
            'shooting_sequence': 'create_shooting_sequence',
            'pass_sequence': 'create_pass_sequence',
            'defensive_box': 'create_defensive_box',
            'neutral_zone_setup': 'create_neutral_zone_setup'
        }
    
    def find_matching_templates(self, description: str) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Find drill templates that match the given description.
        
        Args:
            description: Natural language drill description
            
        Returns:
            Tuple of (matching_templates, available_components)
        """
        description_lower = description.lower()
        matches = []
        
        # Search for keyword matches
        for pattern_name, pattern_info in self.drill_patterns.items():
            # Check if any keyword matches
            if any(keyword in description_lower for keyword in pattern_info['keywords']):
                # Try to load the template if it exists
                template_path = self.template_dir / pattern_info['template_file']
                template_data = None
                
                if template_path.exists():
                    try:
                        with open(template_path, 'r') as f:
                            template_data = json.load(f)
                    except:
                        pass
                
                matches.append({
                    'name': pattern_name,
                    'confidence': self._calculate_confidence(description_lower, pattern_info['keywords']),
                    'template_file': str(template_path),
                    'template_data': template_data,
                    'components': pattern_info['components'],
                    'description': pattern_info['description']
                })
        
        # Sort by confidence
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Return matches and component generators
        return matches, self.component_generators
    
    def _calculate_confidence(self, description: str, keywords: List[str]) -> float:
        """Calculate match confidence based on keyword matches."""
        match_count = sum(1 for keyword in keywords if keyword in description)
        return match_count / len(keywords) if keywords else 0.0
    
    def get_component_code(self, component_name: str) -> str:
        """
        Get the code snippet for a specific component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Python code snippet for the component
        """
        component_snippets = {
            'pivot_player': """
# Pivot player (stationary at faceoff dot)
players.append(Player(
    type='forward',
    position='F1', 
    coordinates={'x': -69, 'y': 22.5},  # Left faceoff dot
    team='home',
    has_puck=True,
    label='F1'
))""",
            'moving_player': """
# Moving player (starts at goal line)
players.append(Player(
    type='forward',
    position='F2',
    coordinates={'x': -69, 'y': 7.5},  # Below faceoff circle
    team='home',
    has_puck=False,
    label='F2'
))""",
            'pass_sequence': """
# Pass sequence
movements.extend([
    Movement(
        type='pass',
        from_pos={'x': -69, 'y': 22.5},
        to_pos={'x': -69, 'y': 7.5},
        style='dotted',
        label='Pass 1'
    ),
    Movement(
        type='pass',
        from_pos={'x': -69, 'y': 15},
        to_pos={'x': -69, 'y': 22.5},
        style='dotted',
        label='Return'
    )
])""",
            'cross_movement': """
# Cross-ice movement with curve
from drill_utilities import create_smooth_path
movements.append(Movement(
    type='skate',
    from_pos={'x': -69, 'y': 22.5},  # Left circle
    to_pos={'x': 69, 'y': -22.5},    # Right circle
    waypoints=create_smooth_path(
        {'x': -69, 'y': 22.5},
        {'x': 69, 'y': -22.5},
        num_points=5
    ),
    style='solid',
    label='Cross ice'
))""",
            'player_queue': """
# Player queue using utility
from drill_utilities import create_player_queue
players.extend(create_player_queue(
    lead_pos={'x': -20, 'y': -38},
    lead_label='X1',
    queue_size=3,
    has_puck=True,
    team='home'
))""",
            'cone_pattern': """
# Cone pattern for skating drill
from drill_utilities import create_equipment_zone
zones.extend([
    create_equipment_zone('cone', {'x': -50, 'y': 0}, size=2.0),
    create_equipment_zone('cone', {'x': -25, 'y': 0}, size=2.0),
    create_equipment_zone('cone', {'x': 0, 'y': 0}, size=2.0),
    create_equipment_zone('cone', {'x': 25, 'y': 0}, size=2.0)
])"""
        }
        
        return component_snippets.get(component_name, f"# Component '{component_name}' not found")
    
    def suggest_drill_structure(self, description: str) -> Dict[str, Any]:
        """
        Suggest a complete drill structure based on the description.
        
        Args:
            description: Natural language drill description
            
        Returns:
            Dictionary with suggested structure and code snippets
        """
        matches, components = self.find_matching_templates(description)
        
        suggestion = {
            'best_match': matches[0] if matches else None,
            'alternative_matches': matches[1:3] if len(matches) > 1 else [],
            'recommended_components': [],
            'code_snippets': [],
            'setup_notes': []
        }
        
        if matches:
            best_match = matches[0]
            
            # Add recommended components
            for component in best_match['components']:
                suggestion['recommended_components'].append({
                    'name': component,
                    'code': self.get_component_code(component)
                })
            
            # Add setup notes based on pattern
            pattern_name = best_match['name']
            if pattern_name == 'give_and_go':
                suggestion['setup_notes'] = [
                    "Place pivot player at faceoff dot",
                    "Moving player starts at goal line",
                    "Use waypoints for curved skating path",
                    "Ensure pass timing matches skating speed"
                ]
            elif pattern_name == 'cross_ice':
                suggestion['setup_notes'] = [
                    "Y-axis change should be 40+ units",
                    "Add slight curve for realistic movement",
                    "Consider using both circles in same zone"
                ]
            elif pattern_name == 'small_area':
                suggestion['setup_notes'] = [
                    "Define zone boundaries clearly",
                    "Consider using mini-nets or cones as goals",
                    "Keep view focused on play area"
                ]
        
        return suggestion


# Convenience function for agent to use
def find_drill_template(description: str) -> Tuple[List[Dict], Dict[str, str]]:
    """
    Main entry point for the hockey-diagram-expert agent.
    
    Args:
        description: Natural language drill description
        
    Returns:
        Tuple of (matching_templates, available_components)
        
    Example:
        templates, components = find_drill_template("give and go shooting drill")
    """
    finder = DrillTemplateFinder()
    return finder.find_matching_templates(description)


def get_drill_suggestion(description: str) -> Dict[str, Any]:
    """
    Get a complete drill structure suggestion.
    
    Args:
        description: Natural language drill description
        
    Returns:
        Dictionary with suggested structure and code snippets
    """
    finder = DrillTemplateFinder()
    return finder.suggest_drill_structure(description)