"""
Enhanced offset system for hockey diagram positioning.

Provides natural language offset descriptors that translate to precise coordinate adjustments
within zones. This system allows for flexible positioning using terms coaches understand.
"""

from typing import Dict, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum


class OffsetType(Enum):
    """Types of offset positioning."""
    DEPTH = "depth"          # Deep/shallow in zone
    HEIGHT = "height"        # High/low relative to center
    BOARDS = "boards"        # Near/away from boards
    NET = "net"             # Near/away from net
    SLOT = "slot"           # Slot positioning adjustments
    CUSTOM = "custom"       # Custom x,y coordinates


@dataclass
class OffsetSpec:
    """Specification for position offset within a zone."""
    x: float
    y: float
    description: str
    priority: int = 0  # Higher priority offsets override lower ones


class EnhancedOffsetSystem:
    """
    Enhanced offset system for natural language positioning within zones.
    
    Converts descriptive terms like 'deep', 'high', 'near boards' into
    precise coordinate adjustments relative to zone centers.
    """
    
    # Descriptive offset mappings
    DESCRIPTIVE_OFFSETS = {
        # Depth offsets (toward/away from goal)
        "deep": OffsetSpec(-8, 0, "Deep in zone (toward boards)", 3),
        "shallow": OffsetSpec(5, 0, "Shallow in zone (toward center)", 3),
        "forward": OffsetSpec(8, 0, "Forward in zone", 2),
        "back": OffsetSpec(-5, 0, "Back in zone", 2),
        
        # Height offsets (relative to center line)
        "high": OffsetSpec(0, 8, "High in zone (away from boards)", 3),
        "low": OffsetSpec(0, -8, "Low in zone (toward boards)", 3),
        "center": OffsetSpec(0, 0, "Zone center", 1),
        "middle": OffsetSpec(0, 0, "Zone middle", 1),
        
        # Board proximity
        "near_boards": OffsetSpec(0, -10, "Near the boards", 4),
        "boards": OffsetSpec(0, -12, "Against the boards", 5),
        "off_boards": OffsetSpec(0, 6, "Away from boards", 2),
        
        # Net proximity (contextual based on zone)
        "net_front": OffsetSpec(8, 0, "In front of net", 4),
        "net_side": OffsetSpec(3, -8, "Side of net", 3),
        "behind_net": OffsetSpec(-12, 0, "Behind net", 4),
        
        # Slot positioning
        "slot": OffsetSpec(5, 0, "In the slot", 3),
        "slot_side": OffsetSpec(3, -5, "Side of slot", 2),
        "high_slot": OffsetSpec(8, 0, "High slot", 3),
        "low_slot": OffsetSpec(-3, 0, "Low slot", 3),
        
        # Corner positioning
        "corner": OffsetSpec(-10, -10, "In the corner", 4),
        "corner_deep": OffsetSpec(-12, -8, "Deep in corner", 5),
        
        # Point positioning (for defensemen)
        "point": OffsetSpec(15, 0, "At the point", 3),
        "point_left": OffsetSpec(12, -15, "Left point", 4),
        "point_right": OffsetSpec(12, 15, "Right point", 4),
        
        # Half-wall positioning
        "half_wall": OffsetSpec(0, -15, "At half wall", 3),
        "wall": OffsetSpec(0, -18, "Against the wall", 4),
        
        # Face-off positioning
        "faceoff": OffsetSpec(3, 0, "Face-off position", 3),
        "faceoff_left": OffsetSpec(2, -5, "Left of face-off", 3),
        "faceoff_right": OffsetSpec(2, 5, "Right of face-off", 3),
        
        # Support positioning
        "support": OffsetSpec(-5, 3, "Support position", 2),
        "support_high": OffsetSpec(-3, 8, "High support", 2),
        "support_low": OffsetSpec(-3, -8, "Low support", 2),
        
        # Coverage positioning
        "coverage": OffsetSpec(0, 0, "Coverage position", 1),
        "pressure": OffsetSpec(5, 0, "Pressure position", 2),
        
        # Breakout positioning
        "breakout": OffsetSpec(-8, 0, "Breakout position", 2),
        "outlet": OffsetSpec(-10, -15, "Outlet position", 3),
    }
    
    # Zone-specific offset modifiers
    ZONE_MODIFIERS = {
        "defensive": {
            "net_front": OffsetSpec(-8, 0, "Net front (defensive)", 4),
            "behind_net": OffsetSpec(-12, 0, "Behind own net", 4),
            "corner": OffsetSpec(-15, -12, "Defensive corner", 4),
        },
        "offensive": {
            "net_front": OffsetSpec(8, 0, "Net front (offensive)", 4),
            "behind_net": OffsetSpec(12, 0, "Behind opponent net", 4),
            "corner": OffsetSpec(15, -12, "Offensive corner", 4),
        },
        "neutral": {
            "center": OffsetSpec(0, 0, "Neutral zone center", 3),
            "wing": OffsetSpec(0, -15, "Neutral zone wing", 3),
        }
    }
    
    def parse_offset_description(self, description: str, zone_type: Optional[str] = None) -> OffsetSpec:
        """
        Parse natural language offset description into coordinate adjustments.
        
        Args:
            description: Natural language description (e.g., "deep near boards")
            zone_type: Zone context ("defensive", "offensive", "neutral")
            
        Returns:
            OffsetSpec with combined coordinate adjustments
        """
        if not description:
            return OffsetSpec(0, 0, "Default position")
        
        # Normalize description
        desc_lower = description.lower().replace(" ", "_").replace("-", "_")
        
        # Check for exact match first
        if desc_lower in self.DESCRIPTIVE_OFFSETS:
            base_offset = self.DESCRIPTIVE_OFFSETS[desc_lower]
            return self._apply_zone_modifier(base_offset, zone_type)
        
        # Parse compound descriptions (e.g., "deep near boards")
        return self._parse_compound_description(desc_lower, zone_type)
    
    def _parse_compound_description(self, description: str, zone_type: Optional[str] = None) -> OffsetSpec:
        """Parse compound descriptions with multiple offset terms."""
        words = description.split("_")
        
        # Collect all matching offsets
        matching_offsets = []
        for word in words:
            if word in self.DESCRIPTIVE_OFFSETS:
                matching_offsets.append(self.DESCRIPTIVE_OFFSETS[word])
        
        if not matching_offsets:
            # No matches found, return default
            return OffsetSpec(0, 0, f"Unrecognized: {description}")
        
        # Combine offsets by priority (higher priority wins for conflicts)
        final_x, final_y = 0.0, 0.0
        descriptions = []
        
        # Sort by priority (highest first)
        matching_offsets.sort(key=lambda x: x.priority, reverse=True)
        
        for offset in matching_offsets:
            # Add offset values (weighted by priority)
            weight = offset.priority / 5.0  # Normalize priority
            final_x += offset.x * weight
            final_y += offset.y * weight
            descriptions.append(offset.description)
        
        # Limit combined offset magnitude
        final_x = max(-20, min(20, final_x))
        final_y = max(-20, min(20, final_y))
        
        combined_desc = " + ".join(descriptions[:2])  # Limit description length
        result = OffsetSpec(final_x, final_y, combined_desc)
        
        return self._apply_zone_modifier(result, zone_type)
    
    def _apply_zone_modifier(self, base_offset: OffsetSpec, zone_type: Optional[str] = None) -> OffsetSpec:
        """Apply zone-specific modifiers to base offset."""
        if not zone_type or zone_type not in self.ZONE_MODIFIERS:
            return base_offset
        
        # Check if there's a zone-specific override
        zone_mods = self.ZONE_MODIFIERS[zone_type]
        base_desc = base_offset.description.lower()
        
        for key, modifier in zone_mods.items():
            if key in base_desc:
                # Use zone-specific offset instead of base
                return modifier
        
        return base_offset
    
    def create_custom_offset(self, x: float, y: float, description: str = "") -> OffsetSpec:
        """Create a custom offset with specific coordinates."""
        desc = description or f"Custom ({x}, {y})"
        return OffsetSpec(x, y, desc, priority=6)
    
    def get_available_offsets(self) -> Dict[str, str]:
        """Get list of available offset descriptors with descriptions."""
        return {key: spec.description for key, spec in self.DESCRIPTIVE_OFFSETS.items()}
    
    def validate_offset_coordinates(self, x: float, y: float, zone_bounds: Optional[Tuple[float, float, float, float]] = None) -> Tuple[float, float]:
        """
        Validate and clamp offset coordinates to reasonable bounds.
        
        Args:
            x: X coordinate offset
            y: Y coordinate offset
            zone_bounds: Optional zone boundaries (x_min, y_min, x_max, y_max)
            
        Returns:
            Tuple of validated (x, y) coordinates
        """
        # Apply general bounds
        x = max(-25, min(25, x))  # ±25 units max
        y = max(-25, min(25, y))
        
        # Apply zone-specific bounds if provided
        if zone_bounds:
            x_min, y_min, x_max, y_max = zone_bounds
            # Keep offset within zone boundaries
            x = max(x_min - 100, min(x_max + 100, x))  # Allow some overflow
            y = max(y_min - 42.5, min(y_max + 42.5, y))
        
        return (x, y)


# Global instance for easy access
offset_system = EnhancedOffsetSystem()


def parse_offset(description: Union[str, Dict[str, float]], zone_type: Optional[str] = None) -> Tuple[float, float]:
    """
    Parse offset description or dictionary into coordinates.
    
    Args:
        description: String description or dict with x, y keys
        zone_type: Zone context for modifiers
        
    Returns:
        Tuple of (x, y) coordinate adjustments
    """
    if isinstance(description, dict):
        # Handle dictionary format: {"x": 5, "y": -3, "description": "deep"}
        x = description.get("x", 0)
        y = description.get("y", 0)
        return offset_system.validate_offset_coordinates(x, y)
    
    if isinstance(description, str):
        # Handle string description
        offset_spec = offset_system.parse_offset_description(description, zone_type)
        return offset_system.validate_offset_coordinates(offset_spec.x, offset_spec.y)
    
    # Fallback to no offset
    return (0.0, 0.0)


def get_offset_description(description: str, zone_type: Optional[str] = None) -> str:
    """Get human-readable description of offset."""
    offset_spec = offset_system.parse_offset_description(description, zone_type)
    return offset_spec.description


# Convenience functions for common offsets
def deep_offset(zone_type: Optional[str] = None) -> Tuple[float, float]:
    """Get 'deep' offset for specified zone type."""
    return parse_offset("deep", zone_type)


def high_offset(zone_type: Optional[str] = None) -> Tuple[float, float]:
    """Get 'high' offset for specified zone type."""
    return parse_offset("high", zone_type)


def boards_offset(zone_type: Optional[str] = None) -> Tuple[float, float]:
    """Get 'near boards' offset for specified zone type."""
    return parse_offset("near_boards", zone_type)


def slot_offset(zone_type: Optional[str] = None) -> Tuple[float, float]:
    """Get 'slot' offset for specified zone type."""
    return parse_offset("slot", zone_type)