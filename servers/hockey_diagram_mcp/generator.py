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
        "X1": "X1", "X2": "X2", "X3": "X3",
        "X4": "X4", "X5": "X5", "XG": "XG"
    }
    
    # Team colors - matching reference images
    HOME_COLOR = "#1E88E5"  # Bright blue - matches reference images
    AWAY_COLOR = "#D32F2F"  # Bright red - matches reference images
    PUCK_COLOR = "#000000"  # Black
    COACH_COLOR = "#4CAF50"  # Green for coaches
    
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
            # Neutral zone (expanded for better tactical visibility)
            ax.set_xlim(-50, 50)
            ax.set_ylim(-42.5, 42.5)
            
    def _draw_players(self, ax, players: List[Player]):
        """Draw players on the rink."""
        for player in players:
            # Skip players with invalid coordinates
            if player.x is None or player.y is None:
                import logging
                logging.warning(f"Skipping player {player.position} with None coordinates")
                continue
                
            # Determine color - check for coach position
            if player.position in ['COACH', 'C', 'Coach']:
                color = self.COACH_COLOR
                position_label = 'C'
            elif player.team == "home":
                color = self.HOME_COLOR
                position_label = self.HOME_POSITIONS.get(player.position, player.position)
            else:
                color = self.AWAY_COLOR
                position_label = self.AWAY_POSITIONS.get(player.position, player.position)
            
            # Use simple label (just position)
            display_label = player.label if player.label else position_label
                
            # Draw filled player circle with white text - matching reference images
            circle = Circle(
                (player.x, player.y), 
                radius=3.5,  # Slightly bigger for better visibility
                facecolor=color,  # Filled with team color
                edgecolor=color,
                linewidth=1,
                zorder=100  # High zorder to ensure players are on top of rink lines
            )
            ax.add_patch(circle)
            
            # Add label inside circle with white text
            ax.text(
                player.x, player.y, display_label,  # Centered in circle
                ha='center', va='center',
                fontsize=10, fontweight='bold',
                color='white',  # White text on colored background
                zorder=101  # Higher than player circle
            )
            
            # Add puck indicator if player has puck
            if player.has_puck:
                puck = Circle(
                    (player.x + 3, player.y - 3),
                    radius=1,
                    facecolor=self.PUCK_COLOR,
                    zorder=102  # Highest priority for puck visibility
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
                
            # Check if path goes through nets and adjust if needed
            start, end = self._adjust_path_around_nets(start, end)
                
            # Draw based on movement type
            if movement.movement_type == "skating":
                # Solid arrow for skating
                arrow = FancyArrowPatch(
                    start, end,
                    arrowstyle='->,head_width=2.0,head_length=1.5',
                    color='black',
                    linewidth=2,
                    zorder=90  # High zorder for visibility
                )
            elif movement.movement_type == "pass":
                # Dashed line for passes
                arrow = FancyArrowPatch(
                    start, end,
                    arrowstyle='->,head_width=2.0,head_length=1.5',
                    color='black',
                    linewidth=2,
                    linestyle='dashed',
                    zorder=90  # High zorder for visibility
                )
            elif movement.movement_type == "shot":
                # Thick arrow for shots
                arrow = FancyArrowPatch(
                    start, end,
                    arrowstyle='->,head_width=2.5,head_length=2.0',
                    color='black',
                    linewidth=3,
                    zorder=90  # High zorder for visibility
                )
            else:  # forecheck or other
                # Curved arrow for forechecking
                arrow = FancyArrowPatch(
                    start, end,
                    arrowstyle='->,head_width=2.0,head_length=1.5',
                    color='gray',
                    linewidth=2,
                    connectionstyle="arc3,rad=0.3",
                    zorder=90  # High zorder for visibility
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
                    zorder=95  # Even higher for movement labels
                )
    
    def _adjust_path_around_nets(self, start: Tuple[float, float], end: Tuple[float, float]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Adjust movement path to avoid going through goal nets.
        
        Args:
            start: Starting coordinates (x, y)
            end: Ending coordinates (x, y)
            
        Returns:
            Adjusted (start, end) coordinates
        """
        # NHL goal net positions (approximate)
        home_net_center = (-89, 0)  # Home team defends this net
        away_net_center = (89, 0)   # Away team defends this net
        net_width = 6  # Goal width
        net_depth = 4  # Goal depth
        
        # Check if path intersects with either net
        adjusted_start, adjusted_end = start, end
        
        # Check home net (left side)
        if self._path_intersects_net(start, end, home_net_center, net_width, net_depth):
            # Adjust path to go around the net
            adjusted_start, adjusted_end = self._route_around_net(start, end, home_net_center, net_width, net_depth)
            
        # Check away net (right side) - only if not already adjusted
        elif self._path_intersects_net(start, end, away_net_center, net_width, net_depth):
            # Adjust path to go around the net  
            adjusted_start, adjusted_end = self._route_around_net(start, end, away_net_center, net_width, net_depth)
            
        return adjusted_start, adjusted_end
    
    def _path_intersects_net(self, start: Tuple[float, float], end: Tuple[float, float], 
                            net_center: Tuple[float, float], net_width: float, net_depth: float) -> bool:
        """Check if a straight line path intersects with a goal net area."""
        net_x, net_y = net_center
        # Define net rectangle bounds
        net_left = net_x - net_depth/2
        net_right = net_x + net_depth/2
        net_bottom = net_y - net_width/2
        net_top = net_y + net_width/2
        
        # Simple line-rectangle intersection check
        # Check if the path line segment intersects with the net rectangle
        x1, y1 = start
        x2, y2 = end
        
        # Check if either endpoint is inside the net
        if (net_left <= x1 <= net_right and net_bottom <= y1 <= net_top) or \
           (net_left <= x2 <= net_right and net_bottom <= y2 <= net_top):
            return True
            
        # Check if line crosses any of the net rectangle edges
        # This is a simplified check - for production might want more sophisticated intersection
        if (x1 < net_left < x2 or x2 < net_left < x1) and \
           (min(y1, y2) <= net_y <= max(y1, y2)):
            return True
            
        if (x1 < net_right < x2 or x2 < net_right < x1) and \
           (min(y1, y2) <= net_y <= max(y1, y2)):
            return True
            
        return False
    
    def _route_around_net(self, start: Tuple[float, float], end: Tuple[float, float],
                         net_center: Tuple[float, float], net_width: float, net_depth: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Route path around a net by choosing the shorter side."""
        net_x, net_y = net_center
        
        # Calculate which side of the net to go around (top or bottom)
        start_y_offset = start[1] - net_y
        end_y_offset = end[1] - net_y
        
        # Choose the side based on average Y position
        avg_y_offset = (start_y_offset + end_y_offset) / 2
        
        if avg_y_offset > 0:
            # Route around the top of the net
            clearance_y = net_y + net_width/2 + 5  # 5 feet clearance
        else:
            # Route around the bottom of the net
            clearance_y = net_y - net_width/2 - 5  # 5 feet clearance
            
        # For now, just adjust the Y coordinates to avoid the net
        # In a more sophisticated implementation, might add intermediate waypoints
        adjusted_start = (start[0], clearance_y if abs(start[0] - net_x) < 15 else start[1])
        adjusted_end = (end[0], clearance_y if abs(end[0] - net_x) < 15 else end[1])
        
        return adjusted_start, adjusted_end
            
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