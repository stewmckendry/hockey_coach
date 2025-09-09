# Hockey Formation Zone Inspection & Feedback

This document provides detailed zone mappings for all preset hockey formations. Please review each formation and provide feedback on accuracy.

## How to Use This Document

1. Review each formation's player positioning and zone mapping
2. Check the **Tactical Analysis** section for coaching accuracy
3. Add your feedback in the **FEEDBACK NEEDED** sections
4. Mark formations as ✅ **APPROVED** or ❌ **NEEDS CHANGES**

## Coordinate System Reference

**NHL Rink Dimensions (using sportypy standard):**
- Full rink: x = -100 to +100, y = -42.5 to +42.5
- Blue lines: x = -25 and +25 (offensive zone starts at x = +25)
- Goal lines: x = -89 and +89
- Center line: x = 0

**Zone Classifications:**
- **Defensive Zone**: x = -100 to -25
- **Neutral Zone**: x = -25 to +25  
- **Offensive Zone**: x = +25 to +100

---

## 32-Zone Grid System Reference

The hockey diagram system uses a precise 32-zone grid (8 columns × 4 rows) to map player positions. Each zone has a specific name and coordinates:

### **🏒 DEFENSIVE ZONES (12 zones: x = -100 to -25)**

| Zone Name | Coordinates | Hockey Location Description |
|-----------|-------------|----------------------------|
| **def-left-high** | x=-100 to -75, y=21.25 to 42.5 | Behind net, left side, upper boards |
| **def-center-left-high** | x=-75 to -50, y=21.25 to 42.5 | Left circle area, upper slot |
| **def-center-right-high** | x=-50 to -25, y=21.25 to 42.5 | Right circle area, upper slot |
| **def-left-mid-high** | x=-100 to -75, y=0 to 21.25 | Behind net, left side, mid-ice |
| **def-center-left-mid-high** | x=-75 to -50, y=0 to 21.25 | Left circle, center ice level |
| **def-center-right-mid-high** | x=-50 to -25, y=0 to 21.25 | Right circle, center ice level |
| **def-left-mid-low** | x=-100 to -75, y=-21.25 to 0 | Behind net, left side, lower mid |
| **def-center-left-mid-low** | x=-75 to -50, y=-21.25 to 0 | Left circle, lower mid area |
| **def-center-right-mid-low** | x=-50 to -25, y=-21.25 to 0 | Right circle, lower mid area |
| **def-left-low** | x=-100 to -75, y=-42.5 to -21.25 | Behind net, left side, lower boards |
| **def-center-left-low** | x=-75 to -50, y=-42.5 to -21.25 | Left circle area, lower boards |
| **def-center-right-low** | x=-50 to -25, y=-42.5 to -21.25 | Right circle area, lower boards |

### **⚡ NEUTRAL ZONES (8 zones: x = -25 to +25)**

| Zone Name | Coordinates | Hockey Location Description |
|-----------|-------------|----------------------------|
| **neu-left-high** | x=-25 to 0, y=21.25 to 42.5 | Blue line to center, left wing area |
| **neu-right-high** | x=0 to 25, y=21.25 to 42.5 | Center to blue line, right wing area |
| **neu-left-mid-high** | x=-25 to 0, y=0 to 21.25 | Blue line to center, left hash marks |
| **neu-right-mid-high** | x=0 to 25, y=0 to 21.25 | Center to blue line, right hash marks |
| **neu-left-mid-low** | x=-25 to 0, y=-21.25 to 0 | Blue line to center, left hash marks |
| **neu-right-mid-low** | x=0 to 25, y=-21.25 to 0 | Center to blue line, right hash marks |
| **neu-left-low** | x=-25 to 0, y=-42.5 to -21.25 | Blue line to center, left wing boards |
| **neu-right-low** | x=0 to 25, y=-42.5 to -21.25 | Center to blue line, right wing boards |

### **🎯 OFFENSIVE ZONES (12 zones: x = +25 to +100)**

| Zone Name | Coordinates | Hockey Location Description |
|-----------|-------------|----------------------------|
| **off-center-left-high** | x=25 to 50, y=21.25 to 42.5 | Blue line to slot, left wing area |
| **off-center-right-high** | x=50 to 75, y=21.25 to 42.5 | Slot to goal line, right wing area |
| **off-right-high** | x=75 to 100, y=21.25 to 42.5 | Goal line to behind net, upper corner |
| **off-center-left-mid-high** | x=25 to 50, y=0 to 21.25 | Blue line to slot, left point area |
| **off-center-right-mid-high** | x=50 to 75, y=0 to 21.25 | Slot to goal line, high slot center |
| **off-right-mid-high** | x=75 to 100, y=0 to 21.25 | Goal line to behind net, right side |
| **off-center-left-mid-low** | x=25 to 50, y=-21.25 to 0 | Blue line to slot, left point area |
| **off-center-right-mid-low** | x=50 to 75, y=-21.25 to 0 | Slot to goal line, low slot center |
| **off-right-mid-low** | x=75 to 100, y=-21.25 to 0 | Goal line to behind net, right side |
| **off-center-left-low** | x=25 to 50, y=-42.5 to -21.25 | Blue line to slot, left wing boards |
| **off-center-right-low** | x=50 to 75, y=-42.5 to -21.25 | Slot to goal line, left wing boards |
| **off-right-low** | x=75 to 100, y=-42.5 to -21.25 | Goal line to behind net, lower corner |

### **📍 Key Hockey Area Mappings:**
- **"Slot"** = off-center-right-mid-high + off-center-right-mid-low (x=50-75, y=-21 to +21)
- **"High Slot"** = off-center-left-mid-high + off-center-left-mid-low (x=25-50, y=-21 to +21)
- **"Point"** = off-center-left-high + off-center-left-mid-high (blue line area)
- **"Corners"** = off-right-high + off-right-low (behind net areas)
- **"Face-off Circles"** = def-center-left + def-center-right (defensive), off-center-left + off-center-right (offensive)

**Zone Distribution:** 12 Defensive + 8 Neutral + 12 Offensive = 32 Total Zones

---

## 1. 2-1-2 FORECHECK ✅ **RECENTLY CORRECTED**

### Player Zone Mapping
| Position | Coordinates | Zone | Role |
|----------|-------------|------|------|
| **F1 (C)** | x=75, y=0 | Deep Offensive | Puck pressure |
| **F2 (LW)** | x=55, y=-25 | Mid Offensive | Low support |
| **F3 (RW)** | x=55, y=25 | Mid Offensive | Low support |
| **D1 (LD)** | x=27, y=-20 | Inside Blue Line | Point coverage |
| **D2 (RD)** | x=27, y=20 | Inside Blue Line | Point coverage |
| **Opposition** | x=80, y=-8 | Deep Offensive | Puck carrier |

### Tactical Analysis
- **F1 Strategy**: Deep pressure on puck carrier (x=75 - corner area)
- **F2/F3 Strategy**: Supporting low (x=55 - mid-zone support)
- **Defence Strategy**: Inside blue line (x=27 - proper positioning)
- **Pressure Zone**: x=65-100 covering offensive zone

### FEEDBACK NEEDED
**Status**: ✅ **CORRECTED BASED ON FEEDBACK**
- Defence now properly inside blue line (x=27 vs previous x=10)
- F1 now deep pressuring puck (x=75 vs previous x=40)
- F2/F3 supporting low (x=55) instead of too high

**Additional feedback?**: ________________________________

---

## 2. 1-2-2 FORECHECK

### Player Zone Mapping
| Position | Coordinates | Zone | Role |
|----------|-------------|------|------|
| **F1 (C)** | x=70, y=0 | Deep Offensive | First pressure |
| **F2 (LW)** | x=50, y=-20 | Mid Offensive | Support pressure |
| **F3 (RW)** | x=50, y=20 | Mid Offensive | Support pressure |
| **D1 (LD)** | x=20, y=-15 | Neutral Zone | Conservative |
| **D2 (RD)** | x=20, y=15 | Neutral Zone | Conservative |

### Tactical Analysis
- **F1 Strategy**: Aggressive first pressure (x=70)
- **F2/F3 Strategy**: Tight support formation (x=50)
- **Defence Strategy**: Conservative neutral zone (x=20)

### FEEDBACK NEEDED
**Status**: ❌ **NEEDS REVIEW**

**Questions:**
1. Should defence be inside blue line (x=25+) instead of neutral zone (x=20)?
2. Is F1 positioning (x=70) aggressive enough for 1-2-2?
3. Are F2/F3 (x=50) positioned correctly for tight support?

**Feedback**: ________________________________

---

## 3. 1-3-1 POWER PLAY

### Player Zone Mapping
| Position | Coordinates | Zone | Role |
|----------|-------------|------|------|
| **F1 (C)** | x=60, y=0 | Mid Offensive | Net front |
| **F2 (LW)** | x=40, y=-30 | Offensive Zone | Half-wall |
| **F3 (RW)** | x=40, y=30 | Offensive Zone | Half-wall |
| **D1 (Point)** | x=30, y=0 | Blue Line | Quarterback |
| **D2 (Support)** | x=25, y=0 | At Blue Line | Support |

### Tactical Analysis
- **Umbrella Formation**: Classic 1-3-1 setup
- **Net Front**: F1 at x=60 for screens/tips
- **Half-Walls**: F2/F3 at x=40 for cycle/entry
- **Point**: D1 at x=30 for shots/distribution

### FEEDBACK NEEDED
**Status**: ❌ **NEEDS REVIEW**

**Questions:**
1. Should net front (F1) be deeper - closer to goal (x=80+)?
2. Are half-wall positions (x=40, y=±30) optimal for umbrella?
3. Is point positioning (x=30) correct for power play umbrella?

**Feedback**: ________________________________

---

## 4. DIAMOND PENALTY KILL

### Player Zone Mapping
| Position | Coordinates | Zone | Role |
|----------|-------------|------|------|
| **F1 (C)** | x=-50, y=0 | Defensive Zone | Box center |
| **F2 (Wing)** | x=-30, y=0 | Blue Line Area | Pressure |
| **D1 (LD)** | x=-70, y=-15 | Deep Defensive | Box low |
| **D2 (RD)** | x=-70, y=15 | Deep Defensive | Box low |

### Tactical Analysis
- **Diamond Shape**: F2 at tip, F1 center, D1/D2 base
- **Pressure Point**: F2 at blue line (x=-30)
- **Box Formation**: Compact defensive structure

### FEEDBACK NEEDED
**Status**: ❌ **NEEDS REVIEW**

**Questions:**
1. Are coordinates flipped for defensive zone perspective?
2. Should the diamond be more compact or spread out?
3. Is F2 positioning (x=-30) optimal for pressure?

**Feedback**: ________________________________

---

## 5. STRONG SIDE BREAKOUT

### Player Zone Mapping
| Position | Coordinates | Zone | Role |
|----------|-------------|------|------|
| **D1 (LD)** | x=-80, y=-20 | Deep Defensive | Puck retrieval |
| **D2 (RD)** | x=-60, y=20 | Defensive Zone | Support |
| **C** | x=-40, y=0 | Neutral Zone | Center support |
| **LW** | x=-20, y=-35 | Wing | Boards |
| **RW** | x=-20, y=35 | Wing | Boards |

### Tactical Analysis
- **Strong Side**: LD retrieves (x=-80)
- **Support**: RD provides option (x=-60)
- **Outlets**: Wings positioned at x=-20 for breakout

### FEEDBACK NEEDED
**Status**: ❌ **NEEDS REVIEW**

**Questions:**
1. Are wing positions (x=-20, y=±35) optimal for breakout?
2. Should center be higher in neutral zone?
3. Is D2 support positioning (x=-60) correct?

**Feedback**: ________________________________

---

## 6. OFFENSIVE ZONE CYCLE

### Player Zone Mapping
| Position | Coordinates | Zone | Role |
|----------|-------------|------|------|
| **LW** | x=80, y=-30 | Corner | Puck possession |
| **RW** | x=50, y=25 | Half-wall | Support |
| **C** | x=70, y=0 | Slot | Net front |
| **LD** | x=30, y=-15 | Point | Shot option |
| **RD** | x=30, y=15 | Point | Shot option |

### Tactical Analysis
- **Cycle Pattern**: LW in corner, RW half-wall support
- **Net Presence**: C in slot for scoring
- **Point Options**: Both D at blue line

### FEEDBACK NEEDED
**Status**: ❌ **NEEDS REVIEW**

**Questions:**
1. Is corner positioning (x=80, y=-30) deep enough for cycle?
2. Should center be closer to net (x=85+)?
3. Are point positions (x=30) optimal for shooting lanes?

**Feedback**: ________________________________

---

## 7. NEUTRAL ZONE TRAP

### Player Zone Mapping
| Position | Coordinates | Zone | Role |
|----------|-------------|------|------|
| **F1** | x=20, y=0 | Neutral Zone | First pressure |
| **F2** | x=0, y=-20 | Center Line | Trap position |
| **F3** | x=0, y=20 | Center Line | Trap position |
| **D1** | x=-15, y=-15 | Defensive Side | Support |
| **D2** | x=-15, y=15 | Defensive Side | Support |

### Tactical Analysis
- **Trap Structure**: F1 forces play, F2/F3 intercept
- **Clogging**: Center ice positioning (x=0)
- **Support**: Defence ready for turnovers

### FEEDBACK NEEDED
**Status**: ❌ **NEEDS REVIEW**

**Questions:**
1. Is F1 positioning (x=20) aggressive enough for pressure?
2. Should F2/F3 be more spread out horizontally?
3. Are defence positions (x=-15) optimal for support?

**Feedback**: ________________________________

---

## 8. DEFENSIVE ZONE COVERAGE

### Player Zone Mapping
| Position | Coordinates | Zone | Role |
|----------|-------------|------|------|
| **LW** | x=-60, y=-30 | Defensive Zone | Wall coverage |
| **RW** | x=-60, y=30 | Defensive Zone | Wall coverage |
| **C** | x=-50, y=0 | Slot | High coverage |
| **LD** | x=-80, y=-15 | Deep Defensive | Net front |
| **RD** | x=-80, y=15 | Deep Defensive | Net front |

### Tactical Analysis
- **Wall Coverage**: Wings protect boards (x=-60)
- **Slot Coverage**: Center covers high slot (x=-50)
- **Net Coverage**: Defence protect crease (x=-80)

### FEEDBACK NEEDED
**Status**: ❌ **NEEDS REVIEW**

**Questions:**
1. Are wing positions (x=-60) correct for wall coverage?
2. Should center be deeper in slot coverage?
3. Is defence positioning (x=-80) optimal for net front?

**Feedback**: ________________________________

---

---

## 9. BOX PENALTY KILL

### Player Zone Mapping
| Position | Coordinates | Zone | Role |
|----------|-------------|------|------|
| **F1 (C)** | x=-50, y=-10 | Defensive Zone | Box front |
| **F2 (RW)** | x=-50, y=10 | Defensive Zone | Box front |
| **D1 (LD)** | x=-70, y=-10 | Deep Defensive | Box back |
| **D2 (RD)** | x=-70, y=10 | Deep Defensive | Box back |

### Tactical Analysis
- **Box Formation**: Compact 4-player box structure
- **Front Line**: F1/F2 at x=-50 for initial pressure  
- **Back Line**: D1/D2 at x=-70 for net protection
- **Coverage Zone**: Defensive zone rectangle (x=-80 to -40)

### FEEDBACK NEEDED
**Status**: ❌ **NEEDS REVIEW**

**Questions:**
1. Is box formation positioning (front x=-50, back x=-70) optimal?
2. Should forwards be more aggressive (closer to x=-40)?
3. Is 20-unit spacing between front/back line correct?

**Feedback**: ________________________________

---

## 10. OVERLOAD POWER PLAY

### Player Zone Mapping
| Position | Coordinates | Zone | Role |
|----------|-------------|------|------|
| **F1 (C)** | x=70, y=-5 | Offensive Zone | Net front |
| **F2 (LW)** | x=85, y=-25 | Deep Offensive | Corner/behind net |
| **F3 (RW)** | x=75, y=-15 | Offensive Zone | Support |
| **D1 (LD)** | x=30, y=-30 | Blue Line | Point (overload side) |
| **D2 (RD)** | x=30, y=20 | Blue Line | Point (weak side) |

### Tactical Analysis
- **Overload Strategy**: 3 forwards concentrated on one side
- **Net Front**: C positioned at x=70 for deflections
- **Corner Play**: LW deep at x=85 for puck possession
- **Point Imbalance**: LD positioned for overload side entry

### FEEDBACK NEEDED
**Status**: ❌ **NEEDS REVIEW**

**Questions:**
1. Is the overload concentration (all at y=-5 to -30) realistic?
2. Should weak-side point (RD) be positioned differently?
3. Is corner positioning (x=85, y=-25) optimal for cycle play?

**Feedback**: ________________________________

---

## 11. DRILL PATTERNS & ZONE DEFINITIONS

### Figure 8 Skating Drill
**Cone Positions**: 
- Cone 1: x=-69, y=-22.5 (Left face-off circle)
- Cone 2: x=-69, y=22.5 (Right face-off circle)

**Path Pattern**: 8 waypoints creating figure-8 around face-off circles

### Horseshoe Passing Drill  
**Station Positions**:
- Station 1: x=69, y=-22.5 (Right circle)
- Station 2: x=85, y=0 (Behind net)
- Station 3: x=69, y=22.5 (Right circle) 
- Station 4: x=40, y=0 (High slot)

### Russian Circles Agility Drill
**Circle Centers**: 5 circles at face-off dots and center ice
- All circles have 15-unit radius

### FEEDBACK NEEDED - DRILL PATTERNS
**Status**: ❌ **NEEDS REVIEW**

**Questions:**
1. Are face-off circle coordinates (x=±69, y=±22.5) NHL-accurate?
2. Is behind-net position (x=85, y=0) realistic for horseshoe drill?
3. Are drill spacing and progressions age-appropriate?

**Feedback**: ________________________________

---

## 12. HOCKEY ZONE DEFINITIONS

### Core Zone Boundaries (Used by All Systems)
| Zone Name | Coordinates (x,y,width,height) | Description |
|-----------|--------------------------------|-------------|
| **Offensive Zone** | [25, -42.5, 75, 85] | Full offensive zone |
| **Defensive Zone** | [-100, -42.5, 75, 85] | Full defensive zone |
| **Neutral Zone** | [-25, -42.5, 50, 85] | Between blue lines |
| **Slot** | [60, -8, 25, 16] | Primary scoring area |
| **High Slot** | [40, -12, 30, 24] | Secondary scoring area |
| **Left Point** | [25, -35, 20, 15] | Left point position |
| **Right Point** | [25, 20, 20, 15] | Right point position |
| **Left Corner** | [80, -42.5, 20, 20] | Left corner area |
| **Right Corner** | [80, 22.5, 20, 20] | Right corner area |
| **Behind Net** | [89, -20, 11, 40] | Behind goal area |

### FEEDBACK NEEDED - ZONE DEFINITIONS
**Status**: ❌ **CRITICAL - USED BY ALL FORMATIONS**

**Questions:**
1. Are blue line coordinates (x=±25) accurate to NHL regulation?
2. Is slot definition (x=60-85, y=-8 to +8) the standard coaching definition?
3. Are corner boundaries (x=80-100) correctly sized?
4. Do point areas (x=25-45) match standard positional coaching?

**Feedback**: ________________________________

---

## 13. MOVEMENT PATTERNS

### Standard Movement Types (Used Across All Formations)
1. **D-to-D Swing**: LD → RD pass with RD movement to x=0, y=20
2. **Give and Go**: C → RW pass, C skates to x=20, y=0, RW returns pass
3. **Drop Pass**: C drops pass at x=-10, y=0, RW retrieves
4. **Cross-Ice Pass**: LW → RW direct pass

### FEEDBACK NEEDED - MOVEMENT PATTERNS
**Status**: ❌ **NEEDS REVIEW**

**Questions:**
1. Are movement distances realistic for NHL-sized rink?
2. Do pass timing and positioning match standard hockey plays?
3. Are skating path coordinates tactically sound?

**Feedback**: ________________________________

---

## COMPREHENSIVE SUMMARY & NEXT STEPS

### ALL PRESET ELEMENTS STATUS:

**✅ CORRECTED:**
- 2-1-2 Forecheck: Fixed and validated

**❌ FORMATIONS NEEDING REVIEW:**
- 1-2-2 Forecheck
- 1-3-1 Power Play  
- Box Penalty Kill
- Strong Side Breakout
- Offensive Zone Cycle
- Neutral Zone Trap
- Defensive Zone Coverage
- Overload Power Play

**❌ FOUNDATIONAL SYSTEMS NEEDING REVIEW:**
- Hockey Zone Definitions (CRITICAL - affects all formations)
- Drill Patterns (Figure 8, Horseshoe, Russian Circles)
- Movement Patterns (D-to-D, Give-and-Go, Drop Pass, Cross-Ice)

**🔥 HIGHEST PRIORITY FOR REVIEW:**
1. **Hockey Zone Definitions** - Used by all formations and parsers
2. **2-1-2 & 1-2-2 Forecheck** - Most common tactical concepts
3. **Power Play Formations** - Critical for special teams accuracy

### How to Provide Feedback:

1. **For Each Formation**: Add specific feedback in the "FEEDBACK NEEDED" sections
2. **Coordinate Changes**: Suggest new x,y coordinates if needed
3. **Tactical Accuracy**: Confirm if the tactical analysis matches real coaching
4. **Priority**: Mark which formations are highest priority to fix first

### Implementation Process:

After your feedback, I'll:
1. Update `elements.py` with corrected coordinates
2. Regenerate test diagrams for verification
3. Update formation descriptions for accuracy
4. Create validation tests for each formation

**Please provide your feedback on the formations above!** 🏒