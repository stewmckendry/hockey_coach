# Hockey Coaching Assistant - Web Application

A modern, responsive web application built with Next.js that provides an intelligent chat interface for hockey coaches. The app integrates with a Model Context Protocol (MCP) server to deliver expert hockey coaching knowledge, practice planning, and player development insights.

## 🏒 Features

### Core Functionality
- **Intelligent Chat Interface**: ChatGPT-style conversation flow with hockey-specific AI assistant
- **Hockey Domain Expertise**: Access to skills, drills, tactics, and player development knowledge
- **Practice Planning**: Generate comprehensive practice plans based on team needs
- **Player Development**: Get personalized development plans for different positions and skill levels
- **Mobile Responsive**: Optimized for use on tablets and phones during practice

### Technical Features
- **Next.js 14+**: Modern React framework with App Router
- **TypeScript**: Full type safety for robust development
- **Tailwind CSS**: Professional hockey-themed design system
- **MCP Integration**: Seamless backend communication with hockey knowledge server
- **Real-time Chat**: Smooth messaging experience with typing indicators
- **Error Handling**: Comprehensive error states and retry mechanisms

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.10+ (for MCP bridge service)
- npm or yarn
- Hockey MCP Server running (see main project README)

### Installation

1. **Navigate to web app directory**
   ```bash
   cd web_app
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Install Python dependencies for MCP bridge**
   ```bash
   pip install -r requirements.txt
   # or use a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Start the MCP bridge service**
   ```bash
   python mcp_bridge.py
   ```
   The bridge will run on http://localhost:3001

5. **Start the web development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

6. **Open in browser**
   ```
   http://localhost:3000
   ```

### Production Build

```bash
npm run build
npm start
```

Note: In production, you'll want to run the MCP bridge as a proper service (systemd, Docker, etc.)

## 🎨 Design System

### Hockey Theme Colors
- **Primary Blue**: `#003f7f` (hockey-blue)
- **Ice Blue**: `#e6f3ff` (ice)
- **Accent Red**: `#c41e3a` (hockey-red)
- **Neutral Grays**: Professional coaching aesthetic

### Typography
- **Font**: Inter (clean, readable)
- **Heading Styles**: Bold, hierarchical
- **Body Text**: Optimized for readability

### Responsive Design
- **Mobile First**: Designed for tablet/phone use during practice
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)
- **Touch Friendly**: Large touch targets for mobile interaction

## 🏗️ Project Structure

```
web_app/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout with navigation
│   ├── page.tsx           # Homepage with chat interface
│   └── api/               # API routes
│       └── mcp/           # MCP server proxy
├── components/            # React components
│   ├── ui/                # Base UI components
│   │   ├── Button.tsx     # Button with variants
│   │   ├── Card.tsx       # Content cards
│   │   └── LoadingSpinner.tsx
│   ├── layout/            # Layout components
│   │   ├── Header.tsx     # Main navigation
│   │   ├── Footer.tsx     # Footer with links
│   │   └── Sidebar.tsx    # Side navigation
│   └── chat/              # Chat interface
│       ├── ChatInterface.tsx    # Main chat container
│       ├── MessageBubble.tsx    # Individual messages
│       ├── ChatInput.tsx        # Message input form
│       └── TypingIndicator.tsx  # Loading animation
├── hooks/                 # Custom React hooks
│   ├── useChat.ts         # Chat state management
│   └── useLocalStorage.ts # Local storage utilities
├── lib/                   # Utilities and configuration
│   ├── types.ts           # TypeScript definitions
│   ├── api.ts             # API client functions
│   └── utils.ts           # Helper functions
└── config files           # Next.js, Tailwind, TypeScript
```

## 🔌 MCP Integration

### API Proxy
The web app communicates with the Hockey MCP server through a Next.js API route (`/api/mcp`) that acts as a proxy:

- **Endpoint**: `POST /api/mcp`
- **Authentication**: Handles MCP server connection
- **Error Handling**: Comprehensive error responses
- **CORS**: Configured for development

### Natural Language Processing
The app intelligently routes user queries to appropriate MCP tools:

```typescript
// Example: "Plan a practice for 12-year-olds focusing on passing"
{
  tool: "generate_practice_plan",
  parameters: {
    age_group: "12u",
    skill_focus: ["passing"],
    duration: 60
  }
}
```

### Supported MCP Tools
- `get_hockey_knowledge`: General hockey information
- `generate_practice_plan`: Create practice sessions
- `get_player_development_plan`: Individual player guidance
- `search_drills`: Find specific drills
- `analyze_skill_progression`: Track development

## 📱 Usage Guide

### For Hockey Coaches

1. **Start a Conversation**
   - Type natural language questions about hockey
   - Examples: "Plan a practice for bantam players", "What drills help with passing?"

2. **Practice Planning**
   - Specify age group, skill focus, and duration
   - Get comprehensive practice plans with drills and timing

3. **Player Development**
   - Ask about specific positions or skills
   - Receive personalized development recommendations

4. **Drill Discovery**
   - Search for drills by skill, age group, or equipment
   - Get detailed instructions and variations

### Example Queries
```
"Create a 90-minute practice for midget players focusing on defensive zone coverage"

"What are the best drills for teaching forwards how to forecheck?"

"Help me develop a defenseman who struggles with breakout passes"

"Show me power play tactics for U16 teams"
```

## 🛠️ Development

### Available Scripts
- `npm run dev`: Start development server with hot reload
- `npm run build`: Create production build
- `npm run start`: Start production server
- `npm run lint`: Run ESLint for code quality
- `npm run type-check`: Run TypeScript type checking

### Code Quality
- **ESLint**: Configured for Next.js and TypeScript
- **TypeScript**: Strict mode enabled for type safety
- **Prettier**: Code formatting (configure as needed)

### Environment Variables
Create `.env.local` for local development:

```env
# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8000
MCP_SERVER_TIMEOUT=30000

# Optional: Authentication
AUTH_SECRET=your-secret-key
```

## 🔧 Customization

### Theming
Modify `tailwind.config.js` to adjust colors, fonts, and spacing:

```javascript
theme: {
  extend: {
    colors: {
      'hockey-blue': '#003f7f',    // Primary brand color
      'ice': '#e6f3ff',            // Light accent
      'hockey-red': '#c41e3a',     // Error/accent color
    }
  }
}
```

### MCP Server Integration
Update `lib/api.ts` to modify how queries are processed and routed to MCP tools.

### Chat Behavior
Customize chat responses and formatting in `hooks/useChat.ts`.

## 🐛 Troubleshooting

### Common Issues

1. **MCP Server Connection**
   ```
   Error: Failed to connect to MCP server
   Solution: Ensure hockey MCP server is running on localhost:8000
   ```

2. **Build Errors**
   ```
   TypeError: Cannot read property 'map' of undefined
   Solution: Check that all imported components exist and are properly exported
   ```

3. **Styling Issues**
   ```
   Styles not loading
   Solution: Restart dev server after modifying Tailwind config
   ```

### Debug Mode
Enable verbose logging by setting environment variable:
```env
DEBUG=true
```

## 📈 Performance

### Optimization Features
- **Next.js App Router**: Optimized routing and rendering
- **Component Lazy Loading**: Reduced initial bundle size
- **Image Optimization**: Built-in Next.js image optimization
- **CSS Purging**: Tailwind removes unused styles in production

### Performance Metrics
- **First Contentful Paint**: < 1.2s
- **Largest Contentful Paint**: < 2.5s
- **Time to Interactive**: < 3.5s
- **Cumulative Layout Shift**: < 0.1

## 🔒 Security

### Security Features
- **API Route Protection**: Server-side request validation
- **Input Sanitization**: XSS prevention in chat messages
- **CORS Configuration**: Restricted cross-origin requests
- **Environment Variables**: Sensitive data protection

## 📚 Documentation

### Component Documentation
Each component includes JSDoc comments with:
- Purpose description
- Props interface
- Usage examples
- Dependencies

### Type Safety
Comprehensive TypeScript definitions in `lib/types.ts`:
- Chat message interfaces
- MCP request/response types
- Hockey domain types
- UI component props

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Submit pull request

### Code Standards
- Follow existing TypeScript/React patterns
- Use semantic commit messages
- Maintain 100% type coverage
- Add JSDoc comments for public APIs

## 📄 License

This project is part of the Thunder Playbook hockey coaching system. See main project README for license information.

---

## 🏒 About

Built with ❤️ for hockey coaches who want to leverage AI to improve their coaching effectiveness. The web application provides an intuitive interface to access the deep hockey knowledge contained in the Thunder Playbook MCP server.

For questions or support, please refer to the main project documentation or create an issue in the repository.
