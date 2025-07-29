# MCP Test Command

Comprehensive testing of MCP server connection and hockey coaching tools.

## Prerequisites
- MCP server running on port 8000
- Python environment activated

## Connection Testing

1. **Basic Health Check**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

2. **MCP Connection Test**
```bash
cd servers/poc
/Users/liammckendry/spacy_env/bin/python test_mcp_connection.py
```

3. **Agent Direct Test**
```bash
/Users/liammckendry/spacy_env/bin/python test_agent_cli.py
```

## Tool Testing

Test each MCP tool individually:

```bash
# Test search_hockey_knowledge
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/call","params":{"name":"search_hockey_knowledge","arguments":{"query":"U10 skating drills","age_groups":["U10"],"content_types":["drill"]}}}'

# Test create_practice_plan  
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/call","params":{"name":"create_practice_plan","arguments":{"age_group":"U12","focus_areas":["passing"],"duration_minutes":60}}}'

# Test get_coaching_recommendations
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/call","params":{"name":"get_coaching_recommendations","arguments":{"situation":"power play tactics","age_group":"U15"}}}'

# Test analyze_player_development
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/call","params":{"name":"analyze_player_development","arguments":{"current_skills":["skating","passing"],"target_skills":["shooting","puck handling"],"age_group":"U10"}}}'
```

## ChromaDB Validation

Verify hockey knowledge collections:
```bash
# Check collection health (if ChromaDB admin interface available)
# Or test via MCP search queries with different content types:
# - drill: hockey drills and exercises
# - ltad: skill development pathways  
# - tactics: team systems and strategies
# - conduct: rules and fair play
# - office: off-ice training
# - insight: NHL expert knowledge
# - video: instructional content
```

## Success Criteria
- ✅ Health check returns 200
- ✅ MCP connection test passes
- ✅ All 4 tools respond without errors
- ✅ Hockey-specific content returned
- ✅ Agent can access tools successfully