# Startup Message for Drill 4 - 3v3 Battle

Copy and paste this entire message into a new Claude Code chat:

---

I need to create Drill 4 - 3v3 Battle hockey diagram as part of GitHub issue #111. This is a continuation from Drill 1 and 2 which are complete.

## Context
- Working directory: `/Users/liammckendry/hockey_coach_issue-111/hockey_diagram_mcp/`
- Virtual env: Activate with `source ../../spacy_env/bin/activate`
- Existing code in `src/` folder with `hockey_diagram_builder.py` and `drill_utilities.py`
- Track iterations in Google Sheets: https://docs.google.com/spreadsheets/d/1_RdgMPxluftZfeFl1SXZKYycDVxAV-GrzzhESIOXt24/

## Drill 4 Description from Practice Plan
**3v3 Battle**
- 3v3 competitive battle in 1 zone
- 2 nets set up the zone; one in usual crease, the other closer to the blue line facing the same direction
- Coach dumps puck to start each shift
- Coaches positioned at middle of blue line, and at each hashmark (must pass to coach before scoring)
- Emphasis on compete level and positioning

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
2. Create initial Drill 4 diagram based on the description
3. Save outputs with timestamp to `outputs/` folder
4. Update Google Sheets with iteration 1
5. Show me the result and await feedback

Remember: This is a battle/competitive drill, so show:
- Multiple simultaneous movements
- Puck battles in key areas (corners, slot, neutral zone)
- Quick transition paths
- Coach position for puck dumps

The goal is to minimize iterations by applying all lessons learned. Good luck!