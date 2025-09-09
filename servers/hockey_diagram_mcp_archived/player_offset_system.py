"""
Player offset system for handling overlapping players in hockey diagrams.

This module provides intelligent offset calculation to prevent players
from overlapping when they're at the same coordinates.
"""

from typing import List, Dict, Tuple
import math
import logging

logger = logging.getLogger(__name__)


class PlayerOffsetCalculator:
    """Calculate offsets for players to prevent overlapping."""
    
    # Standard offset distance (in feet)
    OFFSET_DISTANCE = 3
    
    def calculate_offsets(self, players: List[Dict]) -> List[Dict]:
        """
        Calculate offsets for all players to prevent overlapping.
        
        Args:
            players: List of player dictionaries with x, y, zone, position, team
            
        Returns:
            Updated list of players with adjusted x, y coordinates
        """
        players_copy = [p.copy() for p in players]
        position_groups = self._group_by_position(players_copy)
        
        for pos_key, player_indices in position_groups.items():
            if len(player_indices) > 1:
                self._apply_offsets_to_group(players_copy, player_indices)
        
        return players_copy
    
    def _group_by_position(self, players: List[Dict]) -> Dict[Tuple[float, float], List[int]]:
        """Group players by their x,y coordinates."""
        position_groups = {}
        
        for i, player in enumerate(players):
            x = player.get('x', 0)
            y = player.get('y', 0)
            
            # Skip players with None coordinates
            if x is None or y is None:
                continue
                
            pos_key = (x, y)
            if pos_key not in position_groups:
                position_groups[pos_key] = []
            position_groups[pos_key].append(i)
        
        return position_groups
    
    def _apply_offsets_to_group(self, players: List[Dict], indices: List[int]):
        """Apply offsets to a group of overlapping players."""
        # Check if opposing teams
        teams = set(players[i].get('team', 'home') for i in indices)
        
        if len(teams) > 1:
            # Opposing players - special handling
            self._apply_opposing_offsets(players, indices)
        else:
            # Same team - arrange in formation
            self._apply_team_offsets(players, indices)
    
    def _apply_opposing_offsets(self, players: List[Dict], indices: List[int]):
        """Apply offsets for opposing players (e.g., F1 pressuring D1)."""
        # Separate by team
        home_indices = []
        away_indices = []
        
        for i in indices:
            if players[i].get('team', 'home') == 'home':
                home_indices.append(i)
            else:
                away_indices.append(i)
        
        # Determine who has the puck
        puck_carrier_idx = None
        for i in indices:
            if players[i].get('has_puck'):
                puck_carrier_idx = i
                break
        
        # Apply offsets based on zone and puck possession
        for i in away_indices:
            zone = players[i].get('zone', '')
            
            if 'behind_net' in zone:
                # Forechecking player slightly in front
                players[i]['y'] -= self.OFFSET_DISTANCE
            elif 'corner' in zone:
                # Pressure from center ice side
                if 'left' in zone:
                    players[i]['x'] += self.OFFSET_DISTANCE
                else:
                    players[i]['x'] -= self.OFFSET_DISTANCE
            else:
                # General pressure position
                players[i]['y'] -= self.OFFSET_DISTANCE * 0.5
                
        # Home team adjustments
        for i in home_indices:
            if i == puck_carrier_idx:
                # Puck carrier maintains position
                continue
            else:
                # Support players slightly back
                players[i]['y'] += self.OFFSET_DISTANCE * 0.5
    
    def _apply_team_offsets(self, players: List[Dict], indices: List[int]):
        """Apply offsets for same-team players."""
        n_players = len(indices)
        
        if n_players == 2:
            # Side by side
            players[indices[0]]['x'] -= self.OFFSET_DISTANCE
            players[indices[1]]['x'] += self.OFFSET_DISTANCE
        elif n_players == 3:
            # Triangle formation
            players[indices[0]]['x'] -= self.OFFSET_DISTANCE
            players[indices[1]]['x'] += self.OFFSET_DISTANCE
            players[indices[2]]['y'] -= self.OFFSET_DISTANCE
        else:
            # Circle formation for 4+
            angle_step = 2 * math.pi / n_players
            for i, idx in enumerate(indices):
                angle = i * angle_step
                players[idx]['x'] += self.OFFSET_DISTANCE * math.cos(angle)
                players[idx]['y'] += self.OFFSET_DISTANCE * math.sin(angle)


def apply_player_offsets(diagram_spec: Dict) -> Dict:
    """
    Apply offsets to players in a diagram specification.
    
    Args:
        diagram_spec: The diagram specification with players list
        
    Returns:
        Updated specification with offset players
    """
    if 'players' not in diagram_spec or not diagram_spec['players']:
        return diagram_spec
    
    calculator = PlayerOffsetCalculator()
    diagram_spec['players'] = calculator.calculate_offsets(diagram_spec['players'])
    
    return diagram_spec