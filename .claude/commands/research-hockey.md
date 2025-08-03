---
description: "Research hockey content using Thunder Playbook files, Hockey MCP tools, Exa web search, and YouTube videos for comprehensive content creation"
argument-hint: "<topic> <age-group> [team-name] [research-depth]"
allowed-tools: ["mcp__exa__web_search_exa", "mcp__exa__deep_researcher_start", "mcp__exa__deep_researcher_check", "mcp__youtube__search_videos", "mcp__youtube__get_video", "mcp__youtube__get_transcript", "mcp__notion-remote__search", "mcp__notion-remote__fetch", "mcp__notion-remote__create-pages", "mcp__notion-remote__update-page", "mcp__hockey-coaching__search_hockey_tactics", "mcp__hockey-coaching__search_hockey_videos", "mcp__hockey-coaching__search_hockey_drills", "mcp__hockey-coaching__search_hockey_skills", "mcp__hockey-coaching__search_hockey_dryland", "mcp__hockey-coaching__search_hockey_dryland_videos", "mcp__hockey-coaching__search_hockey_nhl_insights", "mcp__hockey-coaching__search_hockey_rules", "mcp__stability-ai__stability-ai-generate-image-sd35", "mcp__stability-ai__stability-ai-control-structure", "mcp__cloudinary__upload", "Read", "Glob", "Grep", "TodoWrite"]
---

# Hockey Research Command

Comprehensive research workflow that combines Exa AI-powered web search, YouTube video curation, and Thunder Playbook source files to gather high-quality, age-appropriate hockey content for team-specific content creation.

## Research Methodology

### Step 1: Parse Arguments and Team Context
- Extract topic, age group, optional team name, and research depth from arguments
- If team name provided, fetch team context from Team Information database
- Create TodoWrite list for research process tracking
- Apply UX Guidelines standards for age-appropriate research focus

**Error Handling:**
```
If team name provided but not found:
  "Team '[team-name]' not found in Team Information database.
   
   Proceeding with general research for [age-group].
   To enable team-specific research, first run:
   /setup-team '[team-name]' [age-group]"

If age group invalid:
  "Invalid age group '[input]'.
   Valid age groups: U8, U10, U12, U14, U16, U18
   
   Please specify a valid age group."

If Team Information database inaccessible:
  "Warning: Unable to access Team Information database.
   Error: [specific error]
   
   Continuing with topic-based research only."
```

### Step 2: Thunder Playbook Source File Research
**Primary Source Integration:**
```
Thunder Playbook Collections Search Priority:
1. chroma_load/drills/ - On-ice skill development drills
2. chroma_load/ltad/ - Long-term athlete development pathways  
3. chroma_load/tactics/ - Team systems and strategic concepts
4. chroma_load/conduct/ - Rules, safety, and fair play guidance
5. chroma_load/office/ - Off-ice training and conditioning
6. chroma_load/insights/ - NHL expert knowledge and analysis
7. chroma_load/video/ - Instructional video content references
```

**Source File Research Process:**
- Use Glob to identify relevant source files by topic keywords
- Use Grep to search file contents for age-specific and topic-relevant content
- Read detailed content from most relevant source files
- Extract age-appropriate techniques, progressions, and teaching points
- Identify safety considerations and equipment requirements
- Gather coaching tips and common mistakes to avoid

**Thunder Playbook Error Handling:**
```
If source files not accessible:
  "Warning: Unable to access Thunder Playbook source files.
   Path: chroma_load/[collection]/
   
   This may affect research quality. Proceeding with:
   - Hockey MCP knowledge base search
   - External web research
   - YouTube video analysis"

If no relevant files found:
  "No Thunder Playbook files found for '[topic]'.
   
   Expanding search to:
   - Related topics and synonyms
   - General [age-group] resources
   - Hockey MCP knowledge base"
```

### Step 3: Exa AI Web Research Integration
**External Knowledge Enhancement:**
- Use `mcp__exa__web_search_exa` for current hockey coaching trends and techniques
- Focus search on reputable hockey coaching resources and organizations
- Filter results for age-appropriate content and methodologies
- Search for recent developments in coaching philosophy for target age group
- Gather equipment innovations and safety updates

**Deep Research for Complex Topics:**
```
For complex research topics (tactical systems, advanced skills):
1. Use mcp__exa__deep_researcher_start for comprehensive analysis
2. Monitor progress with mcp__exa__deep_researcher_check
3. Synthesize findings with Thunder Playbook source knowledge
4. Cross-reference multiple coaching methodologies
```

### Step 4: YouTube Video Research Integration
**Video Content Enhancement:**
- Use `mcp__youtube__search_videos` for high-quality coaching video discovery
- Search queries constructed with topic + age group + "hockey coaching tutorial"
- Filter for trusted hockey coaching channels and educational content
- Minimum view count thresholds for credibility (1000+ views)
- Duration preferences based on age group (U8: 3-5 min, U10: 5-10 min, U12+: 10-20 min)

**Quality and Safety Validation:**
```
Video Assessment Criteria:
1. Channel Credibility: Verified coaching channels, official organizations
2. Content Quality: Clear demonstrations, professional production
3. Age Appropriateness: Language, complexity, and teaching style
4. Safety Focus: Proper technique emphasis, equipment usage
5. Educational Value: Teaching points, progressions, coaching cues
```

**Transcript Analysis:**
- Extract video transcripts using `mcp__youtube__get_transcript`
- Identify key teaching points and coaching instructions
- Verify age-appropriate language and terminology
- Document safety considerations mentioned in videos
- Create timestamped reference points for specific techniques

### Step 5: Team Context Integration
**Team-Specific Research Focus:**
```
If team context available:
- Coaching Philosophy: [Filter research by coaching approach]
- Season Focus Areas: [Prioritize relevant research topics]
- Available Equipment: [Research equipment-specific techniques]
- Skill Level: [Adjust research complexity and progressions]
- Practice Duration: [Focus on time-appropriate activities]
- Ice Time Type: [Research space-specific adaptations]
```

**Context-Driven Research Priorities:**
- Development-Focused Philosophy → Skill progression research
- Competitive Philosophy → Game situation and tactics research  
- Fun-First Philosophy → Engagement and enjoyment research
- Mixed Skill Levels → Differentiation and modification research

### Step 6: Age-Appropriate Content Filtering
**UX Guidelines Integration:**
```
U8 (8-9 years):
- Research Focus: Basic motor skills, following directions, fun activities
- Content Filter: Simple movements, short activities (5-10 min), visual learning
- Safety Priority: Fundamental safety habits, equipment awareness

U10 (9-10 years):
- Research Focus: Fundamental skills, basic strategy, teamwork
- Content Filter: Step-by-step progressions, clear success indicators (10-15 min)
- Teaching Approach: Simple "why" explanations with concrete examples

U12 (11-12 years):
- Research Focus: Advanced skills, team systems, game situations
- Content Filter: Technical development, cause-and-effect learning (15-20 min)
- Strategy Integration: Basic tactical concepts with skill application

U14+ (13+ years):
- Research Focus: Advanced systems, tactics, mental game, specialization
- Content Filter: Strategic thinking, performance analysis (20-30 min)
- Development Path: Position-specific skills and advanced techniques
```

### Step 7: Visual Research Enhancement
**Generate Supporting Diagrams:**
- Identify key concepts from research that would benefit from visual representation
- For tactical topics: Generate whiteboard diagrams using realistic hockey whiteboard base
- For skill development: Create instructional demonstration images
- For dryland training: Generate exercise diagrams with proper form illustrations
- Upload all images to Cloudinary for immediate embedding in research page
- Include image URLs in research documentation for easy reference

**Visual Content Generation Process:**
```
If research contains tactical concepts:
  1. Generate tactical diagrams using control-structure mode with realistic whiteboard base
  2. Include player positions, movement arrows, and tactical elements
  3. Upload to hockey-coaching/research/ folder in Cloudinary

If research contains skill techniques:
  1. Generate instructional demonstration images showing proper technique
  2. Focus on clear body positioning and equipment usage
  3. Upload with descriptive naming for easy reference

If research contains dryland exercises:
  1. Generate exercise diagrams showing proper form and progression
  2. Include numbered steps and movement indicators
  3. Upload to hockey-coaching/dryland/ folder
```

### Step 8: Research Page Creation and Content Library Integration
**Research Documentation Process:**
- Create full Notion page with comprehensive research findings
- Use structured format for easy reference and navigation
- Include all Thunder Playbook, external research, and video results
- Embed curated videos with quality scores and teaching points
- Create corresponding entry in Content Library database to track the research page:
  - Title: "Research: [Topic] - [Age Group]"
  - Page Type: "Research"
  - Source Type: "Thunder Playbook Data", "Exa Research", or "Combination"
  - Research Notes: Brief summary and key findings
  - Link to target team if team-specific research conducted
  - Tag with relevant coaching philosophy matches
  - Set UX Guidelines compliance status based on age-appropriate filtering

**Research Page Creation Error Handling:**
```
If Content Library database not found:
  "Warning: Unable to locate Content Library database.
   Research page will be created but not tracked.
   
   Please verify Notion integration has access to Content Library."

If page creation fails:
  "Error creating research page in Notion.
   Error: [specific error]
   
   Research findings have been compiled. Options:
   1. Retry page creation
   2. Copy research summary to clipboard
   3. Save research locally"

If duplicate research exists:
  "Similar research already exists:
   '[Existing research title]' created on [date]
   
   Would you like to:
   1. Create new research page anyway
   2. Update existing research with new findings
   3. View existing research"
```

**Version Control for Research Pages:**
```
Before creating research page:
  1. Search Content Library for existing research on topic
  2. If found, compare age groups and dates
  3. Offer options based on findings:
     - No match: Create new research page
     - Exact match: Update or create new version
     - Similar match: Reference in new research
```

## Implementation Workflow

### Phase 1: Setup and Context Gathering
1. Parse command arguments: topic, age group, team name, research depth
2. Search Team Information database if team name provided
3. Create comprehensive TodoWrite research plan
4. Load UX Guidelines standards for target age group
5. Identify relevant Thunder Playbook source file categories

### Phase 2: Thunder Playbook Source Research
6. Use Glob to find relevant source files by topic keywords
7. Use Grep to search for age-specific and topic-relevant content
8. Read detailed content from 3-5 most relevant source files
9. Extract key techniques, progressions, and teaching methodologies
10. Document safety considerations and equipment requirements
11. Identify coaching tips and common implementation challenges

### Phase 3: Hockey MCP Knowledge Base Search
12. Use specialized search tools based on topic type:
    - `search_hockey_tactics` for systems, formations, and plays
    - `search_hockey_drills` for on-ice practice activities
    - `search_hockey_skills` for LTAD and skill development
    - `search_hockey_rules` for regulations and conduct
    - `search_hockey_videos` for instructional video content
    - `search_hockey_dryland` for off-ice training
    - `search_hockey_dryland_videos` for training demonstrations
    - `search_hockey_nhl_insights` for expert knowledge
13. Execute targeted searches across relevant specialized collections
14. Apply age group and position filters as appropriate
15. Extract validated coaching recommendations and best practices
16. Cross-reference MCP findings with Thunder Playbook source files
17. Document unique insights from each specialized collection

**Hockey MCP Error Handling:**
```
If specialized search tools unavailable:
  "Hockey MCP server not responding.
   This may be due to:
   - MCP server not running
   - ChromaDB connection issues
   
   Proceeding with alternative research sources.
   To fix: Check MCP server status with /mcp-test"

If no results from specialized collections:
  "No results found in [collection type] for '[topic]'.
   
   Trying alternative collections:
   - Related content types
   - Broader search terms
   - External web research"
```

### Phase 4: External Research Enhancement
18. Design Exa search queries based on topic and age group
19. Execute targeted web searches for current coaching methods
20. For complex topics, initiate deep research with monitoring
21. Filter external results for credibility and age appropriateness
22. Cross-reference external findings with Thunder Playbook knowledge
23. Identify gaps between internal and external knowledge sources

**Exa Research Error Handling:**
```
If Exa MCP unavailable:
  "Exa web search unavailable.
   Error: [specific error]
   
   This limits access to current web resources.
   Focusing on:
   - Thunder Playbook sources
   - Hockey MCP knowledge base
   - YouTube video content"

If deep research fails to start:
  "Unable to initiate deep research analysis.
   
   Proceeding with standard web search.
   Results may be less comprehensive."

If deep research timeout:
  "Deep research taking longer than expected.
   
   Current progress: [status]
   Options:
   1. Continue waiting (recommended)
   2. Proceed with partial results
   3. Cancel and use standard search"
```

### Phase 5: YouTube Video Research
24. Construct YouTube search queries for hockey coaching videos
25. Use `mcp__youtube__search_videos` with age-appropriate filters
26. Apply quality validation criteria (trusted channels, view counts, safety)
27. Get transcripts for top videos using `mcp__youtube__get_transcript`
28. Extract key teaching points and coaching tips from video content
29. Verify age-appropriate language and demonstration methods
30. Document video resources with quality scores and embed codes

**YouTube Research Error Handling:**
```
If YouTube MCP unavailable:
  "YouTube video search unavailable.
   Error: [specific error]
   
   Known issue: Node.js v23 compatibility
   Proceeding without video content."

If no videos found:
  "No suitable videos found for '[topic] [age-group]'.
   
   Adjusting search to:
   - Broader hockey coaching terms
   - General [age-group] content
   - Alternative video platforms"

If transcript unavailable:
  "Video transcript not available for '[video-title]'.
   
   Using video metadata only:
   - Title and description
   - Channel reputation
   - View count and ratings"

If video quality below threshold:
  "Found videos do not meet quality standards:
   - Low view counts (<1000)
   - Unverified channels
   - Poor safety demonstrations
   
   Excluding from research results."
```

### Phase 6: Synthesis and Documentation
31. Synthesize Thunder Playbook, MCP knowledge, external research, and video findings
32. Apply age-appropriate filtering using UX Guidelines standards
33. Integrate team context if available for personalized insights
34. Create comprehensive research summary with source attribution
35. Create full Notion research page with structured findings
36. Add Content Library database entry to track the research page
37. Prepare research page link for content drafting workflow

### Phase 7: Quality Validation and Output
38. Validate research completeness against topic requirements
39. Ensure age-appropriate content standards are met
40. Verify safety considerations are thoroughly documented
41. Confirm team context integration if applicable
42. Provide research page link and clear next steps for content drafting workflow

## Research Output Structure

### Comprehensive Research Summary
```
# Hockey Research: [Topic] for [Age Group]

## Research Overview
- Topic: [Specific research focus]
- Age Group: [Target age with UX Guidelines standards]
- Research Depth: [Basic/Comprehensive/Deep Analysis]
- Team Context: [If applicable - key team considerations]

## Thunder Playbook Findings
### Core Techniques and Progressions
[Age-appropriate techniques from source files]

### Teaching Points and Coaching Tips
[Extracted coaching wisdom and implementation guidance]

### Safety and Equipment Considerations
[Safety requirements and equipment needs]

### Common Challenges and Solutions
[Typical implementation issues and proven solutions]

## Hockey Knowledge Base Findings
### Tactics and Systems (from search_hockey_tactics)
[Team formations, plays, and strategic concepts]

### Practice Drills (from search_hockey_drills)
[On-ice activities and skill development exercises]

### Skill Development (from search_hockey_skills)
[LTAD framework progressions and age-specific skills]

### Rules and Conduct (from search_hockey_rules)
[Regulations, safety guidelines, and fair play principles]

### Video Resources (from search_hockey_videos)
[Instructional video clips with teaching points]

### Off-Ice Training (from search_hockey_dryland)
[Dryland exercises and conditioning programs]

### NHL Insights (from search_hockey_nhl_insights)
[Expert wisdom and professional coaching perspectives]

## External Research Insights
### Current Coaching Trends
[Recent developments in coaching methodology]

### Expert Perspectives
[Professional coaching insights and recommendations]

### Equipment and Safety Updates
[Latest equipment innovations and safety guidelines]

## 🎥 Video Resources
### Curated Coaching Videos
[Quality-validated videos embedded with teaching points]

### Video Teaching Points
[Key coaching cues extracted from video transcripts]

### Visual Demonstrations
[Timestamped references for specific techniques]

## 📊 Visual Research Content
### Generated Tactical Diagrams
[AI-generated whiteboard diagrams showing key tactical concepts]

### Instructional Images
[Skill demonstration images and exercise diagrams]

### Supporting Visuals
[Equipment, safety, and contextual images for enhanced understanding]

## Integrated Recommendations
### Age-Appropriate Implementation
[Specific recommendations for target age group]

### Team-Specific Adaptations
[If team context available - personalized recommendations]

### Progressive Development Path
[Skill progression and next-step recommendations]

## Source Attribution
- Thunder Playbook Sources: [List of source files referenced]
- External Sources: [Exa research results and credible web sources]
- Video Sources: [YouTube channels and video URLs with quality scores]
- Research Methodology: [Approach used and validation process]

## Content Creation Ready
- Drafting Priority: [High/Medium/Low based on research quality]
- UX Guidelines Compliance: [Age-appropriate content confirmed]
- Team Personalization: [Available context for customization]
- Safety Validation: [All safety considerations documented]
```

## Enhanced Research Capabilities

### Adaptive Research Depth
```
Basic Research (Default):
- 3-5 Thunder Playbook source files
- 3-5 Exa web search results
- Age-appropriate filtering applied
- 15-20 minute research process

Comprehensive Research:
- 8-10 Thunder Playbook source files
- 8-10 Exa web search results with deep analysis
- Cross-reference validation between sources
- Team context integration throughout
- 30-40 minute research process

Deep Analysis Research:
- Complete Thunder Playbook source file analysis
- Exa deep researcher AI-powered comprehensive analysis
- Multiple coaching methodology comparison
- Advanced team personalization
- 45-60 minute research process with AI synthesis
```

### Source Credibility Validation
- **Thunder Playbook Sources**: Pre-validated expert hockey knowledge
- **External Sources**: Filter for established coaching organizations, certified programs
- **Cross-Reference Validation**: Confirm findings across multiple sources
- **Safety Verification**: Ensure all safety recommendations are current and appropriate

## Error Handling and Quality Assurance

### Research Validation
- **Topic Relevance**: Ensure all research directly relates to specified topic
- **Age Appropriateness**: Apply UX Guidelines filtering throughout process
- **Source Quality**: Validate credibility of external research sources
- **Completeness**: Confirm all research areas have been adequately covered

### Integration Testing
- **Database Integration**: Verify Content Library entry creation and population
- **Team Context**: Validate team-specific research adaptations
- **File Access**: Ensure Thunder Playbook source files are accessible and readable
- **MCP Connectivity**: Confirm Exa research tools are functioning properly

### User Experience
- **Progress Tracking**: Use TodoWrite to show research progress clearly
- **Research Quality**: Provide confidence indicators for research findings
- **Next Steps**: Clear guidance on how research feeds into content drafting
- **Source Transparency**: Full attribution for all research sources and methods

## Success Criteria

- ✅ Comprehensive research conducted using both Thunder Playbook and external sources
- ✅ Age-appropriate content filtering applied using UX Guidelines standards
- ✅ Team context integrated throughout research process (if applicable)
- ✅ Full Notion research page created with structured findings
- ✅ Content Library database entry created to track research page
- ✅ Source attribution documented for all research materials
- ✅ Safety considerations thoroughly researched and documented
- ✅ Research page structured for easy reference during content drafting
- ✅ Research quality validated and confidence indicators provided

## Integration with Content Creation Workflow

**Research → Draft Integration:**
- Research findings provide foundation content for `/draft-content` command
- Age-appropriate filtering ensures drafting starts with suitable material
- Team context enables personalized content development
- Source attribution supports credible content creation
- Safety documentation ensures responsible content development

**Quality Assurance Pipeline:**
- Research findings inform content quality standards
- UX Guidelines compliance verified at research stage
- Team-specific adaptations prepared for drafting process
- Safety considerations integrated from research through publication

## Example Usage

```bash
# Basic research for U10 passing skills
/research-hockey "passing fundamentals" U10

# Team-specific research with context integration  
/research-hockey "power play systems" U12 "Thunder Wolves"

# Comprehensive research for complex topic
/research-hockey "defensive zone coverage" U16 comprehensive

# Quick research for practice planning
/research-hockey "skating warm-up activities" U8 basic
```

The research command provides comprehensive, age-appropriate, team-contextualized hockey knowledge that serves as the foundation for high-quality, personalized content creation throughout the entire content development workflow.