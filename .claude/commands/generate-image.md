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
- **Detect content type** from keywords (tactical, dryland, skill, coaching, equipment)
- Parse optional aspect ratio (default: 16:9 for presentations, 4:5 for diagrams)
- Parse optional style preset (auto-selected based on content type if not specified)
- Generate descriptive filename from prompt if not provided
- Create TodoWrite entry for tracking generation process

### Step 1.5: Automatic Prompt Enhancement
**Content Type Detection:**
```
Tactical Keywords: "drill", "play", "formation", "system", "position", "tactic", "strategy"
→ Transform to Whiteboard Style

Dryland Keywords: "dryland", "off-ice", "workout", "exercise", "fitness", "training"
→ Transform to Training Diagram Style

Skill Keywords: "technique", "skill", "demonstration", "how to", "proper form"
→ Transform to Realistic Demonstration Style

Coaching Keywords: "coach", "instruction", "teaching", "explaining"
→ Transform to Coaching Scene Style

Equipment Keywords: "equipment", "gear", "helmet", "stick", "skates"
→ Transform to Product Photography Style
```

**Automatic Style Selection:**
- Tactical Diagrams: `line-art` or `digital-art` for clarity
- Dryland Training: `digital-art` for instructional clarity
- Skill Demonstrations: `photographic` for realism
- Coaching Scenes: `photographic` for authenticity
- Equipment: `photographic` for detail

### Step 2: Generate Image with Stability AI
**Generation Process:**
```
For Tactical Diagrams:
- Method: Use mcp__stability-ai__stability-ai-control-structure
- Base Image: realistic-hockey-whiteboard-base.png (maintains authentic whiteboard look)
- Prompt: Add tactical elements to existing rink layout
- Control Strength: 0.6-0.8 (preserve whiteboard structure, add tactical elements)

For Other Content Types:
- Method: Use mcp__stability-ai__stability-ai-generate-image-sd35
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

### Step 4: Review and Quality Check Generated Image
**Automatic Image Review Process:**
```
1. Read the generated image file using Read tool
2. Analyze image quality against intended content type:
   - Tactical Diagrams: Check for whiteboard aesthetic, simple symbols, clean lines
   - Dryland Training: Verify exercise clarity and instructional value
   - Skill Demonstrations: Confirm realistic hockey context
   - Coaching Scenes: Validate authentic hockey environment
   - Equipment: Check product clarity and detail

3. Quality Assessment Criteria:
   - Content Accuracy: Does it match the intended hockey concept?
   - Style Appropriateness: Does it match the expected format (whiteboard/photo/diagram)?
   - Clarity: Are symbols, positions, and movements clearly visible?
   - Realism: Does it look authentic to hockey coaching context?
   - Simplicity: Is it clean and uncluttered (especially for tactical diagrams)?

4. If quality issues detected:
   - Identify specific problems (too complex, wrong style, unclear symbols)
   - Generate refined prompt addressing the issues
   - Regenerate image with improved prompt
   - Repeat review process (max 2 iterations to control costs)
```

**Quality Issue Examples and Fixes:**
```
Issue: "Generated soccer field instead of hockey rink"
Fix: Add "ice hockey rink" and remove ambiguous terms

Issue: "Too much text and complex graphics on whiteboard"  
Fix: Add "minimal text, simple line drawing, clean markers only"

Issue: "Computer graphics instead of hand-drawn style"
Fix: Add "hand-drawn appearance, slightly imperfect lines, marker sketch"

Issue: "Wrong equipment or setting"
Fix: Specify "hockey equipment, ice rink environment, proper hockey context"
```

### Step 5: Upload to Cloudinary (After Quality Approval)
**Upload Configuration:**
```
Cloudinary Settings:
- Resource Type: image  
- Folder Structure: hockey-coaching/[category]/
- Public ID: Descriptive naming for easy reference
- Tags: Auto-generated from prompt keywords
- Optimization: Automatic format and quality optimization
```

### Step 6: Return Public URL and Usage Instructions
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
For Tactical Diagrams (Drills, Plays, Systems, Formations):
- Detect: Keywords like "drill", "play", "formation", "system", "position", "tactic"
- Use Base Whiteboard: Apply tactical elements to realistic hockey whiteboard base
- Transform to Whiteboard Style:
  - Base Image: Use realistic-hockey-whiteboard-base.png as control structure
  - Add: tactical elements over existing rink layout
  - Player symbols: "letter markers for positions (C, RW, LW, LD, RD, G)"
  - Movement: "hand-drawn arrows for player movement, dotted lines for passes"
  - Style: "coaching diagram aesthetic, maintain whiteboard authenticity"
- Process: Use control-structure mode with realistic whiteboard base for consistency
- Example: "Add tactical elements to hockey whiteboard: [original prompt], 
           position letters (C, RW, LW, LD, RD), movement arrows, maintain rink layout"

For Dryland/Off-Ice Training:
- Detect: Keywords like "dryland", "off-ice", "workout", "exercise", "fitness"
- Transform to Training Diagram:
  - Add: "fitness training diagram, exercise illustration"
  - Include: "gym or training facility background"
  - Style: "clean instructional diagram with exercise positions"
  - Movement: "numbered sequences, motion arrows"
- Example: "Off-ice training exercise diagram showing [original prompt],
           numbered sequence steps, clear body positions, training facility setting"

For Skill Demonstrations:
- Add: "realistic hockey environment, proper technique visible"
- Include: "professional hockey player demonstrating"
- Style: "photographic" for realism

For Coaching Scenes:
- Add: "realistic hockey rink or training facility"
- Include: "authentic hockey equipment and uniforms"
- Style: "photographic" for authenticity

For Equipment/Safety:
- Add: "detailed product photography style"
- Include: "proper lighting, educational context"
- Style: "commercial photography"
```

### Tactical Diagram Legend Standards
**Consistent Symbols for All Whiteboard Diagrams:**
```
Player Position Symbols (Your Team):
- C = Center
- RW = Right Wing  
- LW = Left Wing
- LD = Left Defense
- RD = Right Defense
- G = Goaltender

Opposing Team Symbols:
- X₁, X₂, X₃, X₄, X₅ = Opposing players (numbered)
- X = Generic opposing player
- OG = Opposing goaltender

Coach/Officials:
- COACH = Coach position
- REF = Referee position

Movement Indicators:
- Solid arrows (→) = Player skating/movement
- Dashed arrows (-->) = Pass or puck movement
- Curved arrows (↷) = Turning or pivoting
- Zigzag lines (~) = Stickhandling path
- Double arrows (⟷) = Back and forth movement

Objects:
- Triangle (△) = Cones
- Square (□) = Obstacles/barriers
- Circle with dot (⊙) = Puck
- Double lines (||) = Boards/glass
- Dotted circle = Face-off circle
- X in circle = Player starting position
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