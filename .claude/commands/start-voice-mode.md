---
description: "Start an interactive voice coaching session with configurable duration and focus areas"
argument-hint: "[duration-minutes] [focus-area]"
---

# Start Voice Mode Command

Initiates an interactive voice coaching session using the Voice Mode MCP server with speech-to-text and text-to-speech capabilities.

## Command Usage

```bash
# Basic usage - continuous session
/start-voice-mode

# With duration limit
/start-voice-mode 30

# With focus area
/start-voice-mode 30 "passing drills"
```

## Workflow Implementation

### Phase 1: Parse Arguments and Initialize
1. **Extract Parameters:**
   - Duration (optional, default: continuous)
   - Focus area (optional, for context)

2. **Check Voice Service Status:**
   ```
   mcp__voice-mode__voice_status
   ```
   Verify:
   - STT endpoints available (Whisper or OpenAI)
   - TTS endpoints available (Kokoro or OpenAI)
   - Audio devices configured

### Phase 2: Configure Session
1. **Set Voice Provider Based on Availability:**
   ```
   If Kokoro (local) available:
     tts_provider = "kokoro"
     voice = "af_sky"  # Natural female voice
   Else:
     tts_provider = "openai"
     voice = "nova"    # OpenAI voice
   ```

2. **Calculate Listen Duration:**
   ```
   If duration specified:
     listen_duration = min(duration * 60, 300)  # Max 5 minutes per interaction
   Else:
     listen_duration = 120  # 2 minutes default
   ```

### Phase 3: Start Voice Session
1. **Initial Greeting:**
   ```
   mcp__voice-mode__converse
   message: "Welcome to voice coaching mode! I'm here to help with your hockey coaching needs. What would you like to work on today?"
   wait_for_response: true
   listen_duration: [calculated]
   tts_provider: [selected]
   voice: [selected]
   ```

2. **Process User Response:**
   - Parse coaching intent from voice input
   - Identify hockey terminology and focus areas
   - Prepare contextual response

### Phase 4: Interactive Coaching Loop
Continue conversation based on user requests:

```
While session active:
  1. Listen for user input
  2. Process hockey coaching query
  3. Search relevant resources if needed:
     - mcp__hockey-coaching__search_hockey_drills
     - mcp__hockey-coaching__search_hockey_tactics
     - mcp__hockey-coaching__search_hockey_skills
  4. Formulate coaching response
  5. Speak response using TTS
  6. Wait for next input
```

### Phase 5: Session Management
**Voice Commands to Handle:**
- "Stop listening" or "End session" - Terminate voice mode
- "What can you help with?" - List capabilities
- "Change voice" - Switch TTS voice
- "Repeat that" - Repeat last response

**Example Interactions:**
```
User: "What are some good passing drills for U10?"
Response: Search drills → Format response → Speak results

User: "Show me a 2-1-2 forecheck setup"
Response: Search tactics → Explain system → Offer to create diagram

User: "Create a practice plan for tomorrow"
Response: Gather details → Suggest using /plan-practice command
```

## Response Formatting

**Keep Responses Concise for Voice:**
- Maximum 3-4 sentences per response
- Use clear, simple language
- Avoid technical jargon unless necessary
- Pause between key points

**Example Voice Response:**
```
"I found three excellent passing drills for U10 players. 
The Triangle Passing drill works on accuracy and movement. 
The Partner Gates drill adds fun competition. 
Would you like details on any of these?"
```

## Error Handling

### Voice Service Unavailable
```
If voice services not running:
  "Voice services are not available. Let me help you start them..."
  Provide instructions to run:
  - mcp__voice-mode__service("whisper", "start")
  - mcp__voice-mode__service("kokoro", "start")
```

### No Audio Input Detected
```
"I didn't catch that. Please speak clearly after the chime."
[Retry with increased listen_duration]
```

### Network Issues
```
If cloud services fail:
  "Switching to local voice processing for privacy..."
  [Use local Whisper + Kokoro]
```

## Success Metrics
- Response time < 3 seconds
- Speech recognition accuracy > 90%
- Natural conversation flow
- Hockey terminology correctly recognized

## Example Session

```
Coach: /start-voice-mode 15
Assistant: "Welcome to voice coaching mode! I'm here to help with your hockey coaching needs. What would you like to work on today?"

Coach: [VOICE] "I need help planning passing drills for my U10 team"
Assistant: [VOICE] "I'll help you find great passing drills for U10. Are you looking for stationary drills, moving drills, or game-like situations?"

Coach: [VOICE] "Something with movement and fun"
Assistant: [VOICE] "Perfect! I found the Moving Triangle Passing drill which combines skating and passing. Players form triangles and pass while skating. Would you like the full setup instructions?"

Coach: [VOICE] "Yes please"
Assistant: [Provides detailed drill explanation via voice]

Coach: [VOICE] "End session"
Assistant: [VOICE] "Thanks for using voice coaching mode. Good luck with your practice!"
```