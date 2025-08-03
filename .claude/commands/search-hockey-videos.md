---
description: "Search for high-quality hockey coaching videos with age-appropriate filtering and safety validation using YouTube and Hockey MCP sources"
argument-hint: "<topic> <age-group> [quality-level] [max-results]"
allowed-tools: ["mcp__youtube__search_videos", "mcp__youtube__get_video", "mcp__youtube__get_transcript", "mcp__hockey-coaching__search_hockey_videos", "mcp__hockey-coaching__search_hockey_dryland_videos", "mcp__notion-remote__search", "mcp__notion-remote__create-pages", "mcp__notion-remote__update-page", "TodoWrite"]
---

# Search Hockey Videos Command

Comprehensive hockey video search combining YouTube API and Hockey MCP's curated video collections for maximum coverage of quality coaching content with age-appropriate filtering and safety validation.

## Quality Assessment Framework

### Hockey Coaching Video Quality Criteria
```
High Quality Indicators:
- Certified coaches or reputable hockey organizations
- Clear visual demonstration of techniques
- Age-appropriate language and complexity
- Professional production quality
- Positive coaching methodology
- Safety emphasis

Red Flags (Automatic Exclusion):
- Inappropriate language or content
- Dangerous techniques without safety warnings
- Poor video/audio quality affecting learning
- Misleading or incorrect technique instruction
- Overly aggressive or negative coaching style
- Non-educational fight compilations
```

### Trusted Hockey Channel Whitelist
```
Priority Sources:
- USA Hockey official channels
- Hockey Canada channels
- NHL team development channels
- iTrain Hockey
- HowToHockey
- Coach Jeremy channels
- Professional coaching certification bodies
- University/college hockey programs
```

## Dual-Source Search Strategy

### Video Sources
1. **Hockey MCP Collections** (Primary - Curated Content)
   - `search_hockey_videos`: 1,159 instructional video clips with timestamps
   - `search_hockey_dryland_videos`: 939 off-ice training demonstrations
   - Pre-validated for coaching quality and safety
   - Includes teaching points and skill metadata

2. **YouTube API** (Secondary - Expanded Coverage)
   - Live search for latest content
   - Broader coverage of emerging techniques
   - Access to new channels and creators
   - Real-time availability checking

## Search and Validation Workflow

### Step 1: Parse Arguments and Initialize
- Extract topic, age group, quality level (basic/standard/premium), max results
- Default: standard quality, 5 results max
- Create TodoWrite list for search process tracking
- Load age-appropriate content standards from UX Guidelines
- Determine if topic is on-ice or off-ice training

### Step 2: Search Hockey MCP Collections First
```
Priority Search Order:
1. For on-ice topics: Use search_hockey_videos
2. For off-ice/dryland: Use search_hockey_dryland_videos
3. Apply age group and skill filters
4. Collect pre-validated results with metadata

Benefits of MCP Search:
- Pre-curated coaching content
- Validated teaching points included
- Timestamp segments for specific techniques
- No additional quality validation needed
```

### Step 3: Construct Smart YouTube Search Queries
```
Query Construction Pattern:
- Base: "[topic] hockey [age-group] coaching tutorial"
- Enhanced: Add "drill", "technique", "teaching", "youth"
- Filter: Exclude "fight", "hit", "injury" for younger groups
- Duration: Prefer 3-10 minute videos for skill instruction

Examples:
- U8: "passing fundamentals hockey U8 beginner drill fun"
- U12: "defensive positioning hockey U12 coaching technique"
- U16: "power play systems hockey U16 advanced tactics"
```

### Step 4: Execute YouTube Search (Complementary)
- Use `mcp__youtube__search_videos` with constructed query
- Request enough results to complement MCP findings
- Focus on filling gaps not covered by MCP collections
- Capture video IDs, titles, channels, durations, view counts
- Avoid duplicates already found in MCP search

### Step 5: Merge and Deduplicate Results
```
Result Merging Strategy:
1. Prioritize MCP results (pre-validated quality)
2. Add YouTube results that aren't duplicates
3. Balance sources based on quality scores
4. Maintain requested max_results limit

Deduplication:
- Match by video ID when available
- Match by title + channel for similar content
- Keep highest quality version if duplicates found
```

### Step 6: Quality and Safety Validation (YouTube Results Only)
```
For each video result:
1. Channel Validation:
   - Check against trusted channel whitelist (priority boost)
   - Verify channel has coaching/educational focus
   - Check channel subscriber count (>1000 preferred)

2. Title and Description Analysis:
   - Scan for quality indicators (coaching, teaching, drill)
   - Check for red flag keywords
   - Verify age-appropriate terminology

3. Metadata Assessment:
   - View count threshold (>1000 for credibility)
   - Like/dislike ratio if available
   - Published date (prefer recent for safety standards)
   - Duration check (3-20 minutes optimal)

4. Transcript Quick Scan (if available):
   - Use `mcp__youtube__get_transcript` for top candidates
   - Check for inappropriate language
   - Verify coaching instructions present
   - Assess explanation clarity
```

### Step 7: Age-Appropriate Filtering
```
U8 (8-9 years):
- Maximum 5-minute videos preferred
- Must have visual demonstrations
- Simple, positive language required
- Fun and game-based approaches prioritized

U10 (9-10 years):
- 5-10 minute videos optimal
- Clear step-by-step instruction
- Basic skill focus, no complex systems
- Encouraging coaching tone required

U12 (11-12 years):
- 5-15 minute videos acceptable
- Can include basic tactical concepts
- Technical skill development focus
- Clear progression sequences

U14+ (13+ years):
- 10-20 minute videos acceptable
- Advanced systems and tactics allowed
- Competition-focused content appropriate
- Mental game elements included
```

### Step 8: Create Curated Results
```
Video Result Structure:
{
  "title": "Clear, descriptive title",
  "channel": "Verified coaching channel",
  "duration": "MM:SS format",
  "url": "https://youtube.com/watch?v=...",
  "thumbnail": "High-quality thumbnail URL",
  "quality_score": "Premium/Standard/Basic",
  "age_appropriate": true,
  "key_points": ["Extracted from transcript"],
  "safety_notes": ["Any special considerations"],
  "coaching_tips": ["Best practices from video"]
}
```

### Step 9: Integration with Draft Workflow
- Store curated video results in temporary context
- Make results available to draft-notion-page command
- Include quality scores and safety validations
- Prepare embed codes for Notion integration

## Implementation Details

### Quality Scoring Algorithm
```
Premium (90-100 points):
- Trusted channel: +40 points
- High view count (>10k): +20 points
- Recent publication (<2 years): +10 points
- Has captions/transcript: +10 points
- Optimal duration: +10 points

Standard (70-89 points):
- Known coaching channel: +30 points
- Moderate views (1k-10k): +15 points
- Clear audio/video: +15 points
- Educational focus: +10 points

Basic (50-69 points):
- Minimum quality threshold met
- Safety validation passed
- Age-appropriate content confirmed
```

### Safety Validation Rules
```
Automatic Rejection:
- Any profanity in title/description
- Violence-focused content
- Injury footage without educational context
- Non-coaching entertainment videos
- Copyright-flagged content

Warning Flags (require review):
- Checking/hitting instruction for U12 and under
- Advanced tactics for younger age groups
- Equipment modifications
- Non-standard technique variations
```

## Error Handling

### MCP Collection Errors
```
If hockey MCP unavailable:
  "Hockey MCP collections not accessible.
   Proceeding with YouTube-only search.
   
   To fix: Check MCP server status with /mcp-test"

If no MCP results found:
  "No videos found in Hockey MCP for '[topic]'.
   Expanding search to YouTube for broader coverage."
```

### YouTube Search Failures
- Fallback to broader search terms
- Suggest alternative search queries
- Provide manual search guidance

### No Quality Results
- Explain filtering criteria from both sources
- Suggest adjusting parameters
- Show results from either source if available

### API Limitations
- Handle rate limiting gracefully
- Prioritize MCP results when YouTube limited
- Provide partial results if needed

## Integration Examples

### Standalone Search
```bash
# Basic search for U10 skating drills
/search-hockey-videos "forward skating" U10

# Premium quality search with more results
/search-hockey-videos "passing drills" U12 premium 10

# Quick search for practice ideas
/search-hockey-videos "fun warm-up games" U8 basic 3
```

### Draft Workflow Integration
```bash
# Search and store results for drafting
/search-hockey-videos "defensive zone coverage" U14
# Results automatically available to:
/draft-notion-page "practice plan" U14
```

## Success Metrics

- ✅ Dual-source coverage (MCP + YouTube)
- ✅ 90%+ search results meet quality standards
- ✅ 100% inappropriate content filtered
- ✅ Age-appropriate validation on all results  
- ✅ Clear source attribution (MCP vs YouTube)
- ✅ Seamless integration with draft workflow
- ✅ Safety considerations documented
- ✅ Pre-validated MCP content prioritized
- ✅ No duplicate results between sources
- ✅ Teaching points extracted from both sources

## Enhanced Result Structure

### MCP Collection Results
```
MCP Video Result:
{
  "source": "hockey_mcp",
  "collection": "hockey_videos" | "hockey_dryland_videos",
  "title": "Video title from collection",
  "video_id": "YouTube ID",
  "url": "https://youtube.com/watch?v=...",
  "timestamps": {
    "start": "1:23",
    "end": "4:56"
  },
  "teaching_points": ["Pre-validated teaching points"],
  "skills": ["skating", "passing"],
  "complexity": "beginner|intermediate|advanced",
  "transcript_segment": "Relevant transcript excerpt",
  "quality_score": "Premium (pre-validated)"
}
```

## Output Format

```
🎥 Hockey Video Search Results: [Topic] for [Age Group]

📚 From Hockey MCP Collections (Pre-validated):

1. **[Video Title]** (Premium ⭐⭐⭐) [MCP]
   - Source: Hockey Videos Collection
   - Duration: 3:33 (Full video: 12:45)
   - Teaching Points: Weight transfer, edge control, knee bend
   - Skills: Forward skating, balance
   - 🔗 [View Segment](url#t=1m23s)

2. **[Video Title]** (Premium ⭐⭐⭐) [MCP]
   - Source: Dryland Videos Collection  
   - Duration: 2:15 segment
   - Teaching Points: Core stability, explosive movement
   - Equipment: Resistance bands, cones
   - 🔗 [View Video](url)

🔍 From YouTube Search (Quality Validated):

3. **[Video Title]** (Standard ⭐⭐)
   - Channel: [Trusted Channel Name]
   - Duration: 8:42
   - Key Points: Progressive skill development
   - Safety: Proper warm-up emphasized
   - 🔗 [View Video](url)

[Additional results...]

📊 Search Quality Summary:
- MCP Collection hits: 3
- YouTube additions: 2
- Total screened: 15
- Quality passed: 5
- Average quality: Premium-

These results combine curated content from Hockey MCP with fresh YouTube discoveries!
```