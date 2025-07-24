# MCP Transport Protocols Overview

This document explains the different transport protocols used in the Hockey Coach Playbook's MCP (Model Context Protocol) integration with OpenAI's Responses API.

## 🏗️ Architecture Overview

**System Flow**:
```
Web App (Next.js) → OpenAI Responses API → Railway MCP Server → ChromaDB
```

The MCP server acts as a bridge between OpenAI's AI models and our hockey coaching knowledge base stored in ChromaDB.

## 🚀 Transport Protocols Explained

### 1. STDIO (Standard Input/Output)

```bash
AI Model ↔ stdin/stdout ↔ MCP Server
```

- **How it works**: Like a command-line program that reads from keyboard, writes to screen
- **Use case**: Local development, desktop applications
- **Pros**: Simple, direct communication
- **Cons**: Only works locally, no network support
- **When to use**: Local testing and development

### 2. SSE (Server-Sent Events)

```bash
Web App → HTTP Request → MCP Server
         ← SSE Stream ←
```

- **How it works**: HTTP connection stays open, server pushes data continuously
- **Real-world analogy**: Live sports scores, chat messages, stock tickers
- **Protocol example**: 
  ```http
  GET /mcp HTTP/1.1
  Accept: text/event-stream
  
  Response:
  event: message
  data: {"jsonrpc": "2.0", "result": "..."}
  ```
- **Pros**: Real-time updates, works through firewalls
- **Cons**: One-way communication (server → client), legacy support in some browsers
- **Status**: Legacy but still supported for compatibility

### 3. Streamable-HTTP

```bash
Web App ↔ HTTP POST ↔ MCP Server
```

- **How it works**: Two-way HTTP communication with session management
- **Real-world analogy**: Modern chat APIs (WhatsApp, Slack)
- **Protocol example**:
  ```http
  POST /mcp HTTP/1.1
  Content-Type: application/json
  X-Session-Id: abc123
  
  {"jsonrpc": "2.0", "method": "tools/list", "id": 1}
  ```
- **Pros**: Two-way communication, stateful sessions, modern standard
- **Cons**: More complex session management
- **Status**: Current standard, preferred by OpenAI

## 🔄 Our Implementation: Dual Transport

### Problem with Single Transport
```
OpenAI → https://railway.app/mcp → FastMCP(streamable-http) → Hockey Tools
```
**Issue**: If OpenAI expected SSE but got Streamable-HTTP → session termination

### Solution: Dual Transport
```
OpenAI → https://railway.app/mcp → FastMCP(streamable-http) → Hockey Tools
    OR → https://railway.app/sse → FastMCP(sse) → Hockey Tools
```
**Benefit**: OpenAI can choose the protocol that works best

### Implementation Details

**Single server process serves multiple endpoints**:
```python
# One FastAPI app with multiple mounted transports
app = FastAPI(title="Hockey MCP Dual Transport Server")
app.mount("/mcp", mcp.streamable_http_app)  # Primary endpoint  
app.mount("/sse", mcp.sse_app)              # Legacy endpoint

# Available endpoints:
# https://hockeycoach-production.up.railway.app/mcp (Streamable-HTTP)
# https://hockeycoach-production.up.railway.app/sse (Server-Sent Events)
# https://hockeycoach-production.up.railway.app/health (Health check)
```

## 🎯 Real-World Example: "Find Stick Handling Drills"

**Step-by-step flow when user asks for hockey advice**:

1. **Web App** sends user message to OpenAI Responses API
2. **OpenAI** decides it needs hockey knowledge and connects to MCP server
3. **Tool Discovery**:
   ```http
   POST https://hockeycoach-production.up.railway.app/mcp
   Content-Type: application/json
   
   {"jsonrpc": "2.0", "method": "tools/list", "id": 1}
   ```

4. **MCP Server Response**:
   ```json
   {
     "jsonrpc": "2.0", 
     "id": 1,
     "result": {
       "tools": [
         {"name": "search_hockey_knowledge", "description": "Search hockey drills and tactics"},
         {"name": "get_coaching_recommendations", "description": "Get personalized coaching advice"},
         {"name": "create_practice_plan", "description": "Generate structured practice plans"},
         {"name": "analyze_player_development", "description": "Create development plans"}
       ]
     }
   }
   ```

5. **Tool Execution**:
   ```http
   POST /mcp
   {
     "jsonrpc": "2.0", 
     "method": "tools/call", 
     "params": {
       "name": "search_hockey_knowledge",
       "arguments": {"query": "stick handling drills", "n_results": 5}
     }
   }
   ```

6. **MCP Server** searches ChromaDB and returns hockey knowledge
7. **OpenAI** synthesizes the response using retrieved hockey data
8. **Web App** displays comprehensive coaching advice

## 🔧 Session Management Deep Dive

### Why Sessions Matter

**Successful Session Flow**:
```
Session abc123: OpenAI ← tools/list ← MCP Server ✅
Session abc123: OpenAI ← search_hockey_knowledge ← MCP Server ✅  
Session abc123: OpenAI ← get_coaching_recommendations ← MCP Server ✅
```

**Broken Session Flow**:
```
Session abc123: OpenAI ← tools/list ← MCP Server ✅
Session abc123: TERMINATED ❌
Session xyz789: OpenAI ← search_hockey_knowledge ← MCP Server ❌ (no context)
```

### Session Headers

**Required Headers for Streamable-HTTP**:
```http
POST /mcp HTTP/1.1
Content-Type: application/json
Accept: application/json, text/event-stream
X-Session-ID: unique-session-identifier
```

## 🎭 Transport Protocol Analogies

- **STDIO**: Talking to someone sitting next to you (direct, local)
- **SSE**: Listening to a radio broadcast (one-way, streaming)
- **Streamable-HTTP**: Having a phone conversation (two-way, stateful)

## 📊 Configuration Reference

### Railway Environment Variables
```bash
MCP_TRANSPORT=dual              # Enable both transports
MCP_PORT=8000                  # Server port
MCP_HOST=0.0.0.0              # Bind to all interfaces
OPENAI_API_KEY=sk-proj-...     # OpenAI API access
CHROMA_SERVER_HOST=https://... # ChromaDB connection
CHROMA_TOKEN=...               # ChromaDB authentication
```

### Railway Start Command
```bash
MCP_TRANSPORT=dual MCP_PORT=8000 python servers/hockey_mcp.py
```

### OpenAI Responses API Configuration
```typescript
{
  type: 'mcp' as const,
  server_url: 'https://hockeycoach-production.up.railway.app/mcp',
  server_label: 'hockey_mcp_server',
  allowed_tools: [
    'search_hockey_knowledge',
    'get_coaching_recommendations', 
    'create_practice_plan',
    'analyze_player_development'
  ]
}
```

## 🔍 Debugging Transport Issues

### Railway Server Logs to Watch For

**Healthy Connection**:
```
🚀 Transport mode: dual
→ Starting DUAL transport (SSE + Streamable-HTTP): http://0.0.0.0:8000
INFO:mcp.server.streamable_http_manager:Created new transport with session ID: abc123
🔍 [TOOL CALL] search_hockey_knowledge: query='stick handling', n_results=5
✅ [TOOL COMPLETE] search_hockey_knowledge: returned 3 results in 0.45s
```

**Problem Indicators**:
```
❌ Session terminated prematurely
❌ DELETE /mcp HTTP/1.1 200 OK (unexpected termination)
❌ POST /mcp HTTP/1.1 404 Not Found (after session ended)
❌ Missing session ID errors
```

### Web App Logs to Monitor

**Successful Integration**:
```
📥 Received response from OpenAI Responses API
🛠️ Tools used: ["search_hockey_knowledge"]
Final message: Here are some great stick handling drills for beginners...
```

**Issues to Investigate**:
```
🛠️ Tools used: [] (empty - no tools called)
Final message: I apologize, but I encountered an issue processing your request.
Raw response: undefined or empty content
```

## 🚀 Best Practices

1. **Use Dual Transport**: Provides maximum compatibility with OpenAI
2. **Monitor Sessions**: Watch for premature termination in logs
3. **Health Checks**: Use `/health` endpoint to verify server status
4. **Graceful Fallback**: Web app falls back to enhanced Chat Completions if MCP fails
5. **Comprehensive Logging**: Track tool calls, sessions, and performance metrics

## 🔗 Related Documentation

- [FastMCP Documentation](https://fastmcp.readthedocs.io/)
- [OpenAI Responses API with MCP](https://platform.openai.com/docs/guides/tools-remote-mcp)
- [Project Architecture](./PROJECT_STRUCTURE.md)
- [Production Deployment](./PRODUCTION_DEPLOYMENT.md)