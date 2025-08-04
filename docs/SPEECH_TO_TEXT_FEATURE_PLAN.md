# Speech-to-Text Integration Feature Plan

## Overview
This document outlines the implementation plan for integrating speech-to-text capabilities into the Thunder Playbook project via MCP (Model Context Protocol) servers, enabling voice input for Claude Code interactions.

## Problem Statement
Currently, all interactions with Claude Code require manual typing, which can be inefficient for:
- Long practice plan descriptions during on-ice sessions
- Voice-driven coaching queries while reviewing game footage
- Hands-free workflow during equipment setup or field work
- Accessibility needs for extended typing sessions

## Solution: Voice Mode MCP Server Integration

### Primary Recommendation: Voice Mode MCP Server
**Repository**: `mbailey/voicemode`
**Key Benefits**:
- Complete conversational voice interface (STT + TTS)
- Real-time speech recognition with automatic silence detection
- Supports both cloud (OpenAI) and local (Whisper.cpp) processing
- Seamless integration with Claude Code via MCP protocol
- Active development with good documentation

## Implementation Phases

### Phase 1: Basic Installation & Setup (15 minutes)
**Objective**: Get basic voice input working with Claude Code

**Steps**:
1. Install Voice Mode MCP Server:
   ```bash
   export OPENAI_API_KEY=your-openai-key  
   claude mcp add voice-mode uvx voice-mode
   ```

2. Update Claude Code configuration in `~/.claude.json`:
   ```json
   {
     "mcpServers": {
       "voice-mode": {
         "command": "uvx",
         "args": ["voice-mode"],
         "env": {
           "OPENAI_API_KEY": "your-openai-key"
         }
       }
     }
   }
   ```

3. Test basic functionality:
   - Start Claude Code: `claude`
   - Test voice conversation: `/converse` or "Let's have a voice conversation"
   - Verify microphone access and speech recognition

**Success Criteria**:
- Voice input successfully converts to text in Claude Code prompt
- Basic voice commands trigger appropriate responses
- Microphone permissions properly configured

### Phase 2: Local Processing Setup (Optional - 45 minutes)
**Objective**: Enable offline, privacy-focused speech processing

**Steps**:
1. Install local dependencies:
   ```bash
   # Install whisper.cpp for local STT
   brew install whisper-cpp
   
   # Download Whisper model
   mkdir -p ~/whisper-models
   cd ~/whisper-models
   curl -L -O https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
   ```

2. Install Kokoro TTS for local text-to-speech:
   ```bash
   # Clone and setup Kokoro-FastAPI
   git clone https://github.com/remsky/Kokoro-FastAPI.git
   cd Kokoro-FastAPI
   # Follow setup instructions in repository
   ```

3. Configure Voice Mode for local processing:
   ```bash
   export WHISPER_CPP_PATH=/opt/homebrew/bin/whisper-cpp
   export KOKORO_TTS_URL=http://localhost:8000
   export USE_LOCAL_STT=true
   export USE_LOCAL_TTS=true
   ```

**Success Criteria**:
- Voice processing works offline without OpenAI API calls
- Latency remains acceptable (<2 seconds response time)
- Audio quality meets coaching workflow needs

### Phase 3: Hockey Coaching Integration (30 minutes)
**Objective**: Optimize voice commands for hockey coaching workflows

**Steps**:
1. Update project `CLAUDE.md` with voice configuration:
   - Document Voice Mode MCP server setup
   - Add to existing MCP server list
   - Include troubleshooting section

2. Create hockey-specific voice command examples:
   ```markdown
   ## Voice Command Examples for Hockey Coaching
   
   ### Practice Planning
   - "Create a 60-minute U10 practice focusing on passing and skating"
   - "Plan a fun practice for U8s with lots of small games"
   - "Design a power play practice for U14 players"
   
   ### Diagram Generation
   - "Generate a 2-1-2 forecheck diagram with player movements"
   - "Create a power play umbrella formation diagram"
   - "Show defensive zone coverage for 3-on-3"
   
   ### Research Queries
   - "Find skating drills for beginner players"
   - "Search for passing drills under pressure"
   - "What are good small area games for U12?"
   ```

3. Test hockey-specific workflows:
   - Voice-driven practice plan creation
   - Voice commands for diagram generation via Hockey Diagram MCP
   - Voice queries to hockey knowledge database

**Success Criteria**:
- Voice commands successfully trigger hockey coaching tools
- Practice plans can be created entirely through voice input
- Diagram generation responds to natural language voice descriptions

## Technical Architecture

### Component Integration
```
User Voice Input → Voice Mode MCP → Claude Code → Hockey Coaching Tools
                                              ↓
                                   Thunder Playbook MCP Server
                                              ↓
                                        ChromaDB Search
```

### MCP Server Configuration
The Voice Mode MCP server will be added to the existing MCP server ecosystem:
- **Existing**: hockey-coaching, notion, exa, semgrep, ref-tools, playwright
- **New**: voice-mode (speech-to-text and text-to-speech)

### Data Flow
1. User speaks into microphone
2. Voice Mode MCP captures and processes audio
3. Speech converted to text via Whisper (local) or OpenAI (cloud)
4. Text appears in Claude Code prompt box
5. User can edit or submit directly
6. Claude processes request using existing hockey coaching tools
7. Response can be spoken back via TTS if desired

## Alternative Solutions Considered

### 1. Local Speech-to-Text MCP Server
**Repository**: `SmartLittleApps/local-stt-mcp`
- **Pros**: 100% local processing, optimized for Apple Silicon
- **Cons**: File-based rather than real-time, more complex setup
- **Use Case**: Better for batch processing of recorded audio files

### 2. ElevenLabs MCP Server
**Repository**: `elevenlabs/elevenlabs-mcp`
- **Pros**: Professional-grade quality, voice cloning capabilities
- **Cons**: Expensive subscription, overkill for prompt input
- **Use Case**: Better for content creation and voice agent development

## Success Metrics

### Functional Requirements
- [ ] Voice input successfully converts to text in Claude Code
- [ ] Speech recognition accuracy >90% for hockey terminology
- [ ] Response latency <3 seconds end-to-end
- [ ] Works offline (local processing option)
- [ ] Integrates seamlessly with existing hockey coaching workflows

### User Experience Requirements
- [ ] Natural voice commands feel intuitive
- [ ] Microphone activation/deactivation is clear
- [ ] Error handling provides helpful feedback
- [ ] Voice commands work during active coaching sessions
- [ ] Multiple users can use system without reconfiguration

### Technical Requirements
- [ ] MCP server starts reliably with other services
- [ ] No conflicts with existing MCP servers
- [ ] Minimal performance impact on Claude Code
- [ ] Proper error logging and debugging capabilities
- [ ] Security: no unintended audio recording or transmission

## Risk Assessment & Mitigation

### Technical Risks
1. **Audio Quality Issues**
   - Risk: Poor microphone or noisy environment affects recognition
   - Mitigation: Support multiple audio input devices, noise filtering

2. **Latency Problems**
   - Risk: Slow speech processing disrupts workflow
   - Mitigation: Local processing option, model optimization

3. **Integration Conflicts**
   - Risk: Voice Mode MCP interferes with existing MCP servers
   - Mitigation: Isolated configuration, thorough testing

### Privacy Risks
1. **Unintended Recording**
   - Risk: Audio captured when not intended
   - Mitigation: Clear activation indicators, local processing option

2. **Cloud Processing**
   - Risk: Sensitive coaching discussions sent to OpenAI
   - Mitigation: Local processing mode, user education

## Implementation Timeline

### Week 1: Basic Setup
- Install and configure Voice Mode MCP server
- Test basic functionality with existing Claude Code setup
- Document configuration in project CLAUDE.md

### Week 2: Hockey Integration
- Test voice commands with hockey coaching workflows
- Create examples and documentation for hockey-specific voice commands
- Optimize for common coaching scenarios

### Week 3: Local Processing (Optional)
- Set up local Whisper.cpp and TTS processing
- Test offline functionality and performance
- Document local setup procedures

### Week 4: Testing & Refinement
- User acceptance testing with actual coaching scenarios
- Performance optimization and bug fixes
- Final documentation and training materials

## Future Enhancements

### Phase 4: Advanced Features (Future)
- **Custom Wake Words**: "Hey Coach" activation
- **Voice Shortcuts**: Predefined commands for common tasks
- **Multi-language Support**: French coaching terms for Canadian hockey
- **Voice-driven Navigation**: Navigate through practice plans by voice
- **Integration with Video Analysis**: Voice annotations during game review

### Phase 5: Team Collaboration (Future)
- **Multi-user Voice Sessions**: Multiple coaches in voice conversation
- **Voice Meeting Notes**: Automatic transcription of coaching meetings
- **Voice-driven Team Communication**: Integration with team communication tools

## Resources & References

### Primary Implementation
- [Voice Mode GitHub Repository](https://github.com/mbailey/voicemode)
- [Voice Mode Documentation](https://getvoicemode.com/)
- [MCP Protocol Documentation](https://modelcontextprotocol.com/)

### Alternative Solutions
- [Local STT MCP Server](https://github.com/SmartLittleApps/local-stt-mcp)
- [ElevenLabs MCP Server](https://github.com/elevenlabs/elevenlabs-mcp)

### Technical Dependencies
- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) - Local speech recognition
- [OpenAI Whisper](https://github.com/openai/whisper) - Original Whisper implementation
- [Kokoro TTS](https://github.com/remsky/Kokoro-FastAPI) - Local text-to-speech

---

**Document Version**: 1.0
**Last Updated**: 2025-01-04
**Author**: Claude Code Assistant
**Status**: Ready for Implementation