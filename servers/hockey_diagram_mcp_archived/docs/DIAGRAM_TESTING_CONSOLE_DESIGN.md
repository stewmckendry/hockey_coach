# Hockey Diagram Testing Console - MVP Design

## Overview
A web-based testing console for the hockey diagram MCP server that allows interactive testing, visualization, and feedback collection.

## Architecture
Following the existing Hockey IQ chatbot pattern:
- Next.js web app with dedicated routes
- Server-side API for diagram generation
- File-based logging system for feedback
- Real-time monitoring dashboard

## Key Components

### 1. Frontend Interface (`/hockey-diagram-test`)
- **Input Section**:
  - Text input for diagram prompt (e.g., "2-1-2 forecheck")
  - Generate button
  - Preset examples dropdown

- **Output Section**:
  - Generated diagram image display
  - Processing time indicator
  - Tool chain visualization (e.g., parse_hockey_formation → generate_diagram_from_spec)
  - Collapsible sections for:
    - Parser-generated spec (JSON)
    - Agent traces and steps
    - Raw tool input/output

- **Feedback Section**:
  - Star rating (1-5)
  - Text area for detailed feedback
  - Category checkboxes: Accuracy, Positioning, Clarity, Performance
  - Submit feedback button

### 2. API Routes

#### `/api/hockey-diagram/generate`
- Accepts POST with prompt
- Calls HockeyDiagramExpert agent
- Returns:
  - Base64 image data
  - Processing metadata
  - Tool call traces
  - Parser specification

#### `/api/hockey-diagram/feedback`
- Accepts POST with feedback data
- Logs to file-based system
- Returns confirmation

#### `/api/hockey-diagram/monitor`
- GET endpoints for:
  - Recent generations
  - Feedback entries
  - Statistics
  - Search functionality

### 3. Logger System (`HockeyDiagramLogger`)
Similar to HockeyIQLogger but tracks:
- Generation requests
- Processing times
- Tool usage
- Parser output
- User feedback
- Error rates

### 4. Monitor Dashboard (`/hockey-diagram-test/monitor`)
- Recent generations gallery
- Feedback review interface
- Performance metrics
- Error tracking
- Export functionality

## Data Models

### DiagramGenerationLog
```typescript
interface DiagramGenerationLog {
  id: string;
  timestamp: string;
  prompt: string;
  imageUrl: string;
  
  // Processing details
  processingTimeMs: number;
  toolsUsed: string[];
  parserSpec: any;
  agentTraces: any[];
  
  // Results
  success: boolean;
  error?: string;
  
  // Feedback
  feedback?: {
    rating: number;
    categories: string[];
    comment: string;
    timestamp: string;
  };
}
```

## Implementation Plan

### Phase 1: Core Testing Interface
1. Create basic UI for prompt input and image display
2. Implement generation API route
3. Display generated images with basic metadata

### Phase 2: Detailed Traces
1. Add collapsible sections for spec and traces
2. Enhance tool chain visualization
3. Add processing time breakdown

### Phase 3: Feedback System
1. Implement feedback UI components
2. Create logging system
3. Add feedback API route

### Phase 4: Monitoring Dashboard
1. Create monitor page
2. Implement search and filtering
3. Add export functionality

## File Structure
```
web_app/
├── app/
│   ├── hockey-diagram-test/
│   │   ├── page.tsx              # Main testing interface
│   │   ├── layout.tsx            # Layout with navigation
│   │   └── monitor/
│   │       └── page.tsx          # Monitoring dashboard
│   └── api/
│       └── hockey-diagram/
│           ├── generate/route.ts  # Generation endpoint
│           ├── feedback/route.ts  # Feedback endpoint
│           └── monitor/route.ts   # Monitoring endpoints
├── components/
│   └── hockey-diagram-test/
│       ├── DiagramTester.tsx     # Main testing component
│       ├── FeedbackForm.tsx      # Feedback interface
│       └── TraceViewer.tsx       # Trace visualization
└── lib/
    └── server/
        └── hockeyDiagramLogger.ts # Logging system
```

## MVP Scope (2-3 hours)
For initial MVP, focus on:
1. Basic testing interface with prompt input
2. Image display with tool chain info
3. Simple feedback form
4. File-based logging
5. Basic monitor page showing recent tests

This can be expanded later with more advanced features like:
- Real-time updates
- Batch testing
- Comparison views
- Analytics dashboard
- Export to training data