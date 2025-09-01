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
    waypoints: Optional[List[Tuple[float, float]]] = None  # For smooth curved paths

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
    
    # Youth Hockey Optimized Colors - High visibility for coaching
    HOME_COLOR = "#1E88E5"  # Bright blue - matches reference images
    AWAY_COLOR = "#D32F2F"  # Bright red - matches reference images
    PUCK_COLOR = "#000000"  # Keep black as requested
    CONE_COLOR = "#FF6600"  # Orange - good visibility
    COACH_COLOR = "#4CAF50"  # Green for coaches - distinct from players
    
    # Youth-optimized sizes - bigger for clarity
    PLAYER_RADIUS = 3.5     # Was 2, now 75% bigger
    PUCK_RADIUS = 1.5       # Visible puck size
    ARROW_WIDTH = 3         # Was 1-2, now thicker
    TEXT_SIZE = 11          # Was 10, better readability
    
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
        if spec.rink.get("view") == "custom":
            self._set_view(spec.rink)
        else:
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
        
    def _set_view(self, view: str | dict):
        """Set the rink view (full, offensive, defensive, neutral, half, custom)."""
        if isinstance(view, dict) and view.get('view') == 'custom':
            # Custom view with specific xlim and ylim
            if 'xlim' in view:
                self.ax.set_xlim(view['xlim'])
            if 'ylim' in view:
                self.ax.set_ylim(view['ylim'])
        elif view == "offensive":
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
            # Handle both tuple and dict formats for coordinates
            if isinstance(player.coordinates, tuple):
                x, y = player.coordinates
            else:
                x, y = player.coordinates["x"], player.coordinates["y"]
            color = self.HOME_COLOR if player.team == "home" else self.AWAY_COLOR
            
            # Store position for movement references
            self.player_positions[player.position] = (x, y)
            
            # Draw player based on type (Hockey Canada symbols)
            if player.type == "forward":
                # Filled circle with white text - matching reference images
                circle = Circle((x, y), self.PLAYER_RADIUS, facecolor=color, edgecolor=color, linewidth=1, zorder=100)
                self.ax.add_patch(circle)
                label = player.label or player.position
                # Add position label with white text on colored background
                self.ax.text(x, y, label, ha='center', va='center', fontsize=self.TEXT_SIZE, 
                           fontweight='bold', color='white', zorder=101)
                
            elif player.type == "defense":
                # Filled circle with white text - same as forwards for consistency
                circle = Circle((x, y), self.PLAYER_RADIUS, facecolor=color, edgecolor=color, linewidth=1, zorder=100)
                self.ax.add_patch(circle)
                label = player.label or player.position
                # Add position label with white text
                self.ax.text(x, y, label, ha='center', va='center', fontsize=self.TEXT_SIZE,
                           fontweight='bold', color='white', zorder=101)
                
            elif player.type == "goalie":
                # Half-filled circle with higher z-order - bigger for goalies
                circle = Circle((x, y), self.PLAYER_RADIUS * 1.3, facecolor=color, alpha=0.5, 
                              edgecolor=color, linewidth=2.5, zorder=100)
                self.ax.add_patch(circle)
                label = "G"
                # Add label
                self.ax.text(x, y, label, ha='center', va='center', fontsize=self.TEXT_SIZE,
                           fontweight='bold', color='white', zorder=101)
                
            elif player.type == "coach":
                # Filled circle with distinct color for coaches - high z-order to stay on top
                circle = Circle((x, y), self.PLAYER_RADIUS, facecolor=self.COACH_COLOR, edgecolor=self.COACH_COLOR, linewidth=1, zorder=100)
                self.ax.add_patch(circle)
                label = player.label or "C"
                # Add label with white text
                self.ax.text(x, y, label, ha='center', va='center', fontsize=self.TEXT_SIZE,
                           fontweight='bold', color='white', zorder=101)
                
            elif player.type == "puck":
                # Puck - visible size
                self.ax.plot(x, y, 'o', markersize=8, color=self.PUCK_COLOR, zorder=100)
                continue  # No label needed
                
            else:  # opponent - use filled circles with X labels for consistency
                # Filled circle with X or label text
                circle = Circle((x, y), self.PLAYER_RADIUS, facecolor=color, edgecolor=color, linewidth=1, zorder=100)
                self.ax.add_patch(circle)
                label = player.label or player.position or "X"
                # Add label with white text
                self.ax.text(x, y, label, ha='center', va='center', fontsize=self.TEXT_SIZE,
                           fontweight='bold', color='white', zorder=101)
                
            # Add puck if player has it
            if player.has_puck:
                puck = Circle((x + 2, y + 2), self.PUCK_RADIUS, color=self.PUCK_COLOR, zorder=102)
                self.ax.add_patch(puck)
                
    def _draw_movements(self, movements: List[Movement]):
        """Draw movement arrows and lines."""
        for movement in movements:
            # Check if this movement has waypoints for smooth curved path
            if movement.waypoints and len(movement.waypoints) > 2:
                self._draw_curved_movement(movement)
                continue
                
            # Regular movement handling (straight lines)
            # Resolve positions
            if isinstance(movement.from_pos, str):
                start = self.player_positions.get(movement.from_pos, (0, 0))
            elif isinstance(movement.from_pos, tuple):
                start = movement.from_pos
            else:
                start = (movement.from_pos["x"], movement.from_pos["y"])
                
            if isinstance(movement.to_pos, str):
                end = self.player_positions.get(movement.to_pos, (0, 0))
            elif isinstance(movement.to_pos, tuple):
                end = movement.to_pos
            else:
                end = (movement.to_pos["x"], movement.to_pos["y"])
                
            # Style based on movement type - Youth optimized (thicker, clearer)
            if movement.type == "carry":
                # Solid arrow for puck carrying
                style = "-"
                linewidth = self.ARROW_WIDTH + 1  # Extra thick for carrying
                color = self.PUCK_COLOR
            elif movement.type == "pass":
                # Dotted arrow for passing - very clear dots
                style = ":"
                linewidth = self.ARROW_WIDTH
                color = self.PUCK_COLOR
            elif movement.type == "shot":
                # Dashed arrow for shooting - bold!
                style = "--"
                linewidth = self.ARROW_WIDTH + 1.5
                color = "#FF0000"  # Red for shots - kids remember!
            elif movement.type == "drop_pass":
                # Solid with hook
                style = "-"
                linewidth = self.ARROW_WIDTH
                color = self.PUCK_COLOR
                # Add hook indicator - bigger
                self.ax.plot([start[0], start[0]-3], [start[1], start[1]], 
                           'k-', linewidth=self.ARROW_WIDTH)
            elif movement.type == "backward":
                # Wavy line for backward skating
                self._draw_wavy_line(start, end)
                continue
            elif movement.type == "lateral":
                # Double arrow for lateral movement
                self._draw_double_arrow(start, end)
                continue
            elif movement.type == "pressure":
                # Thick solid arrow for defensive pressure - make it obvious!
                arrow = FancyArrowPatch(
                    start, end,
                    arrowstyle='->,head_width=1.0,head_length=1.2',
                    linewidth=self.ARROW_WIDTH + 2,
                    color='black',
                    alpha=0.8,
                    zorder=90
                )
                self.ax.add_patch(arrow)
                continue
            else:  # Default skating (including "skate" type)
                style = "-" if movement.style == "solid" else "--"
                linewidth = self.ARROW_WIDTH
                # Use team color for skating movements
                color = self.HOME_COLOR if movement.style == "solid" else "gray"
                
            # Draw arrow - bigger arrow heads for youth
            arrow = FancyArrowPatch(
                start, end,
                arrowstyle='->,head_width=0.6,head_length=0.8',
                linestyle=style,
                linewidth=linewidth,
                color=color,
                alpha=0.9,  # More opaque for clarity
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
        length = np.linalg.norm([end[0]-start[0], end[1]-start[1]])
        if length > 0:
            perp_x = -(end[1] - start[1]) / length
            perp_y = (end[0] - start[0]) / length
            wave = np.sin(np.linspace(0, 3*np.pi, 20))
            x += perp_x * wave * 2  # Increased amplitude for visibility
            y += perp_y * wave * 2
        self.ax.plot(x, y, 'k-', linewidth=self.ARROW_WIDTH, alpha=0.9, zorder=90)
        # Add arrow at the end
        self.ax.arrow(x[-2], y[-2], x[-1]-x[-2], y[-1]-y[-2],
                     head_width=2, head_length=1.5, fc='black', ec='black', zorder=91)
        
    def _draw_double_arrow(self, start: Tuple, end: Tuple):
        """Draw a double-headed arrow for lateral movement."""
        arrow = FancyArrowPatch(
            start, end,
            arrowstyle='<->,head_width=0.8,head_length=1.0',
            linewidth=self.ARROW_WIDTH,
            color='black',
            alpha=0.9,
            zorder=90
        )
        self.ax.add_patch(arrow)
        
    def _draw_curved_movement(self, movement: Movement):
        """Draw a curved movement using waypoints."""
        # Determine color and style based on movement type
        if movement.type == "carry":
            color = "black"
            style = "solid"
            linewidth = 3
        elif movement.type == "pass":
            color = "black"
            style = "dotted"
            linewidth = 2
        elif movement.type == "shot":
            color = "black"
            style = "dashed"
            linewidth = 2.5
        elif movement.type == "pressure":
            color = "black"
            style = "solid"
            linewidth = 4
        else:  # skate, backward, lateral
            color = "gray"
            style = "solid" if movement.style == "solid" else "dashed"
            linewidth = 2
            
        # Use the existing curved path method
        self._draw_curved_path(
            movement.waypoints,
            style=style,
            color=color,
            label=movement.label,
            linewidth=linewidth,
            with_puck=movement.with_puck
        )
    
    def _draw_curved_path(self, points: List[Tuple], style: str = 'solid', color: str = 'gray', 
                         label: Optional[str] = None, linewidth: int = 2, with_puck: bool = False):
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
        self.ax.plot(x_smooth, y_smooth, linestyle=linestyle, linewidth=linewidth, color=color, alpha=0.8, zorder=8)
        
        # Add puck indicators if carrying puck
        if with_puck:
            # Add small puck dots along the path
            puck_indices = np.linspace(10, len(x_smooth)-10, 4, dtype=int)
            for idx in puck_indices:
                self.ax.plot(x_smooth[idx], y_smooth[idx], 'ko', markersize=3, zorder=10)
        
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
                va='center',
                color='black',
                zorder=95,  # High z-order for visibility
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                         edgecolor='black', alpha=0.8) if ann.style == "bold" else None
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