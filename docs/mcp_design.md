# 🏗️ MCP Design Architecture

## Overview
The Thunder Playbook uses a three-tier architecture with the Model Context Protocol (MCP) to provide hockey coaching knowledge through a web interface.

## Architecture Diagram

```
┌─────────────────────┐    HTTP/REST     ┌──────────────────────────┐    FastMCP      ┌─────────────────────┐
│                     │    (Port 3000)   │                          │   (in-memory)   │                     │
│    Next.js Web App  │ ────────────────→ │  hockey_mcp_direct_api   │ ──────────────→ │   hockey_mcp.py     │
│                     │                  │     (Port 3003)          │                 │   (Port 8000)       │
│  - React Components │                  │                          │                 │                     │
│  - API Routes       │                  │  - FastAPI Server        │                 │  - FastMCP Server   │
│  - HockeyApiClient  │                  │  - FastMCP Client        │                 │  - MCP Tools        │
│                     │                  │  - HTTP→MCP Bridge       │                 │  - ChromaDB Client  │
└─────────────────────┘                  └──────────────────────────┘                 └─────────────────────┘
            │                                        │                                            │
            │                                        │                                            │
            ▼                                        ▼                                            ▼
   ┌─────────────────┐                    ┌─────────────────────┐                    ┌─────────────────────┐
   │   Browser UI    │                    │   FastMCP Client    │                    │     ChromaDB        │
   │                 │                    │                     │                    │                     │
   │ - Search Forms  │                    │ Client(mcp)         │                    │ Vector Collections: │
   │ - Practice Plans│                    │ - Direct import     │                    │ • drills           │
   │ - Drill Library │                    │ - In-memory trans.  │                    │ • tactics           │
   │ - Coaching Tips │                    │ - Tool execution    │                    │ • ltad              │
   └─────────────────┘                    └─────────────────────┘                    │ • conduct           │
                                                                                     │ • nhl_insights      │
                                                                                     │ • off_ice           │
                                                                                     └─────────────────────┘
```

## Component Details

### 1. 🌐 Next.js Web App (Frontend)
**Location**: `web_app/`  
**Port**: 3000  
**Purpose**: User interface for hockey coaches

**Key Files**:
- `app/api/mcp/route.ts` - API route that bridges to MCP
- `lib/api.ts` - HockeyApiClient for calling MCP tools
- `components/` - React UI components

**Responsibilities**:
- Render coaching interface (search, practice planning, drill browsing)
- Handle user interactions and form submissions
- Call backend API endpoints
- Display search results and coaching recommendations

### 2. 🔗 Hockey MCP Direct API (Bridge Layer)
**Location**: `servers/hockey_mcp_direct_api.py`  
**Port**: 3003  
**Purpose**: HTTP wrapper around FastMCP client

**Key Features**:
- **FastAPI server** providing RESTful endpoints
- **In-memory FastMCP client** (`Client(mcp)`)
- **CORS enabled** for web app integration
- **Direct import** of MCP server for optimal performance

**API Endpoints**:
```
GET  /api/mcp           # Health check and server status
POST /api/mcp           # Execute MCP tool calls
```

**Request/Response Format**:
```json
// POST Request
{
  "tool": "search_hockey_knowledge",
  "arguments": {
    "query": "power play setup",
    "collection": "tactics",
    "limit": 5
  }
}

// Response
{
  "success": true,
  "data": [...],
  "timestamp": "2025-07-23T20:30:00Z"
}
```

### 3. 🧠 Hockey MCP Server (Knowledge Engine)
**Location**: `servers/hockey_mcp.py`  
**Port**: 8000  
**Purpose**: Core hockey knowledge and coaching logic

**MCP Tools Available**:
- `search_hockey_knowledge` - Semantic search across all collections
- `get_coaching_recommendations` - AI-powered coaching advice
- `create_practice_plan` - Generate structured practice sessions
- `get_drill_details` - Detailed drill information
- `get_player_development_plan` - LTAD-based progression plans

**Data Sources**:
- **ChromaDB Collections** with 1000+ hockey resources
- **Semantic embeddings** for intelligent search
- **Structured data models** for consistent responses

## Communication Flow

### 1. User Interaction Flow
```
User Input → React Component → HockeyApiClient → Next.js API Route → Direct API → FastMCP Client → MCP Server → ChromaDB
                                                                                                              │
Result Display ← Component State ← API Response ← HTTP Response ← FastMCP Response ← Tool Result ← Query Results ←┘
```

### 2. Tool Execution Flow
1. **Web App**: User submits search query for "power play tactics"
2. **API Route**: Next.js `/api/mcp` route receives POST request
3. **Direct API**: Forwards request to `hockey_mcp_direct_api.py:3003`
4. **FastMCP Client**: Creates `Client(mcp)` and calls tool
5. **MCP Server**: Executes `search_hockey_knowledge` tool
6. **ChromaDB**: Performs semantic vector search in `tactics` collection
7. **Response Chain**: Results flow back through the same path

## Design Principles

### 🚀 **Performance Optimized**
- **In-memory FastMCP**: Direct server import eliminates network overhead
- **Semantic Search**: Vector embeddings for intelligent query matching
- **Structured Data**: Pydantic models ensure type safety and validation

### 🔧 **Development Friendly**
- **Clear Separation**: Frontend, bridge, and backend are loosely coupled
- **Easy Testing**: Each layer can be tested independently
- **Hot Reload**: Changes to any component restart only that service

### 📈 **Scalable Architecture**
- **Stateless Design**: Each request is independent
- **Microservice Pattern**: Components can be scaled independently
- **Protocol Agnostic**: MCP enables future integrations

## Alternative Architectures

### Option A: FastMCP Proxy (Available but not used)
**File**: `servers/fastmcp_proxy.py`  
**Approach**: Uses SSE transport to connect to separate MCP server process  
**When to use**: Production deployments with separate server processes

### Option B: Direct Integration (Current)
**File**: `servers/hockey_mcp_direct_api.py`  
**Approach**: Direct import with in-memory FastMCP client  
**When to use**: Development, testing, and single-process deployments

## Troubleshooting

### Common Issues
1. **Connection Errors**: Check that all services are running on correct ports
2. **CORS Issues**: Verify CORS middleware includes your frontend URL
3. **Tool Not Found**: Ensure MCP server has registered the requested tool
4. **Slow Responses**: Check ChromaDB connection and collection status

### Debug Commands
```bash
# Check service health
curl http://localhost:8000/health      # MCP Server
curl http://localhost:3003/api/mcp     # Direct API

# Test tool directly
python -c "
from servers.hockey_mcp import mcp
from fastmcp import Client
import asyncio

async def test():
    client = Client(mcp)
    async with client:
        result = await client.call_tool('search_hockey_knowledge', {
            'query': 'skating drills',
            'collection': 'drills',
            'limit': 3
        })
        print(result)

asyncio.run(test())
"
```

This architecture provides a robust, scalable foundation for the Hockey Coach Playbook while maintaining simplicity for development and testing.
