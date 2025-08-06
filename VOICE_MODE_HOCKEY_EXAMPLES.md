# Voice Mode Hockey Coaching Examples

This document provides example voice commands and workflows for hockey coaches using the Voice Mode integration with Thunder Playbook.

## Quick Start Examples

### Starting a Voice Session
```
Coach: /start-voice-mode
Assistant: "Welcome to voice coaching mode! I'm here to help with your hockey coaching needs. What would you like to work on today?"

Coach: [VOICE] "I need help planning tomorrow's practice"
Assistant: [VOICE] "I'd be happy to help plan your practice. What age group are you coaching and how long is the practice?"
```

### Common Voice Commands

#### Drill Search
```
Coach: [VOICE] "Find me some passing drills for beginners"
Assistant: [VOICE] "I found several beginner passing drills. The Partner Passing drill is great for basics - players pair up 10 feet apart and work on accurate passes. Would you like more details?"

Coach: [VOICE] "Yes, and something with movement"
Assistant: [VOICE] "The Moving Partner Pass has players skating slowly while passing. Start stationary, then add forward skating, keeping passes flat on the ice. Want me to find a video demonstration?"
```

#### Skill Progressions
```
Coach: [VOICE] "What's a good progression for teaching backwards skating?"
Assistant: [VOICE] "For backwards skating, start with: 1) Stationary backwards C-cuts against the boards, 2) Backwards gliding between blue lines, 3) Add backward crossovers in the corners, 4) Finally, backwards pivots and transitions. Each step builds confidence before adding complexity."
```

#### Quick Rule Clarifications
```
Coach: [VOICE] "Explain icing for U10 players"
Assistant: [VOICE] "In U10, icing happens when a player shoots the puck from their side of center ice past the other team's goal line without anyone touching it. The key difference for U10 is that many leagues use 'no-touch' icing for safety - play stops as soon as the puck crosses the goal line."
```

## Age-Specific Examples

### U8 Voice Commands
```
Coach: [VOICE] "I need fun skating games for 6 year olds"
Assistant: [VOICE] "Great choices for U8: Red Light Green Light on skates, Sharks and Minnows, and Freeze Tag. These games build skating skills while keeping it fun. The kids won't even realize they're practicing!"

Coach: [VOICE] "Tell me more about Sharks and Minnows"
Assistant: [VOICE] "One player is the 'shark' in center ice. Other players try to skate from one end to the other without being tagged. Tagged players become sharks too. Last minnow swimming wins! Great for agility and fun."
```

### U10 Voice Commands
```
Coach: [VOICE] "Good small area games for U10?"
Assistant: [VOICE] "Try 3-on-3 cross-ice games, Keep Away in the circle, and 2-on-1 continuous. These develop quick decisions and puck skills in tight spaces. Cross-ice especially helps since U10 players see similar space in games."
```

### U12+ Voice Commands
```
Coach: [VOICE] "Explain a 2-1-2 forecheck system"
Assistant: [VOICE] "In a 2-1-2 forecheck, two forwards pressure deep - F1 on the puck carrier, F2 takes away the strong side. F3 stays high in the slot. Defensemen hold the blue line. It's aggressive but requires good conditioning. Want tactics for beating it too?"
```

## Practice Planning Voice Workflow

### Complete Practice Plan Creation
```
Coach: [VOICE] "Help me plan a practice"
Assistant: [VOICE] "I'll help you create a practice plan. What's your team's age group?"

Coach: [VOICE] "U12"
Assistant: [VOICE] "Got it, U12 team. How long is your practice?"

Coach: [VOICE] "One hour"
Assistant: [VOICE] "Perfect. What skills would you like to focus on?"

Coach: [VOICE] "Passing and defensive zone coverage"
Assistant: [VOICE] "Excellent focus areas. Would you like me to create a structured plan with warm-up, skill stations, and scrimmage?"

Coach: [VOICE] "Yes please"
Assistant: [VOICE] "I'll create a 60-minute U12 practice with passing and defensive zone coverage. The plan will include diagrams and can be saved to your Notion workspace. Should I proceed?"

Coach: [VOICE] "Go ahead"
Assistant: [Creates practice plan with drills, timing, and diagrams]
```

## Situational Coaching Examples

### During Practice
```
Coach: [VOICE] "My passing drill isn't working, kids are bored"
Assistant: [VOICE] "Try adding competition - make it a passing race between groups, or add obstacles to pass around. You could also try the 'Pass and Move' game where they must skate to a new spot after each pass. Movement usually increases engagement."
```

### Pre-Game Preparation
```
Coach: [VOICE] "Quick warmup for game in 10 minutes"
Assistant: [VOICE] "For a 10-minute game warmup: 2 minutes of dynamic skating, 3 minutes of passing in pairs, 3 minutes of shot progression from blue line to slot, 2 minutes of goalie shots. Keep intensity building throughout."
```

### Post-Practice Reflection
```
Coach: [VOICE] "How do I track what drills we've done?"
Assistant: [VOICE] "I can help you log today's practice in Notion. What drills did you run? I'll create a practice summary with effectiveness notes you can reference for planning future practices."
```

## Technical Voice Commands

### System Control
```
Coach: [VOICE] "Switch to private mode"
Assistant: "Switching to local processing for privacy. Your conversations will now use Whisper and Kokoro running on your device."

Coach: [VOICE] "Stop listening"
Assistant: "Ending voice session. Use /start-voice-mode to resume anytime."
```

### Configuration
```
Coach: [VOICE] "Change to male voice"
Assistant: "I'll help you change the voice. Use the command: /configure-voice voice am_adam"

Coach: /configure-voice voice am_adam
Assistant: "Voice updated to am_adam (natural male voice)"
```

## Tips for Effective Voice Coaching

### Best Practices
1. **Speak clearly** - Hockey rink acoustics can be challenging
2. **Use specific terms** - "U10 passing" instead of just "drills"
3. **Break complex requests** - Ask step by step for detailed plans
4. **Confirm understanding** - Assistant will verify before creating content

### Voice Command Shortcuts
- "More details" - Expands on current topic
- "Next drill" - Moves to alternative options
- "Save that" - Stores information to Notion
- "Start over" - Resets current query

### Hands-Free Scenarios
- **On-ice demonstrations** - Get drill explanations while showing players
- **Equipment room** - Search for drills while organizing gear
- **Driving to rink** - Plan practice during commute
- **Between drills** - Quick rule clarifications or progressions

## Advanced Workflows

### Multi-Step Planning
```
Coach: [VOICE] "I need a month of practice plans"
Assistant: [VOICE] "I can help create a monthly plan. Let's start with your team's current focus areas and I'll build a progressive 4-week program. What's the main skill development goal for this month?"
```

### Integration with Notion
```
Coach: [VOICE] "Save this drill to my U10 collection"
Assistant: [VOICE] "I'll save this drill to your U10 Notion collection. Would you like me to include the diagram and coaching points?"

Coach: [VOICE] "Yes, include everything"
Assistant: "Drill saved to Notion with diagram and full instructions. You can access it anytime through your team workspace."
```

## Troubleshooting Common Issues

### Voice Not Recognized
```
Coach: [VOICE] "[Unclear speech]"
Assistant: [VOICE] "I didn't catch that. Could you repeat your question?"

Coach: [VOICE] "[Speaks clearly] "Defensive zone faceoff play"
Assistant: [VOICE] "For defensive zone faceoffs, position your wingers on the boards, center ties up, and defensemen ready to retrieve. Want specific plays for won or lost draws?"
```

### Background Noise
```
If in noisy rink:
- Move to quieter area (lobby, office)
- Use /configure-voice provider local for better processing
- Consider headset with microphone
```

## Quick Reference Card

```
🎤 VOICE MODE QUICK COMMANDS

Start/Stop:
- /start-voice-mode          - Begin voice session
- "Stop listening"           - End voice mode

Common Requests:
- "Find [age] [skill] drills"
- "Explain [concept/rule]"
- "Create practice plan"
- "What's a progression for [skill]"

Navigation:
- "More details"
- "Next option"
- "Save this"
- "Start over"

Settings:
- /configure-voice          - Change settings
- "Switch to private mode"  - Use local processing
```

This guide provides comprehensive examples for coaches to effectively use voice mode in various hockey coaching scenarios.