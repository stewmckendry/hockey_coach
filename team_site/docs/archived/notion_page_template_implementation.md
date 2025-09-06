# ⚡ Thunder Play Card - Notion Page Template Implementation

## 🎯 Template Overview
This document provides the exact Notion page template structure that can be used to create dynamic play cards from the Thunder Hockey Systems database.

---

## 🔧 TEMPLATE STRUCTURE (Copy to Notion)

### Template Name: "Thunder Play Card Template"
### Database: Thunder Hockey Systems (ID: 2650cdbf-4977-8160-8c5b-f7c6d4139ed5)

```markdown
# ⚡ THUNDER PLAY CARD #{{Card Number}}

[Hero Image - Database Property: Hero Image]

# {{Card Title}}
## "{{Play Nickname}}"

> 🎯 **ONE BIG IDEA:** {{One Big Idea}}

---

## 📺 WATCH FIRST (2 minutes)
[Video Embed: {{YouTube Video URL}}]
*"{{Video Description}}"*

---

## 🏒 YOUR JOB (Pick Your Position)

### ⚡ FORWARDS - CENTER
📍 **WHERE YOU START:** Middle of the ice, below the puck
🎯 **WHAT YOU DO:**
{{Center Instructions}}

⚡ **THUNDER TIP:** "{{Center Thunder Tip}}"
❌ **DON'T DO THIS:** {{Center Don't Do}}

### ⚡ FORWARDS - WINGERS  
📍 **WHERE YOU START:** Cover the point (defenseman at blue line)
🎯 **WHAT YOU DO:**
{{Winger Instructions}}

⚡ **THUNDER TIP:** "{{Winger Thunder Tip}}"
❌ **DON'T DO THIS:** {{Winger Don't Do}}

### 🛡️ DEFENSE
📍 **WHERE YOU START:** In front of our net
🎯 **WHAT YOU DO:**
{{Defense Instructions}}

⚡ **THUNDER TIP:** "{{Defense Thunder Tip}}"
❌ **DON'T DO THIS:** {{Defense Don't Do}}

### 🥅 GOALIE
📍 **WHERE YOU ARE:** In your crease
🎯 **WHAT YOU DO:**
{{Goalie Instructions}}

⚡ **THUNDER TIP:** "{{Goalie Thunder Tip}}"

---

## 🎮 PRACTICE IT LIKE A VIDEO GAME

### Level 1: Walking Speed (No Pucks)
✅ {{Level 1 Criteria}}

### Level 2: Skating Speed (Still No Pucks)  
✅ {{Level 2 Criteria}}

### Level 3: Add Pucks
✅ {{Level 3 Criteria}}

### Level 4: Game Speed
✅ {{Level 4 Criteria}}

### Level 5: Thunder Mode ⚡
✅ {{Level 5 Criteria}}

**OUR CURRENT LEVEL:** [Progress based on {{Current Team Level}}]

---

## 🎯 WHEN TO USE THIS PLAY

### Game Situations:
[Dynamic checkboxes - render only checked items]
{{#if When To Use Situation 1}}☑️ {{When To Use Label 1}}{{/if}}
{{#if When To Use Situation 2}}☑️ {{When To Use Label 2}}{{/if}}
{{#if When To Use Situation 3}}☑️ {{When To Use Label 3}}{{/if}}
{{#if When To Use Situation 4}}☑️ {{When To Use Label 4}}{{/if}}

{{#unless When To Use Situation 1}}☐ {{When To Use Label 1}}{{/unless}}
{{#unless When To Use Situation 2}}☐ {{When To Use Label 2}}{{/unless}}
{{#unless When To Use Situation 3}}☐ {{When To Use Label 3}}{{/unless}}
{{#unless When To Use Situation 4}}☐ {{When To Use Label 4}}{{/unless}}

---

## 💭 REMEMBER THE SHAPE

```
{{Formation Diagram}}
```
**"Make a {{Formation Type}} shape - protect our home!"**

---

## 🏆 COACH'S KEY POINTS

1. **"{{Coach Key Point 1}}"**
2. **"{{Coach Key Point 2}}"**
3. **"{{Coach Key Point 3}}"**

---

## 📊 HOW IT LOOKS WHEN IT WORKS

✅ {{How It Looks Success 1}}
✅ {{How It Looks Success 2}}
✅ {{How It Looks Success 3}}
✅ {{How It Looks Success 4}}

---

*Next Card: "{{Next Card Reference}}"*
```

---

## 🎨 NOTION IMPLEMENTATION STEPS

### Step 1: Create Template Button
1. Open Thunder Hockey Systems database
2. Click "New" → "New template"  
3. Name it "Thunder Play Card Template"
4. Use the structure above with property references

### Step 2: Property Reference Syntax
In Notion templates, use this syntax:
- Text properties: `{{Property Name}}`
- Select properties: `{{Property Name}}` (shows selected option)
- Checkbox properties: Use conditional blocks (see Step 3)
- Number properties: `{{Property Name}}`
- File properties: Drag from database or reference

### Step 3: Conditional Rendering for Checkboxes
Notion doesn't have native if/then templating, so manually create:
- Checked scenarios with ☑️
- Unchecked scenarios with ☐
- Use database filters or manual updating

### Step 4: Progress Bar Implementation
Create a formula property in the database:
```
if(prop("Current Team Level") == "Level 1", "[▓░░░░] Level 1 - Learning the basics!",
if(prop("Current Team Level") == "Level 2", "[▓▓░░░] Level 2 - Getting there!", 
if(prop("Current Team Level") == "Level 3", "[▓▓▓░░] Level 3 - Adding pucks!",
if(prop("Current Team Level") == "Level 4", "[▓▓▓▓░] Level 4 - Game speed!",
if(prop("Current Team Level") == "Level 5", "[▓▓▓▓▓] Level 5 - Thunder Mode!", "")))))
```

---

## 🔄 USAGE WORKFLOW

### For Each New Play Card:
1. Open Thunder Hockey Systems database
2. Click "New" → "Thunder Play Card Template"  
3. Fill in all database properties
4. Template auto-populates the page structure
5. Add hero image and any custom formatting
6. Review and publish

### For Updates:
1. Edit database properties
2. Page content updates automatically
3. No need to edit individual pages

---

## 🎯 TEMPLATE BENEFITS

### Consistency
- Every play card has identical structure
- Thunder branding maintained throughout
- Position-specific sections always present

### Efficiency  
- New cards created in minutes, not hours
- Database-driven content management
- Easy bulk updates across all cards

### Scalability
- Works for 5 cards or 50 cards
- Template handles all formatting
- Focus on content, not layout

### User Experience
- Familiar navigation for players/parents
- Predictable information architecture
- Mobile-optimized structure

---

## 📱 MOBILE OPTIMIZATION NOTES

### Section Lengths
- Each section fits mobile viewport
- Clear visual breaks between sections
- Scannable bullet points

### Typography Hierarchy
- Large headers for easy reading
- Consistent emoji usage for visual cues
- Short paragraphs for 9-year-olds

### Interactive Elements
- Checkboxes provide visual feedback
- Progress bars show advancement
- Video embeds work on mobile

---

## 🚀 NEXT STEPS

1. **Create template** in Notion using this structure
2. **Test template** with defensive zone coverage data
3. **Refine formatting** based on actual display
4. **Create 2-3 more cards** to validate consistency
5. **Train coaches** on adding new plays
6. **Launch with team** for feedback

---

## 📊 SUCCESS METRICS

### Template Efficiency
- Time to create new card: Target <10 minutes
- Consistency score: 100% structural match
- Error rate: <5% formatting issues

### User Engagement  
- Page views per card
- Time spent on each section
- Parent/player feedback scores

### Content Management
- Database utilization rate
- Template adoption by coaches
- Maintenance time reduction

---

*Template Version: 1.0*
*Compatible with: Thunder Hockey Systems Database*
*Last Updated: 2025-09-05*