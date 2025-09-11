# Quick Drill Search Guide

## Overview
Guide for searching hockey drills using available MCP tools.

---

## Search Instructions

To search for hockey drills, use the `search_hockey_drills` tool from the hockey-coaching MCP server with these parameters:

### Tool Call Format
```
search_hockey_drills(
    query="your search terms",
    age_groups=["U8", "U10"],  # Optional: filter by age
    skill_focus=["skating", "passing"],  # Optional: filter by skills
    n_results=10  # Number of results to return
)
```

---

## Common Search Scenarios

### 1. Search by Skill Focus
**Need:** Drills for specific skills
```
search_hockey_drills(
    query="edge control skating",
    skill_focus=["skating", "edges"],
    age_groups=["U10"],
    n_results=5
)
```

### 2. Search by Age Group
**Need:** Age-appropriate drills only
```
search_hockey_drills(
    query="fun games",
    age_groups=["U8"],
    n_results=10
)
```

### 3. Search for Station Drills
**Need:** Drills that work well in stations
```
search_hockey_drills(
    query="station drill 3 groups",
    n_results=8
)
```

### 4. Search for Small Area Games
**Need:** Games for limited ice
```
search_hockey_drills(
    query="3v3 small area game cross ice",
    skill_focus=["game_situation"],
    n_results=5
)
```

### 5. Search for Warm-up Activities
**Need:** Dynamic warm-up drills
```
search_hockey_drills(
    query="warm up dynamic stretching skating",
    n_results=5
)
```

---

## Search Parameters Explained

### query (required)
- Main search terms
- Can include: skill names, drill types, equipment, number of players
- Examples: "passing", "2v1", "cone drills", "no equipment"

### age_groups (optional)
- Filter by age appropriateness
- Options: ["U8", "U10", "U12", "U14", "U16", "U18"]
- Can specify multiple: ["U10", "U12"]

### skill_focus (optional)
- Filter by primary skills developed
- Common options:
  - "skating"
  - "passing"
  - "shooting"
  - "puck_handling"
  - "checking"
  - "positioning"
  - "game_situation"
  - "team_play"

### n_results (optional)
- Number of drills to return
- Default: 10
- Range: 1-20

---

## Interpreting Search Results

Each drill result includes:
- **Title**: Drill name
- **Summary**: Quick description
- **Age Groups**: Appropriate ages
- **Skills Developed**: Primary and secondary skills
- **Duration**: Typical time needed
- **Equipment**: Required items
- **Setup**: How to organize
- **Key Points**: Coaching focus
- **Variations**: Ways to modify

---

## Advanced Search Tips

### Combine Multiple Skills
Find drills that develop multiple skills simultaneously:
```
search_hockey_drills(
    query="passing skating combination",
    skill_focus=["passing", "skating"],
    n_results=5
)
```

### Equipment-Specific Searches
Find drills for available equipment:
```
search_hockey_drills(
    query="cones only no pucks",
    n_results=10
)
```

### Competitive vs Fun
Balance practice types:
```
# Fun drills
search_hockey_drills(
    query="fun games relay race",
    age_groups=["U8", "U10"]
)

# Competitive drills
search_hockey_drills(
    query="compete battle drill 1v1",
    age_groups=["U12", "U14"]
)
```

### Progressive Difficulty
Find drill progressions:
```
search_hockey_drills(
    query="backward skating progression beginner to advanced",
    n_results=6
)
```

---

## Drill Selection Criteria

When reviewing search results, consider:

### ✅ GOOD FIT IF:
- Matches your available time
- Appropriate for player skill level
- Uses available equipment
- Addresses identified skill gaps
- Engages player interest level

### ⚠️ MODIFY IF:
- Too complex for age group
- Requires unavailable equipment
- Takes too long for time slot
- Doesn't match group size

### ❌ SKIP IF:
- Safety concerns for skill level
- Requires equipment you don't have
- Too advanced/basic for group
- Doesn't align with practice goals

---

## Creating Drill Combinations

### Efficient Pairing
Look for drills that:
1. Use same equipment setup
2. Cover complementary skills
3. Flow well in sequence
4. Vary intensity levels

### Example Combination Search
```
# First: Find passing drill
search_hockey_drills(
    query="stationary passing",
    age_groups=["U10"],
    n_results=3
)

# Then: Find compatible skating drill
search_hockey_drills(
    query="skating drill uses same cones setup",
    age_groups=["U10"],
    n_results=3
)
```

---

## Saving Favorite Drills

After finding good drills:

1. **Note for Airtable**: Save drill name and rating
2. **Track Usage**: Record when used and effectiveness
3. **Document Modifications**: Note any adjustments made
4. **Build Library**: Create categories of go-to drills

---

## Quick Reference Commands

**Most Common Searches:**

1. **"I need a fun warm-up for U10"**
2. **"Find passing drills that work in stations"**
3. **"Search for 3v3 small area games"**
4. **"Get shooting drills for U12 players"**
5. **"Find drills for backward skating development"**