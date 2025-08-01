---
description: "Search for high-quality hockey coaching videos with age-appropriate filtering and safety validation"
argument-hint: "<topic> <age-group> [quality-level] [max-results]"
allowed-tools: ["mcp__youtube__search_videos", "mcp__youtube__get_video", "mcp__youtube__get_transcript", "mcp__notion-remote__search", "mcp__notion-remote__create-pages", "mcp__notion-remote__update-page", "TodoWrite"]
---

# Search Hockey Videos Command

Intelligent YouTube video search with hockey-specific quality validation, age-appropriate filtering, and safety guardrails for seamless integration into Notion content creation.

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

## Search and Validation Workflow

### Step 1: Parse Arguments and Initialize
- Extract topic, age group, quality level (basic/standard/premium), max results
- Default: standard quality, 5 results max
- Create TodoWrite list for search process tracking
- Load age-appropriate content standards from UX Guidelines

### Step 2: Construct Smart Search Queries
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

### Step 3: Execute YouTube Search
- Use `mcp__youtube__search_videos` with constructed query
- Request 2x desired results to account for filtering
- Capture video IDs, titles, channels, durations, view counts
- Sort by relevance and view count combination

### Step 4: Quality and Safety Validation
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

### Step 5: Age-Appropriate Filtering
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

### Step 6: Create Curated Results
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

### Step 7: Integration with Draft Workflow
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

### Search Failures
- Fallback to broader search terms
- Suggest alternative search queries
- Provide manual search guidance

### No Quality Results
- Explain filtering criteria
- Suggest adjusting parameters
- Offer to search without strict filtering

### API Limitations
- Handle rate limiting gracefully
- Cache results when possible
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

- ✅ 90%+ search results meet quality standards
- ✅ 100% inappropriate content filtered
- ✅ Age-appropriate validation on all results  
- ✅ Clear quality scoring for each video
- ✅ Seamless integration with draft workflow
- ✅ Safety considerations documented
- ✅ Trusted source prioritization
- ✅ Transcript analysis when available

## Output Format

```
🎥 Hockey Video Search Results: [Topic] for [Age Group]

Found 5 high-quality coaching videos:

1. **[Video Title]** (Premium ⭐⭐⭐)
   - Channel: [Trusted Channel Name]
   - Duration: 6:42
   - Key Points: Proper stance, weight transfer, edge control
   - Safety: Ensure proper protective equipment
   - 🔗 [View Video](url)

2. **[Video Title]** (Standard ⭐⭐)
   - Channel: [Coaching Channel]
   - Duration: 8:15
   - Key Points: Progressive drill sequence, common mistakes
   - Age Note: Perfect complexity for U10
   - 🔗 [View Video](url)

[Additional results...]

📊 Search Quality Summary:
- Videos screened: 12
- Quality passed: 5
- Trusted channels: 3/5
- Average quality: Standard+

These results are ready for integration into your Notion content!
```