import json
import requests

spec = {
    "diagram_type": "formation",
    "title": "Power Play Umbrella Formation",
    "view": "offensive",
    "players": [
        {"position": "C", "zone": "top_of_circles", "team": "home", "has_puck": False},
        {"position": "LW", "zone": "left_point", "team": "home", "has_puck": False},
        {"position": "RW", "zone": "right_point", "team": "home", "has_puck": False},
        {"position": "F1", "zone": "high_slot", "team": "home", "has_puck": False},
        {"position": "G", "zone": "crease", "team": "home", "has_puck": False}
    ]
}

feedback = "Move LW down to the goal line for a low umbrella setup"

response = requests.post(
    "http://localhost:8001/mcp",
    json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "process_diagram_feedback",
            "arguments": {
                "current_spec": spec,
                "feedback": feedback
            }
        },
        "id": 1
    }
)

result = response.json()
print("Full response:")
print(json.dumps(result, indent=2))
