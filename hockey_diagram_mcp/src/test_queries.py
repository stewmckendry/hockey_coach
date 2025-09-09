"""Test queries for validating the atomic pipeline."""

TEST_QUERIES = [
    {
        "id": "simple_2v1",
        "query": "2v1 rush",
        "description": "Basic 2v1 rush - minimal info provided",
        "expected": {
            "players": 3,  # 2 offensive + 1 defensive
            "movements": ["rush", "pass", "shot"],
            "zones": ["neutral", "offensive"]
        }
    },
    {
        "id": "detailed_3v2",
        "query": "3v2 drill starting from defensive zone with breakout pass to center, regroup in neutral zone, then attack",
        "description": "Complex multi-zone drill with specific instructions",
        "expected": {
            "players": 5,  # 3 offensive + 2 defensive
            "movements": ["breakout", "pass", "regroup", "rush"],
            "zones": ["defensive", "neutral", "offensive"]
        }
    },
    {
        "id": "positional_drill",
        "query": "F1 at left dot, F2 in high slot, D1 at point. F1 passes to F2, F2 shoots",
        "description": "Drill with specific positions and movements",
        "expected": {
            "players": 3,
            "specific_positions": True,
            "movements": ["pass", "shot"],
            "zones": ["offensive"]
        }
    },
    {
        "id": "give_and_go",
        "query": "Give and go between two forwards against one defender",
        "description": "Standard hockey play pattern",
        "expected": {
            "players": 3,
            "movements": ["pass", "skate", "pass_back"],
            "pattern": "give_and_go"
        }
    },
    {
        "id": "power_play",
        "query": "5v4 power play umbrella setup with point shot",
        "description": "Special teams formation",
        "expected": {
            "players": 9,  # Could be just 5 offensive shown
            "formation": "umbrella",
            "movements": ["pass", "shot"],
            "zones": ["offensive"]
        }
    }
]

def get_test_query(query_id: str):
    """Get a specific test query by ID."""
    for query in TEST_QUERIES:
        if query["id"] == query_id:
            return query
    return None

def list_test_queries():
    """List all available test queries."""
    return [(q["id"], q["query"]) for q in TEST_QUERIES]