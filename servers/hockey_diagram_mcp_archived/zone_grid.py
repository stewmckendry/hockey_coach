"""
Simplified zone-based positioning system for hockey diagrams.

This module provides a grid-based zone system for the hockey rink,
dividing the ice surface into 32 named zones with complete coverage and no overlaps.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ZoneArea(Enum):
    """Zone area designations."""
    DEFENSIVE = "def"
    NEUTRAL = "neu"
    OFFENSIVE = "off"


@dataclass
class Zone:
    """A zone on the hockey rink."""
    name: str
    center_x: float
    center_y: float
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    area: ZoneArea
    description: str


class ZoneGrid:
    """
    Simple grid-based positioning system for hockey diagrams.
    
    Divides the NHL regulation rink into 32 named zones using a 8x4 grid:
    - 4 rows (top to bottom): high, mid-high, mid-low, low  
    - 8 columns (left to right): def-left, def-center-left, def-center-right, def-right,
                                 off-left, off-center-left, off-center-right, off-right
    """
    
    def __init__(self):
        """Initialize the zone grid with all 32 zones."""
        self.zones = self._create_simple_grid()
        self.zone_lookup = {zone.name: zone for zone in self.zones}
        self.adjacency_map = self._build_adjacency_map()
    
    def _create_simple_grid(self) -> List[Zone]:
        """Create a simple 8x4 grid of zones."""
        zones = []
        
        # Grid parameters
        # X-axis: -100 to +100 (200 units total) -> 8 columns of 25 units each
        # Y-axis: -42.5 to +42.5 (85 units total) -> 4 rows of 21.25 units each
        
        x_boundaries = [-100, -75, -50, -25, 0, 25, 50, 75, 100]
        y_boundaries = [-42.5, -21.25, 0, 21.25, 42.5]
        
        # Row labels (from bottom to top)
        row_labels = ["low", "mid-low", "mid-high", "high"]
        
        # Column labels and areas
        col_info = [
            ("def-left", ZoneArea.DEFENSIVE),
            ("def-center-left", ZoneArea.DEFENSIVE), 
            ("def-center-right", ZoneArea.DEFENSIVE),
            ("def-right", ZoneArea.DEFENSIVE),
            ("off-left", ZoneArea.OFFENSIVE),
            ("off-center-left", ZoneArea.OFFENSIVE),
            ("off-center-right", ZoneArea.OFFENSIVE),
            ("off-right", ZoneArea.OFFENSIVE)
        ]
        
        # Create zones for each grid cell
        for row_idx in range(4):
            for col_idx in range(8):
                # Skip middle columns for neutral zone handling
                if col_idx in [3, 4]:  # These will be neutral zone
                    continue
                    
                x_min = x_boundaries[col_idx]
                x_max = x_boundaries[col_idx + 1]
                y_min = y_boundaries[row_idx]
                y_max = y_boundaries[row_idx + 1]
                
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                
                col_label, area = col_info[col_idx]
                row_label = row_labels[row_idx]
                
                zone_name = f"{area.value}-{col_label.split('-', 1)[1]}-{row_label}"
                if col_label == "def-left":
                    zone_name = f"def-left-{row_label}"
                elif col_label == "def-center-left":
                    zone_name = f"def-center-left-{row_label}"
                elif col_label == "def-center-right": 
                    zone_name = f"def-center-right-{row_label}"
                elif col_label == "def-right":
                    zone_name = f"def-right-{row_label}"
                elif col_label == "off-left":
                    zone_name = f"off-left-{row_label}"
                elif col_label == "off-center-left":
                    zone_name = f"off-center-left-{row_label}"
                elif col_label == "off-center-right":
                    zone_name = f"off-center-right-{row_label}"
                elif col_label == "off-right":
                    zone_name = f"off-right-{row_label}"
                
                zones.append(Zone(
                    name=zone_name,
                    center_x=center_x,
                    center_y=center_y,
                    x_min=x_min,
                    y_min=y_min,
                    x_max=x_max,
                    y_max=y_max,
                    area=area,
                    description=f"{area.value.title()} zone: {col_label} {row_label}"
                ))
        
        # Add neutral zone (middle 2 columns)
        for row_idx in range(4):
            for col_offset in [0, 1]:  # Two neutral columns
                col_idx = 3 + col_offset  # Columns 3 and 4
                
                x_min = x_boundaries[col_idx]
                x_max = x_boundaries[col_idx + 1]
                y_min = y_boundaries[row_idx]
                y_max = y_boundaries[row_idx + 1]
                
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                
                row_label = row_labels[row_idx]
                side = "left" if col_offset == 0 else "right"
                
                zone_name = f"neu-{side}-{row_label}"
                
                zones.append(Zone(
                    name=zone_name,
                    center_x=center_x,
                    center_y=center_y,
                    x_min=x_min,
                    y_min=y_min,
                    x_max=x_max,
                    y_max=y_max,
                    area=ZoneArea.NEUTRAL,
                    description=f"Neutral zone: {side} {row_label}"
                ))
        
        return zones
    
    def get_zone_position(self, zone_name: str, offset_x: float = 0, offset_y: float = 0) -> Tuple[float, float]:
        """Get center coordinates for a zone with optional offset."""
        if zone_name not in self.zone_lookup:
            return (0 + offset_x, 0 + offset_y)
        
        zone = self.zone_lookup[zone_name]
        return (zone.center_x + offset_x, zone.center_y + offset_y)
    
    def get_zone_by_position(self, x: float, y: float) -> str:
        """Find which zone contains the given position."""
        for zone in self.zones:
            if (zone.x_min <= x <= zone.x_max and 
                zone.y_min <= y <= zone.y_max):
                return zone.name
        
        return "neu-left-mid-low"  # Fallback
    
    def get_adjacent_zones(self, zone_name: str) -> List[str]:
        """Get list of zones adjacent to the given zone."""
        return self.adjacency_map.get(zone_name, [])
    
    def get_zone_bounds(self, zone_name: str) -> Tuple[float, float, float, float]:
        """Get boundary coordinates for a zone."""
        if zone_name not in self.zone_lookup:
            return (-12.5, -10.625, 12.5, 10.625)
        
        zone = self.zone_lookup[zone_name]
        return (zone.x_min, zone.y_min, zone.x_max, zone.y_max)
    
    def _build_adjacency_map(self) -> Dict[str, List[str]]:
        """Build adjacency relationships between zones."""
        adjacency = {}
        
        for zone in self.zones:
            adjacent = []
            
            for other_zone in self.zones:
                if zone.name == other_zone.name:
                    continue
                
                if self._zones_adjacent(zone, other_zone):
                    adjacent.append(other_zone.name)
            
            adjacency[zone.name] = adjacent
        
        return adjacency
    
    def _zones_adjacent(self, zone1: Zone, zone2: Zone) -> bool:
        """Check if two zones are adjacent (share a boundary)."""
        # Horizontal adjacency (share a vertical edge)
        if (zone1.x_min == zone2.x_max or zone1.x_max == zone2.x_min):
            # Check if they overlap in y direction
            if not (zone1.y_max <= zone2.y_min or zone2.y_max <= zone1.y_min):
                return True
        
        # Vertical adjacency (share a horizontal edge)
        if (zone1.y_min == zone2.y_max or zone1.y_max == zone2.y_min):
            # Check if they overlap in x direction
            if not (zone1.x_max <= zone2.x_min or zone2.x_max <= zone1.x_min):
                return True
        
        return False
    
    def get_zone_area_distribution(self) -> Dict[str, int]:
        """Get count of zones by area."""
        distribution = {"def": 0, "neu": 0, "off": 0}
        
        for zone in self.zones:
            distribution[zone.area.value] += 1
        
        return {
            "defensive": distribution["def"],
            "neutral": distribution["neu"], 
            "offensive": distribution["off"]
        }
    
    def list_all_zones(self) -> List[str]:
        """Get list of all zone names."""
        return list(self.zone_lookup.keys())
    
    def get_zone_info(self, zone_name: str) -> Optional[Zone]:
        """Get complete zone information."""
        return self.zone_lookup.get(zone_name)


# Create global instance
zone_grid = ZoneGrid()


# Convenience functions
def get_zone_position(zone_name: str, offset_x: float = 0, offset_y: float = 0) -> Tuple[float, float]:
    return zone_grid.get_zone_position(zone_name, offset_x, offset_y)


def get_zone_by_position(x: float, y: float) -> str:
    return zone_grid.get_zone_by_position(x, y)


def get_adjacent_zones(zone_name: str) -> List[str]:
    return zone_grid.get_adjacent_zones(zone_name)


def get_zone_bounds(zone_name: str) -> Tuple[float, float, float, float]:
    return zone_grid.get_zone_bounds(zone_name)