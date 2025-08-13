import json
import requests

# The spec from the previous generation
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

# Test feedback processing
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
if "result" in result:
    content = json.loads(result["result"]["content"][0]["text"])
    print("✅ Feedback processed successfully\!")
    print(f"Explanation: {content.get('explanation', 'N/A')}")
    print(f"Changes: {content.get('changes', [])}")
    print(f"Processing time: {content.get('processing_time', 0):.2f}s")
else:
    print(f"❌ Error: {result.get('error', {}).get('message', 'Unknown error')}")
