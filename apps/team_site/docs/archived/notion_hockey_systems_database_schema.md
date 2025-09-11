# ⚡ Thunder Hockey Systems - Notion Database Schema

## 🎯 Overview
Complete database schema and template design for the Thunder Hockey Systems based on the validated defensive zone coverage play card.

---

## 🗄️ DATABASE PROPERTIES SCHEMA

### Core Identification
| Property | Type | Purpose | Example |
|----------|------|---------|---------|
| **Card Title** | Title | Primary identifier | "Defensive Zone Coverage" |
| **Card Number** | Number | Sequential ordering | 1, 2, 3... |
| **Play Nickname** | Rich Text | Fun team name | "The Thunder Box" or "5 on a Die" |
| **Hero Image** | Files | Main diagram | Hockey rink with formation |
| **One Big Idea** | Rich Text | Core concept (1 sentence) | "Everyone protects the house - stay between your man and our net!" |

### Categorization
| Property | Type | Purpose | Options |
|----------|------|---------|---------|
| **Zone Focus** | Select | Where play happens | Defensive Zone, Neutral Zone, Offensive Zone |
| **Play Type** | Select | System category | Coverage, Breakout, Forecheck, Cycle, Special Teams |
| **Complexity Level** | Select | Difficulty rating | ⚡ Basic, ⚡⚡ Intermediate, ⚡⚡⚡ Advanced |
| **Formation Type** | Rich Text | Tactical formation | "5 on a die", "2-1-2", "1-2-2", etc. |

### Position-Specific Instructions
| Property | Type | Purpose |
|----------|------|---------|
| **Center Instructions** | Rich Text | What centers do (3 numbered points) |
| **Winger Instructions** | Rich Text | What wingers do (3 numbered points) |  
| **Defense Instructions** | Rich Text | What defense does (3 numbered points) |
| **Goalie Instructions** | Rich Text | What goalie does (2 numbered points) |
| **Center Thunder Tip** | Rich Text | Key tip for centers |
| **Winger Thunder Tip** | Rich Text | Key tip for wingers |
| **Defense Thunder Tip** | Rich Text | Key tip for defense |
| **Goalie Thunder Tip** | Rich Text | Key tip for goalies |
| **Center Don't Do** | Rich Text | Common mistake to avoid |
| **Winger Don't Do** | Rich Text | Common mistake to avoid |
| **Defense Don't Do** | Rich Text | Common mistake to avoid |

### Practice & Learning System
| Property | Type | Purpose | Options |
|----------|------|---------|---------|
| **Current Team Level** | Select | Where team is at | Level 1, Level 2, Level 3, Level 4, Level 5 |
| **Level 1 Criteria** | Rich Text | Walking speed requirements | "Everyone finds their spot" |
| **Level 2 Criteria** | Rich Text | Skating speed requirements | "Skate to positions quickly" |
| **Level 3 Criteria** | Rich Text | With pucks requirements | "Coach passes puck around" |
| **Level 4 Criteria** | Rich Text | Game speed requirements | "5-on-5 with light pressure" |
| **Level 5 Criteria** | Rich Text | Thunder mode requirements | "Full game situation" |
| **Progress Bar Display** | Formula | Visual progress | Based on Current Team Level |

### Game Application
| Property | Type | Purpose |
|----------|------|---------|
| **When To Use Situation 1** | Checkbox | Game scenario checkbox |
| **When To Use Label 1** | Rich Text | Description of scenario |
| **When To Use Situation 2** | Checkbox | Game scenario checkbox |
| **When To Use Label 2** | Rich Text | Description of scenario |
| **When To Use Situation 3** | Checkbox | Game scenario checkbox |
| **When To Use Label 3** | Rich Text | Description of scenario |
| **When To Use Situation 4** | Checkbox | Game scenario checkbox |
| **When To Use Label 4** | Rich Text | Description of scenario |

### Media & Learning Resources  
| Property | Type | Purpose |
|----------|------|---------|
| **YouTube Video URL** | URL | Educational video link |
| **Video Description** | Rich Text | What video shows |
| **Formation Diagram** | Rich Text | ASCII art formation |

### Coach Resources
| Property | Type | Purpose |
|----------|------|---------|
| **Coach Key Point 1** | Rich Text | Important coaching reminder |
| **Coach Key Point 2** | Rich Text | Important coaching reminder |
| **Coach Key Point 3** | Rich Text | Important coaching reminder |
| **How It Looks Success 1** | Rich Text | Success indicator |
| **How It Looks Success 2** | Rich Text | Success indicator |
| **How It Looks Success 3** | Rich Text | Success indicator |
| **How It Looks Success 4** | Rich Text | Success indicator |

### Tracking & Relations
| Property | Type | Purpose |
|----------|------|---------|
| **Next Card Reference** | Rich Text | Link to next logical card |
| **Last Updated** | Last edited time | Track changes |
| **Created Date** | Created time | Track creation |

---

## 🎨 NOTION PAGE TEMPLATE STRUCTURE

### Template Layout Pattern
```markdown
[HERO IMAGE - Full width]

# [Card Title]
## "[Play Nickname]"

[One Big Idea - Large callout]

---

## 📺 WATCH FIRST (2 minutes)
[YouTube Video Embed]
[Video Description]

---

## 🏒 YOUR JOB (Pick Your Position)

### ⚡ FORWARDS - CENTER
📍 **WHERE YOU START:** [Visual context]
🎯 **WHAT YOU DO:**
[Center Instructions - 3 numbered points]

⚡ **THUNDER TIP:** [Center Thunder Tip]
❌ **DON'T DO THIS:** [Center Don't Do]

### ⚡ FORWARDS - WINGERS
📍 **WHERE YOU START:** [Visual context]
🎯 **WHAT YOU DO:**
[Winger Instructions - 3 numbered points]

⚡ **THUNDER TIP:** [Winger Thunder Tip]
❌ **DON'T DO THIS:** [Winger Don't Do]

### 🛡️ DEFENSE
📍 **WHERE YOU START:** [Visual context]
🎯 **WHAT YOU DO:**
[Defense Instructions - 3 numbered points]

⚡ **THUNDER TIP:** [Defense Thunder Tip]
❌ **DON'T DO THIS:** [Defense Don't Do]

### 🥅 GOALIE
📍 **WHERE YOU ARE:** [Visual context]
🎯 **WHAT YOU DO:**
[Goalie Instructions - 2 numbered points]

⚡ **THUNDER TIP:** [Goalie Thunder Tip]

---

## 🎮 PRACTICE IT LIKE A VIDEO GAME

### Level 1: Walking Speed (No Pucks)
✅ [Level 1 Criteria]

### Level 2: Skating Speed (Still No Pucks)
✅ [Level 2 Criteria]

### Level 3: Add Pucks
✅ [Level 3 Criteria]

### Level 4: Game Speed
✅ [Level 4 Criteria]

### Level 5: Thunder Mode ⚡
✅ [Level 5 Criteria]

**OUR CURRENT LEVEL:** [Progress Bar Display] [Current Team Level description]

---

## 🎯 WHEN TO USE THIS PLAY

### Game Situations:
[Dynamic checkboxes based on When To Use properties]

---

## 💭 REMEMBER THE SHAPE

[Formation Diagram - ASCII art]
**"[Formation description based on Formation Type]"**

---

## 🏆 COACH'S KEY POINTS

1. **[Coach Key Point 1]**
2. **[Coach Key Point 2]**
3. **[Coach Key Point 3]**

---

## 📊 HOW IT LOOKS WHEN IT WORKS

✅ [How It Looks Success 1]
✅ [How It Looks Success 2]
✅ [How It Looks Success 3]
✅ [How It Looks Success 4]

---

*Next Card: [Next Card Reference]*
```

---

## 🔧 FORMULA CALCULATIONS

### Progress Bar Display
```
if(prop("Current Team Level") == "Level 1", "[▓░░░░] Level 1 - Learning the basics!",
if(prop("Current Team Level") == "Level 2", "[▓▓░░░] Level 2 - Getting there!", 
if(prop("Current Team Level") == "Level 3", "[▓▓▓░░] Level 3 - Adding pucks!",
if(prop("Current Team Level") == "Level 4", "[▓▓▓▓░] Level 4 - Game speed!",
if(prop("Current Team Level") == "Level 5", "[▓▓▓▓▓] Level 5 - Thunder Mode!", "")))))
```

### Game Situations Display
Dynamic rendering based on checkbox states and labels:
- If checkbox checked → ☑️ [Label]  
- If checkbox unchecked → ☐ [Label]

---

## 🎯 ADDRESSING USER FEEDBACK

### 1. "5 on a Die" Terminology
- **Solution**: Added `Formation Type` property to capture specific formation names
- **Implementation**: Display in template as "Remember the Shape" subtitle

### 2. Corner Battles Question  
- **Recommendation**: Separate card (#7 from content calendar)
- **Reasoning**: Corner battles are specific skill/situation, not formation-based like defensive coverage

### 3. Thunder Coloring
- **Database Level**: Use Thunder red (#DC2626) for section headers
- **Template Level**: Consistent ⚡ emoji and Thunder terminology throughout

### 4. Card Length Optimization
- **Current Length**: ~130 lines optimized for:
  - Mobile viewing (scrollable sections)
  - 9-year-old attention span (visual breaks)
  - Position-specific focus (tabs in implementation)

---

## 📱 IMPLEMENTATION NOTES

### Database Creation Order:
1. Create database with all properties
2. Set up proper property types and options  
3. Create first entry (Defensive Zone Coverage)
4. Build template that references all properties
5. Test template rendering with sample data

### Template Features:
- **Dynamic Content**: All text pulls from database properties
- **Visual Consistency**: Thunder branding throughout
- **Mobile Optimized**: Short sections, clear headers
- **Position Focused**: Clear role separation
- **Progress Tracking**: Visual level system

### Next Steps:
1. Create database with this schema
2. Build template using property references
3. Import defensive zone coverage data
4. Test template rendering and UX
5. Refine based on actual display

---

*Schema Version: 1.0*
*Based on validated play card: Defensive Zone Coverage*
*Compatible with: Thunder Play Card System v2.1*