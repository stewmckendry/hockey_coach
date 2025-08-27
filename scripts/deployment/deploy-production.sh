#!/bin/bash

# Production Deployment Script
set -e

echo "🚀 Deploying Hockey Coach Playbook to Production"

# Check required files
if [ ! -f ".env.production" ]; then
    echo "❌ Missing .env.production file"
    echo "   Copy .env.production.example and fill in your values"
    exit 1
fi

# Load production environment
source .env.production

# Build and start services
echo "📦 Building Docker images..."
docker-compose -f docker-compose.prod.yml build

echo "🏒 Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Health checks
echo "🔍 Checking service health..."

# Check MCP Server
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ MCP Server is healthy"
else
    echo "❌ MCP Server health check failed"
fi

# Check Bridge API
if curl -f http://localhost:3003/health > /dev/null 2>&1; then
    echo "✅ Bridge API is healthy"
else
    echo "❌ Bridge API health check failed"
fi

# Check Web App
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Web App is healthy"
else
    echo "❌ Web App health check failed"
fi

echo ""
echo "🎉 Production deployment complete!"
echo ""
echo "Services running at:"
echo "  🌐 Web App:     http://localhost:3000"
echo "  🔗 Bridge API:  http://localhost:3003"
echo "  🧠 MCP Server:  http://localhost:8000"
echo "  🗄️  ChromaDB:    ${CHROMA_SERVER_HOST} (cloud)"
echo ""
echo "To view logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "To stop:      docker-compose -f docker-compose.prod.yml down"
