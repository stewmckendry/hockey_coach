#!/bin/bash

echo "🏒 Hockey Coach - OpenAI Responses API Test"
echo "=============================================="

# Check if environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not found in environment"
    echo "Please set it with: export OPENAI_API_KEY=your_api_key"
else
    echo "✅ OPENAI_API_KEY found"
fi

# Check if FastMCP server is running
echo ""
echo "Testing FastMCP server connection..."
if curl -s http://localhost:3001/health > /dev/null; then
    echo "✅ FastMCP server is running on port 3001"
else
    echo "❌ FastMCP server not responding on port 3001"
    echo "Start it with: cd web_app && npm run dev"
fi

# Check project structure
echo ""
echo "Checking project files..."

files=(
    "web_app/lib/server/responsesAgent.ts"
    "web_app/app/api/chat/route.ts"
    "web_app/hooks/useChat.ts"
    "web_app/components/chat/ChatInterface.tsx"
    "web_app/components/chat/ConversationSidebar.tsx"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

echo ""
echo "🚀 Ready to test OpenAI Responses API integration!"
echo ""
echo "Test scenarios:"
echo "1. Start conversation: 'I coach U10 A hockey'"
echo "2. Continue: 'What drills should I focus on?'"
echo "3. Follow-up: 'Show me a practice plan'"
echo ""
echo "Expected: OpenAI automatically remembers context between messages"
echo ""
echo "To run the development server:"
echo "cd web_app && npm run dev"
