# Trace Check Command

Verify OpenAI tracing functionality and dashboard visibility for hockey coaching agent.

## Prerequisites  
- OpenAI API key configured
- Agent HTTP server running on port 8002
- MCP server operational

## Direct Trace Testing

1. **Simple Agent Test with Trace**
```bash
cd servers/poc
/Users/liammckendry/spacy_env/bin/python -c "
import asyncio
from poc_agents.web_native_mcp_agent import run_web_mcp_agent_with_logging

async def test():
    response = await run_web_mcp_agent_with_logging(
        'What are good skating techniques?', 
        group_id='trace-validation-test'
    )
    print('Response received:', response[:100] + '...')

asyncio.run(test())
"
```

2. **Check Trace URL Output**
Look for log line:
```
🔍 View trace in OpenAI Dashboard: https://platform.openai.com/logs/trace?trace_id=trace_abc123...
```

## HTTP Server Trace Testing

```bash
# Test with group_id for session tracking
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"What are effective passing drills?","group_id":"trace-test-session"}' \
  http://localhost:8002
```

Monitor server logs:
```bash
tail -f agent_server.log
```

## Dashboard Verification

1. **Copy Trace URL from logs**
2. **Open in browser**: `https://platform.openai.com/logs?api=traces`
3. **Verify trace contains:**
   - Workflow name: "Hockey Coaching Agent"
   - Metadata: query_length, query_preview, agent_type, mcp_server
   - Group ID (if provided)
   - Tool calls with parameters
   - LLM generations
   - Timing information
   - Token usage

## Multiple Tool Call Testing

Test queries that trigger multiple tools:

```bash
# Should trigger create_practice_plan multiple times
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"Create a comprehensive practice plan for U12 players focusing on passing, shooting, and defensive positioning","group_id":"multi-tool-test"}' \
  http://localhost:8002
```

Expected trace output:
```
🔧 MCP TOOLS USED - Query: 'Create a comprehensive practice plan...'
   📊 Response: 1105 chars | Tool calls: 3
   🛠️  Tools: create_practice_plan, create_practice_plan, create_practice_plan
   └─ Call 1: create_practice_plan (ID: call_abc...)
   └─ Call 2: create_practice_plan (ID: call_def...)
   └─ Call 3: create_practice_plan (ID: call_ghi...)
```

## Trace Ingestion Verification

Check for successful trace ingestion in logs:
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/traces/ingest "HTTP/1.1 204 No Content"
```

**Success response**: `204 No Content`
**Error responses**: Check for 400/500 errors and metadata validation issues

## Session Grouping Testing

Test related queries with same group_id:

```bash
# Query 1
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"What are basic skating skills for beginners?","group_id":"coaching-conversation-123"}' \
  http://localhost:8002

# Query 2 (same group_id)
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"How do I progress from basic to intermediate skating?","group_id":"coaching-conversation-123"}' \
  http://localhost:8002
```

Verify both traces appear under same group in dashboard.

## Error Handling Testing

Test trace recording during errors:

```bash
# Test with invalid MCP server (stop MCP server first)
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"Test error handling","group_id":"error-test"}' \
  http://localhost:8002
```

Verify trace still records even with MCP errors.

## Performance Analysis

Use traces to analyze:
- **Response Time Breakdown**: MCP calls vs LLM generation
- **Token Usage**: Input/output tokens per request
- **Tool Selection**: Which tools chosen for different query types
- **Error Patterns**: Common failure points

## Success Criteria
- ✅ Trace URLs generated for each agent run
- ✅ Traces visible in OpenAI dashboard
- ✅ Metadata correctly populated
- ✅ Tool calls captured with parameters
- ✅ Session grouping works with group_id
- ✅ Trace ingestion returns 204 No Content
- ✅ Error scenarios still create traces
- ✅ Performance data available for analysis