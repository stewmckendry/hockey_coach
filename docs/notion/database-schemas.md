# Notion Database Schemas for Hockey Team Content Management

## Database 1: Team Information

**Purpose**: Central repository for team-specific context and settings

### Properties Schema:
- **Team Name** (Title): Primary identifier for the team
- **Age Group** (Select): U8, U10, U12, U14, U16, U18
- **Season** (Select): Fall, Winter, Spring, Summer, Year-Round
- **Head Coach** (Person): Primary coach contact
- **Assistant Coaches** (People): Multiple coach assignment
- **Team Email** (Email): Official team communication
- **Practice Days** (Multi-select): Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
- **Practice Time** (Rich Text): Standard practice schedule details
- **Home Rink** (Rich Text): Primary practice and game location
- **League** (Select): GTHL, OMHA, ALLIANCE, Other
- **Team Goals** (Rich Text): Season objectives and development focus
- **Parent Communication** (URL): Link to parent information hub
- **Emergency Contact** (Phone): Team emergency contact number
- **Team Colors** (Multi-select): Primary, Secondary colors for content theming
- **Skill Focus Areas** (Multi-select): Skating, Passing, Shooting, Checking, Goaltending, Systems
- **Created** (Created time): Auto-generated
- **Last Updated** (Last edited time): Auto-generated

### UX Guidelines Integration:
- Age Group property drives content appropriateness across all linked content
- Skill Focus Areas align with hockey terminology tiers from UX guidelines
- Team Goals support differentiated content generation

---

## Database 2: Content Library

**Purpose**: Comprehensive repository for all hockey educational content

### Properties Schema:
- **Content Title** (Title): Descriptive name for the content piece
- **Content Type** (Select): Practice Plan, Drill Instructions, Concept Explanation, Team Context, Video Analysis, Game Strategy
- **Age Groups** (Multi-select): U8, U10, U12, U14, U16, U18 (multiple selections allowed)
- **Status** (Select): Draft, In Review, Published, Archived
- **Primary Author** (Person): Content creator
- **Contributors** (People): Additional content contributors
- **Skill Categories** (Multi-select): Skating, Passing, Shooting, Checking, Goaltending, Tactics, Conditioning, Mental Game
- **Difficulty Level** (Select): Beginner, Intermediate, Advanced
- **Duration** (Number): Estimated time in minutes
- **Equipment Needed** (Multi-select): Pucks, Cones, Sticks, Nets, Boards, Full Ice, Half Ice, No Equipment
- **Safety Considerations** (Rich Text): Key safety points and prerequisites
- **Visual Content Ratio** (Number): Percentage of visual content (aligns with UX guidelines)
- **Terminology Tier** (Select): Tier 1 (U8-U10), Tier 2 (U10-U12), Tier 3 (U12+)
- **Source References** (Relation): Links to Source References database
- **Teams Using** (Relation): Links to Team Information database
- **Publishing URL** (URL): Public sharing link when published
- **Engagement Score** (Formula): Calculated from analytics data
- **Last Review Date** (Date): Content quality review tracking
- **Content Tags** (Multi-select): Searchable keywords and categories
- **Parent-Friendly** (Checkbox): Suitable for parent viewing
- **Coach Notes** (Rich Text): Internal coaching observations and tips
- **Created** (Created time): Auto-generated
- **Last Updated** (Last edited time): Auto-generated

### UX Guidelines Integration:
- Age Groups and Terminology Tier enforce age-appropriate content
- Visual Content Ratio ensures proper visual-to-text ratios per age group
- Safety Considerations prioritize player safety per UX guidelines
- Difficulty Level supports progressive skill development

---

## Database 3: Source References

**Purpose**: Attribution and source management for content integrity

### Properties Schema:
- **Source Title** (Title): Name or description of the source
- **Source Type** (Select): Thunder Playbook Data, Web Research (Exa), Video Content (YouTube), NHL Insights, Coaching Manual, Academic Research, Peer Review
- **Source URL** (URL): Link to original source
- **Author/Organization** (Rich Text): Source creator or publisher
- **Publication Date** (Date): When source was published
- **Access Date** (Date): When source was accessed/retrieved
- **Reliability Score** (Select): High, Medium, Low, Unverified
- **Applicable Ages** (Multi-select): U8, U10, U12, U14, U16, U18
- **Content Categories** (Multi-select): Skills, Tactics, Rules, Safety, Equipment, Psychology, Nutrition, Conditioning
- **Key Insights** (Rich Text): Main takeaways from the source
- **Usage Rights** (Select): Public Domain, Attribution Required, Permission Required, Internal Use Only
- **Content Using** (Relations): Links to Content Library entries that reference this source
- **Research Notes** (Rich Text): Additional context or limitations
- **Verification Status** (Select): Verified, Pending Review, Needs Update, Deprecated
- **Language** (Select): English, French, Other
- **Regional Relevance** (Select): Canada, USA, International, Ontario-Specific
- **Created** (Created time): Auto-generated
- **Last Updated** (Last edited time): Auto-generated

### Integration Points:
- Links to Content Library for source attribution
- Supports multi-source content generation from Issue #85
- Reliability tracking ensures content quality

---

## Database 4: Content Analytics

**Purpose**: Performance tracking and engagement metrics for continuous improvement

### Properties Schema:
- **Content Piece** (Relation): Links to Content Library database
- **Metric Type** (Select): Page Views, Time on Page, Engagement Rate, Feedback Score, Usage Frequency, Share Count
- **Metric Value** (Number): Numerical value of the metric
- **Measurement Date** (Date): When metric was recorded
- **Audience Type** (Select): Players, Parents, Coaches, Public
- **Team Context** (Relation): Links to Team Information database
- **Age Group** (Select): U8, U10, U12, U14, U16, U18
- **Platform** (Select): Notion Public, Direct Share, Email, Print, Mobile App
- **Feedback Comments** (Rich Text): Qualitative feedback and suggestions
- **Improvement Actions** (Rich Text): Planned content improvements based on metrics
- **Seasonal Relevance** (Select): Pre-Season, Regular Season, Playoffs, Off-Season, Year-Round
- **Performance Rating** (Select): Excellent, Good, Average, Needs Improvement, Poor
- **Benchmark Comparison** (Number): How content performs vs. team average
- **Geographic Region** (Select): Local, Regional, Provincial, National
- **Device Type** (Select): Desktop, Mobile, Tablet, Print
- **Created** (Created time): Auto-generated
- **Reporting Period** (Formula): Calculated date range for metrics

### Analytics Integration:
- Supports publishing system requirements from Issue #86
- Enables data-driven content improvement
- Tracks multi-audience engagement per permission levels
- Supports A/B testing of age-appropriate content approaches

---

## Database Relationships

### Primary Relationships:
1. **Team Information ↔ Content Library**: Many-to-many (teams can use multiple content pieces, content can serve multiple teams)
2. **Content Library ↔ Source References**: Many-to-many (content can cite multiple sources, sources can support multiple content pieces)
3. **Content Library ↔ Content Analytics**: One-to-many (each content piece has multiple analytics records)
4. **Team Information ↔ Content Analytics**: Many-to-many (teams generate analytics, analytics can be aggregated across teams)

### Data Flow:
1. **Team Setup**: Team Information database populated with team-specific context
2. **Content Creation**: Content Library entries created with appropriate age group and skill focus
3. **Source Attribution**: Source References linked to provide credibility
4. **Performance Tracking**: Content Analytics capture usage and engagement data
5. **Continuous Improvement**: Analytics drive content refinement and new creation

---

## Permission Integration

### Database-Level Permissions:
- **Team Information**: Coach (Full), Assistant Coach (Edit), Team (View), Parents (No Access)
- **Content Library**: Coach (Full), Assistant Coach (Create/Edit), Team (View Published), Parents (View Parent-Friendly)
- **Source References**: Coach (Full), Assistant Coach (View), Team (No Access), Parents (No Access)
- **Content Analytics**: Coach (Full), Assistant Coach (View Team-Specific), Team (No Access), Parents (No Access)

This schema supports the comprehensive content management workflow while maintaining appropriate access controls and age-appropriate content standards.