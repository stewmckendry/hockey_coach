#!/usr/bin/env python3
"""
Drill Diagram Renderer v0.1 with file output option
Renders hockey drill diagrams from v0.1 spec format.
"""

import os
import sys
import json
import base64
import logging
import math
import uuid
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO

# Add hockey_diagram_mcp to path for sportypy imports
hockey_diagram_path = Path(__file__).parent.parent.parent / "servers" / "hockey_diagram_mcp"
sys.path.insert(0, str(hockey_diagram_path))

try:
    from sportypy.surfaces.hockey import NHLRink
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import FancyArrowPatch, Arc
    from matplotlib.patheffects import withStroke
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please install: pip install sportypy matplotlib")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Storage directory for images
IMAGE_DIR = Path(__file__).parent / "drill_images"
IMAGE_DIR.mkdir(exist_ok=True)

# Landmark coordinate mappings (NHL regulation)
LANDMARKS = {
    # Neutral zone landmarks
    "center_dot": (0, 0),
    "blue_line_left": (25, -30),
    "blue_line_right": (25, 30),
    "left_boards": (0, -42),
    "right_boards": (0, 42),
    
    # Offensive zone landmarks
    "left_hashmarks": (69, -22),
    "right_hashmarks": (69, 22),
    "low_slot": (80, 0),
    "behind_net": (89, 0),
}

# Player symbols
PLAYER_SYMBOLS = {
    "X": {"marker": "o", "size": 12, "color": "blue", "label_prefix": "X"},
    "C": {"marker": "s", "size": 12, "color": "green", "label_prefix": "C"},
    "G": {"marker": "D", "size": 14, "color": "red", "label_prefix": "G"},
    "Puck": {"marker": ".", "size": 10, "color": "black", "label_prefix": "P"},
}

# Action styles
ACTION_STYLES = {
    "skate": {"color": "blue", "linestyle": "-", "width": 2, "arrow_style": "->"},
    "pass": {"color": "black", "linestyle": "--", "width": 2, "arrow_style": "->"},
    "shoot": {"color": "red", "linestyle": "-", "width": 3, "arrow_style": "->"},
    "receive": {"color": "gray", "linestyle": ":", "width": 1, "arrow_style": "->"},
}

def validate_spec(spec: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate v0.1 drill spec."""
    # Check schema version
    if spec.get("schema_version") != "0.1":
        return False, f"Invalid schema version: {spec.get('schema_version')} (expected 0.1)"
    
    # Check type
    if spec.get("type") != "drill":
        return False, f"Invalid type: {spec.get('type')} (expected drill)"
    
    # Check required fields
    if "title" not in spec:
        return False, "Missing required field: title"
    
    if "players" not in spec or not isinstance(spec["players"], list):
        return False, "Missing or invalid players array"
    
    if "drill" not in spec or "sequence" not in spec["drill"]:
        return False, "Missing drill.sequence"
    
    # Validate players
    for player in spec["players"]:
        if "id" not in player or "role" not in player or "location" not in player:
            return False, f"Invalid player: {player}"
        
        if "landmark" not in player["location"]:
            return False, f"Player {player['id']} missing location.landmark"
    
    return True, None

def get_landmark_coords(landmark: str, offset: Optional[Dict] = None) -> Tuple[float, float]:
    """Get coordinates for a landmark with optional offset."""
    if landmark not in LANDMARKS:
        logger.warning(f"Unknown landmark: {landmark}, using center")
        x, y = 0, 0
    else:
        x, y = LANDMARKS[landmark]
    
    # Apply offset if provided
    if offset:
        dx = offset.get("dx", 0) * 10  # Scale offset
        dy = offset.get("dy", 0) * 10
        x += dx
        y += dy
    
    return x, y

def draw_arc_path(ax, from_coords: Tuple, to_coords: Tuple, path_spec: Dict, style: Dict):
    """Draw an arc path (curved movement)."""
    if path_spec.get("type") != "arc":
        return
    
    center = LANDMARKS.get(path_spec.get("around_landmark", "center_dot"), (0, 0))
    direction = path_spec.get("direction", "cw")
    sweep = path_spec.get("sweep_degrees", 180)
    
    # Calculate angles
    from_angle = math.atan2(from_coords[1] - center[1], from_coords[0] - center[0])
    to_angle = math.atan2(to_coords[1] - center[1], to_coords[0] - center[0])
    
    # Convert to degrees
    from_angle_deg = math.degrees(from_angle)
    to_angle_deg = math.degrees(to_angle)
    
    # Adjust for direction
    if direction == "ccw":
        if to_angle_deg < from_angle_deg:
            to_angle_deg += 360
    else:  # cw
        if to_angle_deg > from_angle_deg:
            from_angle_deg += 360
    
    # Calculate radius
    radius = math.sqrt((from_coords[0] - center[0])**2 + (from_coords[1] - center[1])**2)
    
    # Draw arc
    arc = Arc(
        center,
        2 * radius,
        2 * radius,
        angle=0,
        theta1=min(from_angle_deg, to_angle_deg),
        theta2=max(from_angle_deg, to_angle_deg),
        color=style["color"],
        linewidth=style["width"],
        linestyle=style["linestyle"]
    )
    ax.add_patch(arc)
    
    # Add arrow at end
    arrow_length = 5
    end_angle = to_angle if direction == "cw" else to_angle
    arrow_start = to_coords
    arrow_end = (
        arrow_start[0] + arrow_length * math.cos(end_angle + math.pi/6),
        arrow_start[1] + arrow_length * math.sin(end_angle + math.pi/6)
    )
    
    ax.annotate(
        "",
        xy=to_coords,
        xytext=(to_coords[0] - 3, to_coords[1] - 3),
        arrowprops=dict(
            arrowstyle="->",
            color=style["color"],
            lw=style["width"]
        )
    )

def render_drill_diagram(spec: Dict[str, Any], output_file: Optional[str] = None) -> str:
    """Render drill diagram from v0.1 spec."""
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Draw rink
    rink = NHLRink()
    rink.draw(ax=ax)
    
    # Draw players
    player_positions = {}
    for player in spec["players"]:
        coords = get_landmark_coords(
            player["location"]["landmark"],
            player["location"].get("offset")
        )
        player_positions[player["id"]] = coords
        
        # Get player style
        style = PLAYER_SYMBOLS.get(player["role"], PLAYER_SYMBOLS["X"])
        
        # Draw player
        ax.plot(
            coords[0], coords[1],
            marker=style["marker"],
            markersize=style["size"],
            color=style["color"],
            markeredgecolor="black",
            markeredgewidth=1,
            zorder=10
        )
        
        # Add label
        ax.text(
            coords[0], coords[1] - 5,
            player["id"],
            fontsize=10,
            ha="center",
            va="top",
            weight="bold",
            path_effects=[withStroke(linewidth=3, foreground="white")]
        )
    
    # Draw drill sequence
    for step in spec["drill"]["sequence"]:
        for action in step["actions"]:
            actor = action["actor"]
            action_type = action["action"]
            
            # Skip actions without proper landmark fields
            if "from_landmark" not in action and "to_landmark" not in action:
                # Handle actor-to-actor actions (pass/receive)
                if "to_actor" in action and actor in player_positions:
                    to_actor = action["to_actor"]
                    if to_actor in player_positions:
                        from_coords = player_positions[actor]
                        to_coords = player_positions[to_actor]
                        
                        # Get action style
                        style = ACTION_STYLES.get(action_type, ACTION_STYLES["skate"])
                        
                        # Draw straight arrow
                        arrow = FancyArrowPatch(
                            from_coords, to_coords,
                            arrowstyle=style["arrow_style"],
                            color=style["color"],
                            linewidth=style["width"],
                            linestyle=style["linestyle"],
                            zorder=5
                        )
                        ax.add_patch(arrow)
                continue
            
            # Get landmarks if they exist
            from_landmark = action.get("from_landmark")
            to_landmark = action.get("to_landmark")
            
            # Skip if neither landmark exists
            if not from_landmark and not to_landmark:
                continue
                
            # Get coordinates
            if from_landmark:
                from_coords = get_landmark_coords(from_landmark)
            else:
                from_coords = player_positions.get(actor, (0, 0))
                
            if to_landmark:
                to_coords = get_landmark_coords(to_landmark)
            else:
                # If only to_actor specified
                if "to_actor" in action and action["to_actor"] in player_positions:
                    to_coords = player_positions[action["to_actor"]]
                else:
                    to_coords = player_positions.get(actor, (0, 0))
            
            # Override with player position if actor in positions
            if actor in player_positions and from_landmark:
                from_coords = player_positions[actor]
            
            # Get action style
            style = ACTION_STYLES.get(action_type, ACTION_STYLES["skate"])
            
            # Check for arc path
            if "path" in action and action["path"].get("type") == "arc":
                draw_arc_path(ax, from_coords, to_coords, action["path"], style)
            else:
                # Draw straight arrow
                arrow = FancyArrowPatch(
                    from_coords, to_coords,
                    arrowstyle=style["arrow_style"],
                    color=style["color"],
                    linewidth=style["width"],
                    linestyle=style["linestyle"],
                    zorder=5
                )
                ax.add_patch(arrow)
            
            # Update player position for next action
            if action_type in ["skate", "receive"]:
                player_positions[actor] = to_coords
    
    # Add title
    ax.set_title(spec.get("title", "Hockey Drill"), fontsize=16, weight="bold", pad=20)
    
    # Add legend
    legend_elements = []
    for action_type, style in ACTION_STYLES.items():
        legend_elements.append(
            plt.Line2D(
                [0], [0],
                color=style["color"],
                linewidth=style["width"],
                linestyle=style["linestyle"],
                label=action_type.capitalize()
            )
        )
    ax.legend(handles=legend_elements, loc="upper left", framealpha=0.9)
    
    # Save to file or buffer
    if output_file:
        plt.savefig(output_file, format="png", dpi=150, bbox_inches="tight")
        plt.close()
        return output_file
    else:
        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        return f"data:image/png;base64,{image_base64}"

# Store generated images
image_store = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "drill-renderer-v0.1"})

@app.route('/render', methods=['POST'])
def render():
    """
    Render drill diagram from v0.1 spec.
    
    Expected JSON payload:
    {
        "spec": { /* v0.1 drill spec */ },
        "output": "base64" | "file"  // Optional, default is base64
    }
    """
    try:
        data = request.get_json()
        spec = data.get("spec")
        output_mode = data.get("output", "base64")
        
        # Log the received spec for debugging
        logger.info(f"Received spec: {json.dumps(spec, indent=2) if spec else 'None'}")
        
        if not spec:
            return jsonify({
                "error": "Missing spec in request",
                "details": "Request must include 'spec' field"
            }), 400
        
        # Validate spec
        is_valid, error_msg = validate_spec(spec)
        if not is_valid:
            return jsonify({
                "error": "Invalid spec",
                "details": error_msg
            }), 400
        
        if output_mode == "file":
            # Generate unique filename
            image_id = str(uuid.uuid4())
            output_file = IMAGE_DIR / f"drill_{image_id}.png"
            
            # Render to file
            render_drill_diagram(spec, output_file)
            
            # Store reference
            image_store[image_id] = output_file
            
            return jsonify({
                "image_url": f"/image/{image_id}",
                "image_id": image_id,
                "warnings": []
            })
        else:
            # Render as base64
            image_url = render_drill_diagram(spec)
            
            return jsonify({
                "image_url": image_url,
                "warnings": []
            })
        
    except Exception as e:
        logger.error(f"Error rendering drill: {str(e)}")
        return jsonify({
            "error": "Rendering failed",
            "details": str(e)
        }), 500

@app.route('/image/<image_id>', methods=['GET'])
def get_image(image_id):
    """Serve rendered image file."""
    if image_id in image_store:
        image_path = image_store[image_id]
        if image_path.exists():
            return send_file(image_path, mimetype='image/png')
    
    return jsonify({"error": "Image not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)