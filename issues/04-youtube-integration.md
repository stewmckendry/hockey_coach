# Issue 4: YouTube Integration & Video Curation

## Overview
Implement comprehensive YouTube integration for hockey team content creation, including video search, curation, transcript extraction, and embedding workflows. This will enable content creators to easily find, evaluate, and integrate relevant hockey instructional videos into team materials.

## Objectives
- Set up YouTube MCP server for video search and transcript extraction
- Create video curation workflows with quality assessment criteria
- Build hockey-specific video libraries organized by skill and age group
- Establish embedding standards for Notion pages
- Develop video content validation and safety protocols

## YouTube MCP Server Setup

### Installation Requirements
```bash
# Primary option: YouTube transcript server
claude mcp add youtube -s user -- npx -y @sinco-lab/mcp-youtube-transcript

# Alternative: Full YouTube API server (requires API key)
claude mcp add youtube-api -s user -- npx -y bendelpino-youtube-mcp
```

### Configuration
**File Location**: `~/.claude.json`

**Basic Configuration (Transcript Only)**:
```json
{
  "mcpServers": {
    "youtube": {
      "command": "npx",
      "args": ["-y", "@sinco-lab/mcp-youtube-transcript"]
    }
  }
}
```

**Advanced Configuration (with API Key)**:
```json
{
  "mcpServers": {
    "youtube-full": {
      "command": "npx",
      "args": ["-y", "bendelpino-youtube-mcp"],
      "env": {
        "YOUTUBE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Available Tools
- **Video Search**: Search YouTube for hockey-related content
- **Transcript Extraction**: Get text transcripts from videos
- **Video Metadata**: Retrieve title, description, duration, and channel info
- **Content Analysis**: AI-powered content evaluation for appropriateness

## Video Curation Workflows

### Content Discovery Process
```python
# Pseudo-workflow for video discovery
def discover_hockey_videos(skill_topic, age_group):
    # 1. Structured search queries
    primary_query = f"{skill_topic} hockey drill {age_group}"
    secondary_queries = [
        f"{skill_topic} hockey tutorial kids",
        f"{skill_topic} hockey coaching {age_group}",
        f"how to teach {skill_topic} hockey youth"
    ]
    
    # 2. Search multiple channels
    trusted_channels = [
        "USA Hockey", "Hockey Canada", "Ice Hockey Systems",
        "HockeyShot Training", "iTrain Hockey", "Coach Jeremy"
    ]
    
    # 3. Combine search results
    videos = []
    for query in [primary_query] + secondary_queries:
        results = youtube_search(query, max_results=10)
        videos.extend(filter_by_quality_criteria(results))
    
    # 4. Prioritize trusted sources
    curated_videos = prioritize_trusted_sources(videos, trusted_channels)
    
    return curated_videos
```

### Quality Assessment Criteria

#### Technical Quality Standards
- **Video Resolution**: 720p minimum, 1080p preferred
- **Audio Quality**: Clear narration without background noise
- **Duration**: 30 seconds to 10 minutes (age-appropriate attention spans)
- **Production Value**: Professional or semi-professional presentation
- **Upload Date**: Prefer content from last 3 years for current techniques

#### Content Quality Standards
- **Accuracy**: Techniques align with current hockey best practices
- **Safety**: Proper safety equipment and protocols demonstrated
- **Age Appropriateness**: Content suitable for target age group
- **Educational Value**: Clear instructional content with learning objectives
- **Demonstration Quality**: Multiple angles, slow motion where helpful

#### Channel Credibility Assessment
```markdown
**Tier 1 (Highest Credibility)**:
- USA Hockey official channels
- Hockey Canada official channels
- Professional team training content
- Certified coaching organization content

**Tier 2 (High Credibility)**:
- Established hockey training companies
- Former professional players with coaching credentials
- Recognized hockey skills instructors
- Equipment manufacturer instructional content

**Tier 3 (Medium Credibility)**:
- Local hockey organizations
- Independent coaches with good production value
- Player development specialists
- Hockey camps and academies

**Tier 4 (Use with Caution)**:
- Individual players without coaching background
- Content with limited production quality
- Unverified training methods
- Marketing-focused content
```

### Content Safety Protocol

#### Age-Appropriate Content Validation
```python
def validate_content_safety(video_metadata, target_age):
    safety_checks = {
        "language": check_appropriate_language(video_metadata.transcript),
        "checking": assess_checking_content(video_metadata, target_age),
        "equipment": verify_safety_equipment(video_metadata),
        "instruction": validate_progressive_instruction(video_metadata),
        "environment": check_safe_environment(video_metadata)
    }
    
    return all(safety_checks.values())

def check_appropriate_language(transcript):
    # Screen for inappropriate language
    flagged_words = ["list of inappropriate terms"]
    return not any(word in transcript.lower() for word in flagged_words)

def assess_checking_content(metadata, age_group):
    # Ensure checking content is age-appropriate
    if age_group in ["U8", "U10"]:
        return "checking" not in metadata.title.lower()
    return True  # Checking content OK for U12+
```

#### Content Moderation Checklist
- [ ] **Language Appropriateness**: No profanity or inappropriate language
- [ ] **Violence Level**: Age-appropriate level of contact/checking
- [ ] **Safety Equipment**: Proper equipment demonstrated throughout
- [ ] **Instruction Quality**: Clear, safe teaching progression
- [ ] **Channel Reputation**: Verified credible source
- [ ] **Content Freshness**: Recent content with current techniques

## Hockey Video Library Organization

### Skill-Based Categories
```
Hockey Video Library/
├── 🥅 Skating Fundamentals/
│   ├── U8-U10: Basic Skating
│   ├── U10-U12: Stride Development  
│   ├── U12+: Advanced Techniques
│   └── Goalie Skating
├── 🏒 Stick Skills/
│   ├── Basic Stickhandling
│   ├── Passing Techniques
│   ├── Receiving & Control
│   └── Advanced Moves
├── 🎯 Shooting/
│   ├── Wrist Shots
│   ├── Slap Shots
│   ├── Quick Release
│   └── Scoring Techniques
├── 🛡️ Defense/
│   ├── Positioning
│   ├── Stick Checking
│   ├── Body Positioning
│   └── Transition Play
├── 🧠 Game Concepts/
│   ├── Offensive Systems
│   ├── Defensive Systems
│   ├── Special Teams
│   └── Game Situations
└── 🏃‍♀️ Conditioning/
    ├── On-Ice Fitness
    ├── Off-Ice Training
    ├── Agility & Speed
    └── Injury Prevention
```

### Video Database Schema
```json
{
  "database_name": "Hockey Video Library",
  "properties": {
    "Video Title": {
      "type": "title",
      "description": "YouTube video title"
    },
    "YouTube URL": {
      "type": "url",
      "description": "Direct link to YouTube video"
    },
    "Skill Category": {
      "type": "select",
      "options": [
        "Skating", "Stick Skills", "Shooting", "Defense", 
        "Game Concepts", "Conditioning", "Goaltending"
      ]
    },
    "Subcategory": {
      "type": "select",
      "options": ["Varies by category"]
    },
    "Age Group": {
      "type": "multi_select",
      "options": ["U8", "U10", "U12", "U14", "U16", "U18", "All Ages"]
    },
    "Skill Level": {
      "type": "select",
      "options": ["Beginner", "Intermediate", "Advanced", "All Levels"]
    },
    "Duration": {
      "type": "number",
      "description": "Video length in minutes"
    },
    "Channel Name": {
      "type": "rich_text",
      "description": "YouTube channel/creator"
    },
    "Credibility Tier": {
      "type": "select",
      "options": ["Tier 1", "Tier 2", "Tier 3", "Tier 4"]
    },
    "Content Quality": {
      "type": "select",
      "options": ["Excellent", "Good", "Fair", "Needs Review"]
    },
    "Safety Approved": {
      "type": "checkbox",
      "description": "Passed safety content review"
    },
    "Transcript Available": {
      "type": "checkbox",
      "description": "Video has transcript for analysis"
    },
    "Key Teaching Points": {
      "type": "rich_text",
      "description": "Main instructional content summary"
    },
    "Equipment Shown": {
      "type": "multi_select",
      "options": [
        "Skates", "Stick", "Helmet", "Pads", "Pucks", "Cones", 
        "Nets", "Special Equipment"
      ]
    },
    "Embed Code": {
      "type": "rich_text",
      "description": "Notion-ready embed code"
    },
    "Related Content": {
      "type": "relation",
      "related_database": "Content Library",
      "description": "Team content that uses this video"
    },
    "Added Date": {
      "type": "created_time"
    },
    "Last Reviewed": {
      "type": "date"
    },
    "Review Notes": {
      "type": "rich_text",
      "description": "Quality assessment and usage notes"
    }
  }
}
```

## Video Integration Workflows

### Search and Curation Workflow
```python
def curate_videos_for_topic(topic, age_group, count=5):
    """Complete workflow for finding and curating videos"""
    
    # 1. Multi-query search
    search_results = comprehensive_video_search(topic, age_group)
    
    # 2. Apply quality filters
    quality_filtered = apply_quality_criteria(search_results)
    
    # 3. Safety validation
    safety_approved = validate_content_safety_batch(quality_filtered, age_group)
    
    # 4. Extract transcripts for analysis
    with_transcripts = extract_transcripts_batch(safety_approved)
    
    # 5. AI-powered content analysis
    analyzed_videos = analyze_instructional_value(with_transcripts, topic)
    
    # 6. Rank by relevance and quality
    ranked_videos = rank_by_relevance(analyzed_videos, topic, age_group)
    
    # 7. Return top results
    return ranked_videos[:count]
```

### Embedding Standards for Notion

#### Embed Code Generation
```python
def generate_notion_embed(youtube_url, title, description=""):
    """Generate standardized embed code for Notion pages"""
    
    # Extract video ID from URL
    video_id = extract_youtube_id(youtube_url)
    
    # Create responsive embed
    embed_code = f"""
<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
  <iframe 
    src="https://www.youtube.com/embed/{video_id}?rel=0&showinfo=0&modestbranding=1"
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
    frameborder="0"
    allowfullscreen
    title="{title}">
  </iframe>
</div>
"""
    
    if description:
        embed_code += f"\n**Video**: {description}"
    
    return embed_code
```

#### Video Integration Template
```markdown
## Video Demonstration 📹
**Title**: [Video title]
**Duration**: [X] minutes
**Source**: [Channel name] ([Credibility tier])

[Embedded video with responsive sizing]

### What to Watch For 👀
- [Key point 1 with timestamp]
- [Key point 2 with timestamp]  
- [Key point 3 with timestamp]

### Discussion Questions 💭
- [Question about technique shown]
- [Question about application]
- [Question about safety/equipment]

### Additional Resources 🔗
- [Link to related video]
- [Link to practice drill]
```

## Content Integration Features

### Transcript Analysis for Content Creation
```python
def analyze_video_transcript(transcript, topic):
    """Extract key teaching points from video transcripts"""
    
    analysis = {
        "key_techniques": extract_technique_mentions(transcript),
        "safety_points": identify_safety_mentions(transcript),
        "common_mistakes": find_mistake_discussions(transcript),
        "progression_steps": identify_skill_progression(transcript),
        "equipment_mentions": extract_equipment_references(transcript)
    }
    
    return analysis

def create_content_from_video(video_data, age_group):
    """Generate drill or concept content based on video analysis"""
    
    transcript_analysis = analyze_video_transcript(
        video_data.transcript, 
        video_data.skill_category
    )
    
    content_template = select_appropriate_template(age_group, "drill")
    
    generated_content = populate_template(
        template=content_template,
        video_insights=transcript_analysis,
        video_embed=video_data.embed_code,
        age_adaptations=get_age_adaptations(age_group, transcript_analysis)
    )
    
    return generated_content
```

### Video Library Maintenance

#### Automated Content Review System
```python
def schedule_video_review():
    """Periodic review of video library for outdated content"""
    
    videos_to_review = get_videos_older_than(months=6)
    
    for video in videos_to_review:
        # Check if video still exists
        if not video_exists(video.youtube_url):
            mark_for_removal(video.id)
            continue
        
        # Check for updated content on same topic
        newer_alternatives = search_newer_videos(
            video.skill_category, 
            video.age_group,
            after_date=video.added_date
        )
        
        if newer_alternatives:
            suggest_updates(video.id, newer_alternatives)
        
        # Mark as reviewed
        update_review_date(video.id)
```

#### Quality Maintenance Checklist
- [ ] **Broken Links**: Check for removed or private videos monthly
- [ ] **Content Freshness**: Review videos older than 1 year
- [ ] **Safety Updates**: Verify safety standards remain current
- [ ] **New Content**: Search for updated content on existing topics
- [ ] **Usage Analytics**: Track which videos are most/least used
- [ ] **Feedback Integration**: Update based on coach/player feedback

## Implementation Specifications

### MCP Integration Points
```python
class YouTubeVideoManager:
    def __init__(self, notion_client, youtube_mcp):
        self.notion = notion_client
        self.youtube = youtube_mcp
        
    async def search_and_curate(self, topic, age_group, count=5):
        # Search YouTube via MCP
        search_results = await self.youtube.search_videos(
            query=f"{topic} hockey drill {age_group}",
            max_results=20
        )
        
        # Process and filter results
        curated = self.apply_curation_criteria(search_results, age_group)
        
        # Store in Notion database
        for video in curated[:count]:
            await self.notion.add_to_video_library(video)
        
        return curated[:count]
    
    async def extract_transcript_insights(self, video_url):
        transcript = await self.youtube.get_transcript(video_url)
        return self.analyze_instructional_content(transcript)
```

### Slash Command Integration
```bash
# New slash commands for video workflows
/find-videos <skill-topic> [age-group] [count]
# Example: /find-videos "wrist shot" U10 3

/curate-library <section>
# Example: /curate-library "skating fundamentals"

/analyze-video <youtube-url>
# Extract teaching points and create content outline

/update-video-library
# Run maintenance and quality checks
```

## Acceptance Criteria

### MCP Server Setup
- [ ] YouTube MCP server installed and configured
- [ ] Video search functionality works reliably
- [ ] Transcript extraction operates correctly
- [ ] Error handling for unavailable videos

### Content Curation
- [ ] Quality assessment criteria applied automatically
- [ ] Safety validation process prevents inappropriate content
- [ ] Credibility ranking system functions properly
- [ ] Age-appropriate filtering works correctly

### Library Organization
- [ ] Video database schema supports all required metadata
- [ ] Skill-based categorization is intuitive and complete
- [ ] Search and filtering work across all criteria
- [ ] Related content linking functions properly

### Integration Features
- [ ] Videos embed properly in Notion pages
- [ ] Transcript analysis extracts meaningful insights
- [ ] Content generation from videos meets quality standards
- [ ] Video library maintenance runs automatically

## Testing Requirements

### Functionality Testing
- Search for videos across different skill categories
- Test transcript extraction with various video types
- Verify safety filtering with edge cases
- Validate embedding in different Notion page contexts

### Content Quality Testing
- Verify age-appropriate content filtering
- Test credibility ranking accuracy
- Validate safety assessment with actual hockey content
- Confirm instructional value analysis works correctly

### Integration Testing
- Test slash command functionality
- Verify Notion database updates work properly
- Test content generation from video analysis
- Validate maintenance workflows

## Timeline Estimate
**Total**: 1-2 hours
- MCP server setup and configuration: 30 minutes
- Curation workflow development: 45 minutes
- Testing and validation: 15 minutes

## Dependencies
- Notion database structure from Issue #3
- UX guidelines from Issue #2 for age-appropriate content
- Slash command system from Issue #1

## Success Metrics
- Video search returns relevant results >90% accuracy
- Safety filtering prevents inappropriate content 100% of the time
- Content creation time reduced by 40% with video integration
- Video library grows to 100+ curated videos within first month
- User engagement with video-enhanced content increases by 60%