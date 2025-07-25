# Screenshots Directory

This directory contains visual validation screenshots for the Hockey Coach AI Assistant.

## Organization

### UI Components
- `desktop-chat-interface.png` - Main chat interface at 1920x1080
- `mobile-chat-interface.png` - Mobile responsive view at 375x667
- `agent-test-page.png` - Agent test page layout

### Functionality Screenshots
- `hockey-response-example.png` - Example of hockey coaching response
- `tool-usage-display.png` - UI showing tool usage information
- `loading-state.png` - Loading indicators during processing
- `error-state.png` - Error state display

### Before/After Comparisons
- `before-feature-X.png` / `after-feature-X.png` - Feature implementation comparisons
- `responsive-before.png` / `responsive-after.png` - Responsive design improvements

## Guidelines

### Screenshot Standards
- **Desktop**: 1920x1080 resolution
- **Mobile**: 375x667 resolution (iPhone SE)
- **Format**: PNG with descriptive filenames
- **Browser**: Chrome preferred for consistency

### Naming Convention
- Use kebab-case: `feature-name-state.png`
- Include device type: `desktop-`, `mobile-`
- Include state: `-loading`, `-error`, `-success`
- Date for comparisons: `-2025-01-25`

### Content Guidelines  
- Show realistic hockey coaching content
- Hide sensitive information (API keys, personal data)
- Include browser chrome for context when relevant
- Capture full page or focused component area

## Usage in Development

1. **Before Changes**: Capture baseline screenshots
2. **After Changes**: Capture updated screenshots  
3. **Compare**: Visual diff to verify improvements
4. **Document**: Reference in commit messages and PRs

## Integration with Testing

Screenshots should be captured during:
- `/web-validate` slash command execution
- UI component development
- Responsive design testing
- Error handling validation
- Performance optimization verification

## Tools

Recommended screenshot tools:
- **macOS**: Cmd+Shift+4 for selections, Cmd+Shift+3 for full screen
- **Browser DevTools**: Device mode for responsive testing
- **Automated**: Playwright/Puppeteer for CI integration (future)

Keep this directory organized and remove outdated screenshots during cleanup phases.