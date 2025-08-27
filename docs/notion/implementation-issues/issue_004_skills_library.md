# Issue #4: Build Skills Library

## Overview
Create a comprehensive skills library with 15-20 pages covering fundamental hockey skills for U10 players. Each page will use the iterative workflow: research → draft → edit → publish, with 70% visual content.

## Objectives
- Create engaging skill instruction pages
- Apply U10 UX guidelines throughout
- Use multiple MCP tools for rich content
- Ensure consistent quality and format
- Build a library parents and players will use

## Skills to Cover (15-20 pages)

### Skating Skills (5 pages)
1. **Forward Skating Basics** - Proper stance, stride, balance
2. **Backward Skating** - C-cuts, posture, looking behind
3. **Stopping** - Hockey stop both sides, T-stop
4. **Crossovers** - Forward and backward crossovers
5. **Agility & Edges** - Tight turns, mohawks, edge control

### Passing Skills (4 pages)
6. **Forehand Pass** - Technique, weight transfer, follow-through
7. **Backhand Pass** - Wrist position, blade angle
8. **Receiving Passes** - Cushioning, stick positioning
9. **Saucer Pass** - When and how to elevate the puck

### Shooting Skills (4 pages)
10. **Wrist Shot** - Mechanics, weight transfer, release
11. **Backhand Shot** - Close-range scoring technique
12. **Snap Shot** - Quick release fundamentals
13. **Shooting Positions** - Where to shoot from

### Defensive Skills (4 pages)
14. **Stick Positioning** - Defensive stance and stick placement
15. **Gap Control** - Basic 1-on-1 defense
16. **Angling** - Using the boards to your advantage
17. **Backchecking** - Hustle and positioning

### General Skills (3 pages)
18. **Stickhandling** - Basic puck control patterns
19. **Face-offs** - Basic technique for centers
20. **Hockey Sense** - Reading the play basics

## Workflow for Each Skill Page

### 1. Research Phase
```bash
/research-hockey "U10 [skill name] fundamentals drills progressions"
```
- Use Hockey MCP tools to find relevant drills
- Search YouTube MCP for demonstration videos
- Use Exa MCP for coaching best practices

### 2. Draft Phase
```bash
/draft-content "[Skill Name] Fundamentals" U10
```
- Ensure 70% visual content
- Include clear learning objectives
- Add step-by-step breakdowns
- Include common mistakes section

### 3. Visual Content Creation
- Use StabilityAI MCP to generate skill diagrams
- Find/create progression images
- Use Cloudinary MCP to host all images
- Embed YouTube videos for demonstrations

### 4. Edit Phase
```bash
/edit-content [page-url] "Simplify language, add more visuals, ensure safety tips included"
```
- Verify Grade 3-4 reading level
- Check 10-15 minute completion time
- Ensure positive, encouraging tone

### 5. Publish Phase
```bash
/publish-page [page-url]
```
- Verify mobile responsiveness
- Check all images load properly
- Test video embeds

## Page Template Structure
Each skill page should follow:
```markdown
# [Skill Name]

## What You'll Learn 🎯
[One clear sentence objective]

## Why It Matters 🌟
[Simple explanation for U10 players]

## Watch This First 📹
[Embedded video demonstration]

## Step-by-Step Guide 📋
### 1. Setup
[Visual + brief text]

### 2. The Move
[Visual + brief text]

### 3. Follow Through
[Visual + brief text]

## Practice Tips 💡
- Start slow and focus on form
- [Specific tip]
- [Safety reminder]

## Common Mistakes ⚠️
- [Mistake 1 with visual]
- [Mistake 2 with visual]

## Try This Challenge 🏆
[Age-appropriate skill challenge]

## Remember 🧠
[Key takeaway in kid-friendly language]
```

## Tools Usage Plan
- **Hockey MCP**: Research drills and progressions
- **Notion MCP**: Create and organize pages
- **YouTube MCP**: Find demonstration videos
- **StabilityAI MCP**: Generate skill diagrams
- **Cloudinary MCP**: Host all visual content
- **Exa MCP**: Research best practices
- **Claude LLM**: Content generation and editing

## File Locations
- Work in: `docs/notion/`
- Store images: Cloudinary `hockey-coaching/skills/`
- Reference: `UX_GUIDELINES.md` for standards

## Success Criteria
- [ ] 15-20 skill pages created
- [ ] 70% visual content achieved
- [ ] Consistent template used
- [ ] All videos and images working
- [ ] Mobile-friendly design
- [ ] Grade 3-4 reading level
- [ ] Positive, encouraging tone

## Quality Checklist (Per Page)
- [ ] Clear learning objective
- [ ] Video demonstration included
- [ ] 3-5 step breakdown with visuals
- [ ] Safety tips included
- [ ] Common mistakes addressed
- [ ] Fun challenge included
- [ ] Page loads in under 3 seconds

## Notes
- Prioritize fundamentals over advanced techniques
- Use diverse players in visuals
- Keep instructions concise
- Always include safety considerations
- Make practice tips actionable