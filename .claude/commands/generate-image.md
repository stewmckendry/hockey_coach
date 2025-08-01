---
description: "Generate AI images for hockey coaching content with automatic upload to Cloudinary for easy embedding in Notion and web platforms"
argument-hint: "<prompt> [aspect-ratio] [style] [output-name]"
allowed-tools: ["mcp__stability-ai__stability-ai-generate-image", "mcp__stability-ai__stability-ai-generate-image-sd35", "mcp__cloudinary__upload", "mcp__stability-ai__stability-ai-0-list-resources", "TodoWrite"]
---

# Image Generation and Upload Command

Streamlined workflow for generating AI images using Stability AI and automatically uploading them to Cloudinary, providing public URLs for immediate use in Notion pages, web content, and documentation.

## Image Generation Workflow

### Step 1: Parse Arguments and Initialize
- Extract prompt description from arguments
- Parse optional aspect ratio (default: 16:9 for presentations, 4:5 for diagrams)
- Parse optional style preset (default: digital-art for clean diagrams)
- Generate descriptive filename from prompt if not provided
- Create TodoWrite entry for tracking generation process

### Step 2: Generate Image with Stability AI
**Generation Process:**
```
Image Generation Parameters:
- Prompt: Enhanced with coaching context keywords
- Aspect Ratio: Optimized for intended use case
- Style: Selected based on content type
- Output: Saved to local storage directory
```

**Hockey-Specific Enhancements:**
- Diagram prompts: Add "clean tactical diagram, overhead view" automatically
- Drill illustrations: Include "clear player positions, movement arrows"
- Coaching photos: Add "professional coaching environment"
- Equipment images: Include "detailed view, educational style"

### Step 3: Upload to Cloudinary
**Upload Configuration:**
```
Cloudinary Settings:
- Resource Type: image
- Folder Structure: hockey-coaching/[category]/
- Public ID: Descriptive naming for easy reference
- Tags: Auto-generated from prompt keywords
- Optimization: Automatic format and quality optimization
```

**Folder Organization:**
- `hockey-coaching/drills/` - Practice drill diagrams
- `hockey-coaching/tactics/` - Team systems and formations
- `hockey-coaching/skills/` - Individual skill demonstrations
- `hockey-coaching/equipment/` - Equipment and safety visuals
- `hockey-coaching/team/` - Team photos and events

### Step 4: Return Public URL and Usage Instructions
**Output Format:**
```
✅ Image Generated and Uploaded Successfully!

📸 Image Details:
- Prompt: [User's prompt with enhancements]
- Style: [Selected style preset]
- Dimensions: [Aspect ratio and pixel dimensions]

🔗 Public URL:
https://res.cloudinary.com/dmygzngzd/image/upload/v[version]/[path].png

📋 Usage Examples:
- Notion: <image source="[URL]">Caption</image>
- Markdown: ![Caption]([URL])
- HTML: <img src="[URL]" alt="Caption">

💰 Cost: ~$0.03 (Stability AI generation)
```

## Implementation Details

### Enhanced Prompt Engineering
**Automatic Prompt Improvements:**
```
For Tactical Diagrams:
- Add: "overhead view, ice rink visible, clear player positions"
- Include: "movement arrows, tactical annotations"
- Style: "clean diagram style, high contrast"

For Skill Demonstrations:
- Add: "side view, proper technique visible"
- Include: "step-by-step progression markers"
- Style: "educational illustration style"

For Coaching Scenes:
- Add: "professional coaching environment"
- Include: "age-appropriate players, proper equipment"
- Style: "photographic or digital-art"
```

### Error Handling
```
If image generation fails:
  "Image generation failed: [specific error]
   
   This may be due to:
   - Invalid prompt content
   - API quota exceeded
   - Network connectivity
   
   Try: Simplifying prompt or checking API status"

If Cloudinary upload fails:
  "Upload failed: [specific error]
   
   Local image saved at: [local path]
   
   Options:
   1. Retry upload
   2. Use local file
   3. Check Cloudinary credentials"

If both MCP servers unavailable:
  "Image generation services unavailable.
   
   Please check:
   - MCP server status: claude mcp list
   - API credentials in configuration
   - Restart Claude Code if needed"
```

### Age-Appropriate Adaptations
**U8-U10 Images:**
- Bright, colorful, cartoon-friendly styles
- Simple compositions with clear focal points
- Fun, engaging visual elements
- Safety equipment prominently displayed

**U12-U14 Images:**
- More realistic but still approachable
- Technical details with clear labels
- Progressive skill demonstrations
- Team-oriented compositions

**U16+ Images:**
- Professional, technical diagrams
- Complex tactical formations
- Performance-focused imagery
- Strategic depth visualization

## Advanced Features

### Batch Image Generation
**Multiple Images from Single Command:**
```
For creating image series:
1. Parse multiple prompts from input
2. Generate images with consistent style
3. Upload with sequential naming
4. Return all URLs in organized format
```

### Image Variations
**Creating Multiple Versions:**
- Generate base image
- Create variations with different angles/styles
- Upload all versions for selection
- Provide comparison view URLs

### Integration with Other Commands

**Research Command Enhancement:**
```
When /research-hockey completes:
- Identify key concepts for visualization
- Generate relevant diagrams automatically
- Include URLs in research summary
```

**Draft Content Enhancement:**
```
When /draft-content includes tactics/drills:
- Generate supporting diagrams
- Embed URLs directly in content
- Update Content Library with image references
```

## Usage Examples

### Basic Usage
```bash
# Simple drill diagram
/generate-image "hockey passing drill with 3 players in triangle formation"

# Tactical formation with specific style
/generate-image "2-1-2 power play formation diagram" 4:5 digital-art

# Coaching demonstration photo
/generate-image "youth hockey coach demonstrating proper stick grip" 3:2 photographic

# Equipment safety illustration  
/generate-image "proper hockey helmet fitting for youth players" 1:1 educational
```

### Advanced Usage
```bash
# Complex tactical diagram with custom naming
/generate-image "neutral zone trap 1-3-1 formation with forechecking routes" 16:9 digital-art "nz-trap-131"

# Series generation for skill progression
/generate-image "wrist shot technique 4-step progression" 4:5 line-art "wrist-shot-steps"

# Team photo style with specific parameters
/generate-image "U12 hockey team celebrating goal" 16:9 photographic "team-celebration"
```

## Cost Management

### Usage Tracking
```
Per-Session Tracking:
- Images generated: [count]
- Total cost: $[amount]
- Remaining budget: $[amount]
- Cost per image: ~$0.03
```

### Budget Alerts
```
At 80% of budget ($16 of $20):
  "⚠️ Budget Alert: 80% of monthly budget used
   
   Remaining: $4.00 (~133 images)
   Consider: Prioritizing essential images"

At 100% of budget:
  "❌ Budget Limit Reached
   
   Monthly limit of $20 reached.
   Images generated this month: [count]
   
   Options:
   1. Wait for next billing cycle
   2. Increase budget limit
   3. Use existing images"
```

## Success Metrics

- ✅ Image generated in <30 seconds
- ✅ Cloudinary upload completed successfully
- ✅ Public URL immediately accessible
- ✅ Proper folder organization maintained
- ✅ Cost tracking accurate and visible
- ✅ Integration with Notion formatting provided
- ✅ Error handling comprehensive
- ✅ Age-appropriate style selection

## Quality Assurance

### Image Validation
- Verify appropriate content generation
- Check resolution and dimensions
- Validate style matches intent
- Ensure hockey-specific accuracy

### URL Accessibility
- Test public URL immediately
- Verify HTTPS secure access
- Confirm CDN distribution
- Check mobile responsiveness

The generate-image command provides a seamless workflow for creating professional hockey coaching visuals with automatic cloud hosting, enabling immediate use across all content creation workflows.