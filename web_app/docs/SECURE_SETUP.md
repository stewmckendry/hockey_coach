# 🔒 Secure LLM Architecture - Setup Guide

This implementation provides a **secure, server-side** LLM integration for your hockey coaching app. All API keys and business logic remain protected on your server.

## 🏗️ Architecture Overview

```
Browser (Client)                    Next.js Server                FastMCP Server
┌─────────────────┐                ┌─────────────────┐           ┌─────────────────┐
│ User: "Plan     │   HTTPS        │ LLM Agent       │    SSE    │ Hockey Tools    │
│ U10 practice"   │ ──────────────► │ + OpenAI        │ ◄────────► │ (ChromaDB)      │
│                 │                │ (Server-side)   │           │                 │
│ Chat Interface  │ ◄────────────── │ API Routes      │           │ search_hockey_  │
│ (No API keys)   │   Streaming    │ (Secure)        │           │ knowledge()     │
└─────────────────┘                └─────────────────┘           └─────────────────┘
```

## 🔐 Security Benefits

| Aspect | ❌ Client-Side | ✅ Server-Side |
|--------|----------------|----------------|
| **API Keys** | Exposed in browser | Hidden on server |
| **Cost Control** | Users can abuse | Rate limiting + monitoring |
| **Logic Protection** | Prompts visible | Business logic protected |
| **Input Validation** | Client can bypass | Server-side validation |
| **Rate Limiting** | Not possible | IP-based limits |

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
cd web_app
npm install openai
```

### 2. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env.local
```

Add your OpenAI API key to `.env.local`:
```bash
# REQUIRED: OpenAI API Key (keep this secret!)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Optional: MCP Server URL
NEXT_PUBLIC_FASTMCP_URL=http://localhost:3001
```

**⚠️ IMPORTANT**: Never commit `.env.local` to version control!

### 3. Start Your Services

1. **Start the FastMCP Server** (in the root directory):
   ```bash
   python start_services.py
   ```

2. **Start the Next.js App** (in the web_app directory):
   ```bash
   npm run dev
   ```

### 4. Test the Secure Chat

Visit `http://localhost:3000` and try these examples:
- "Plan a U10 practice focused on skating"
- "Show me passing drills for U14"
- "Create a development plan for a beginner goalie"

## 📁 New Files Created

```
web_app/
├── lib/server/
│   └── hockeyAgent.ts          # 🔒 Secure LLM agent (server-only)
├── app/api/chat/
│   └── route.ts                # 🛡️ Protected API endpoint
├── components/
│   └── SecureChatDemo.tsx      # 🎨 Example chat component
└── .env.example                # 📝 Updated with OpenAI config
```

## 🔧 How It Works

### 1. User Sends Message
```typescript
// Client-side: No API keys exposed
await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ message: "Plan U10 practice" })
})
```

### 2. Server Processes Securely
```typescript
// Server-side: API key protected
const agent = new SecureHockeyAgent() // Uses process.env.OPENAI_API_KEY
const result = await agent.processMessage(userMessage)
```

### 3. Intent Analysis
```typescript
// Determines what the user wants:
{
  intent: 'practice_planning',
  confidence: 0.95,
  parameters: { age_group: 'U10', skills: ['skating'] }
}
```

### 4. Tool Execution
```typescript
// Calls appropriate hockey tools:
await apiClient.createPracticePlan('U10', 60, [{ skill: 'skating', time_minutes: 20 }])
```

### 5. Response Synthesis
```typescript
// Generates natural coaching response:
"Great! I've created a 60-minute U10 practice focused on skating..."
```

## 🛡️ Security Features

### Rate Limiting
- **10 requests per hour** per IP address
- Configurable limits
- Redis support for production

### Input Validation
```typescript
// Message length limits
if (body.message.length > 1000) {
  return NextResponse.json({ error: 'Message too long' }, { status: 400 })
}
```

### Error Handling
```typescript
// Safe error messages (no internal details exposed)
catch (error) {
  return NextResponse.json({ error: 'Unable to process coaching request' }, { status: 500 })
}
```

## 📊 Monitoring & Analytics

Each request includes metadata:
```typescript
{
  response: "Your coaching response...",
  metadata: {
    intent: { intent: 'practice_planning', confidence: 0.95 },
    toolsCalled: ['create_practice_plan'],
    processingTimeMs: 1250
  }
}
```

## 🚀 Production Considerations

### Redis for Distributed Rate Limiting
```bash
# Add to .env.local for production
RATE_LIMIT_REDIS_URL=redis://your-redis-url
```

### User Authentication (Future)
```typescript
// Can add user-specific quotas
const userQuota = await getUserQuota(userId)
if (userQuota.used >= userQuota.limit) {
  // Block request
}
```

### Request Caching
```typescript
// Cache common responses to reduce OpenAI costs
const cachedResponse = await redis.get(`coaching:${hash}`)
if (cachedResponse) return cachedResponse
```

## 🎯 Usage Examples

### Practice Planning
```
User: "Plan a 90-minute U14 practice focusing on passing and shooting"

Response: Creates structured practice with warmup, drills, and cooldown
```

### Drill Search
```
User: "Show me 3v2 drills for developing decision making"

Response: Returns relevant drills with teaching points and setup
```

### Player Development
```
User: "Create a 6-week development plan for a U12 defenseman"

Response: Structured plan with skills, drills, and progress markers
```

## 🔍 Troubleshooting

### OpenAI API Key Issues
```
Error: "OpenAI API key not configured"
Solution: Add OPENAI_API_KEY to .env.local
```

### Rate Limiting
```
Error: "Rate limit exceeded"
Solution: Wait 1 hour or adjust limits in route.ts
```

### MCP Server Connection
```
Error: "Unable to process coaching request"
Solution: Ensure FastMCP server is running on port 3001
```

## 📚 Next Steps

1. **Add User Authentication**: Implement user accounts with individual quotas
2. **Add Caching**: Cache responses to reduce OpenAI costs
3. **Enhanced Analytics**: Track popular questions and usage patterns
4. **Streaming Responses**: Add real-time response streaming
5. **Advanced Rate Limiting**: Use Redis for distributed rate limiting

This secure architecture gives you all the benefits of LLM integration while keeping your costs controlled and your intellectual property protected! 🏒
