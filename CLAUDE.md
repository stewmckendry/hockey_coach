# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a Hockey Coach AI Assistant platform with a **hybrid MCP + Responses API architecture**:

### Core Components
- **MCP Server** (`servers/hockey_mcp.py`): FastMCP server providing 4 hockey coaching tools
- **Direct API Server** (`servers/hockey_mcp_direct_api.py`): API wrapper for MCP server (port 3003) 
- **Next.js Web App** (`web_app/`): Frontend with server-side AI integration using OpenAI Responses API
- **Vector Database**: ChromaDB with 8 hockey knowledge collections (1000+ items)
- **AI Image Generation** (`image_gen/`): Two-agent system for hockey diagrams

### Data Flow
1. Raw hockey data → ChromaDB processing → Vector embeddings
2. User queries → MCP tools → Semantic search → AI-powered responses
3. Web app uses both MCP server AND OpenAI Responses API for different features

## Essential Development Commands

### Starting Services
```bash
# All services at once (recommended)
python start_services.py

# Or manually:
python servers/hockey_mcp.py &           # MCP server (port 8000)
python servers/hockey_mcp_direct_api.py &  # API wrapper (port 3003)
cd web_app && npm run dev                # Next.js app (port 3000)
```

### Web App Development
```bash
cd web_app
npm install
npm run dev          # Development server
npm run build        # Production build
npm run start        # Production start
npm run lint         # ESLint
npm run type-check   # TypeScript check
```

### Python Testing
```bash
# Run specific tests
python -m pytest tests/test_fastmcp_client.py
python -m pytest tests/test_age_group.py

# Test MCP server endpoints
curl http://localhost:8000/health
curl http://localhost:3003/api/mcp
```

### ChromaDB Management
```bash
# Index all hockey data (first-time setup)
python chroma_load/scripts/index_drills_chroma.py
python chroma_load/scripts/index_ltad_chroma.py
python chroma_load/scripts/index_tactics.py
# ... (other indexing scripts)
```

## Key Architecture Patterns

### MCP Tools (4 main tools)
- `search_hockey_knowledge`: Semantic search across all collections
- `get_coaching_recommendations`: AI coaching advice
- `create_practice_plan`: Structured practice planning
- `analyze_player_development`: Player skill progression

### ChromaDB Collections
- `conduct-*`: Rules and ethics
- `drill-*`: On-ice drills  
- `ltad-*`: Skill development
- `tactics-*`: Team systems
- `office-*`: Off-ice training
- `insight-*`: NHL expert knowledge
- `video-*`: Instructional content

### Web App Structure
- `app/api/chat/route.ts`: Chat API using OpenAI Responses API
- `app/api/mcp/route.ts`: MCP server proxy
- `lib/server/hockeyAgent.ts`: Server-side AI agent (OpenAI Responses API)
- `lib/server/responsesAgent.ts`: Responses API implementation
- `components/chat/`: Chat interface components

### Data Models
All Pydantic models in `models/`:
- `ltad.py`: Skill development models
- `conduct.py`: Rules and conduct
- `dryland_models.py`: Off-ice training
- Plus domain-specific models

## Environment Setup

Required environment variables:
```bash
OPENAI_API_KEY=your_key_here
CHROMA_HOST=localhost
CHROMA_PORT=8000
LOG_LEVEL=INFO
```

Virtual environment setup:
```bash
# Use existing spacy_env (as per README)
cd ..
source spacy_env/bin/activate  
cd thunder_playbook
```

## Important File Locations

- `start_services.py`: Unified service startup
- `utils/chroma_utils.py`: ChromaDB connection utilities
- `web_app/hooks/useChat.ts`: Chat state management
- `web_app/lib/types.ts`: TypeScript type definitions
- `image_gen/image_agent/hockey_image_iterative.py`: AI diagram generation

## Service Health Checks

Verify all services are running:
```bash
curl http://localhost:8000/health     # MCP Server
curl http://localhost:3003/api/mcp    # Direct API  
curl http://localhost:3000            # Web App
```