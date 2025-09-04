"""
Curve generation functions for smooth hockey movement paths.
Provides waypoint generation for different types of hockey movements.
"""

import math
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

def generate_curve_waypoints(
    start: Dict[str, float],
    end: Dict[str, float], 
    curve_type: str = "standard",
    curve_intensity: float = 0.5,
    num_waypoints: int = 3,
    circle_center: Optional[Dict[str, float]] = None
) -> List[Dict[str, float]]:
    """
    Generate waypoints for smooth curved paths between two points.
    
    Args:
        start: Starting position {"x": float, "y": float}
        end: Ending position {"x": float, "y": float}
        curve_type: Type of curve - "standard", "behind_net", "rush", "bank", "button_hook", "cycle", 
                    "circle", "turn_tight", "turn_gradual"
        curve_intensity: How much curve to apply (0.0 = straight, 1.0 = maximum curve)
        num_waypoints: Number of intermediate waypoints to generate
        circle_center: For "circle" type, the center of the faceoff circle to skate around
        
    Returns:
        List of waypoint dictionaries with x, y coordinates
    """
    waypoints = []
    
    # Extract coordinates
    x1, y1 = start["x"], start["y"]
    x2, y2 = end["x"], end["y"]
    
    # Calculate distance and angle
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    
    if distance < 0.1:  # Too close, no waypoints needed
        return []
    
    if curve_type == "standard":
        # Standard skating curve - gentle arc
        # Uses quadratic Bezier curve
        # Control point is perpendicular to the midpoint
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Perpendicular offset for curve
        perp_x = -dy / distance * (distance * curve_intensity * 0.3)
        perp_y = dx / distance * (distance * curve_intensity * 0.3)
        
        control_x = mid_x + perp_x
        control_y = mid_y + perp_y
        
        # Generate points along Bezier curve
        for i in range(1, num_waypoints + 1):
            t = i / (num_waypoints + 1)
            # Quadratic Bezier formula
            wx = (1-t)**2 * x1 + 2*(1-t)*t * control_x + t**2 * x2
            wy = (1-t)**2 * y1 + 2*(1-t)*t * control_y + t**2 * y2
            waypoints.append({"x": round(wx, 1), "y": round(wy, 1)})
    
    elif curve_type == "behind_net":
        # Movement behind the net - needs to curve around the net
        # Net is at x=89 (offensive) or x=-89 (defensive)
        net_x = 89 if x2 > 50 else -89
        
        # Check if movement goes behind net or near the net area
        if abs(net_x - x1) < 20 or abs(net_x - x2) < 20:
            # Add waypoint behind the net
            behind_x = net_x + (3 if net_x > 0 else -3)
            waypoints.append({"x": behind_x, "y": 0})
            
            # Add transition waypoints
            if y1 != 0:
                waypoints.insert(0, {"x": behind_x, "y": y1/2})
            if y2 != 0:
                waypoints.append({"x": behind_x, "y": y2/2})
        else:
            # Not actually behind net, create arc that suggests net avoidance
            # Add curved path that goes around where the net would be
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            # Push the midpoint away from the net
            if abs(mid_x - net_x) < 15:
                offset_y = 20 if mid_y >= 0 else -20
                waypoints.append({"x": round(mid_x, 1), "y": round(mid_y + offset_y, 1)})
            else:
                # Standard curve with emphasis on going around
                for i in range(1, num_waypoints + 1):
                    progress = i / (num_waypoints + 1)
                    wx = x1 + dx * progress
                    wy = y1 + dy * progress + math.sin(progress * math.pi) * 10
                    waypoints.append({"x": round(wx, 1), "y": round(wy, 1)})
    
    elif curve_type == "rush":
        # Rush pattern - fast movement with slight weave
        # Add slight S-curve for realism
        segment_length = distance / (num_waypoints + 1)
        
        for i in range(1, num_waypoints + 1):
            progress = i / (num_waypoints + 1)
            # Linear interpolation with sine wave offset
            wx = x1 + dx * progress
            
            # Add slight weave (S-curve)
            wave_offset = math.sin(progress * math.pi * 2) * curve_intensity * 5
            wy = y1 + dy * progress + wave_offset
            
            # Keep within rink bounds
            wy = max(-42.5, min(42.5, wy))
            waypoints.append({"x": round(wx, 1), "y": round(wy, 1)})
    
    elif curve_type == "bank":
        # Bank pass off boards - calculate reflection point
        # Find closest board
        if abs(y1) > abs(y2):  # Starting closer to boards
            board_y = 42.5 if y1 > 0 else -42.5
            # Calculate where puck hits boards
            t = (board_y - y1) / (dy if dy != 0 else 0.1)
            board_x = x1 + dx * t
            waypoints.append({"x": round(board_x, 1), "y": board_y})
        else:
            # Simple bank - just add midpoint near boards
            mid_x = (x1 + x2) / 2
            board_y = 42.5 if (y1 + y2) / 2 > 0 else -42.5
            waypoints.append({"x": round(mid_x, 1), "y": board_y * 0.9})
    
    elif curve_type == "button_hook":
        # Button hook - curl back toward starting position
        # Create a loop that comes back
        curl_back_x = x1 + dx * 0.7  # Go 70% forward
        curl_back_y = y1 + dy * 0.7
        
        # Then curve back
        waypoints.append({"x": round(curl_back_x, 1), "y": round(curl_back_y, 1)})
        
        # Add lateral movement
        lateral_offset = 10 * curve_intensity
        if dy == 0:  # Moving horizontally, add vertical curl
            waypoints.append({
                "x": round(curl_back_x + dx * 0.1, 1),
                "y": round(curl_back_y + lateral_offset, 1)
            })
        else:  # Has vertical component, add horizontal curl
            waypoints.append({
                "x": round(curl_back_x + lateral_offset, 1),
                "y": round(curl_back_y + dy * 0.1, 1)
            })
    
    elif curve_type == "cycle":
        # Cycle pattern - along the boards
        # Keep close to boards throughout movement
        board_y = 38 if abs(y1) > 30 or abs(y2) > 30 else None
        
        if board_y:
            board_y = board_y if y1 > 0 or y2 > 0 else -board_y
            # Generate waypoints along the boards
            for i in range(1, num_waypoints + 1):
                progress = i / (num_waypoints + 1)
                wx = x1 + dx * progress
                # Stay near boards with slight variation
                wy = board_y + (math.sin(progress * math.pi) * 3)
                waypoints.append({"x": round(wx, 1), "y": round(wy, 1)})
        else:
            # Not near boards, use standard curve
            return generate_curve_waypoints(start, end, "standard", curve_intensity, num_waypoints)
    
    elif curve_type == "circle":
        # Circle skating - around faceoff circles
        # Faceoff circles have radius of approximately 15 units
        if not circle_center:
            # Try to find nearest faceoff circle
            circle_center = find_nearest_faceoff_circle(start)
        
        if circle_center:
            cx, cy = circle_center["x"], circle_center["y"]
            radius = 15  # Standard faceoff circle radius
            
            # Calculate angles for start and end positions relative to circle center
            start_angle = math.atan2(y1 - cy, x1 - cx)
            end_angle = math.atan2(y2 - cy, x2 - cx)
            
            # Determine direction (clockwise or counter-clockwise)
            # Take the shorter arc
            angle_diff = end_angle - start_angle
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Generate waypoints along the arc
            for i in range(1, num_waypoints + 1):
                progress = i / (num_waypoints + 1)
                angle = start_angle + angle_diff * progress
                wx = cx + radius * math.cos(angle)
                wy = cy + radius * math.sin(angle)
                waypoints.append({"x": round(wx, 1), "y": round(wy, 1)})
        else:
            # No exact circle center, create circular arc motion anyway
            # Use midpoint as pivot for circular motion
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            # Calculate radius from start to midpoint
            radius = math.sqrt((mid_x - x1)**2 + (mid_y - y1)**2)
            if radius < 5:  # Too small, use minimum radius
                radius = 10
            
            # Create arc from start to end around midpoint
            start_angle = math.atan2(y1 - mid_y, x1 - mid_x)
            end_angle = math.atan2(y2 - mid_y, x2 - mid_x)
            
            angle_diff = end_angle - start_angle
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Generate circular waypoints
            for i in range(1, num_waypoints + 1):
                progress = i / (num_waypoints + 1)
                angle = start_angle + angle_diff * progress
                wx = mid_x + radius * math.cos(angle)
                wy = mid_y + radius * math.sin(angle)
                # Keep within bounds
                wx = max(-100, min(100, wx))
                wy = max(-42.5, min(42.5, wy))
                waypoints.append({"x": round(wx, 1), "y": round(wy, 1)})
    
    elif curve_type == "turn_tight":
        # Tight turn - sharp turn that loops back toward starting position
        # Creates a tight U-turn or hairpin turn
        
        # Go forward first
        forward_distance = distance * 0.3  # Go 30% forward
        forward_x = x1 + (dx / distance) * forward_distance
        forward_y = y1 + (dy / distance) * forward_distance
        
        # Then sharp turn perpendicular
        perp_x = -dy / distance * (10 * curve_intensity)  # Tight radius
        perp_y = dx / distance * (10 * curve_intensity)
        
        # Waypoints for tight turn
        waypoints.append({"x": round(forward_x, 1), "y": round(forward_y, 1)})
        waypoints.append({"x": round(forward_x + perp_x, 1), "y": round(forward_y + perp_y, 1)})
        
        # If ending back near start, add return path
        if distance < 20:  # Returning to near start position
            waypoints.append({"x": round(x1 + perp_x, 1), "y": round(y1 + perp_y, 1)})
    
    elif curve_type == "turn_gradual":
        # Gradual turn - wide sweeping turn that loops back
        # Creates a large loop or figure-8 pattern
        
        # Calculate loop parameters
        loop_radius = distance * 0.5 * curve_intensity
        
        # Determine loop direction (perpendicular to movement)
        perp_x = -dy / distance * loop_radius
        perp_y = dx / distance * loop_radius
        
        # Create smooth loop waypoints
        angles = [math.pi * 0.25, math.pi * 0.5, math.pi * 0.75, math.pi]
        for angle in angles[:num_waypoints]:
            # Points along a semi-circle
            wx = x1 + dx * 0.5 + perp_x * math.sin(angle)
            wy = y1 + dy * 0.5 + perp_y * math.sin(angle)
            
            # Add some forward progress
            wx += (dx / distance) * (10 * angle / math.pi)
            wy += (dy / distance) * (10 * angle / math.pi)
            
            waypoints.append({"x": round(wx, 1), "y": round(wy, 1)})
    
    return waypoints


def find_nearest_faceoff_circle(position: Dict[str, float]) -> Optional[Dict[str, float]]:
    """
    Find the nearest faceoff circle to a given position.
    
    Returns:
        Center coordinates of nearest faceoff circle, or None if too far
    """
    # Standard faceoff circle locations
    faceoff_circles = [
        {"x": 0, "y": 0},        # Center ice
        {"x": 69, "y": 22.5},    # Offensive right
        {"x": 69, "y": -22.5},   # Offensive left
        {"x": -69, "y": 22.5},   # Defensive right
        {"x": -69, "y": -22.5},  # Defensive left
    ]
    
    px, py = position["x"], position["y"]
    nearest = None
    min_distance = float('inf')
    
    for circle in faceoff_circles:
        distance = math.sqrt((px - circle["x"])**2 + (py - circle["y"])**2)
        if distance < min_distance and distance < 30:  # Within reasonable range
            min_distance = distance
            nearest = circle
    
    return nearest


def validate_path(
    start: Dict[str, float],
    end: Dict[str, float],
    waypoints: List[Dict[str, float]]
) -> Dict[str, any]:
    """
    Validate that a path is legal and realistic for hockey.
    
    Returns:
        Dictionary with validation results and any issues found
    """
    issues = []
    
    # Check bounds for all points
    all_points = [start] + waypoints + [end]
    
    for i, point in enumerate(all_points):
        # Check rink boundaries
        if abs(point["x"]) > 100:
            issues.append(f"Point {i} out of bounds (x={point['x']})")
        if abs(point["y"]) > 42.5:
            issues.append(f"Point {i} out of bounds (y={point['y']})")
        
        # Check if path goes through net area
        # Nets are at (89, 0) and (-89, 0)
        if abs(point["x"] - 89) < 3 and abs(point["y"]) < 4:
            issues.append(f"Point {i} goes through offensive net")
        if abs(point["x"] + 89) < 3 and abs(point["y"]) < 4:
            issues.append(f"Point {i} goes through defensive net")
    
    # Check for unrealistic jumps between points
    for i in range(len(all_points) - 1):
        p1 = all_points[i]
        p2 = all_points[i + 1]
        distance = math.sqrt((p2["x"] - p1["x"])**2 + (p2["y"] - p1["y"])**2)
        
        if distance > 50:  # Unusually large jump
            issues.append(f"Unrealistic jump between points {i} and {i+1} (distance={distance:.1f})")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "total_distance": calculate_path_distance(all_points)
    }


def calculate_path_distance(points: List[Dict[str, float]]) -> float:
    """Calculate total distance of a path through all points."""
    if len(points) < 2:
        return 0.0
    
    total = 0.0
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        distance = math.sqrt((p2["x"] - p1["x"])**2 + (p2["y"] - p1["y"])**2)
        total += distance
    
    return round(total, 1)


def suggest_curve_type(
    movement_type: str,
    start: Dict[str, float],
    end: Dict[str, float],
    description: str = ""
) -> Dict[str, any]:
    """
    Suggest the best curve type based on movement context.
    
    Returns:
        Dictionary with suggested curve type and parameters
    """
    dx = end["x"] - start["x"]
    dy = end["y"] - start["y"]
    distance = math.sqrt(dx**2 + dy**2)
    
    # Check for specific patterns in description
    description_lower = description.lower()
    
    # Circle skating check
    if "circle" in description_lower or "around" in description_lower and ("faceoff" in description_lower or "dot" in description_lower):
        # Check if near a faceoff circle
        circle_center = find_nearest_faceoff_circle(start)
        if circle_center:
            return {
                "curve_type": "circle",
                "curve_intensity": 1.0,
                "num_waypoints": 4,
                "circle_center": circle_center,
                "reasoning": "Skating around faceoff circle drill"
            }
    
    # Turn checks
    if "turn" in description_lower or "loop" in description_lower:
        if "tight" in description_lower or "sharp" in description_lower or "quick" in description_lower:
            return {
                "curve_type": "turn_tight",
                "curve_intensity": 0.9,
                "num_waypoints": 3,
                "reasoning": "Tight turn maneuver"
            }
        elif "gradual" in description_lower or "wide" in description_lower or "sweep" in description_lower:
            return {
                "curve_type": "turn_gradual",
                "curve_intensity": 0.7,
                "num_waypoints": 4,
                "reasoning": "Gradual sweeping turn"
            }
        else:
            # Default turn
            return {
                "curve_type": "turn_gradual" if distance > 20 else "turn_tight",
                "curve_intensity": 0.8,
                "num_waypoints": 3,
                "reasoning": "Turn movement detected"
            }
    
    # Behind net check
    if "behind" in description_lower and "net" in description_lower:
        return {
            "curve_type": "behind_net",
            "curve_intensity": 0.7,
            "num_waypoints": 3,
            "reasoning": "Movement described as going behind net"
        }
    
    # Bank pass check
    if "bank" in description_lower or ("off" in description_lower and "boards" in description_lower):
        return {
            "curve_type": "bank",
            "curve_intensity": 0.5,
            "num_waypoints": 1,
            "reasoning": "Bank pass off boards detected"
        }
    
    # Cycle check
    if "cycle" in description_lower or "corner" in description_lower:
        return {
            "curve_type": "cycle",
            "curve_intensity": 0.6,
            "num_waypoints": 3,
            "reasoning": "Cycling play along boards"
        }
    
    # Rush check
    if distance > 60 and movement_type == "skate":
        return {
            "curve_type": "rush",
            "curve_intensity": 0.3,
            "num_waypoints": 2,
            "reasoning": f"Long skating movement ({distance:.1f} units) suggests rush"
        }
    
    # Button hook check (now more specific)
    if "button" in description_lower and "hook" in description_lower:
        return {
            "curve_type": "button_hook",
            "curve_intensity": 0.8,
            "num_waypoints": 2,
            "reasoning": "Button hook movement detected"
        }
    
    # Curl back check (could be turn or button hook)
    if "curl" in description_lower:
        if "back" in description_lower or "return" in description_lower:
            return {
                "curve_type": "turn_tight",
                "curve_intensity": 0.8,
                "num_waypoints": 3,
                "reasoning": "Curl back movement detected"
            }
    
    # Default based on movement type
    if movement_type == "pass":
        # Passes are usually straight unless specified
        return {
            "curve_type": "standard",
            "curve_intensity": 0.1,  # Very slight curve for realism
            "num_waypoints": 1,
            "reasoning": "Standard pass with minimal curve"
        }
    elif movement_type == "skate":
        # Skating has natural curves
        return {
            "curve_type": "standard",
            "curve_intensity": 0.4,
            "num_waypoints": 2,
            "reasoning": "Standard skating pattern with natural curve"
        }
    elif movement_type == "carry":
        # Carrying puck with slight weave
        return {
            "curve_type": "standard",
            "curve_intensity": 0.3,
            "num_waypoints": 2,
            "reasoning": "Puck carry with controlled movement"
        }
    
    # Default fallback
    return {
        "curve_type": "standard",
        "curve_intensity": 0.3,
        "num_waypoints": 2,
        "reasoning": "Default curve parameters"
    }