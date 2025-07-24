# 🏗️ MCP Design Architecture - Secure LLM Integration

## Overview
The Thunder Playbook uses a secure three-tier architecture with the Model Context Protocol (MCP) and server-side LLM integration to provide intelligent hockey coaching through a web interface.

## Architecture Diagram

```
┌─────────────────────┐    HTTPS        ┌──────────────────────────┐    FastMCP      ┌─────────────────────┐
│                     │   (Port 3001)   │                          │   (in-memory)   │                     │
│    Next.js Web App  │ ────────────────→ │  🔒 Secure LLM Server    │ ──────────────→ │   hockey_mcp.py     │
│                     │                  │     (Server-side)        │                 │   (Port 8000)       │
│  - React Components │                  │                          │                 │                     │
│  - Chat Interface   │                  │  - Protected API Routes  │                 │  - FastMCP Server   │
│  - SecureChat Hook  │                  │  - OpenAI Integration    │                 │  - MCP Tools        │
│  (No API Keys)      │                  │  - Intent Analysis       │                 │  - ChromaDB Client  │
│                     │                  │  - Rate Limiting         │                 │                     │
└─────────────────────┘                  └──────────────────────────┘                 └─────────────────────┘
            │                                        │                                            │
            │                                        │                                            │
            ▼                                        ▼                                            ▼
   ┌─────────────────┐                    ┌─────────────────────┐                    ┌─────────────────────┐
   │   Browser UI    │                    │   🤖 LLM Agent      │                    │     ChromaDB        │
   │                 │                    │                     │                    │                     │
   │ - Secure Chat   │                    │ - Intent Analysis   │                    │ Vector Collections: │
   │ - Rate Limited  │                    │ - Tool Orchestration│                    │ • drills           │
   │ - No Secrets    │                    │ - Response Synthesis│                    │ • tactics           │
   │ - Metadata View │                    │ - Error Handling    │                    │ • ltad              │
   └─────────────────┘                    └─────────────────────┘                    │ • conduct           │
                                                                                     │ • nhl_insights      │
                                                                                     │ • off_ice           │
                                                                                     └─────────────────────┘
```

## 🔒 Secure LLM Integration (NEW)

### Security Architecture
```
🌐 Browser          🛡️ Next.js Server         🔐 Protected APIs
┌─────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│ Chat UI     │────│ /api/chat           │────│ OpenAI API      │
│ (No Keys)   │    │ - Rate Limiting     │    │ (Server Only)   │
│             │    │ - Input Validation  │    │                 │
│ Metadata    │────│ SecureHockeyAgent   │────│ FastMCP Client  │
│ Display     │    │ - Intent Analysis   │    │ (Hockey Tools)  │
└─────────────┘    └─────────────────────┘    └─────────────────┘
```

### Key Security Features:
- 🔐 **API Keys Protected**: OpenAI key never exposed to browser
- 🛡️ **Rate Limited**: 10 requests/hour per IP (configurable)
- 🕵️‍♂️ **Logic Hidden**: Prompts and orchestration stay server-side
- ✅ **Input Validated**: Message length and format validation
- 🔒 **Error Sanitized**: No internal details exposed to users

## Component Details

### 1. 🌐 Next.js Web App (Frontend + Secure Backend)
**Location**: `web_app/`  
**Port**: 3001  
**Purpose**: User interface + secure LLM processing

**Key Files**:
- `app/api/chat/route.ts` - 🔒 Secure chat endpoint with rate limiting
- `app/api/mcp/route.ts` - Legacy MCP bridge (still available)
- `lib/server/hockeyAgent.ts` - 🤖 Server-side LLM agent
- `lib/api.ts` - MCP client for hockey tools
- `hooks/useChat.ts` - Secure chat hook (calls server-side)
- `components/SecureChatDemo.tsx` - Chat interface with security indicators

**Responsibilities**:
- 🎨 Render coaching interface (search, chat, practice planning)
- 🔒 Process LLM requests securely on server-side
- 🛡️ Rate limiting and input validation
- 🤖 Intent analysis and tool orchestration
- 📊 Display coaching recommendations with metadata

### 2. 🤖 Secure LLM Agent (NEW)
**Location**: `web_app/lib/server/hockeyAgent.ts`  
**Runtime**: Server-side only  
**Purpose**: Intelligent coaching assistant with protected API keys

**Key Features**:
- **🔍 Intent Analysis**: Understands user requests using OpenAI GPT-4o-mini
- **🛠️ Tool Orchestration**: Intelligently selects and calls hockey tools
- **💬 Response Synthesis**: Generates natural coaching responses
- **🛡️ Security**: API keys and prompts never exposed to client

**Processing Pipeline**:
```
User Message → Intent Analysis → Tool Selection → Tool Execution → Response Synthesis
     ↓               ↓               ↓               ↓               ↓
"Plan U10        practice_         create_practice_   Practice      "Great! Here's a
 practice"       planning (95%)    plan + search      plan data     60-min U10..."
```

**Intent Categories**:
- `practice_planning` - Full practice session creation
- `drill_search` - Finding specific drills and exercises
- `coaching_advice` - General tips and recommendations
- `season_setup` - Long-term planning and team structure
- `general_chat` - Hockey-related conversations

### 3. 🔒 Secure API Routes
**Location**: `web_app/app/api/chat/route.ts`  
**Purpose**: Protected endpoint for LLM interactions

**Security Features**:
```typescript
// Rate limiting by IP
const rateLimitMap = new Map<string, { count: number; resetTime: number }>()

// Input validation
if (body.message.length > 1000) {
  return NextResponse.json({ error: 'Message too long' }, { status: 400 })
}

// Server-side processing only
const result = await secureHockeyAgent.processMessage(userMessage, history)
```

**Request/Response Format**:
```json
// POST Request to /api/chat
{
  "message": "Plan a U10 practice focused on skating",
  "conversationHistory": [...]
}

// Response
{
  "success": true,
  "response": "Great! I've created a 60-minute U10 practice...",
  "metadata": {
    "intent": { "intent": "practice_planning", "confidence": 0.95 },
    "toolsCalled": ["create_practice_plan"],
    "processingTimeMs": 1250
  }
}
```

### 4. 🔗 Hockey MCP Direct API (Bridge Layer)
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

### 5. 🧠 Hockey MCP Server (Knowledge Engine)
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

### 1. 🔒 Secure LLM Chat Flow (NEW - Recommended)
```
User Input → Chat Interface → /api/chat → SecureHockeyAgent → Intent Analysis → Tool Selection → MCP Server → ChromaDB
                                                │                    │              │              │           │
Response Display ← Streaming UI ← Server Response ← Response Synthesis ← Tool Results ← MCP Response ← Query Results ←┘
```

**Example Flow**:
1. **User**: "Plan a 60-minute U10 practice focused on skating"
2. **Chat Interface**: Sends POST to `/api/chat` with message + history
3. **Secure Agent**: Analyzes intent → `practice_planning` (confidence: 0.95)
4. **Tool Selection**: Chooses `create_practice_plan` with parameters
5. **MCP Execution**: Calls hockey knowledge tools
6. **Response Synthesis**: Creates natural coaching response
7. **UI Update**: Displays response with metadata (intent, tools used, timing)

### 2. 🔧 Direct MCP Flow (Legacy - Still Available)
```
User Input → React Component → HockeyApiClient → Next.js API Route → Direct API → FastMCP Client → MCP Server → ChromaDB
                                                                                                              │
Result Display ← Component State ← API Response ← HTTP Response ← FastMCP Response ← Tool Result ← Query Results ←┘
```

### 3. Tool Execution Flow
1. **Web App**: User submits chat message: "Show me power play tactics"
2. **Secure Agent**: Analyzes intent → `drill_search` for "power play" content
3. **Tool Selection**: Chooses `search_hockey_knowledge` with tactical focus
4. **MCP Execution**: Calls hockey MCP server with search parameters
5. **ChromaDB**: Performs semantic vector search in `tactics` collection
6. **Response Synthesis**: LLM creates coaching explanation of results
7. **UI Display**: Shows natural response with metadata about search process

## Design Principles

### � **Security First (NEW)**
- **Protected API Keys**: OpenAI credentials never leave the server
- **Rate Limiting**: Configurable limits prevent abuse and control costs
- **Input Validation**: Message sanitization and length restrictions
- **Error Handling**: Graceful fallbacks without exposing internal details
- **Intent Validation**: Ensures requests are legitimate coaching queries

### �🚀 **Performance Optimized**
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

## 📁 File Organization

### Web App Structure
```
web_app/
├── app/
│   ├── api/
│   │   ├── chat/route.ts          # 🔒 Secure LLM endpoint
│   │   └── mcp/route.ts           # Legacy MCP bridge
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   └── SecureChatDemo.tsx         # 🎨 Chat interface
├── hooks/
│   ├── useChat.ts                 # 🔒 Secure chat hook
│   └── useLocalStorage.ts
├── lib/
│   ├── server/
│   │   └── hockeyAgent.ts         # 🤖 Server-side LLM agent
│   ├── api.ts                     # MCP client
│   ├── types.ts                   # TypeScript types
│   └── utils.ts
├── docs/                          # 📚 Documentation
│   ├── DEBUG_SUMMARY.md
│   └── SECURE_SETUP.md
├── scripts/                       # 🛠️ Utility scripts
│   ├── check-environment.js
│   ├── test-secure-chat.js
│   ├── test-agent.mjs
│   └── start-dev.sh
├── .env.example                   # 🔧 Environment template
├── .env.local                     # 🔐 Local secrets (gitignored)
├── package.json
└── README.md
```

### Server Structure
```
servers/
├── hockey_mcp.py                  # 🧠 Core MCP server
├── hockey_mcp_direct_api.py       # 🔗 HTTP bridge (legacy)
└── fastmcp_proxy.py              # 🌐 SSE proxy (alternative)
```

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
1. **🔐 OpenAI API Key Missing**: Check `.env.local` has valid `OPENAI_API_KEY`
2. **🛡️ Rate Limit Exceeded**: Wait for rate limit reset or adjust limits
3. **🔍 Intent Analysis Failing**: Check OpenAI API connectivity and quotas
4. **⚠️ Connection Errors**: Verify all services running on correct ports
5. **🌐 CORS Issues**: Check CORS middleware includes your frontend URL
6. **🛠️ Tool Not Found**: Ensure MCP server has registered the requested tool
7. **🐌 Slow Responses**: Check ChromaDB connection and collection status

### Debug Commands
```bash
# Check environment setup
cd web_app && node scripts/check-environment.js

# Test secure chat API
curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Plan a U10 practice", "conversationHistory": []}'

# Check service health
curl http://localhost:8000/health      # MCP Server
curl http://localhost:3003/api/mcp     # Direct API (if using legacy)

# Test MCP tool directly
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

### 🔒 Security Testing
```bash
# Test rate limiting
for i in {1..15}; do 
  curl -X POST http://localhost:3001/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "test '${i}'"}' &
done

# Test input validation
curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "'$(head -c 2000 < /dev/zero | tr '\0' 'x')'"}'
```

This architecture provides a **secure, intelligent, and scalable** foundation for the Hockey Coach Playbook. The addition of server-side LLM integration creates a ChatGPT-like experience while maintaining enterprise-grade security and cost control. The system gracefully handles errors and provides fallbacks, making it suitable for both development and production environments.

## FastMCP SDK Compliance

Our implementation follows FastMCP best practices with a hybrid architecture:

- **Server Components**: Use FastMCP SDK directly (`hockey_mcp.py`, `hockey_mcp_direct_api.py`)
- **Web Components**: Use HTTP bridge for browser compatibility (`lib/api.ts`)  
- **Security Layer**: Server-side LLM integration with protected API keys (`lib/server/hockeyAgent.ts`)

For detailed compliance analysis, see [`FASTMCP_COMPLIANCE.md`](./FASTMCP_COMPLIANCE.md).

## Production Deployment

For production deployment with HTTP transport and containerized services, see [`PRODUCTION_DEPLOYMENT.md`](./PRODUCTION_DEPLOYMENT.md).

Key production changes:
- **HTTP Transport**: FastMCP client connects to remote MCP server via HTTP
- **Microservices**: Each component runs in separate containers
- **Environment-Aware**: Automatic switching between in-memory (dev) and HTTP (prod)
- **Scalability**: Independent scaling of web app, bridge API, and MCP server

## Summary

This document provides a comprehensive overview of our MCP-based hockey coaching system. The modular architecture allows for easy extension and maintenance while providing rich hockey-specific functionality to users.
