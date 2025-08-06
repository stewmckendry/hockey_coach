---
description: "Configure voice mode settings including providers, voices, and audio preferences"
argument-hint: "[setting] [value]"
---

# Configure Voice Command

Manages Voice Mode configuration settings for optimal hockey coaching experience.

## Command Usage

```bash
# Show current configuration
/configure-voice

# Change specific setting
/configure-voice provider local
/configure-voice voice af_sky
/configure-voice feedback on

# Test configuration
/configure-voice test
```

## Available Settings

### Provider Settings
```bash
# Switch between local and cloud processing
/configure-voice provider local    # Use Whisper + Kokoro
/configure-voice provider cloud    # Use OpenAI API
/configure-voice provider auto     # Auto-select best available
```

### Voice Selection
```bash
# Set TTS voice
/configure-voice voice af_sky      # Kokoro natural female
/configure-voice voice am_adam     # Kokoro natural male
/configure-voice voice nova        # OpenAI voice
/configure-voice voice list        # Show all available voices
```

### Audio Preferences
```bash
# Audio feedback settings
/configure-voice feedback on       # Enable feedback sounds
/configure-voice feedback off      # Disable feedback sounds
/configure-voice save-audio on     # Save recordings for review
/configure-voice save-audio off    # Don't save recordings
```

### Language Settings
```bash
# Configure language for non-English coaching
/configure-voice language en       # English (default)
/configure-voice language fr       # French
/configure-voice language es       # Spanish
```

## Workflow Implementation

### Phase 1: Parse Command Arguments
1. **No arguments - Show Current Config:**
   ```
   mcp__voice-mode__voice_status
   mcp__voice-mode__list_config_keys (if detailed view needed)
   ```

2. **With arguments - Parse Setting:**
   - Setting name (provider, voice, feedback, etc.)
   - New value

### Phase 2: Execute Configuration Change

#### Provider Change
```python
if setting == "provider":
    if value == "local":
        mcp__voice-mode__update_config("VOICEMODE_PREFER_LOCAL", "true")
        mcp__voice-mode__update_config("VOICEMODE_ALWAYS_TRY_LOCAL", "true")
    elif value == "cloud":
        mcp__voice-mode__update_config("VOICEMODE_PREFER_LOCAL", "false")
        mcp__voice-mode__update_config("VOICEMODE_ALWAYS_TRY_LOCAL", "false")
```

#### Voice Change
```python
if setting == "voice":
    if value == "list":
        # List all available voices
        mcp__voice-mode__list_tts_voices()
    else:
        # Update preferred voice
        current_voices = get_config("VOICEMODE_TTS_VOICES")
        new_voices = f"{value},{current_voices}" if current_voices else value
        mcp__voice-mode__update_config("VOICEMODE_TTS_VOICES", new_voices)
```

#### Audio Settings
```python
if setting == "feedback":
    mcp__voice-mode__update_config("VOICEMODE_AUDIO_FEEDBACK", value)
elif setting == "save-audio":
    mcp__voice-mode__update_config("VOICEMODE_SAVE_AUDIO", value)
```

### Phase 3: Test Configuration

When `/configure-voice test` is called:

1. **Test Audio Devices:**
   ```
   mcp__voice-mode__check_audio_devices()
   ```

2. **Test Voice Synthesis:**
   ```
   mcp__voice-mode__converse(
       message="Testing voice configuration. This is how I'll sound during coaching sessions.",
       wait_for_response=false,
       tts_provider=current_provider,
       voice=current_voice
   )
   ```

3. **Test Speech Recognition:**
   ```
   mcp__voice-mode__converse(
       message="Now testing speech recognition. Please say any hockey term like 'forecheck' or 'power play'.",
       wait_for_response=true,
       listen_duration=10
   )
   ```

4. **Report Results:**
   ```
   ✅ Voice Configuration Test Results:
   - Audio Input: Working (device: MacBook Pro Microphone)
   - Audio Output: Working (device: MacBook Pro Speakers)
   - TTS Provider: Kokoro (local)
   - TTS Voice: af_sky
   - STT Provider: Whisper (local)
   - Recognition: "forecheck" detected correctly
   - Latency: 1.2s (excellent)
   ```

## Configuration Profiles

### Privacy-First Profile
```
Provider: local
Voice: af_sky (Kokoro)
Save Audio: off
Feedback: on
```

### Performance Profile
```
Provider: cloud
Voice: nova (OpenAI)
Save Audio: off
Feedback: on
```

### Development Profile
```
Provider: auto
Voice: af_sky
Save Audio: on
Feedback: on
Debug: on
```

## Interactive Examples

### Basic Configuration Check
```
Coach: /configure-voice
Assistant: 
Current Voice Mode Configuration:
- Provider: Local (Whisper + Kokoro)
- Voice: af_sky (natural female)
- Language: English
- Audio Feedback: Enabled
- Save Recordings: Disabled

Available commands:
- /configure-voice provider [local|cloud|auto]
- /configure-voice voice [voice-name|list]
- /configure-voice feedback [on|off]
- /configure-voice test
```

### Changing Voice
```
Coach: /configure-voice voice list
Assistant:
Available TTS Voices:

Kokoro (Local):
- af_sky, af_sarah (female, natural)
- am_adam, am_michael (male, natural)
- bf_emma, bf_isabella (female, expressive)
- bm_george, bm_lewis (male, expressive)
[... more voices ...]

OpenAI (Cloud):
- alloy, echo, fable, onyx, nova, shimmer

Current: af_sky
To change: /configure-voice voice [name]
```

### Testing New Configuration
```
Coach: /configure-voice voice am_adam
Assistant: Voice updated to am_adam (male, natural)

Coach: /configure-voice test
Assistant: [VOICE: am_adam] "Testing voice configuration. This is how I'll sound during coaching sessions."
[Waits for user to speak]
Coach: [VOICE] "Power play setup"
Assistant: Great! I heard "power play setup" clearly. Configuration test successful!
```

## Error Handling

### Service Not Running
```
If Whisper/Kokoro not running when local selected:
"Local voice services aren't running. Starting them now..."
mcp__voice-mode__service("whisper", "start")
mcp__voice-mode__service("kokoro", "start")
```

### Invalid Voice Name
```
"Voice 'xyz' not found. Use '/configure-voice voice list' to see available voices."
```

### Configuration Write Error
```
"Unable to update configuration. Please check permissions for ~/.voicemode/voicemode.env"
```

## Success Indicators
- Configuration updates applied immediately
- Test confirms all components working
- Voice changes audible in test
- Settings persist across sessions

## Quick Reference Card

```
🎙️ Voice Mode Configuration Quick Reference

PROVIDERS:
  local  - Private, offline processing
  cloud  - Fast, online processing
  auto   - Best available

POPULAR VOICES:
  af_sky     - Natural female (recommended)
  am_adam    - Natural male
  nova       - OpenAI female
  alloy      - OpenAI neutral

COMMANDS:
  /configure-voice              - Show config
  /configure-voice test         - Test setup
  /configure-voice voice list   - List voices
  /configure-voice provider local - Use offline

TROUBLESHOOTING:
  No audio? → /configure-voice test
  Wrong voice? → /configure-voice voice list
  Too slow? → /configure-voice provider cloud
```