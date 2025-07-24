#!/bin/bash

# Development Setup Script
set -e

echo "🔧 Setting up Hockey Coach Playbook for Development"

# Check required files
if [ ! -f ".env.development" ]; then
    echo "📄 Creating .env.development from example..."
    cp .env.development.example .env.development
    echo "⚠️  Please edit .env.development and add your API keys and ChromaDB credentials"
fi

# Load development environment
source .env.development

# Check if OpenAI API key is set
if [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ Please set your OPENAI_API_KEY in .env.development"
    exit 1
fi

# Check if ChromaDB cloud configuration is set
if [ "$CHROMA_SERVER_HOST" = "your_chroma_host_here" ]; then
    echo "❌ Please configure ChromaDB cloud settings in .env.development:"
    echo "   - CHROMA_SERVER_HOST"
    echo "   - CHROMA_SERVER_HTTP_PORT" 
    echo "   - CHROMA_TOKEN"
    exit 1
fi

# Test ChromaDB cloud connection
echo "🗄️ Testing ChromaDB cloud connection..."
timeout=10
echo "   → Connecting to: $CHROMA_SERVER_HOST:$CHROMA_SERVER_HTTP_PORT"

# Simple connection test using curl if available
if command -v curl >/dev/null 2>&1; then
    if curl -s --max-time 5 "$CHROMA_SERVER_HOST/api/v1/heartbeat" >/dev/null; then
        echo "✅ ChromaDB cloud connection successful"
    else
        echo "⚠️  ChromaDB connection test inconclusive (this may be normal)"
        echo "    The MCP server will test the connection with proper authentication"
    fi
else
    echo "ℹ️  curl not available, skipping connection test"
fi

echo ""
echo "🎉 Development environment ready!"
echo ""
echo "To start the services:"
echo "  1. 🧠 MCP Server:   cd servers && python hockey_mcp.py"
echo "  2. 🔗 Bridge API:   cd servers && python hockey_mcp_production_api.py"
echo "  3. 🌐 Web App:      cd web_app && npm run dev"
echo ""
echo "Services will be available at:"
echo "  🌐 Web App:     http://localhost:3000"
echo "  🔗 Bridge API:  http://localhost:3003" 
echo "  🧠 MCP Server:  http://localhost:8000"
echo "  🗄️  ChromaDB:    $CHROMA_SERVER_HOST (cloud)"
