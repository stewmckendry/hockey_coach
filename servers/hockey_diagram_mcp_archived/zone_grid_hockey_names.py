"""
Hockey-friendly zone grid system for hockey diagrams.

This module provides the same 32-zone grid system but with intuitive hockey terminology
instead of technical names like 'def-left-high'.
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
    hockey_name: str  # New field for hockey-friendly name


class HockeyZoneGrid:
    """
    Hockey-friendly zone grid system.
    
    Uses intuitive hockey terminology for all 32 zones while maintaining
    the same precise coordinate system.
    """
    
    # Zone name mapping from technical to hockey-friendly
    ZONE_NAME_MAP = {
        # Defensive zones
        "def-left-high": "d-corner-left-high",
        "def-center-left-high": "d-circle-left-high", 
        "def-center-right-high": "d-circle-right-high",
        "def-right-high": "d-corner-right-high",
        "def-left-mid-high": "d-behind-net-left",
        "def-center-left-mid-high": "d-circle-left-center",
        "def-center-right-mid-high": "d-circle-right-center",
        "def-right-mid-high": "d-behind-net-right",
        "def-left-mid-low": "d-behind-net-left",
        "def-center-left-mid-low": "d-circle-left-low",
        "def-center-right-mid-low": "d-circle-right-low",
        "def-right-mid-low": "d-behind-net-right",
        "def-left-low": "d-corner-left-low",
        "def-center-left-low": "d-circle-left-boards",
        "def-center-right-low": "d-circle-right-boards",
        "def-right-low": "d-corner-right-low",
        
        # Neutral zones
        "neu-left-high": "neutral-left-wing-high",
        "neu-right-high": "neutral-right-wing-high",
        "neu-left-mid-high": "neutral-left-center-high",
        "neu-right-mid-high": "neutral-right-center-high",
        "neu-left-mid-low": "neutral-left-center-low",
        "neu-right-mid-low": "neutral-right-center-low",
        "neu-left-low": "neutral-left-wing-low",
        "neu-right-low": "neutral-right-wing-low",
        
        # Offensive zones
        "off-left-high": "o-corner-left-high",
        "off-center-left-high": "o-point-left",
        "off-center-right-high": "o-high-slot-high",
        "off-right-high": "o-corner-right-high",
        "off-left-mid-high": "o-behind-net-left",
        "off-center-left-mid-high": "o-point-center-left",
        "off-center-right-mid-high": "o-slot-high",
        "off-right-mid-high": "o-behind-net-right",
        "off-left-mid-low": "o-behind-net-left",
        "off-center-left-mid-low": "o-point-center-right",
        "off-center-right-mid-low": "o-slot-low",
        "off-right-mid-low": "o-behind-net-right",
        "off-left-low": "o-corner-left-low",
        "off-center-left-low": "o-point-right",
        "off-center-right-low": "o-low-slot",
        "off-right-low": "o-corner-right-low"
    }
    
    def __init__(self):
        """Initialize the hockey zone grid with all 32 zones."""
        self.zones = self._create_hockey_grid()
        self.zone_lookup = {zone.hockey_name: zone for zone in self.zones}
        # Also support lookup by technical name for backward compatibility
        self.technical_lookup = {zone.name: zone for zone in self.zones}
        self.adjacency_map = self._build_adjacency_map()
    
    def _create_hockey_grid(self) -> List[Zone]:
        """Create the grid with hockey-friendly names."""
        zones = []
        
        # Grid parameters
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
                if col_idx in [3, 4]:
                    continue
                    
                x_min = x_boundaries[col_idx]
                x_max = x_boundaries[col_idx + 1]
                y_min = y_boundaries[row_idx]
                y_max = y_boundaries[row_idx + 1]
                
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                
                col_label, area = col_info[col_idx]
                row_label = row_labels[row_idx]
                
                # Build technical name
                if col_idx == 0:
                    technical_name = f"def-left-{row_label}"
                elif col_idx == 1:
                    technical_name = f"def-center-left-{row_label}"
                elif col_idx == 2: 
                    technical_name = f"def-center-right-{row_label}"
                elif col_idx == 3:
                    technical_name = f"def-right-{row_label}"
                elif col_idx == 4:
                    technical_name = f"off-left-{row_label}"
                elif col_idx == 5:
                    technical_name = f"off-center-left-{row_label}"
                elif col_idx == 6:
                    technical_name = f"off-center-right-{row_label}"
                elif col_idx == 7:
                    technical_name = f"off-right-{row_label}"
                
                # Get hockey-friendly name
                hockey_name = self.ZONE_NAME_MAP.get(technical_name, technical_name)
                
                # Create description based on hockey name
                description = self._get_hockey_description(hockey_name)
                
                zones.append(Zone(
                    name=technical_name,
                    center_x=center_x,
                    center_y=center_y,
                    x_min=x_min,
                    y_min=y_min,
                    x_max=x_max,
                    y_max=y_max,
                    area=area,
                    description=description,
                    hockey_name=hockey_name
                ))
        
        # Add neutral zones
        for row_idx in range(4):
            for col_offset in [0, 1]:
                col_idx = 3 + col_offset
                
                x_min = x_boundaries[col_idx]
                x_max = x_boundaries[col_idx + 1]
                y_min = y_boundaries[row_idx]
                y_max = y_boundaries[row_idx + 1]
                
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                
                row_label = row_labels[row_idx]
                side = "left" if col_offset == 0 else "right"
                
                technical_name = f"neu-{side}-{row_label}"
                hockey_name = self.ZONE_NAME_MAP.get(technical_name, technical_name)
                description = self._get_hockey_description(hockey_name)
                
                zones.append(Zone(
                    name=technical_name,
                    center_x=center_x,
                    center_y=center_y,
                    x_min=x_min,
                    y_min=y_min,
                    x_max=x_max,
                    y_max=y_max,
                    area=ZoneArea.NEUTRAL,
                    description=description,
                    hockey_name=hockey_name
                ))
        
        return zones
    
    def _get_hockey_description(self, hockey_name: str) -> str:
        """Get descriptive text for a hockey zone name."""
        descriptions = {
            # Defensive zones
            "d-corner-left-high": "Defensive corner, left side upper boards",
            "d-circle-left-high": "Left defensive circle, upper area",
            "d-circle-right-high": "Right defensive circle, upper area",
            "d-behind-net-left": "Behind our net, left side",
            "d-circle-left-center": "Left defensive circle, center ice level",
            "d-circle-right-center": "Right defensive circle, center ice level",
            "d-behind-net-right": "Behind our net, right side",
            "d-circle-left-low": "Left defensive circle, lower area",
            "d-circle-right-low": "Right defensive circle, lower area",
            "d-corner-left-low": "Defensive corner, left side lower boards",
            "d-circle-left-boards": "Left circle extending to boards",
            "d-circle-right-boards": "Right circle extending to boards",
            
            # Neutral zones
            "neutral-left-wing-high": "Neutral zone, left wing lane upper",
            "neutral-right-wing-high": "Neutral zone, right wing lane upper",
            "neutral-left-center-high": "Neutral zone, left center ice upper",
            "neutral-right-center-high": "Neutral zone, right center ice upper",
            "neutral-left-center-low": "Neutral zone, left center ice lower",
            "neutral-right-center-low": "Neutral zone, right center ice lower",
            "neutral-left-wing-low": "Neutral zone, left wing lane lower",
            "neutral-right-wing-low": "Neutral zone, right wing lane lower",
            
            # Offensive zones
            "o-point-left": "Left point position",
            "o-high-slot-high": "High slot area, upper portion",
            "o-corner-right-high": "Offensive corner, right side upper",
            "o-point-center-left": "Point area, left of center",
            "o-slot-high": "Slot area, upper portion",
            "o-behind-net-right": "Behind opponent's net, right side",
            "o-point-center-right": "Point area, right of center",
            "o-slot-low": "Slot area, lower portion",
            "o-behind-net-left": "Behind opponent's net, left side",
            "o-point-right": "Right point position",
            "o-low-slot": "Low slot and crease area",
            "o-corner-left-low": "Offensive corner, left side lower"
        }
        return descriptions.get(hockey_name, f"Zone: {hockey_name}")
    
    def get_zone_position(self, zone_name: str, offset_x: float = 0, offset_y: float = 0) -> Tuple[float, float]:
        """Get center coordinates for a zone (supports both technical and hockey names)."""
        zone = None
        
        # Try hockey name first
        if zone_name in self.zone_lookup:
            zone = self.zone_lookup[zone_name]
        # Fall back to technical name
        elif zone_name in self.technical_lookup:
            zone = self.technical_lookup[zone_name]
        
        if zone:
            return (zone.center_x + offset_x, zone.center_y + offset_y)
        else:
            return (0 + offset_x, 0 + offset_y)
    
    def get_zone_by_position(self, x: float, y: float) -> str:
        """Find which zone contains the given position (returns hockey name)."""
        for zone in self.zones:
            if (zone.x_min <= x <= zone.x_max and 
                zone.y_min <= y <= zone.y_max):
                return zone.hockey_name
        
        return "neutral-left-center-low"  # Fallback
    
    def get_adjacent_zones(self, zone_name: str) -> List[str]:
        """Get list of zones adjacent to the given zone."""
        # Find the zone object
        zone_obj = None
        if zone_name in self.zone_lookup:
            zone_obj = self.zone_lookup[zone_name]
        elif zone_name in self.technical_lookup:
            zone_obj = self.technical_lookup[zone_name]
        
        if zone_obj:
            return self.adjacency_map.get(zone_obj.hockey_name, [])
        return []
    
    def get_zone_bounds(self, zone_name: str) -> Tuple[float, float, float, float]:
        """Get boundary coordinates for a zone."""
        zone = None
        
        if zone_name in self.zone_lookup:
            zone = self.zone_lookup[zone_name]
        elif zone_name in self.technical_lookup:
            zone = self.technical_lookup[zone_name]
        
        if zone:
            return (zone.x_min, zone.y_min, zone.x_max, zone.y_max)
        else:
            return (-12.5, -10.625, 12.5, 10.625)
    
    def _build_adjacency_map(self) -> Dict[str, List[str]]:
        """Build adjacency relationships between zones using hockey names."""
        adjacency = {}
        
        for zone in self.zones:
            adjacent = []
            
            for other_zone in self.zones:
                if zone.hockey_name == other_zone.hockey_name:
                    continue
                
                if self._zones_adjacent(zone, other_zone):
                    adjacent.append(other_zone.hockey_name)
            
            adjacency[zone.hockey_name] = adjacent
        
        return adjacency
    
    def _zones_adjacent(self, zone1: Zone, zone2: Zone) -> bool:
        """Check if two zones are adjacent (share a boundary)."""
        # Horizontal adjacency
        if (zone1.x_min == zone2.x_max or zone1.x_max == zone2.x_min):
            if not (zone1.y_max <= zone2.y_min or zone2.y_max <= zone1.y_min):
                return True
        
        # Vertical adjacency
        if (zone1.y_min == zone2.y_max or zone1.y_max == zone2.y_min):
            if not (zone1.x_max <= zone2.x_min or zone2.x_max <= zone1.x_min):
                return True
        
        return False
    
    def list_all_zones(self) -> List[str]:
        """Get list of all zone names (hockey-friendly)."""
        return list(self.zone_lookup.keys())
    
    def get_zone_info(self, zone_name: str) -> Optional[Zone]:
        """Get complete zone information."""
        if zone_name in self.zone_lookup:
            return self.zone_lookup[zone_name]
        elif zone_name in self.technical_lookup:
            return self.technical_lookup[zone_name]
        return None
    
    def convert_technical_to_hockey(self, technical_name: str) -> str:
        """Convert a technical zone name to hockey-friendly name."""
        return self.ZONE_NAME_MAP.get(technical_name, technical_name)
    
    def get_key_hockey_areas(self) -> Dict[str, List[str]]:
        """Get common hockey areas as combinations of zones."""
        return {
            "slot": ["o-slot-high", "o-slot-low"],
            "high_slot": ["o-high-slot-high", "o-point-center-left", "o-point-center-right"],
            "point": ["o-point-left", "o-point-right"],
            "crease": ["o-low-slot"],
            "corners": ["o-corner-left-low", "o-corner-right-high", "d-corner-left-low", "d-corner-left-high"],
            "behind_net": ["o-behind-net-left", "o-behind-net-right", "d-behind-net-left", "d-behind-net-right"],
            "neutral_zone": [z.hockey_name for z in self.zones if z.area == ZoneArea.NEUTRAL]
        }


# Create global instance
hockey_zone_grid = HockeyZoneGrid()


# Convenience functions matching original API
def get_zone_position(zone_name: str, offset_x: float = 0, offset_y: float = 0) -> Tuple[float, float]:
    return hockey_zone_grid.get_zone_position(zone_name, offset_x, offset_y)


def get_zone_by_position(x: float, y: float) -> str:
    return hockey_zone_grid.get_zone_by_position(x, y)


def get_adjacent_zones(zone_name: str) -> List[str]:
    return hockey_zone_grid.get_adjacent_zones(zone_name)


def get_zone_bounds(zone_name: str) -> Tuple[float, float, float, float]:
    return hockey_zone_grid.get_zone_bounds(zone_name)


def list_all_zones() -> List[str]:
    return hockey_zone_grid.list_all_zones()


def get_zone_info(zone_name: str) -> Optional[Zone]:
    return hockey_zone_grid.get_zone_info(zone_name)


def convert_technical_to_hockey(technical_name: str) -> str:
    return hockey_zone_grid.convert_technical_to_hockey(technical_name)


def get_key_hockey_areas() -> Dict[str, List[str]]:
    return hockey_zone_grid.get_key_hockey_areas()