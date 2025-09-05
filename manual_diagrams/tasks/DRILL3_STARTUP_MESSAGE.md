# Startup Message for Drill 3 - 3v2 Breakout & Breakin

Copy and paste this entire message into a new Claude Code chat:

---

I need to create Drill 3 - 3v2 Breakout & Breakin hockey diagram as part of GitHub issue #111. This is a continuation from Drill 1 and 2 which are complete.

## Context
- Working directory: `/Users/liammckendry/hockey_coach_issue-111/manual_diagrams/`
- Virtual env: Activate with `source ../../spacy_env/bin/activate`
- Existing code in `src/` folder with `hockey_diagram_builder.py` and `drill_utilities.py`
- Track iterations in Google Sheets: https://docs.google.com/spreadsheets/d/1_RdgMPxluftZfeFl1SXZKYycDVxAV-GrzzhESIOXt24/

## Drill 3 Description from Practice Plan
**3v2 Breakout & Breakin**
***PART 1 - BREAK OUT***
- Setup: 3 forwards on red line, 2 defensemen on blue line, 1 coach on other blue line, 1 goalie in net
- Coach dumps puck into the zone
- All players skate into zone. 
    - left defense skates to get puck, 
    - right defense goes in front of net, 
    - left wing goes to hashmarks to get pass
    - centre curls close to winger to support and get pass from left wing
    - right wing curls in middle of ice
- forwards move out of defensive zone into neutral zone. Forward with puck passes to coach, and gets pass back

***PART 2 - BREAK IN***
- After getting puck back from coach, the forwards skate back towards zone and go 3 on 2 against defense
- forward with puck goes wide
- centre drives to the net
- other forward stay high for a pass

***Photos of whiteboard drawings***
check out drill3_part1.jpeg and drill3_part2.jpeg under manual_diagrams/drawings folder

## Key Learnings from Previous Drills
1. **Z-order values**: Equipment at 11, players at 10, goalie at 12
2. **Pylons**: Use `Zone(type='cone', shape='polygon')` with triangle vertices
3. **Pucks**: Use `Player(type='puck')` for simple black dots
4. **Cross-ice**: Big Y-axis changes show cross-ice movement
5. **Coordinates**: Blue lines at x=±25, goal lines at x=±89, circles at (±69, ±22.5)

## Efficient Iteration Approach
1. Start with DESCRIBING the drill flow in natural language first
2. Map descriptions to coordinates using landmarks
3. Use proper z-order from the start
4. Create waypoints for paths around obstacles
5. Test equipment visibility first, then add movements

## First Task
1. Read the existing code files to understand the implementation
2. Create an initial Drill 3 diagrams based on the description - one for each part
3. Save outputs with timestamp to `outputs/` folder
4. Update Google Sheets with iteration 1 (get table columns and data first to align your update format)
5. Show me the result and await feedback

Remember: Focus on natural hockey flow. Players should move smoothly with realistic paths. Use the utilities for arc generation when needed.

The goal is to minimize iterations by applying all lessons learned. Good luck!