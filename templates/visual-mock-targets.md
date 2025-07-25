# Visual Mock Targets for UI Development

Use these visual targets to guide UI implementation and validation.

## Current UI State

### Agent Test Page (`/agent-test`)
**Current Implementation**: Basic chat interface with:
- Simple message input field
- Submit button
- Response display area
- Basic styling

**Target Improvements**:
- Enhanced visual feedback during processing
- Better typography and spacing
- Hockey-themed visual elements
- Mobile-responsive design

## Visual Mock Targets

### 1. Enhanced Chat Interface

**Desktop Target (1920x1080)**:
```
┌─────────────────────────────────────────────────────────────┐
│ 🏒 Hockey Coach AI Assistant              [Settings] [Help] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  👤 User: What are good U10 skating drills?                │
│                                                             │
│  🤖 Coach AI: Here are some excellent skating drills...    │
│     📋 **Forward Skating**                                  │
│     - Focus on gliding and pushing off                     │
│     - Long, powerful strides                               │
│                                                             │
│     🔧 Tools Used: search_hockey_knowledge                  │
│     🔍 View Trace: [Dashboard Link]                        │
│                                                             │
│     ⚡ Response Time: 8.2s                                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 💬 Ask your coaching question...              [📎] [Send]  │
└─────────────────────────────────────────────────────────────┘
```

**Mobile Target (375x667)**:
```
┌─────────────────────────────┐
│ 🏒 Hockey Coach AI     [≡]  │
├─────────────────────────────┤
│                             │
│ 👤 What are good U10        │
│    skating drills?          │
│                             │
│ 🤖 Here are excellent       │
│    skating drills for U10:  │
│                             │
│    📋 **Forward Skating**   │
│    - Focus on gliding       │
│    - Long strides           │
│                             │
│    🔧 search_hockey_know... │
│    ⚡ 8.2s                   │
│                             │
├─────────────────────────────┤
│ Ask coaching question...    │
│                     [Send]  │
└─────────────────────────────┘
```

### 2. Loading States

**During Processing**:
```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 Coach AI is analyzing hockey knowledge...               │
│                                                             │
│ ⚡ Searching drills database...        [████████░░] 80%     │
│ 🔧 Using MCP tools...                 [████████░░] 75%     │
│ 🧠 Generating response...             [████░░░░░░] 40%     │
│                                                             │
│ ⏱️  Processing time: 6.3s                                   │
└─────────────────────────────────────────────────────────────┘
```

### 3. Error States

**MCP Server Error**:
```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️  Connection Issue                                         │
│                                                             │
│ I'm having trouble accessing my hockey knowledge base.     │
│ Please try again in a moment.                              │
│                                                             │
│ 🔧 Technical details:                                       │
│ - MCP server timeout (5.0s)                                │
│ - Retry available in 30s                                   │
│                                                             │
│ [Retry Now] [Report Issue]                                 │
└─────────────────────────────────────────────────────────────┘
```

### 4. Tool Usage Display

**Enhanced Tool Feedback**:
```
┌─────────────────────────────────────────────────────────────┐
│ 🔧 MCP Tools Used:                                          │
│                                                             │
│ 🔍 search_hockey_knowledge                                  │
│    ├─ Query: "U10 skating drills"                          │
│    ├─ Age Groups: [U10]                                    │
│    ├─ Content Types: [drill]                               │
│    └─ Results: 15 relevant drills found                    │
│                                                             │
│ 📊 Response: 1,192 characters | Processing: 8.2s           │
│ 🔍 [View Full Trace in OpenAI Dashboard]                   │
└─────────────────────────────────────────────────────────────┘
```

### 5. Multiple Tool Calls

**Complex Query Response**:
```
┌─────────────────────────────────────────────────────────────┐
│ 🔧 Multiple Tools Used:                                     │
│                                                             │
│ 1️⃣ create_practice_plan                                     │
│    ├─ Age: U12 | Focus: passing | Duration: 60min         │
│    └─ Generated structured plan                            │
│                                                             │
│ 2️⃣ search_hockey_knowledge                                  │
│    ├─ Query: "passing drills U12"                          │
│    └─ Found 12 relevant drills                             │
│                                                             │
│ 3️⃣ get_coaching_recommendations                             │
│    ├─ Situation: "skill development"                       │
│    └─ Provided progression tips                            │
│                                                             │
│ ⚡ Total processing: 14.7s | Tools: 3 | Tokens: 2,847      │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Guidelines

### Color Scheme (Hockey Theme)
- **Primary**: Hockey blue (#003087)
- **Secondary**: Ice white (#F8F9FA)
- **Accent**: Orange (#FF6B35) 
- **Success**: Green (#28A745)
- **Warning**: Amber (#FFC107)
- **Error**: Red (#DC3545)

### Typography
- **Headers**: Bold, clean sans-serif
- **Body**: Readable sans-serif (16px base)
- **Code/Technical**: Monospace font
- **Emphasis**: Semi-bold for tool names and metrics

### Icons and Emojis
- 🏒 Hockey stick for branding
- 🤖 Robot for AI responses
- 👤 Person for user messages
- 🔧 Wrench for tool usage
- ⚡ Lightning for performance metrics
- 🔍 Magnifying glass for search/trace links
- 📋 Clipboard for structured content

### Responsive Breakpoints
- **Desktop**: 1200px+ (full feature set)
- **Tablet**: 768px-1199px (condensed layout)
- **Mobile**: <768px (stacked layout, simplified UI)

### Animation/Transitions
- **Loading**: Smooth progress bars with pulsing
- **Tool calls**: Staggered reveal of tool information
- **Responses**: Typewriter effect for AI responses
- **Errors**: Gentle shake animation for attention

## Component Implementation Targets

### 1. ChatMessage Component
```typescript
interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  toolUsage?: ToolUsageInfo;
  processingTime?: number;
  traceUrl?: string;
  timestamp: Date;
}
```

### 2. ToolUsageDisplay Component
```typescript
interface ToolUsageDisplayProps {
  tools: ToolCall[];
  totalTime: number;
  responseLength: number;
  traceUrl: string;
}
```

### 3. LoadingIndicator Component
```typescript
interface LoadingIndicatorProps {
  stage: 'searching' | 'processing' | 'generating';
  progress: number;
  elapsedTime: number;
}
```

### 4. ErrorDisplay Component
```typescript
interface ErrorDisplayProps {
  type: 'mcp_timeout' | 'api_error' | 'network_error';
  message: string;
  technicalDetails?: string;
  retryAvailable: boolean;
  onRetry?: () => void;
}
```

## Validation Checklist

When implementing against these mocks:

- [ ] **Visual Hierarchy**: Clear distinction between user/AI messages
- [ ] **Tool Transparency**: Prominent display of tool usage
- [ ] **Performance Feedback**: Processing time and trace links visible
- [ ] **Error Handling**: Graceful degradation with helpful messaging
- [ ] **Responsive Design**: All breakpoints working correctly
- [ ] **Accessibility**: Proper contrast, screen reader support
- [ ] **Hockey Context**: Theme appropriate for coaching audience
- [ ] **Professional Feel**: Suitable for coaches and hockey organizations

Use these mock targets as the benchmark for visual validation during development and testing phases.