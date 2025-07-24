# 📁 Project Structure Documentation

## Overview
The Thunder Playbook project is a production-ready hockey coaching assistant with secure LLM integration, FastMCP compliance, and cloud deployment capabilities. The architecture supports both development and production environments with automatic transport switching.

## Directory Structure

```
thunder_playbook/
├── 📁 servers/                    # MCP servers and API services
│   ├── hockey_mcp.py             # Main FastMCP hockey knowledge server (port 8000)
│   ├── hockey_mcp_direct_api.py  # Legacy direct API wrapper (development only)
│   ├── hockey_mcp_production_api.py # Environment-aware bridge API (secure production)
│   ├── hockey_mcp_backup.py      # Backup/previous version of main server
│   ├── fastmcp_proxy.py          # FastMCP proxy server (alternative approach)
│   └── off_ice/                  # Off-ice training specific server modules
│
├── 🌐 web_app/                    # Next.js 14+ frontend application
│   ├── app/                      # Next.js app directory with API routes
│   │   ├── api/chat/             # Secure chat API endpoint
│   │   ├── api/mcp/              # MCP bridge API endpoints
│   │   ├── layout.tsx            # Root layout with proper Next.js 14 metadata
│   │   └── page.tsx              # Main chat interface page
│   ├── components/               # React components
│   │   └── SecureChatDemo.tsx    # Enhanced secure chat interface
│   ├── lib/                      # Client and server utilities
│   │   ├── server/               # Server-side utilities
│   │   │   └── hockeyAgent.ts    # Secure LLM agent with OpenAI integration
│   │   ├── api.ts               # API client functions
│   │   ├── types.ts             # TypeScript type definitions
│   │   └── utils.ts             # Utility functions
│   ├── scripts/                  # Development and testing scripts
│   │   ├── check-environment.js  # Environment validation
│   │   ├── start-dev.sh         # Development startup script
│   │   ├── test-agent.mjs       # Agent testing utilities
│   │   └── test-secure-chat.js  # Secure chat testing
│   └── docs/                     # Web app specific documentation
│
├── 🧪 tests/                      # All test files and test data
│   ├── test_age_group.py         # Age group functionality tests
│   ├── test_fastmcp_client.py    # FastMCP client integration tests
│   ├── test_ltad_enrichment.py   # LTAD enrichment tests
│   ├── test_positions.py         # Position-related tests
│   ├── test_single_extraction.py # Single extraction tests
│   └── test_extraction_output.json # Test data and expected outputs
│
├── 📜 scripts/                    # Utility and processing scripts
│   ├── analyze_drills_metadata.py # Drill metadata analysis
│   ├── debug_html_extraction.py  # HTML extraction debugging
│   └── generate_image.py         # Image generation utilities
│
├── 📊 models/                     # Pydantic data models and schemas
│   ├── conduct.py                # Conduct-related models
│   ├── dryland_models.py         # Dryland training models
│   ├── enriched_off_ice.py       # Enriched off-ice training models
│   ├── ltad.py                   # Long-term athlete development models
│   ├── mlhs_article.py           # MLHS article models
│   ├── nhl_insight.py            # NHL insights models
│   ├── off_ice.py                # Off-ice training models
│   └── ...                       # Other domain models
│
├── 🔧 utils/                      # Shared utility functions
│   ├── chroma_utils.py           # ChromaDB interaction utilities
│   ├── datetime_tools.py         # Date/time helper functions
│   └── ...                       # Other utility modules
│
├── 📸 image_gen/                  # AI image generation tools
│   ├── image_agent/              # Image generation agents
│   ├── inputs/                   # Input images and templates
│   ├── outputs/                  # Generated output images
│   └── prompts/                  # Image generation prompts
│
├── 📦 chroma_load/                # Data processing and vector DB
│   ├── raw/                      # Raw source data
│   ├── processed/                # Processed and enriched data
│   ├── indexed/                  # Indexed data for ChromaDB
│   ├── scripts/                  # Data processing scripts
│   └── prompts/                  # Processing prompts
│
├── 📖 docs/                       # Documentation files
│   ├── Agents.md                 # Agent architecture documentation
│   ├── mcp_design.md             # MCP design and architecture
│   └── PROJECT_STRUCTURE.md      # This file - project structure overview
│
├── 🐳 Production Deployment Files  # Docker and deployment configuration
│   ├── docker-compose.prod.yml   # Production Docker Compose configuration
│   ├── Dockerfile.mcp            # MCP server container configuration
│   ├── Dockerfile.bridge         # Bridge API container configuration
│   ├── .env.production.example   # Production environment template
│   └── .env.development.example  # Development environment template
│
├── 🚀 start_services.py           # Convenient startup script for all services
├── 📋 requirements.txt            # Python dependencies
├── 📦 pyproject.toml             # Poetry configuration
├── 🔒 uv.lock                    # UV lock file
├── 🔐 .env                       # Environment variables (development)
├── 🔐 .env.development           # Development-specific environment
└── 📖 README.md                  # Main project documentation
```

## Key Architecture Features

### 🔒 **Secure LLM Integration**
- **Server-side OpenAI Integration**: API keys protected on backend
- **SecureHockeyAgent**: Intent analysis, tool orchestration, response synthesis
- **Rate Limiting**: Built-in protection against abuse
- **Environment-aware Configuration**: Automatic development/production switching

### 🚀 **Production-Ready Deployment**
- **Docker Containerization**: Multi-service Docker Compose setup
- **Environment Management**: Separate development and production configurations
- **Cloud ChromaDB Integration**: Pre-configured for Railway deployment
- **Health Checks**: Built-in monitoring and health verification

### ⚡ **FastMCP Compliance**
- **Hybrid Transport**: In-memory (development) + HTTP (production)
- **Excellent SDK Compliance**: Verified FastMCP standards adherence
- **Automatic Client Selection**: Environment-based transport switching
- **Connection Management**: Robust connection handling and cleanup

### 🎯 **Enhanced User Experience**
- **ChatGPT-style Interface**: Modern chat experience with typing indicators
- **Mobile Responsive**: Optimized for tablets and phones during practice
- **Error Handling**: Comprehensive error states and retry mechanisms
- **Debug Information**: Development debugging and monitoring tools

## Development vs Production Architecture

### Development Environment
```
Next.js Dev Server ──HTTP──→ SecureHockeyAgent ──In-Memory FastMCP──→ hockey_mcp.py
     (Port 3000)                (Built-in)                              (Port 8000)
                                     │                                        │
                                     └──OpenAI API                           └──ChromaDB Cloud
                                     (Server-side)                          (Railway)
```

### Production Environment  
```
Next.js App ──HTTP──→ Bridge API ──HTTP FastMCP──→ MCP Server ──→ ChromaDB Cloud
(Port 3000)         (Port 3003)                  (Port 8000)      (Railway)
     │                   │                           │
     └──Docker Container └──Docker Container        └──Docker Container
```

## Key Changes Made

### ✅ **Secure Architecture Implementation**
- **Protected API Keys**: OpenAI keys stored server-side only
- **Secure Chat Endpoint**: Rate-limited `/api/chat` route
- **Intent Analysis**: Smart request processing and validation
- **Tool Security**: Controlled access to MCP tools and functions

### ✅ **Production Deployment Ready**
- **Docker Configuration**: Complete containerization setup
- **Environment Templates**: Pre-configured development and production environments
- **Cloud Integration**: ChromaDB deployed to Railway cloud service
- **Health Monitoring**: Built-in service health checks and monitoring

### ✅ **FastMCP Standards Compliance**
- **SDK Compliance**: Verified excellent adherence to FastMCP standards
- **Transport Flexibility**: Automatic switching between in-memory and HTTP transport
- **Connection Management**: Robust client lifecycle management
- **Error Handling**: Comprehensive FastMCP error handling and recovery

### ✅ **Enhanced Developer Experience**
- **Environment Validation**: Automatic environment setup verification
- **Testing Scripts**: Comprehensive testing for secure chat and agent functionality
- **Debug Tools**: Built-in debugging and monitoring capabilities
- **Documentation**: Updated architecture and deployment documentation

## Usage

### Quick Start (Development)
```bash
# Start all services with secure architecture
cd web_app && npm run dev
# The Next.js app includes built-in secure backend integration
# No separate server startup needed for development
```

### Production Deployment
```bash
# Deploy using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or build and run individual containers
docker build -f Dockerfile.mcp -t hockey-mcp .
docker build -f Dockerfile.bridge -t hockey-bridge .
```

### Environment Setup
```bash
# Development environment
cp .env.development.example .env.development
cp web_app/.env.example web_app/.env.local
# Edit with your API keys and configuration

# Production environment  
cp .env.production.example .env.production
# Configure for your production deployment
```

### Development Workflow
1. **Backend changes**: Edit files in `servers/` or `web_app/lib/server/`
2. **Frontend changes**: Edit files in `web_app/app/` and `web_app/components/`
3. **Data processing**: Use scripts in `chroma_load/scripts/`
4. **Testing**: Run tests from `tests/` and `web_app/scripts/`
5. **Utilities**: Add shared code to `utils/`

### Testing and Validation
```bash
# Test secure chat functionality
cd web_app && node scripts/test-secure-chat.js

# Test agent functionality
cd web_app && node scripts/test-agent.mjs

# Validate environment setup
cd web_app && node scripts/check-environment.js
```

## Service Architecture

### Current Secure Architecture (Production-Ready)
```
┌─────────────────┐    HTTPS      ┌──────────────────────────┐    OpenAI API    ┌─────────────────┐
│    Next.js      │ ──────────────→ │    SecureHockeyAgent     │ ────────────────→ │   OpenAI GPT    │
│   Frontend      │               │   (Built-in Backend)     │                 │   (GPT-4o/mini) │
│  (Port 3000)    │               │  • Intent Analysis       │                 └─────────────────┘
└─────────────────┘               │  • Rate Limiting         │
                                  │  • Tool Orchestration    │                 ┌─────────────────┐
                                  │  • Response Synthesis    │    FastMCP       │   hockey_mcp    │
                                  └──────────────────────────┘ ────────────────→ │   MCP Server    │
                                                │                (In-Memory/HTTP) │  (Port 8000)    │
                                                │                                └─────────────────┘
                                    ┌───────────▼────────────┐                            │
                                    │   Environment-Aware   │                            │
                                    │   FastMCP Transport    │                   ┌────────▼─────────┐
                                    │  • Dev: In-Memory      │                   │    ChromaDB      │
                                    │  • Prod: HTTP          │                   │ Vector Database  │
                                    └────────────────────────┘                   │ (Railway Cloud)  │
                                                                                └──────────────────┘
```

### Legacy Architecture (Development Fallback)
```
┌─────────────┐    HTTP     ┌──────────────────────┐    FastMCP     ┌─────────────────┐
│   Next.js   │ ────────────→ │ hockey_mcp_direct_api │ ──────────────→ │   hockey_mcp    │
│  Frontend   │             │    (Port 3003)       │  (in-memory)   │  (Port 8000)    │
│ (Port 3000) │             └──────────────────────┘                └─────────────────┘
└─────────────┘                        │                                      │
                                       │                                      │
                               ┌───────▼───────┐                    ┌─────────▼──────────┐
                               │  FastMCP      │                    │    ChromaDB        │
                               │  Client       │                    │ Vector Database    │
                               │ (in-memory)   │                    │ (Hockey Knowledge) │
                               └───────────────┘                    └────────────────────┘
```

## Security and Best Practices

### 🔐 **API Key Protection**
- OpenAI API keys stored server-side only
- No client-side exposure of sensitive credentials
- Environment-based configuration management
- Secure environment variable handling

### ⚡ **Performance Optimization**  
- In-memory FastMCP transport for development speed
- HTTP transport for production scalability
- Connection pooling and management
- Efficient vector database queries

### 🛡️ **Error Handling and Resilience**
- Comprehensive error boundaries in React components
- FastMCP connection retry logic
- Graceful degradation for service failures
- User-friendly error messages and recovery options

### 📊 **Monitoring and Debugging**
- Built-in health checks for all services
- Comprehensive logging architecture
- Debug information in development mode
- Production monitoring capabilities

This architecture provides a secure, scalable, and maintainable foundation for the Hockey Coaching Assistant, with excellent FastMCP compliance and production-ready deployment capabilities.
