"""
Hockey diagram generator using sportypy for precise NHL-regulation rinks.
Generates tactical diagrams programmatically with exact specifications.
"""

import io
import base64
from typing import Dict, List, Optional, Tuple, Literal, Union
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
import numpy as np
from sportypy.surfaces.hockey import NHLRink
from zone_grid import zone_grid

@dataclass
class Player:
    """Represents a player on the ice."""
    position: str  # C, RW, LW, LD, RD, G
    x: float
    y: float
    team: Literal["home", "away"]
    has_puck: bool = False
    label: Optional[str] = None  # Custom label to display (e.g., zone name)
    zone: Optional[str] = None  # Zone name for display purposes
    
@dataclass
class Movement:
    """Represents a movement or pass."""
    from_position: str  # Player position or coordinates
    to_position: Union[Tuple[float, float], str]  # Coordinates or player position
    movement_type: Literal["skating", "pass", "shot", "forecheck", "carry", "lateral", "support"]
    label: Optional[str] = None  # Label to display on the movement arrow
    
@dataclass 
class CoverageZone:
    """Represents a coverage or pressure zone."""
    zone_type: str  # "coverage", "pressure", "neutral"
    area: Union[str, Tuple[float, float, float, float]]  # Named area or bounds
    team: Literal["home", "away"]
    opacity: float = 0.2  # Zone opacity for better visibility

class HockeyDiagramGenerator:
    """Generates precise hockey tactical diagrams using sportypy."""
    
    # Standard player position markers
    HOME_POSITIONS = {
        "C": "C", "RW": "RW", "LW": "LW", 
        "LD": "LD", "RD": "RD", "G": "G"
    }
    
    AWAY_POSITIONS = {
        "X1": "X�", "X2": "X�", "X3": "X�",
        "X4": "X�", "X5": "X�", "XG": "XG"
    }
    
    # Team colors
    HOME_COLOR = "#1E40AF"  # Blue
    AWAY_COLOR = "#DC2626"  # Red
    PUCK_COLOR = "#000000"  # Black
    
    def __init__(self, rink_config: Optional[Dict] = None):
        """Initialize generator with optional rink configuration."""
        self.rink_config = rink_config or {}
        
    def generate_diagram(
        self,
        players: List[Player],
        movements: Optional[List[Movement]] = None,
        zones: Optional[List[CoverageZone]] = None,
        view: Literal["full", "offensive", "defensive", "neutral"] = "full",
        title: Optional[str] = None,
        output_format: Literal["png", "svg"] = "png"
    ) -> str:
        """
        Generate a hockey diagram and return as base64 encoded string.
        
        Args:
            players: List of players with positions
            movements: List of movements/passes
            zones: List of coverage zones
            view: Rink view (full, offensive zone, etc.)
            title: Diagram title
            output_format: Output format (png or svg)
            
        Returns:
            Base64 encoded image string
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Draw NHL rink using sportypy
        rink = NHLRink(**self.rink_config)
        rink.draw(ax=ax)
        
        # Set view based on parameter
        self._set_view(ax, view)
        
        # Draw zones if specified
        if zones:
            self._draw_zones(ax, zones)
            
        # Draw players
        self._draw_players(ax, players)
        
        # Draw movements
        if movements:
            self._draw_movements(ax, players, movements)
            
        # Add title if specified
        if title:
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            
        # Remove axis labels for cleaner look
        ax.set_xlabel('')
        ax.set_ylabel('')
        
        # Save to buffer
        buffer = io.BytesIO()
        if output_format == "png":
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        else:
            plt.savefig(buffer, format='svg', bbox_inches='tight')
        plt.close()
        
        # Encode to base64
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        return image_base64
    
    def _set_view(self, ax, view: str):
        """Set the axis limits based on the view."""
        if view == "full":
            # Full rink view (default sportypy view)
            pass
        elif view == "offensive":
            # Offensive zone only
            ax.set_xlim(25, 100)
            ax.set_ylim(-42.5, 42.5)
        elif view == "defensive":
            # Defensive zone only
            ax.set_xlim(-100, -25)
            ax.set_ylim(-42.5, 42.5)
        elif view == "neutral":
            # Neutral zone
            ax.set_xlim(-25, 25)
            ax.set_ylim(-42.5, 42.5)
            
    def _draw_players(self, ax, players: List[Player]):
        """Draw players on the rink."""
        for player in players:
            # Skip players with invalid coordinates
            if player.x is None or player.y is None:
                import logging
                logging.warning(f"Skipping player {player.position} with None coordinates")
                continue
                
            # Determine color
            if player.team == "home":
                color = self.HOME_COLOR
                position_label = self.HOME_POSITIONS.get(player.position, player.position)
            else:
                color = self.AWAY_COLOR
                position_label = self.AWAY_POSITIONS.get(player.position, player.position)
            
            # Create combined label (position + zone/custom label)
            if player.label:
                # Use custom label if provided
                display_label = f"{position_label}\n({player.label})"
            elif player.zone:
                # Use zone name if provided
                display_label = f"{position_label}\n{player.zone}"
            else:
                # Just show position
                display_label = position_label
                
            # Draw player circle
            circle = Circle(
                (player.x, player.y), 
                radius=3,
                facecolor='white',
                edgecolor=color,
                linewidth=2,
                zorder=10
            )
            ax.add_patch(circle)
            
            # Add combined label (position + zone)
            ax.text(
                player.x, player.y - 5, display_label,  # Offset below circle
                ha='center', va='top',
                fontsize=8, fontweight='bold',
                color=color,
                zorder=11,
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor=color, alpha=0.8)
            )
            
            # Add puck indicator if player has puck
            if player.has_puck:
                puck = Circle(
                    (player.x + 3, player.y - 3),
                    radius=1,
                    facecolor=self.PUCK_COLOR,
                    zorder=12
                )
                ax.add_patch(puck)
                
    def _draw_movements(self, ax, players: List[Player], movements: List[Movement]):
        """Draw movement arrows and passes."""
        # Create player position map for lookups (skip players with None coordinates)
        player_map = {p.position: (p.x, p.y) for p in players if p.x is not None and p.y is not None}
        
        for movement in movements:
            # Get start position
            if isinstance(movement.from_position, str):
                start = player_map.get(movement.from_position, (0, 0))
            else:
                start = movement.from_position
                
            # Get end position
            if isinstance(movement.to_position, str):
                end = player_map.get(movement.to_position, (0, 0))
            else:
                end = movement.to_position
                
            # Draw based on movement type
            if movement.movement_type == "skating":
                # Solid arrow for skating
                arrow = FancyArrowPatch(
                    start, end,
                    arrowstyle='->,head_width=0.8,head_length=0.4',
                    color='black',
                    linewidth=2,
                    zorder=5
                )
            elif movement.movement_type == "pass":
                # Dashed line for passes
                arrow = FancyArrowPatch(
                    start, end,
                    arrowstyle='->,head_width=0.8,head_length=0.4',
                    color='black',
                    linewidth=2,
                    linestyle='dashed',
                    zorder=5
                )
            elif movement.movement_type == "shot":
                # Thick arrow for shots
                arrow = FancyArrowPatch(
                    start, end,
                    arrowstyle='->,head_width=1.0,head_length=0.5',
                    color='black',
                    linewidth=3,
                    zorder=5
                )
            else:  # forecheck or other
                # Curved arrow for forechecking
                arrow = FancyArrowPatch(
                    start, end,
                    arrowstyle='->,head_width=0.8,head_length=0.4',
                    color='gray',
                    linewidth=2,
                    connectionstyle="arc3,rad=0.3",
                    zorder=5
                )
                
            ax.add_patch(arrow)
            
            # Add movement label if provided
            if hasattr(movement, 'label') and movement.label:
                # Calculate midpoint of the arrow
                mid_x = (start[0] + end[0]) / 2
                mid_y = (start[1] + end[1]) / 2
                
                # Add label with background for visibility
                ax.text(
                    mid_x, mid_y, movement.label,
                    ha='center', va='center',
                    fontsize=7, fontweight='bold',
                    color='black',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow', alpha=0.7),
                    zorder=6
                )
            
    def _draw_zones(self, ax, zones: List[CoverageZone]):
        """Draw coverage or pressure zones."""
        for zone in zones:
            color = self.HOME_COLOR if zone.team == "home" else self.AWAY_COLOR
            
            # Handle named zones
            if isinstance(zone.area, str):
                bounds = self._get_zone_bounds(zone.area)
            else:
                bounds = zone.area
                
            if bounds:
                x, y, width, height = bounds
                # Use zone opacity
                opacity = zone.opacity
                rect = Rectangle(
                    (x, y), width, height,
                    facecolor=color,
                    alpha=opacity,
                    zorder=1
                )
                ax.add_patch(rect)
                
    def _get_zone_bounds(self, area_name: str) -> Optional[Tuple[float, float, float, float]]:
        """Get bounds for named areas using ZoneGrid system."""
        
        # First check if it's a ZoneGrid zone name
        if area_name in zone_grid.zone_lookup:
            zone = zone_grid.zone_lookup[area_name]
            # Return as (x, y, width, height) for Rectangle
            width = zone.x_max - zone.x_min
            height = zone.y_max - zone.y_min
            return (zone.x_min, zone.y_min, width, height)
        
        # Handle legacy zone names and parser output format
        zone_bounds = {
            "slot": (-20, -8, 40, 16),  # Slot area
            "point": (-30, 15, 60, 10),  # Point area
            "crease": (-6, -4, 12, 8),   # Goal crease
            "high_slot": (-20, -12, 40, 24),  # High slot
            "low_zone": (-100, -42.5, 30, 85),  # Low defensive zone
            
            # Fix zone name mismatch - parser outputs these names:
            "left_corner": (80, -42.5, 20, 20),  # Left corner (offensive)
            "right_corner": (80, 22.5, 20, 20),  # Right corner (offensive)
            "defensive_left_corner": (-100, -42.5, 20, 20),  # Left corner (defensive)
            "defensive_right_corner": (-100, 22.5, 20, 20),  # Right corner (defensive)
            
            # Keep legacy names for backward compatibility
            "corner_left": (-100, -42.5, 20, 20),  # Left corner (legacy)
            "corner_right": (-100, 22.5, 20, 20),  # Right corner (legacy)
        }
        return zone_bounds.get(area_name)
    
    def save_to_file(self, diagram_base64: str, filename: str, format: str = "png"):
        """Save the base64 diagram to a file."""
        image_data = base64.b64decode(diagram_base64)
        with open(filename, 'wb') as f:
            f.write(image_data)


# Utility function for quick diagram generation
def create_hockey_diagram(
    description: str,
    players: List[Dict],
    movements: Optional[List[Dict]] = None,
    zones: Optional[List[Dict]] = None,
    **kwargs
) -> str:
    """
    Quick helper to create a hockey diagram from dictionaries.
    
    Args:
        description: Diagram description/title
        players: List of player dicts with position, x, y, team
        movements: List of movement dicts
        zones: List of zone dicts
        **kwargs: Additional arguments for generate_diagram
        
    Returns:
        Base64 encoded diagram
    """
    generator = HockeyDiagramGenerator()
    
    # Convert dicts to dataclasses
    player_objects = [Player(**p) for p in players]
    movement_objects = [Movement(**m) for m in movements] if movements else None
    zone_objects = [CoverageZone(**z) for z in zones] if zones else None
    
    return generator.generate_diagram(
        players=player_objects,
        movements=movement_objects,
        zones=zone_objects,
        title=description,
        **kwargs
    )