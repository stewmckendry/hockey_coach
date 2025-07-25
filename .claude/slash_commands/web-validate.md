# Web Validate Command

Complete web integration testing with visual validation and screenshots.

## Prerequisites
- All services running (MCP server, Agent HTTP server, Web app)
- Screenshots directory created: `mkdir -p docs/screenshots`

## Browser Testing

1. **Navigate to Test Interface**
```
Open browser: http://localhost:3000/agent-test
```

2. **Functional Testing**

Test these hockey coaching scenarios:

```
• "What are good U10 skating drills for beginners?"
  → Expected: search_hockey_knowledge tool usage

• "Create a practice plan for U12 players focusing on passing"  
  → Expected: create_practice_plan tool usage

• "How should I develop a player's shooting skills?"
  → Expected: analyze_player_development tool usage

• "What are effective powerplay formations for U15?"
  → Expected: search_hockey_knowledge (tactics)
```

3. **API Testing**
```bash
# Test agent HTTP server directly
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"What are good skating techniques?","group_id":"validation-test"}' \
  http://localhost:8002

# Test web API endpoint
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"Create a practice plan for defensive skills"}' \
  http://localhost:3000/api/agent-test
```

## Visual Validation Checklist

### Desktop View (1920x1080)
- [ ] Chat interface loads properly
- [ ] Message input field functional
- [ ] Submit button works
- [ ] Hockey responses display with formatting
- [ ] Loading indicators show during processing
- [ ] Error states display appropriately

### Mobile View (375x667)  
- [ ] Responsive layout works
- [ ] Chat interface scales correctly
- [ ] Touch interactions functional
- [ ] Text remains readable

### Screenshot Locations
Save screenshots to `docs/screenshots/`:
- `desktop-chat-interface.png`
- `mobile-chat-interface.png`
- `hockey-response-example.png`
- `loading-state.png`
- `error-state.png`

## Trace Validation

1. **Check Server Logs**
```bash
tail -f servers/poc/agent_server.log
```

Look for:
```
🔧 MCP TOOLS USED - Query: 'What are good U10 skating drills?...'
   📊 Response: 1192 chars | Tool calls: 1
   🛠️  Tools: search_hockey_knowledge
🔍 View trace in OpenAI Dashboard: https://platform.openai.com/logs/trace?trace_id=trace_abc123...
```

2. **Dashboard Verification**
- Copy trace URL from logs
- Open in browser
- Verify trace shows:
  - Tool calls with parameters
  - LLM generations
  - Timing information
  - Token usage

## Performance Validation

Expected behavior:
- Response times: 5-15 seconds
- Hockey-specific advice in responses
- Age-appropriate recommendations
- Structured formatting with bullet points
- Video links when available

## Browser Compatibility

Test in available browsers:
- [ ] Chrome (primary)
- [ ] Firefox
- [ ] Safari (if available)

## Troubleshooting Commands

```bash
# Check all services status
curl http://localhost:8000/health      # MCP server
curl http://localhost:8002             # Agent HTTP server  
curl http://localhost:3000             # Web app

# Check browser console for errors
# Check network tab for failed requests  
# Check agent server logs for processing errors
```

## Success Criteria
- ✅ All test queries return hockey-specific responses
- ✅ Tool usage logged with trace URLs
- ✅ Visual validation passes on desktop and mobile
- ✅ Screenshots captured for documentation
- ✅ Performance within expected ranges
- ✅ No browser console errors