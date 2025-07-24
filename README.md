# 🏒 Hockey Coach Playbook: AI-Powered Coaching Assistant

The Hockey Coach Playbook is a comprehensive hockey coaching platform that combines AI-powered knowledge search, practice planning, player development, and visual aids. It leverages an MCP (Model Context Protocol) server, semantic vector database (ChromaDB), and AI agents to provide intelligent coaching recommendations and generate hockey diagrams.

## 📁 Project Structure

```
thunder_playbook/
├── 🏒 servers/              # MCP servers and APIs
│   ├── hockey_mcp.py        # Main FastMCP hockey server (port 8000)
│   ├── hockey_mcp_direct_api.py  # Direct API wrapper (port 3003)
│   └── fastmcp_proxy.py     # FastMCP proxy server
├── 🌐 web_app/              # Next.js frontend application
├── 🧪 tests/                # Test files and test data
├── 📜 scripts/              # Utility and processing scripts
├── 📊 models/               # Pydantic data models
├── 🔧 utils/                # Utility functions (ChromaDB, etc.)
├── 📸 image_gen/            # AI image generation tools
├── 📦 chroma_load/          # Data processing and vector DB management
├── 📖 docs/                 # Documentation files
├── 🚀 start_services.py     # Convenient startup script
└── 📋 requirements.txt      # Python dependencies
```

## 🚀 Quick Start

### Option 1: Use the Startup Script (Recommended)
```bash
# Activate virtual environment
cd ..
source spacy_env/bin/activate
cd thunder_playbook

# Start all services
python start_services.py
```

### Option 2: Manual Setup
```bash
# 1. Start the hockey MCP server
python servers/hockey_mcp.py &

# 2. Start the direct API
python servers/hockey_mcp_direct_api.py &

# 3. Start the web application
cd web_app
npm run dev
```

## 🧪 Development & Testing

### CLI Mode: Testing MCP Server
```bash
# Activate virtual environment first
source ../spacy_env/bin/activate

# Test MCP server status
curl http://localhost:8000/health

# Test direct API health check
curl http://localhost:3003/api/mcp

# List available MCP tools (via direct API)
curl -X GET "http://localhost:3003/api/mcp" | jq '.mcpServer.tools_available'

# Test tool call - Search hockey knowledge
curl -X POST "http://localhost:3003/api/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "search_hockey_knowledge", 
    "arguments": {
      "query": "power play setup", 
      "collection": "tactics", 
      "limit": 3
    }
  }' | jq '.data'

# Test tool call - Get coaching recommendations
curl -X POST "http://localhost:3003/api/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_coaching_recommendations", 
    "arguments": {
      "age_group": "bantam", 
      "skill_focus": "skating", 
      "practice_length": 60
    }
  }' | jq '.data'
```

### UI Mode: Running in Browser
```bash
# 1. Start all backend services
python start_services.py

# 2. In a new terminal, start the web app
cd web_app
npm install  # First time only
npm run dev

# 3. Open browser and navigate to:
#    http://localhost:3000

# 4. Test the interface:
#    - Search hockey knowledge in the search bar
#    - Create practice plans with custom parameters
#    - Browse different collections (drills, tactics, etc.)
#    - Generate coaching recommendations for different age groups
```

### Service Status Check
```bash
# Check if all services are running
curl http://localhost:8000/health     # MCP Server
curl http://localhost:3003/api/mcp    # Direct API
curl http://localhost:3000            # Web App (should show HTML)
```

### Access Points
- 🏒 **Hockey MCP Server**: http://localhost:8000
- 🔗 **Direct API**: http://localhost:3003  
- 🌐 **Web App**: http://localhost:3000

---

## 🔍 What It Does

- 🏒 **Hockey Knowledge Search**: Semantic search across 1000+ hockey drills, tactics, skills, and coaching resources
- 📋 **Practice Planning**: AI-generated practice plans with custom time allocations and skill focuses  
- 👤 **Player Development**: Personalized development plans with skill progression tracking
- 🎯 **Coaching Recommendations**: Context-aware advice for specific coaching situations
- 🖼️ **Visual Aids**: AI-generated hockey diagrams and instructional images for kids
- 📊 **Comprehensive Logging**: Production-ready monitoring and debugging capabilities

---

## 🛠 MCP Tools Available

| Tool | Purpose | Description |
|------|---------|-------------|
| `search_hockey_knowledge` | Knowledge Discovery | Search across all hockey content types with semantic matching |
| `get_coaching_recommendations` | AI Coaching Advice | Get personalized coaching recommendations based on context |
| `create_practice_plan` | Practice Planning | Generate structured practice plans with time allocations |
| `analyze_player_development` | Player Development | Create personalized skill development plans and progressions |

---

## 📚 Hockey Knowledge Sources (ChromaDB Collections)

| Collection Prefix | Content Type | Description |
|-------------------|--------------|-------------|
| `conduct-` | Hockey Rules & Ethics | Hockey rules, code of conduct, fair play guidelines |
| `drill-` | On-Ice Drills | Hockey on-ice practice drills and exercises |
| `ltad-` | Development Skills | Long-term athlete development skills and progressions |
| `insight-` | Expert Knowledge | NHL coach and player interview quotes and insights |
| `office-` | Off-Ice Training | Off-ice dryland workout drills and conditioning |
| `tactics-` | Team Systems | Hockey plays, systems, positioning, zone coverage tactics |
| `video-` | Instructional Content | YouTube hockey instructional video transcripts |
| `dryland-` | Training Videos | YouTube dryland training video clip transcripts |

---

## 🗂 Project Structure

```bash
thunder_playbook/
├── hockey_mcp.py        # Main MCP server with coaching tools
├── models/              # Pydantic data models
│   ├── conduct.py       # Rule and conduct models
│   ├── ltad.py         # Skill development models  
│   ├── dryland_models.py # Off-ice training models
│   └── ...             # Other domain models
├── chroma_load/         # ChromaDB data pipeline
│   ├── raw/            # Original source data
│   ├── processed/      # Enriched and structured data
│   ├── indexed/        # ChromaDB-ready files
│   ├── scripts/        # Data processing and indexing scripts
│   └── prompts/        # LLM enrichment prompts
├── image_gen/          # Hockey diagram generation
│   ├── image_agent/    # AI-powered image generation
│   │   └── hockey_image_iterative.py # Two-agent image system
│   ├── prompts/        # External agent prompt files
│   └── outputs/        # Generated hockey diagrams
├── utils/              # Shared utilities
│   ├── chroma_utils.py # ChromaDB helper functions
│   └── datetime_tools.py # Date/time utilities
└── README.md
```

---

## 🚀 How to Run It

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt
# or
uv sync
```

### 1. Start ChromaDB Server
```bash
# Install and start ChromaDB
pip install chromadb
chroma run --host localhost --port 8000 --no-auth
```

### 2. Index Hockey Knowledge (First Time Setup)
```bash
# Index all hockey content into ChromaDB collections
python chroma_load/scripts/index_drills_chroma.py
python chroma_load/scripts/index_ltad_chroma.py  
python chroma_load/scripts/index_tactics.py
python chroma_load/scripts/index_conduct_chroma.py
python chroma_load/scripts/index_nhl_insights_chroma.py
python chroma_load/scripts/index_office_manual_chroma.py
python chroma_load/scripts/index_video_clips_chroma.py
python chroma_load/scripts/index_video_clips_dryland.py
```

### 3. Start the MCP Server
```bash
# Run the hockey coaching MCP server
python hockey_mcp.py
```

### 4. Generate Hockey Diagrams (Optional)
```bash
# Generate instructional hockey images
python image_gen/image_agent/hockey_image_iterative.py
```

---

## 🧠 AI Agents Overview

| Component | Status | Description |
|-----------|---------|-------------|
| **Hockey MCP Server** | ✅ **Production Ready** | Complete coaching toolkit with 4 main tools |
| **Hockey Image Generator** | ✅ **Available** | `image_gen/image_agent/hockey_image_iterative.py` |
| **Other Agents** | 🚧 **Under Construction** | Additional specialized coaching agents in development |

The hockey image generator uses a two-agent system:
- **Generator Agent**: Creates hockey diagrams based on coaching requests
- **Reviewer Agent**: Evaluates and iteratively improves image quality
- **External Prompts**: Maintainable prompt files in `image_gen/prompts/`

---

## 🛠 Tech Stack

- **FastMCP** – Model Context Protocol server framework
- **OpenAI GPT-4** – LLM for coaching recommendations and practice planning
- **ChromaDB** – Vector database for semantic hockey knowledge search
- **Pydantic** – Type-safe data models and validation
- **Python Logging** – Comprehensive debugging and monitoring
- **OpenAI Agents SDK** – Two-agent image generation system

---

## ✅ Status

### Core Platform
- ✅ **MCP Server Tools** - Complete coaching toolkit (search, recommendations, planning, development)
- ✅ **ChromaDB Integration** - 8 hockey knowledge collections with 1000+ items
- ✅ **Comprehensive Logging** - Production-ready monitoring and debugging
- ✅ **Type Safety** - Pydantic models for all data structures

### Knowledge Base  
- ✅ **On-Ice Drills** - Searchable drill database with skill categorization
- ✅ **Tactical Systems** - Hockey plays, positioning, and zone coverage
- ✅ **Player Development** - LTAD-based skill progressions  
- ✅ **Off-Ice Training** - Dryland and conditioning exercises
- ✅ **Rules & Conduct** - Hockey rules and fair play guidelines
- ✅ **Expert Insights** - NHL coach and player interview content

### AI Features
- ✅ **Semantic Search** - Natural language queries across all content
- ✅ **Practice Planning** - Custom time allocations and skill focuses
- ✅ **Player Development Plans** - Personalized progression tracking
- ✅ **Visual Aids** - AI-generated hockey diagrams for instruction

### In Development
- 🚧 **Advanced Agent Workflows** - Specialized coaching agents
- 🚧 **Web Interface** - Coach-friendly UI for easier interaction
- 🚧 **Mobile App** - On-ice coaching assistant

---

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key
CHROMA_HOST=localhost
CHROMA_PORT=8000
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### ChromaDB Collections
The system automatically creates and manages these collections:
- `drills` - On-ice hockey drills  
- `ltad` - Skill development progressions
- `tactics` - Team systems and plays
- `conduct` - Rules and fair play
- `nhl_insights` - Expert coaching knowledge
- `office_manual` - Off-ice training
- `video_clips` - Instructional content
- `video_clips_dryland` - Dryland training content

---

## 📊 Logging & Monitoring

The system includes comprehensive logging with:
- 🔍 **Search Operations** - Query processing and result tracking
- 🤖 **AI Interactions** - OpenAI API calls and response monitoring  
- ✅ **Success Tracking** - Operation completion and result counts
- ❌ **Error Handling** - Detailed error reporting with fallback mechanisms
- ⚠️ **Warnings** - Time allocation mismatches and data quality issues

Log levels can be configured via `LOG_LEVEL` environment variable.

---

## 📬 Feedback

Open an issue or connect if you'd like to collaborate on expanding the Hockey Coach Playbook for other sports or training domains!
