"""
Hockey Diagram Builder using sportypy and Hockey Canada template.
Builds diagrams based on the hockey_diagram_spec.md specification.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, Polygon, Path, PathPatch, Arc
import numpy as np
from sportypy.surfaces.hockey import NHLRink
from typing import Dict, List, Tuple, Optional, Literal
from dataclasses import dataclass, asdict
from datetime import datetime
import os

@dataclass
class Player:
    """Player element per specification."""
    type: Literal["forward", "defense", "goalie", "coach", "opponent"]
    position: str  # C, LW, RW, LD, RD, G, X1-X5
    coordinates: Dict[str, float]  # {"x": 0, "y": 0}
    team: Literal["home", "away"] = "home"
    has_puck: bool = False
    label: Optional[str] = None
    number: Optional[int] = None

@dataclass
class Movement:
    """Movement element per specification."""
    type: Literal["carry", "pass", "shot", "drop_pass", "skate", "backward", "lateral", "pressure"]
    from_pos: Dict[str, float] | str  # Coordinates or player_id
    to_pos: Dict[str, float] | str
    style: Literal["solid", "dashed", "dotted", "wavy"] = "solid"
    with_puck: bool = False
    label: Optional[str] = None

@dataclass
class Zone:
    """Zone element per specification."""
    type: Literal["coverage", "pressure", "lane"]
    shape: Literal["rectangle", "circle", "polygon"]
    bounds: Dict[str, float]  # x, y, width, height or radius
    team: Literal["home", "away"]
    opacity: float = 0.2
    color: str = "blue"
    label: Optional[str] = None

@dataclass
class Annotation:
    """Text annotation per specification."""
    text: str
    position: Dict[str, float]
    size: Literal["small", "medium", "large"] = "medium"
    style: Literal["normal", "bold"] = "normal"

@dataclass
class DiagramSpec:
    """Complete diagram specification."""
    title: str
    rink: Dict[str, any]
    players: List[Player]
    movements: List[Movement]
    zones: List[Zone]
    annotations: List[Annotation]
    metadata: Dict[str, any]

class DiagramBuilder:
    """Builds hockey diagrams from specifications using sportypy."""
    
    # Hockey Canada Template Colors
    HOME_COLOR = "#0066CC"  # Blue
    AWAY_COLOR = "#CC0000"  # Red
    PUCK_COLOR = "#000000"  # Black
    CONE_COLOR = "#FF6600"  # Orange
    
    def __init__(self):
        self.fig = None
        self.ax = None
        self.rink = None
        self.player_positions = {}  # Track player positions for movements
        
    def build(self, spec: DiagramSpec, output_path: str) -> str:
        """
        Build a diagram from specification and save to file.
        
        Returns:
            Path to the saved diagram
        """
        # Create figure
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        
        # Draw rink using sportypy with lower z-order
        self.rink = NHLRink()
        self.rink.draw(ax=self.ax)
        
        # Set view based on spec
        self._set_view(spec.rink.get("view", "full"))
        
        # Draw elements in order with higher z-order
        if spec.zones:
            self._draw_zones(spec.zones)
        if spec.players:
            self._draw_players(spec.players)
        if spec.movements:
            self._draw_movements(spec.movements)
        if spec.annotations:
            self._draw_annotations(spec.annotations)
            
        # Add title
        if spec.title:
            self.ax.set_title(spec.title, fontsize=16, fontweight='bold', pad=20)
            
        # Force redraw to ensure our elements are on top
        self.fig.canvas.draw()
        
        # Save diagram
        self.fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return output_path
        
    def _set_view(self, view: str):
        """Set the rink view (full, offensive, defensive, neutral, half)."""
        if view == "offensive":
            self.ax.set_xlim(25, 100)
            self.ax.set_ylim(-42.5, 42.5)
        elif view == "defensive":
            self.ax.set_xlim(-100, -25)
            self.ax.set_ylim(-42.5, 42.5)
        elif view == "neutral":
            self.ax.set_xlim(-25, 25)
            self.ax.set_ylim(-42.5, 42.5)
        elif view == "half":
            self.ax.set_xlim(0, 100)
            self.ax.set_ylim(-42.5, 42.5)
        # else: full view (default sportypy view)
        
    def _draw_players(self, players: List[Player]):
        """Draw players on the rink."""
        for player in players:
            x, y = player.coordinates["x"], player.coordinates["y"]
            color = self.HOME_COLOR if player.team == "home" else self.AWAY_COLOR
            
            # Store position for movement references
            self.player_positions[player.position] = (x, y)
            
            # Draw player based on type (Hockey Canada symbols)
            if player.type == "forward":
                # Open circle
                circle = Circle((x, y), 2, fill=False, edgecolor=color, linewidth=2, zorder=10)
                self.ax.add_patch(circle)
                label = player.label or player.position
                
            elif player.type == "defense":
                # Triangle
                triangle = Polygon(
                    [(x, y+2.5), (x-2, y-2), (x+2, y-2)],
                    fill=False, edgecolor=color, linewidth=2, zorder=10
                )
                self.ax.add_patch(triangle)
                label = player.label or player.position
                
            elif player.type == "goalie":
                # Half-filled circle with higher z-order
                circle = Circle((x, y), 2, facecolor=color, alpha=0.5, edgecolor=color, linewidth=2, zorder=12)
                self.ax.add_patch(circle)
                label = "G"
                
            elif player.type == "coach":
                # Circle with C
                circle = Circle((x, y), 2, fill=False, edgecolor=color, linewidth=2, zorder=10)
                self.ax.add_patch(circle)
                label = "C"
                
            elif player.type == "puck":
                # Just a black dot for puck
                self.ax.plot(x, y, 'o', markersize=6, color='black', zorder=10)
                continue  # No label needed
                
            else:  # opponent
                # X marker
                self.ax.plot(x, y, 'x', markersize=12, markeredgewidth=2, color=color, zorder=10)
                label = player.position
                
            # Add label
            if player.type not in ["opponent", "puck"]:
                label_z_order = 13 if player.type == "goalie" else 11
                self.ax.text(x, y, label, ha='center', va='center', 
                           fontsize=8, fontweight='bold', color='white' if player.type == "goalie" else color, zorder=label_z_order)
                
            # Add puck if player has it
            if player.has_puck:
                puck = Circle((x + 0.5, y + 0.5), 0.8, color=self.PUCK_COLOR, zorder=12)
                self.ax.add_patch(puck)
                
    def _draw_movements(self, movements: List[Movement]):
        """Draw movement arrows and lines."""
        for movement in movements:
            # Resolve positions
            if isinstance(movement.from_pos, str):
                start = self.player_positions.get(movement.from_pos, (0, 0))
            else:
                start = (movement.from_pos["x"], movement.from_pos["y"])
                
            if isinstance(movement.to_pos, str):
                end = self.player_positions.get(movement.to_pos, (0, 0))
            else:
                end = (movement.to_pos["x"], movement.to_pos["y"])
                
            # Style based on movement type (Hockey Canada template)
            if movement.type == "carry":
                # Solid arrow for puck carrying
                style = "-"
                linewidth = 3
                color = "black"
            elif movement.type == "pass":
                # Dotted arrow for passing
                style = ":"
                linewidth = 2
                color = "black"
            elif movement.type == "shot":
                # Dashed arrow for shooting
                style = "--"
                linewidth = 2.5
                color = "black"
            elif movement.type == "drop_pass":
                # Solid with hook
                style = "-"
                linewidth = 2
                color = "black"
                # Add hook indicator
                self.ax.plot([start[0], start[0]-2], [start[1], start[1]], 
                           'k-', linewidth=2)
            elif movement.type == "backward":
                # Wavy line for backward skating
                self._draw_wavy_line(start, end)
                continue
            elif movement.type == "lateral":
                # Double arrow for lateral movement
                self._draw_double_arrow(start, end)
                continue
            elif movement.type == "pressure":
                # Thick solid line for defensive pressure
                self.ax.plot([start[0], end[0]], [start[1], end[1]], 
                           'k-', linewidth=4, alpha=0.7)
                continue
            else:  # Default skating
                style = "-" if movement.style == "solid" else "--"
                linewidth = 2
                color = "gray"
                
            # Draw arrow
            arrow = FancyArrowPatch(
                start, end,
                arrowstyle='->,head_width=0.4,head_length=0.6',
                linestyle=style,
                linewidth=linewidth,
                color=color,
                alpha=0.8,
                zorder=8
            )
            self.ax.add_patch(arrow)
            
            # Add label if specified
            if movement.label:
                mid_x = (start[0] + end[0]) / 2
                mid_y = (start[1] + end[1]) / 2
                self.ax.text(mid_x, mid_y + 2, movement.label, 
                           fontsize=8, ha='center', style='italic', zorder=9)
                
    def _draw_wavy_line(self, start: Tuple, end: Tuple):
        """Draw a wavy line for backward skating."""
        x = np.linspace(start[0], end[0], 20)
        y = np.linspace(start[1], end[1], 20)
        # Add sine wave perturbation
        perp_x = -(end[1] - start[1]) / np.linalg.norm([end[0]-start[0], end[1]-start[1]])
        perp_y = (end[0] - start[0]) / np.linalg.norm([end[0]-start[0], end[1]-start[1]])
        wave = np.sin(np.linspace(0, 3*np.pi, 20))
        x += perp_x * wave * 0.5
        y += perp_y * wave * 0.5
        self.ax.plot(x, y, 'k-', linewidth=2, alpha=0.7)
        
    def _draw_double_arrow(self, start: Tuple, end: Tuple):
        """Draw a double-headed arrow for lateral movement."""
        arrow = FancyArrowPatch(
            start, end,
            arrowstyle='<->,head_width=0.4,head_length=0.6',
            linewidth=2,
            color='black',
            alpha=0.8
        )
        self.ax.add_patch(arrow)
        
    def _draw_curved_path(self, points: List[Tuple], style: str = 'solid', color: str = 'gray', label: Optional[str] = None):
        """Draw a smooth curved path through multiple points."""
        if len(points) < 2:
            return
            
        # Convert points to numpy array
        points = np.array(points)
        
        # Create smooth curve through points using cubic spline interpolation
        from scipy.interpolate import CubicSpline
        t = np.arange(len(points))
        cs_x = CubicSpline(t, points[:, 0])
        cs_y = CubicSpline(t, points[:, 1])
        
        # Generate smooth curve points
        t_smooth = np.linspace(0, len(points)-1, 100)
        x_smooth = cs_x(t_smooth)
        y_smooth = cs_y(t_smooth)
        
        # Draw the curve
        linestyle = '-' if style == 'solid' else '--' if style == 'dashed' else ':'
        self.ax.plot(x_smooth, y_smooth, linestyle=linestyle, linewidth=2, color=color, alpha=0.8, zorder=8)
        
        # Add arrowhead at the end
        if len(x_smooth) > 1:
            dx = x_smooth[-1] - x_smooth[-5]
            dy = y_smooth[-1] - y_smooth[-5]
            self.ax.arrow(x_smooth[-5], y_smooth[-5], dx*0.8, dy*0.8,
                         head_width=1.5, head_length=1, fc=color, ec=color, zorder=9, alpha=0.8)
        
        # Add label if specified
        if label:
            mid_idx = len(x_smooth) // 2
            self.ax.text(x_smooth[mid_idx], y_smooth[mid_idx] + 2, label,
                        fontsize=8, ha='center', style='italic', zorder=9)
        
    def _draw_zones(self, zones: List[Zone]):
        """Draw coverage and pressure zones."""
        for zone in zones:
            color = self.HOME_COLOR if zone.team == "home" else self.AWAY_COLOR
            if zone.color:
                color = zone.color
            
            # Higher z-order for cones/pylons
            z_order = 11 if zone.type == "cone" else 6
            fill_cone = zone.type == "cone" and zone.opacity >= 1.0
                
            if zone.shape == "rectangle":
                rect = Rectangle(
                    (zone.bounds["x"], zone.bounds["y"]),
                    zone.bounds["width"],
                    zone.bounds["height"],
                    facecolor=color,
                    alpha=zone.opacity,
                    edgecolor=color,
                    linewidth=1,
                    zorder=z_order
                )
                self.ax.add_patch(rect)
                
            elif zone.shape == "circle":
                circle = Circle(
                    (zone.bounds["x"], zone.bounds["y"]),
                    zone.bounds.get("radius", 10),
                    facecolor=color if fill_cone else color,
                    alpha=zone.opacity if not fill_cone else 1.0,
                    edgecolor=color,
                    linewidth=2 if zone.type == "cone" else 1,
                    fill=fill_cone or zone.opacity > 0,
                    zorder=z_order
                )
                self.ax.add_patch(circle)
                
            elif zone.shape == "polygon":
                # For triangular pylons
                vertices = zone.bounds.get("vertices", [])
                if vertices:
                    polygon = Polygon(
                        vertices,
                        facecolor=color,
                        alpha=zone.opacity,
                        edgecolor=color,
                        linewidth=1,
                        zorder=z_order
                    )
                    self.ax.add_patch(polygon)
                
            # Add zone label
            if zone.label:
                cx = zone.bounds["x"] + zone.bounds.get("width", 0) / 2
                cy = zone.bounds["y"] + zone.bounds.get("height", 0) / 2
                label_color = 'white' if fill_cone else 'white' if zone.opacity > 0.5 else color
                self.ax.text(cx, cy, zone.label, 
                           fontsize=10, ha='center', va='center',
                           color=label_color, fontweight='bold', zorder=z_order+1)
                
    def _draw_annotations(self, annotations: List[Annotation]):
        """Draw text annotations."""
        size_map = {"small": 8, "medium": 10, "large": 12}
        
        for ann in annotations:
            weight = 'bold' if ann.style == "bold" else 'normal'
            self.ax.text(
                ann.position["x"], 
                ann.position["y"],
                ann.text,
                fontsize=size_map[ann.size],
                fontweight=weight,
                ha='center',
                va='center'
            )
            
    def spec_to_json(self, spec: DiagramSpec) -> str:
        """Convert diagram spec to JSON string."""
        spec_dict = {
            "title": spec.title,
            "rink": spec.rink,
            "players": [asdict(p) for p in spec.players],
            "movements": [asdict(m) for m in spec.movements],
            "zones": [asdict(z) for z in spec.zones],
            "annotations": [asdict(a) for a in spec.annotations],
            "metadata": spec.metadata
        }
        return json.dumps(spec_dict, indent=2)
        
    def json_to_spec(self, json_str: str) -> DiagramSpec:
        """Convert JSON string to diagram spec."""
        data = json.loads(json_str)
        return DiagramSpec(
            title=data["title"],
            rink=data["rink"],
            players=[Player(**p) for p in data["players"]],
            movements=[Movement(**m) for m in data["movements"]],
            zones=[Zone(**z) for z in data["zones"]],
            annotations=[Annotation(**a) for a in data["annotations"]],
            metadata=data["metadata"]
        )