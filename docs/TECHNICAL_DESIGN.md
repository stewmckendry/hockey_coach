# Hockey Coach AI Assistant - Technical Design Document

## 🎯 System Overview

The Hockey Coach AI Assistant is a comprehensive platform that provides AI-powered coaching guidance through a multi-tier architecture combining vector databases, MCP (Model Context Protocol) tools, OpenAI's Responses API, and a Next.js web interface.

### Core Value Proposition
- **Knowledge Base**: 1000+ indexed hockey coaching items across 8 specialized collections
- **AI-Powered Coaching**: Context-aware conversations using OpenAI Responses API with native tool integration
- **Scalable Architecture**: Hybrid MCP + Responses API design with production-ready deployment

---

## 🏗️ System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  Next.js Web App (Port 3000)                                  │
│  ├── Chat Interface (React Components)                        │
│  ├── Conversation Management (useChat hook)                   │
│  └── State Management (LocalStorage + OpenAI Context)         │
└─────────────────┬───────────────────────────────────────────────┘
                  │ API Calls
┌─────────────────▼───────────────────────────────────────────────┐
│                    Application Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  API Routes (/api/chat, /api/mcp)                              │
│  ├── Hockey Agent (Hybrid Responses API + MCP Fallback)       │
│  ├── Rate Limiting & Security                                 │
│  └── Error Handling & Validation                              │
└─────────────┬───────────────────────┬───────────────────────────┘
              │                       │
              │ OpenAI Responses API  │ MCP Bridge API
              │ (Primary)             │ (Fallback)
┌─────────────▼───────────────────────▼───────────────────────────┐
│                     AI/LLM Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  OpenAI Responses API               │  Enhanced Chat Completions│
│  ├── Native MCP Tool Integration    │  ├── Manual Intent Analysis│
│  ├── Automatic Context Management  │  ├── Tool Execution Logic │
│  └── Single-Call Tool + Response   │  └── Response Synthesis   │
└─────────────┬───────────────────────┬───────────────────────────┘
              │                       │
              │ Direct MCP Calls      │ Bridge API Calls
              │                       │
┌─────────────▼───────────────────────▼───────────────────────────┐
│                    MCP Tool Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  Hockey MCP Server (Port 8000)     │  Bridge API (Port 3003)   │
│  ├── FastMCP Framework             │  ├── FastAPI Framework    │
│  ├── 4 Hockey Tools                │  ├── Environment-aware    │
│  └── Railway Deployment            │  └── Local/Remote MCP     │
└─────────────┬───────────────────────────────────────────────────┘
              │ ChromaDB Queries
┌─────────────▼───────────────────────────────────────────────────┐
│                     Data Layer                                 │
├─────────────────────────────────────────────────────────────────┤
│  ChromaDB Vector Database                                      │
│  ├── 8 Specialized Collections (1000+ items)                  │
│  ├── Semantic Search & Embeddings                             │
│  └── Hockey Domain Knowledge                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Architecture

### ChromaDB Collections Structure

```
ChromaDB Instance
├── conduct-* (Rules & Ethics)
│   ├── Fair play codes
│   ├── GTHL rulebook
│   └── Respect policies
├── drill-* (On-Ice Drills)
│   ├── Source 1: Basic drills
│   ├── Source 2: Advanced drills  
│   └── Source 3: Specialty drills
├── ltad-* (Long-Term Athletic Development)
│   ├── Age-specific core skills (U7-U18)
│   ├── Positional development paths
│   └── Goaltending pathways
├── tactics-* (Team Systems)
│   ├── Forechecking systems (1-2-2, 2-1-2, etc.)
│   ├── Power play formations
│   └── Defensive zone coverage
├── office-* (Off-Ice Training)
│   ├── Dryland exercises
│   ├── Conditioning programs
│   └── Skill-specific training
├── insight-* (NHL Expert Knowledge)
│   ├── Professional coaching interviews
│   ├── NHL strategy analysis
│   └── Elite development insights
├── video-* (Instructional Content)
│   ├── Drill demonstrations
│   ├── Technique videos
│   └── Tactical explanations
└── Metadata & Embeddings
    ├── Vector embeddings for semantic search
    ├── Age group classifications
    └── Skill complexity ratings
```

### Data Processing Pipeline

```
Raw Data Sources → Processing Scripts → Enrichment (OpenAI) → ChromaDB Indexing
       │                    │                │                      │
   ├── PDFs            ├── Python        ├── AI Enhancement    ├── Vector DB
   ├── HTML           ├── Extraction     ├── Standardization   ├── Embeddings  
   ├── JSON           ├── Validation     ├── Metadata         ├── Collections
   └── Videos         └── Cleaning       └── Structure        └── Search Index
```

---

## 🔧 Component Architecture

### 1. Frontend (Next.js Web App)

**Technology Stack:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Hooks for state management

**Key Components:**
```
web_app/
├── app/
│   ├── api/
│   │   ├── chat/route.ts         # Main chat API endpoint
│   │   └── mcp/route.ts          # MCP bridge endpoint
│   ├── layout.tsx                # App layout
│   └── page.tsx                  # Main chat page
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx     # Main chat container
│   │   ├── ChatInput.tsx         # Message input with suggestions
│   │   ├── MessageBubble.tsx     # Message display
│   │   ├── ConversationSidebar.tsx # Thread management
│   │   └── TypingIndicator.tsx   # Loading states
│   └── ui/                       # Reusable UI components
├── hooks/
│   ├── useChat.ts               # Chat state & API calls
│   └── useLocalStorage.ts       # Persistent storage
└── lib/
    ├── types.ts                 # TypeScript definitions
    ├── api.ts                   # MCP API client
    └── server/
        └── hockeyAgent.ts       # Server-side AI agent
```

**Data Flow:**
1. User input → ChatInput component
2. useChat hook → API call to /api/chat
3. Server processes with Responses API + MCP tools
4. Response → Message display + conversation storage

### 2. Backend (API Layer)

**Hockey Agent Architecture:**
```typescript
class SecureResponsesAgent {
  // Primary: OpenAI Responses API with native MCP
  async processWithResponsesAPI() {
    // Single API call with MCP tools
    return await openai.responses.create({
      model: 'gpt-4o-2024-11-20',
      tools: [{ type: 'mcp', server_url: 'railway-mcp-server' }],
      previous_response_id: conversationId
    })
  }
  
  // Fallback: Enhanced Chat Completions  
  async processWithEnhancedChat() {
    // Multi-step process
    const intent = await this.analyzeIntentEnhanced()
    const toolResults = await this.executeToolsSecurely()
    return await this.synthesizeEnhancedResponse()
  }
}
```

**API Security:**
- Rate limiting (10 requests/hour per IP)
- Input validation & sanitization  
- OpenAI API key server-side only
- CORS configuration for production

### 3. MCP Tool Layer

**Primary: Hockey MCP Server (Production)**
```python
# servers/hockey_mcp.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Enhanced Hockey MCP Server", stateless_http=True)

@mcp.tool("search_hockey_knowledge")
def search_hockey_knowledge(query, content_types, age_groups, n_results):
    # Semantic search across all collections
    
@mcp.tool("create_practice_plan") 
def create_practice_plan(age_group, duration_minutes, skill_focus_areas):
    # AI-generated practice plans with knowledge integration
    
@mcp.tool("get_coaching_recommendations")
def get_coaching_recommendations(team_age, skill_focus, available_time):
    # Personalized coaching advice
    
@mcp.tool("analyze_player_development")
def analyze_player_development(player_position, current_skills, target_skills):
    # Individual development plans
```

**Fallback: Bridge API**
```python  
# servers/hockey_mcp_production_api.py  
from fastapi import FastAPI

app = FastAPI(title="Hockey MCP Production API")

@app.post("/api/mcp")
async def call_mcp_tool(request: ToolRequest):
    # Environment-aware MCP client routing
    client = get_mcp_client()  # Local or remote
    return await client.call_tool(request.tool, request.parameters)
```

### 4. Data Layer (ChromaDB)

**Connection Architecture:**
```python
# utils/chroma_utils.py
def get_chroma_collection():
    if ENVIRONMENT == 'production':
        # ChromaDB Cloud
        client = chromadb.CloudClient(
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE, 
            api_key=CHROMA_TOKEN
        )
    else:
        # Local ChromaDB
        client = chromadb.Client()
    
    return client.get_collection("hockey_knowledge")
```

**Search & Retrieval:**
- Vector similarity search using OpenAI embeddings
- Metadata filtering (age groups, complexity, content type)
- Relevance scoring and result ranking

---

## 🔄 Data Flow & Integration Patterns

### Primary Flow (OpenAI Responses API + Native MCP)

```
1. User Message → Next.js Frontend
   ├── useChat hook captures input
   └── Calls /api/chat endpoint

2. API Route → Hockey Agent
   ├── Extracts message + previousResponseId  
   ├── Rate limiting & validation
   └── Calls secureResponsesAgent.processMessage()

3. Responses API + MCP Integration
   ├── Single openai.responses.create() call
   ├── OpenAI discovers MCP tools automatically  
   ├── LLM decides which tools to call
   ├── Tools execute → ChromaDB searches
   ├── Results integrated into LLM context
   └── Final response synthesized natively

4. Response Processing
   ├── Extract response.output_text
   ├── Store responseId for conversation continuity
   └── Return structured response

5. Frontend Update  
   ├── Display assistant message
   ├── Update conversation thread
   └── Store responseId for next turn
```

### Fallback Flow (Enhanced Chat Completions)

```
1. Intent Analysis (GPT-4o-mini)
   ├── Analyze user message + conversation context
   ├── Classify intent (practice_planning, drill_search, etc.)
   └── Extract parameters & reasoning

2. Tool Execution (Python + ChromaDB)
   ├── Route to appropriate MCP tools via bridge API
   ├── Execute multiple ChromaDB searches
   ├── Gather relevant hockey knowledge
   └── Aggregate tool results

3. Response Synthesis (GPT-4o) 
   ├── Combine user message + intent + tool results
   ├── Generate conversational coaching response
   ├── Maintain context via prompt engineering
   └── Return final response + metadata
```

---

## 🚀 Deployment & Infrastructure

### Development Environment

**Local Setup:**
```bash
# Start all services
python start_services.py

# Individual services  
python servers/hockey_mcp.py          # MCP Server (Port 8000)
python servers/hockey_mcp_direct_api.py # Bridge API (Port 3003)  
cd web_app && npm run dev             # Next.js (Port 3000)
```

**Environment Configuration:**
```bash
# .env.development
OPENAI_API_KEY=sk-...
CHROMA_HOST=localhost
CHROMA_PORT=8000
LOG_LEVEL=INFO
NEXT_PUBLIC_FASTMCP_URL=http://localhost:3003
```

### Production Deployment

**Docker Compose Architecture:**
```yaml
# docker-compose.prod.yml
services:
  hockey-mcp:     # MCP Server
    ports: ["8000:8000"]
    environment:
      - MCP_TRANSPORT=http
      - CHROMA_SERVER_HOST=${CHROMA_SERVER_HOST}
      
  hockey-bridge:  # Bridge API  
    ports: ["3003:3003"]
    depends_on: [hockey-mcp]
    
  web-app:       # Next.js
    ports: ["3000:3000"] 
    depends_on: [hockey-bridge]
```

**Production Infrastructure:**
- **MCP Server**: Railway deployment with auto-scaling
- **ChromaDB**: ChromaDB Cloud with persistent vectors
- **Web App**: Vercel/Railway deployment
- **Bridge API**: Railway containerized deployment

### Environment Configurations

**Development:**
- Local ChromaDB instance
- In-memory MCP client
- Hot-reload development servers
- Detailed logging & debugging

**Production:**
- ChromaDB Cloud (managed vector database)
- HTTP/SSE MCP transport protocols  
- Container orchestration via Docker Compose
- Production logging & monitoring

---

## 🎛️ Configuration & Customization

### MCP Server Configuration

**Transport Protocols:**
```python
# Supports multiple transports for compatibility
if transport == 'stdio':        # Development
    mcp.run(transport="stdio")
elif transport == 'sse':         # HTTP Server-Sent Events  
    uvicorn.run(mcp.sse_app)
else:                           # Streamable HTTP (preferred)
    uvicorn.run(mcp.streamable_http_app)
```

**Tool Configuration:**
```python
# Hockey-specific tool definitions
@mcp.tool("search_hockey_knowledge") 
def search_hockey_knowledge(
    query: str,
    content_types: Optional[List[str]] = None,  # drill, video, skill, tactic
    complexity_levels: Optional[List[str]] = None,  # beginner, intermediate, advanced
    age_groups: Optional[List[str]] = None,  # U8, U10, U12, etc.
    n_results: int = 10
):
    # Intelligent filtering across all hockey knowledge types
```

### Conversation Management

**OpenAI Responses API Context:**
```typescript
// Native conversation state management
const response = await openai.responses.create({
  previous_response_id: "resp_abc123",  // Automatic context continuation
  store: true,  // OpenAI manages conversation server-side
  tools: [{ type: 'mcp', server_url: 'mcp-server' }]
})
```

**Frontend Thread Management:**
```typescript
// useChat hook - conversation threads
interface ConversationThread {
  id: string
  title: string  
  responseId: string     // OpenAI's conversation state
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}
```

---

## 📈 Performance & Scalability

### Performance Optimizations

**OpenAI Responses API:**
- Tool caching: `mcp_list_tools` cached at conversation level
- Single LLM inference vs. multiple Chat Completion calls
- Native conversation state management (no large context payloads)

**ChromaDB Optimizations:**
- Vector embeddings for semantic search
- Metadata indexing for efficient filtering
- Result pagination and relevance scoring

**Frontend Optimizations:**
- React component memoization
- LocalStorage for conversation persistence
- Debounced input handling

### Scalability Considerations

**Horizontal Scaling:**
- Stateless MCP server design
- Containerized deployments
- Load balancer compatible

**Data Scaling:**
- ChromaDB Cloud auto-scaling
- Collection-based knowledge partitioning
- Efficient vector storage and retrieval

---

## 🔒 Security & Compliance

### API Security

**Authentication & Authorization:**
- OpenAI API key server-side only
- Rate limiting by IP address
- Input validation and sanitization
- CORS configuration for production origins

**Data Protection:**
- No PII storage in conversation threads
- ChromaDB Cloud encryption at rest
- Secure environment variable management

### Privacy Considerations

**Conversation Data:**
- OpenAI manages conversation state (GDPR compliant)
- Local conversation metadata only (titles, timestamps)
- No sensitive coach/player information stored

---

## 🛠️ Development Workflow

### Key Development Commands

```bash
# Environment Setup
cd .. && source spacy_env/bin/activate && cd thunder_playbook

# Service Management  
python start_services.py              # Start all services
curl http://localhost:8000/health      # Health checks
curl http://localhost:3003/api/mcp

# Web App Development
cd web_app
npm install && npm run dev             # Development server
npm run build && npm run start        # Production build
npm run lint && npm run type-check    # Code quality

# Data Management
python chroma_load/scripts/index_drills_chroma.py    # Index data
python chroma_load/scripts/index_ltad_chroma.py
```

### Testing Strategy

**Component Testing:**
- React component unit tests
- API endpoint testing
- MCP tool functionality tests

**Integration Testing:**
- End-to-end conversation flows
- OpenAI Responses API integration
- ChromaDB data retrieval

**Performance Testing:**
- Response time benchmarks
- Concurrent user handling
- ChromaDB query performance

---

## 🔮 Future Enhancements

### Planned Features

**Enhanced AI Capabilities:**
- Multi-modal support (image generation for drills)
- Voice input/output for hands-free coaching
- Real-time practice plan adjustments

**Advanced Analytics:**
- Coaching conversation insights
- Usage pattern analysis
- Recommendation effectiveness metrics

**Integration Expansions:**
- Calendar integration for practice scheduling
- Video platform connections
- Team management system APIs

### Technical Debt & Improvements

**Code Quality:**
- Comprehensive TypeScript coverage
- Enhanced error handling patterns
- Performance monitoring integration

**Architecture Enhancements:**
- Microservices decomposition
- Event-driven architecture
- Caching layer optimization

---

## 📋 Appendices

### A. Environment Variables Reference

```bash
# Core Configuration
OPENAI_API_KEY=sk-...                    # OpenAI API access
ENVIRONMENT=development|production        # Deployment mode

# ChromaDB Configuration  
CHROMA_HOST=localhost                    # ChromaDB server
CHROMA_PORT=8000                        # ChromaDB port
CHROMA_SERVER_HOST=cloud.host           # Production ChromaDB
CHROMA_TOKEN=token                      # ChromaDB Cloud auth

# Service Ports
MCP_PORT=8000                          # MCP server port
BRIDGE_PORT=3003                       # Bridge API port
WEB_PORT=3000                         # Next.js port

# URLs
NEXT_PUBLIC_FASTMCP_URL=http://localhost:3003  # Bridge API URL
MCP_SERVER_URL=https://railway.app/mcp         # Production MCP URL
```

### B. API Endpoints Reference

```
GET  /api/chat                         # Health check
POST /api/chat                         # Send chat message
GET  /api/mcp                          # MCP health check  
POST /api/mcp                          # Call MCP tool

# MCP Server Endpoints
GET  /health                           # Server health
GET  /tools                           # List available tools
POST /tools/invoke                     # Execute tool
```

### C. ChromaDB Collection Schema

```python
# Collection Structure
{
  "id": "drill-skating-001",
  "metadata": {
    "title": "Forward Skating Progression",
    "content_type": "drill",
    "age_group": "U10",
    "complexity": "beginner", 
    "skills": ["skating", "balance"],
    "equipment": ["cones", "pucks"],
    "source": "Hockey Canada"
  },
  "document": "Full drill description with setup, execution, and teaching points...",
  "embedding": [0.1, 0.2, ...]  # Vector embedding
}
```

---

**Document Version:** 2.0  
**Last Updated:** January 2025  
**Authors:** Development Team  
**Status:** Current Architecture