"""
Zone-based positioning system for hockey diagrams.

This module provides a comprehensive zone grid system for the hockey rink,
dividing the ice surface into 32 named zones with complete coverage.
Each zone has center coordinates and boundaries based on NHL regulation dimensions.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math


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
    Zone-based positioning system for hockey diagrams.
    
    Divides the NHL regulation rink into 32 named zones with 100% ice coverage:
    - Defensive zone: 12 zones
    - Neutral zone: 8 zones  
    - Offensive zone: 12 zones
    
    NHL coordinate system: X-axis from -100 to +100, Y-axis from -42.5 to +42.5
    """
    
    def __init__(self):
        """Initialize the zone grid with all 32 zones."""
        self.zones = self._create_zone_grid()
        self.zone_lookup = {zone.name: zone for zone in self.zones}
        self.adjacency_map = self._build_adjacency_map()
    
    def _create_zone_grid(self) -> List[Zone]:
        """Create all 32 zones covering the entire rink."""
        zones = []
        
        # Defensive Zone (12 zones)
        # Behind net area
        zones.append(Zone(
            name="def-behind-net",
            center_x=-92, center_y=0,
            x_min=-100, y_min=-10, x_max=-89, y_max=10,
            area=ZoneArea.DEFENSIVE,
            description="Behind the net"
        ))
        
        # Goal crease area
        zones.append(Zone(
            name="def-crease",
            center_x=-86, center_y=0,
            x_min=-89, y_min=-6, x_max=-83, y_max=6,
            area=ZoneArea.DEFENSIVE,
            description="Goal crease"
        ))
        
        # Low slot (prime scoring area in front of net)
        zones.append(Zone(
            name="def-low-slot",
            center_x=-78, center_y=0,
            x_min=-83, y_min=-10, x_max=-73, y_max=10,
            area=ZoneArea.DEFENSIVE,
            description="Low slot"
        ))
        
        # Left and right corners  
        zones.append(Zone(
            name="def-left-corner",
            center_x=-87, center_y=-32,
            x_min=-100, y_min=-42.5, x_max=-74, y_max=-21.5,
            area=ZoneArea.DEFENSIVE,
            description="Left corner"
        ))
        
        zones.append(Zone(
            name="def-right-corner", 
            center_x=-87, center_y=32,
            x_min=-100, y_min=21.5, x_max=-74, y_max=42.5,
            area=ZoneArea.DEFENSIVE,
            description="Right corner"
        ))
        
        # Left and right half-walls
        zones.append(Zone(
            name="def-left-half-wall",
            center_x=-60, center_y=-32,
            x_min=-74, y_min=-42.5, x_max=-46, y_max=-21.5,
            area=ZoneArea.DEFENSIVE,
            description="Left half-wall"
        ))
        
        zones.append(Zone(
            name="def-right-half-wall",
            center_x=-60, center_y=32,
            x_min=-74, y_min=21.5, x_max=-46, y_max=42.5,
            area=ZoneArea.DEFENSIVE,
            description="Right half-wall"
        ))
        
        # Left and right face-off circle areas
        zones.append(Zone(
            name="def-left-circle",
            center_x=-69, center_y=-22.5,
            x_min=-83, y_min=-37.5, x_max=-55, y_max=-7.5,
            area=ZoneArea.DEFENSIVE,
            description="Left face-off circle"
        ))
        
        zones.append(Zone(
            name="def-right-circle",
            center_x=-69, center_y=22.5,
            x_min=-83, y_min=7.5, x_max=-55, y_max=37.5,
            area=ZoneArea.DEFENSIVE,
            description="Right face-off circle"
        ))
        
        # High slot (defensive zone)
        zones.append(Zone(
            name="def-high-slot",
            center_x=-62, center_y=0,
            x_min=-73, y_min=-10, x_max=-51, y_max=10,
            area=ZoneArea.DEFENSIVE,
            description="High slot"
        ))
        
        # Left and right point areas
        zones.append(Zone(
            name="def-left-point",
            center_x=-38, center_y=-25,
            x_min=-51, y_min=-42.5, x_max=-25, y_max=-7.5,
            area=ZoneArea.DEFENSIVE,
            description="Left point"
        ))
        
        zones.append(Zone(
            name="def-right-point",
            center_x=-38, center_y=25, 
            x_min=-51, y_min=7.5, x_max=-25, y_max=42.5,
            area=ZoneArea.DEFENSIVE,
            description="Right point"
        ))
        
        # Neutral Zone (8 zones)
        # Center ice (face-off circle) - make it smaller than the strip
        zones.append(Zone(
            name="neu-center-ice",
            center_x=0, center_y=0,
            x_min=-5, y_min=-5, x_max=5, y_max=5,
            area=ZoneArea.NEUTRAL,
            description="Center ice face-off"
        ))
        
        # Left and right boards (neutral zone)
        zones.append(Zone(
            name="neu-left-boards",
            center_x=0, center_y=-32.25,
            x_min=-25, y_min=-42.5, x_max=25, y_max=-22,
            area=ZoneArea.NEUTRAL,
            description="Left boards neutral zone"
        ))
        
        zones.append(Zone(
            name="neu-right-boards",
            center_x=0, center_y=32.25,
            x_min=-25, y_min=22, x_max=25, y_max=42.5,
            area=ZoneArea.NEUTRAL,
            description="Right boards neutral zone"
        ))
        
        # Left middle zone (between center and boards)
        zones.append(Zone(
            name="neu-left-middle",
            center_x=-12.5, center_y=-15,
            x_min=-25, y_min=-22, x_max=0, y_max=-8,
            area=ZoneArea.NEUTRAL,
            description="Left middle neutral zone"
        ))
        
        zones.append(Zone(
            name="neu-right-middle",
            center_x=-12.5, center_y=15,
            x_min=-25, y_min=8, x_max=0, y_max=22,
            area=ZoneArea.NEUTRAL,
            description="Right middle neutral zone"
        ))
        
        zones.append(Zone(
            name="neu-left-middle-off",
            center_x=12.5, center_y=-15,
            x_min=0, y_min=-22, x_max=25, y_max=-8,
            area=ZoneArea.NEUTRAL,
            description="Left middle offensive neutral zone"
        ))
        
        zones.append(Zone(
            name="neu-right-middle-off",
            center_x=12.5, center_y=15,
            x_min=0, y_min=8, x_max=25, y_max=22,
            area=ZoneArea.NEUTRAL,
            description="Right middle offensive neutral zone"
        ))
        
        # Central strip (combining both sides to maintain 8 total neutral zones)
        zones.append(Zone(
            name="neu-center-strip",
            center_x=0, center_y=0,
            x_min=-8, y_min=-8, x_max=8, y_max=8,
            area=ZoneArea.NEUTRAL,
            description="Central neutral zone strip"
        ))
        
        # Offensive Zone (12 zones) - mirror of defensive
        # Behind net area
        zones.append(Zone(
            name="off-behind-net",
            center_x=92, center_y=0,
            x_min=84, y_min=-10, x_max=100, y_max=10,
            area=ZoneArea.OFFENSIVE,
            description="Behind the net"
        ))
        
        # Goal crease area
        zones.append(Zone(
            name="off-crease",
            center_x=86, center_y=0,
            x_min=83, y_min=-6, x_max=89, y_max=6,
            area=ZoneArea.OFFENSIVE,
            description="Goal crease"
        ))
        
        # Low slot (prime scoring area)
        zones.append(Zone(
            name="off-low-slot",
            center_x=78, center_y=0,
            x_min=73, y_min=-10, x_max=83, y_max=10,
            area=ZoneArea.OFFENSIVE,
            description="Low slot"
        ))
        
        # Left and right corners
        zones.append(Zone(
            name="off-left-corner",
            center_x=87, center_y=-32,
            x_min=74, y_min=-42.5, x_max=100, y_max=-21.5,
            area=ZoneArea.OFFENSIVE,
            description="Left corner"
        ))
        
        zones.append(Zone(
            name="off-right-corner",
            center_x=87, center_y=32,
            x_min=74, y_min=21.5, x_max=100, y_max=42.5,
            area=ZoneArea.OFFENSIVE,
            description="Right corner"
        ))
        
        # Left and right half-walls
        zones.append(Zone(
            name="off-left-half-wall",
            center_x=60, center_y=-32,
            x_min=46, y_min=-42.5, x_max=74, y_max=-21.5,
            area=ZoneArea.OFFENSIVE,
            description="Left half-wall"
        ))
        
        zones.append(Zone(
            name="off-right-half-wall",
            center_x=60, center_y=32,
            x_min=46, y_min=21.5, x_max=74, y_max=42.5,
            area=ZoneArea.OFFENSIVE,
            description="Right half-wall"
        ))
        
        # Left and right face-off circle areas
        zones.append(Zone(
            name="off-left-circle",
            center_x=69, center_y=-22.5,
            x_min=55, y_min=-37.5, x_max=83, y_max=-7.5,
            area=ZoneArea.OFFENSIVE,
            description="Left face-off circle"
        ))
        
        zones.append(Zone(
            name="off-right-circle",
            center_x=69, center_y=22.5,
            x_min=55, y_min=7.5, x_max=83, y_max=37.5,
            area=ZoneArea.OFFENSIVE,
            description="Right face-off circle"
        ))
        
        # High slot (offensive zone)
        zones.append(Zone(
            name="off-high-slot",
            center_x=62, center_y=0,
            x_min=51, y_min=-10, x_max=73, y_max=10,
            area=ZoneArea.OFFENSIVE,
            description="High slot"
        ))
        
        # Left and right point areas
        zones.append(Zone(
            name="off-left-point",
            center_x=38, center_y=-25,
            x_min=25, y_min=-42.5, x_max=51, y_max=-7.5,
            area=ZoneArea.OFFENSIVE,
            description="Left point"
        ))
        
        zones.append(Zone(
            name="off-right-point",
            center_x=38, center_y=25,
            x_min=25, y_min=7.5, x_max=51, y_max=42.5,
            area=ZoneArea.OFFENSIVE,
            description="Right point"
        ))
        
        return zones
    
    def get_zone_position(self, zone_name: str, offset_x: float = 0, offset_y: float = 0) -> Tuple[float, float]:
        """
        Get center coordinates for a zone with optional offset.
        
        Args:
            zone_name: Name of the zone
            offset_x: X-axis offset from zone center
            offset_y: Y-axis offset from zone center
            
        Returns:
            Tuple of (x, y) coordinates
        """
        if zone_name not in self.zone_lookup:
            # Return center ice as fallback
            return (0 + offset_x, 0 + offset_y)
        
        zone = self.zone_lookup[zone_name]
        return (zone.center_x + offset_x, zone.center_y + offset_y)
    
    def get_zone_by_position(self, x: float, y: float) -> str:
        """
        Find which zone contains the given position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Name of the zone containing the position
        """
        for zone in self.zones:
            if (zone.x_min <= x <= zone.x_max and 
                zone.y_min <= y <= zone.y_max):
                return zone.name
        
        # Fallback if no zone found (shouldn't happen with proper coverage)
        return "neu-center-ice"
    
    def get_adjacent_zones(self, zone_name: str) -> List[str]:
        """
        Get list of zones adjacent to the given zone.
        
        Args:
            zone_name: Name of the zone
            
        Returns:
            List of adjacent zone names
        """
        return self.adjacency_map.get(zone_name, [])
    
    def get_zone_bounds(self, zone_name: str) -> Tuple[float, float, float, float]:
        """
        Get boundary coordinates for a zone.
        
        Args:
            zone_name: Name of the zone
            
        Returns:
            Tuple of (x_min, y_min, x_max, y_max)
        """
        if zone_name not in self.zone_lookup:
            # Return center ice bounds as fallback
            return (-12.5, -15, 12.5, 15)
        
        zone = self.zone_lookup[zone_name]
        return (zone.x_min, zone.y_min, zone.x_max, zone.y_max)
    
    def _build_adjacency_map(self) -> Dict[str, List[str]]:
        """Build adjacency relationships between zones."""
        adjacency = {}
        
        # For each zone, find all zones that share a boundary
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
        # Check if zones share an edge
        # Horizontal adjacency
        if (zone1.y_min == zone2.y_max or zone1.y_max == zone2.y_min):
            # Check if they overlap in x direction
            if not (zone1.x_max < zone2.x_min or zone2.x_max < zone1.x_min):
                return True
        
        # Vertical adjacency  
        if (zone1.x_min == zone2.x_max or zone1.x_max == zone2.x_min):
            # Check if they overlap in y direction
            if not (zone1.y_max < zone2.y_min or zone2.y_max < zone1.y_min):
                return True
        
        return False
    
    def get_zone_by_area(self, area: ZoneArea) -> List[str]:
        """
        Get all zones in a specific area.
        
        Args:
            area: Zone area (defensive, neutral, offensive)
            
        Returns:
            List of zone names in the area
        """
        return [zone.name for zone in self.zones if zone.area == area]
    
    def get_zone_info(self, zone_name: str) -> Optional[Zone]:
        """
        Get complete zone information.
        
        Args:
            zone_name: Name of the zone
            
        Returns:
            Zone object or None if not found
        """
        return self.zone_lookup.get(zone_name)
    
    def list_all_zones(self) -> List[str]:
        """Get list of all zone names."""
        return list(self.zone_lookup.keys())
    
    def get_zones_by_description(self, keyword: str) -> List[str]:
        """
        Find zones by description keyword.
        
        Args:
            keyword: Keyword to search for in descriptions
            
        Returns:
            List of matching zone names
        """
        keyword_lower = keyword.lower()
        return [
            zone.name for zone in self.zones 
            if keyword_lower in zone.description.lower()
        ]
    
    def distance_between_zones(self, zone1_name: str, zone2_name: str) -> float:
        """
        Calculate distance between centers of two zones.
        
        Args:
            zone1_name: First zone name
            zone2_name: Second zone name
            
        Returns:
            Distance between zone centers
        """
        pos1 = self.get_zone_position(zone1_name)
        pos2 = self.get_zone_position(zone2_name)
        
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        
        return math.sqrt(dx * dx + dy * dy)
    
    def get_zones_in_radius(self, center_zone: str, radius: float) -> List[str]:
        """
        Get all zones within a certain radius of a center zone.
        
        Args:
            center_zone: Name of the center zone
            radius: Search radius
            
        Returns:
            List of zone names within radius (including center zone)
        """
        zones_in_radius = []
        
        for zone_name in self.zone_lookup:
            if self.distance_between_zones(center_zone, zone_name) <= radius:
                zones_in_radius.append(zone_name)
        
        return zones_in_radius
    
    def get_zone_area_distribution(self) -> Dict[str, int]:
        """
        Get count of zones by area.
        
        Returns:
            Dictionary with area names and zone counts
        """
        distribution = {"def": 0, "neu": 0, "off": 0}
        
        for zone in self.zones:
            distribution[zone.area.value] += 1
        
        # Convert to full names for readability
        return {
            "defensive": distribution["def"],
            "neutral": distribution["neu"], 
            "offensive": distribution["off"]
        }


# Create global instance for easy access
zone_grid = ZoneGrid()


def get_zone_position(zone_name: str, offset_x: float = 0, offset_y: float = 0) -> Tuple[float, float]:
    """Convenience function to get zone position."""
    return zone_grid.get_zone_position(zone_name, offset_x, offset_y)


def get_zone_by_position(x: float, y: float) -> str:
    """Convenience function to find zone by position."""
    return zone_grid.get_zone_by_position(x, y)


def get_adjacent_zones(zone_name: str) -> List[str]:
    """Convenience function to get adjacent zones."""
    return zone_grid.get_adjacent_zones(zone_name)


def get_zone_bounds(zone_name: str) -> Tuple[float, float, float, float]:
    """Convenience function to get zone bounds."""
    return zone_grid.get_zone_bounds(zone_name)


def list_all_zones() -> List[str]:
    """Convenience function to list all zones."""
    return zone_grid.list_all_zones()


def get_zones_by_area(area: str) -> List[str]:
    """Convenience function to get zones by area."""
    area_enum = ZoneArea(area.lower())
    return zone_grid.get_zone_by_area(area_enum)