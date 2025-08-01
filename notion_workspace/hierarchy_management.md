# Notion Workspace Hierarchy Management System

## 🏗️ Automated Hierarchy Placement

**Goal**: When Claude Code creates new pages through slash commands, automatically determine correct parent-child relationships and place content in appropriate workspace location.

---

## 📊 Hierarchy Decision Matrix

### Content Type → Parent Page Mapping

| Content Type | Parent Page | Database Filter | Reasoning |
|--------------|-------------|-----------------|-----------|
| **Practice Plan** | `📋 Practice Plans` | Content Type = "Practice Plan" | Organized practice planning content |
| **Drill Instructions** | `🥅 Skills & Drills` → `Individual Skills` | Content Type = "Drill Instructions" | Skill-focused drill library |
| **Team Systems** | `🥅 Skills & Drills` → `🎯 Team Systems & Tactics` | Content Type = "Team Systems" | Strategic and tactical content |
| **Concept Explanation** | `🎓 Hockey Education` | Content Type = "Concept Explanation" | Educational content for players/parents |
| **Team Context** | `🏒 Team Home` | Content Type = "Team Context" | Team-specific information |

### Age-Specific Sub-Organization

| Age Group | Additional Hierarchy Level | Example Path |
|-----------|---------------------------|--------------|
| **U8-U10** | `Fundamentals` subfolder | `🥅 Skills & Drills` → `Individual Skills` → `🥅 Fundamentals (U8-U10)` |
| **U10-U12** | `Intermediate Skills` subfolder | `🥅 Skills & Drills` → `Individual Skills` → `⚡ Intermediate Skills (U10-U12)` |
| **U12+** | `Advanced Development` subfolder | `🥅 Skills & Drills` → `Individual Skills` → `🏆 Advanced Development (U12+)` |

### Skill Category Sub-Organization

| Skill Category | Parent Section | Specific Location |
|----------------|----------------|-------------------|
| **Skating** | `Individual Skills` | `Skating Fundamentals` |
| **Passing** | `Individual Skills` | `Passing & Receiving` |
| **Shooting** | `Individual Skills` | `Shooting Development` |
| **Systems** | `Team Systems & Tactics` | Based on system type |
| **Goaltending** | `Individual Skills` | `Goaltending Skills` |

---

## 🤖 Claude Code Decision Logic

### Step 1: Content Analysis
```javascript
// Pseudo-code for Claude Code's decision process
function determineHierarchy(contentData) {
    const { contentType, ageGroups, skillCategories, title } = contentData;
    
    // Primary placement by content type
    let parentPath = getContentTypeParent(contentType);
    
    // Age-specific sub-organization
    if (ageGroups.length === 1) {
        parentPath += getAgeSpecificPath(ageGroups[0]);
    }
    
    // Skill-specific sub-organization
    if (skillCategories.length === 1) {
        parentPath += getSkillSpecificPath(skillCategories[0]);
    }
    
    return parentPath;
}
```

### Step 2: Parent Page Resolution
```javascript
function getContentTypeParent(contentType) {
    const mapping = {
        'Practice Plan': '/🏒 Team Home/📋 Practice Plans',
        'Drill Instructions': '/🏒 Team Home/🥅 Skills & Drills/Individual Skills',
        'Team Systems': '/🏒 Team Home/🥅 Skills & Drills/🎯 Team Systems & Tactics',
        'Concept Explanation': '/🏒 Team Home/🎓 Hockey Education',
        'Team Context': '/🏒 Team Home'
    };
    return mapping[contentType] || '/🏒 Team Home';
}
```

### Step 3: MCP Tool Integration
```javascript
// When creating new page, Claude Code will:
async function createContentWithHierarchy(contentData) {
    // 1. Analyze content to determine placement
    const hierarchyPath = determineHierarchy(contentData);
    
    // 2. Find or create parent page
    const parentPageId = await findOrCreateParentPage(hierarchyPath);
    
    // 3. Create page with proper parent relationship
    const newPage = await mcp_notion_remote_create_pages({
        parent: { page_id: parentPageId },  // ← KEY: Specify parent
        pages: [{
            properties: { title: contentData.title },
            content: contentData.content
        }]
    });
    
    // 4. Update parent page navigation if needed
    await updateParentNavigation(parentPageId, newPage);
    
    return newPage;
}
```

---

## 📋 Required Parent Page Structure

### Root Structure Creation
When setting up initial workspace, Claude Code should create this structure:

```
🏒 Team Home (Root)
├── 📋 Practice Plans
│   ├── 🥅 U8-U10 Practices
│   ├── ⚡ U10-U12 Practices
│   └── 🏆 U12+ Practices
├── 🥅 Skills & Drills
│   ├── Individual Skills
│   │   ├── 🥅 Fundamentals (U8-U10)
│   │   ├── ⚡ Intermediate Skills (U10-U12)
│   │   ├── 🏆 Advanced Development (U12+)
│   │   ├── Skating Fundamentals
│   │   ├── Passing & Receiving
│   │   ├── Shooting Development
│   │   └── Goaltending Skills
│   └── 🎯 Team Systems & Tactics
│       ├── Forechecking Systems
│       ├── Defensive Coverage
│       ├── Power Play
│       └── Penalty Kill
├── 🎓 Hockey Education
│   ├── Rules & Regulations
│   ├── Safety Guidelines
│   └── Development Concepts
└── 📞 Contact & Info
```

---

## 🔧 Implementation in Slash Commands

### Enhanced Content Creation Flow

#### For `/new-page` Command:
```bash
User: "/new-page practice plan for U10 skating skills"

Claude Code Process:
1. Parse: contentType="Practice Plan", ageGroup="U10", skill="Skating"
2. Determine hierarchy: /🏒 Team Home/📋 Practice Plans/🥅 U8-U10 Practices
3. Find parent page ID for "🥅 U8-U10 Practices"
4. Create page with parent relationship
5. Update parent page navigation
6. Add to Content Library database with proper metadata
```

#### For `/draft-content` Command:
```bash
User: "/draft-content drill for passing fundamentals for U12"

Claude Code Process:
1. Parse: contentType="Drill Instructions", skill="Passing", ageGroup="U12"
2. Determine hierarchy: /🏒 Team Home/🥅 Skills & Drills/Individual Skills/Passing & Receiving
3. Create content in correct location
4. Link to parent navigation
5. Database entry with proper categorization
```

---

## 🎯 Hierarchy Guidelines Reference

### Content Placement Rules

#### Rule 1: Content Type Priority
- **Practice Plans** → Always under Practice Plans section
- **Drills** → Always under Skills & Drills → Individual Skills
- **Systems** → Always under Skills & Drills → Team Systems & Tactics
- **Education** → Always under Hockey Education

#### Rule 2: Age Group Sub-Organization
- **Single Age Group** → Place in age-specific subfolder
- **Multiple Age Groups** → Place in parent category with age tags
- **All Ages** → Place in parent category root

#### Rule 3: Skill Category Sub-Organization
- **Single Skill Focus** → Place in skill-specific subfolder
- **Multiple Skills** → Place in parent category with skill tags
- **General Content** → Place in category root

#### Rule 4: Navigation Updates
- **New Page Created** → Add link to parent page navigation section
- **Parent Page Missing** → Create parent page structure automatically
- **Database View** → Update filtered views to include new content

---

## 🔍 Parent Page Resolution Algorithm

### Step-by-Step Process:

#### 1. Content Analysis
```javascript
function analyzeContent(userInput, contentData) {
    return {
        contentType: extractContentType(userInput, contentData),
        primaryAgeGroup: extractPrimaryAge(contentData.ageGroups),
        primarySkill: extractPrimarySkill(contentData.skillCategories),
        complexity: determineComplexity(contentData.difficultyLevel)
    };
}
```

#### 2. Hierarchy Path Construction
```javascript
function buildHierarchyPath(analysis) {
    let path = ['/🏒 Team Home'];
    
    // Add content type level
    path.push(getContentTypeSection(analysis.contentType));
    
    // Add specialization level if applicable
    if (analysis.contentType === 'Drill Instructions') {
        path.push('Individual Skills');
        if (analysis.primarySkill) {
            path.push(getSkillSection(analysis.primarySkill));
        }
    }
    
    // Add age-specific level if single age group
    if (analysis.primaryAgeGroup && isSpecificAge(analysis.primaryAgeGroup)) {
        path.push(getAgeSection(analysis.primaryAgeGroup));
    }
    
    return path.join('/');
}
```

#### 3. Parent Page Creation/Location
```javascript
async function ensureParentStructure(hierarchyPath) {
    const pathParts = hierarchyPath.split('/').filter(p => p);
    let currentParent = null;
    
    for (let i = 0; i < pathParts.length; i++) {
        const pageName = pathParts[i];
        const existingPage = await findPageByName(pageName, currentParent);
        
        if (!existingPage) {
            // Create missing parent page
            const newParent = await createNavigationPage(pageName, currentParent);
            currentParent = newParent.id;
        } else {
            currentParent = existingPage.id;
        }
    }
    
    return currentParent;
}
```

---

## 📊 Implementation Success Criteria

### Automated Hierarchy Management
- [ ] New pages automatically placed in correct parent structure
- [ ] Parent pages created automatically if missing
- [ ] Navigation links updated when new content added
- [ ] Database filters properly categorize content

### User Experience
- [ ] Logical content organization that matches hockey coaching workflow
- [ ] Easy navigation between related content
- [ ] Age-appropriate content grouped together
- [ ] Skill-specific content easily discoverable

### Integration
- [ ] Works seamlessly with slash commands
- [ ] Maintains UX guidelines compliance
- [ ] Database relationships preserved
- [ ] Public sharing respects hierarchy structure

This hierarchy management system ensures that all new content created through Claude Code slash commands will be automatically organized in a logical, navigable structure that grows naturally with content creation.