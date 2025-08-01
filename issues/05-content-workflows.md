# Issue 5: Content Generation Workflows

## Overview
Build comprehensive content creation workflows that integrate multiple data sources (Thunder Playbook ChromaDB, Exa web research, YouTube videos) to generate high-quality, age-appropriate hockey team content. These workflows will support iterative refinement and maintain consistency with UX guidelines.

## Objectives
- Create multi-source research and content generation processes
- Implement iterative content refinement workflows with feedback integration
- Build source material integration from Thunder Playbook repository
- Establish quality assurance checkpoints throughout content creation
- Enable seamless integration between research, generation, and publishing phases

## Multi-Source Research Integration

### Data Source Architecture
```
Content Generation Pipeline
├── 🏒 Thunder Playbook Data (ChromaDB)
│   ├── Drill collections (8 categories)
│   ├── Coaching knowledge base
│   ├── Skill development frameworks
│   └── Best practice guidelines
├── 🌐 Web Research (Exa MCP)
│   ├── Latest training methodologies
│   ├── Equipment reviews and updates
│   ├── Safety guideline updates
│   └── Coaching technique innovations
├── 📹 Video Content (YouTube MCP)
│   ├── Instructional demonstrations
│   ├── Professional technique examples
│   ├── Age-appropriate tutorials
│   └── Equipment usage guides
└── 🎯 Team Context (Notion)
    ├── Age group specifications
    ├── Skill level assessments
    ├── Coaching philosophy
    └── Equipment availability
```

### Research Orchestration Workflow
```python
class ContentResearchOrchestrator:
    def __init__(self, thunder_mcp, exa_mcp, youtube_mcp, notion_client):
        self.thunder = thunder_mcp
        self.exa = exa_mcp
        self.youtube = youtube_mcp
        self.notion = notion_client
        
    async def comprehensive_research(self, topic, team_context):
        """Orchestrate research across all data sources"""
        
        research_results = {
            "local_knowledge": await self.research_thunder_playbook(topic),
            "web_insights": await self.research_web_content(topic, team_context),
            "video_resources": await self.research_video_content(topic, team_context),
            "synthesis": None
        }
        
        # Synthesize findings across sources
        research_results["synthesis"] = await self.synthesize_research(
            research_results, topic, team_context
        )
        
        return research_results
    
    async def research_thunder_playbook(self, topic):
        """Query local ChromaDB collections for relevant content"""
        
        # Search across all relevant collections
        collections = ["drill-*", "ltad-*", "tactics-*", "conduct-*"]
        results = []
        
        for collection in collections:
            matches = await self.thunder.search_hockey_knowledge(
                query=topic,
                collection_filter=collection,
                limit=5
            )
            results.extend(matches)
        
        # Deduplicate and rank results
        ranked_results = self.rank_by_relevance(results, topic)
        
        return {
            "source": "Thunder Playbook",
            "content": ranked_results[:10],
            "confidence": "high",  # Local data has high confidence
            "coverage": self.assess_topic_coverage(ranked_results, topic)
        }
    
    async def research_web_content(self, topic, team_context):
        """Research latest web content for topic"""
        
        # Construct context-aware search queries
        base_query = f"{topic} hockey coaching"
        age_specific = f"{topic} hockey {team_context.age_group}"
        safety_focused = f"{topic} hockey safety youth"
        equipment_related = f"{topic} hockey equipment training"
        
        web_results = []
        for query in [base_query, age_specific, safety_focused, equipment_related]:
            results = await self.exa.web_search_exa(query, numResults=3)
            web_results.extend(results)
        
        # Filter and analyze results
        filtered_results = self.filter_credible_sources(web_results)
        analyzed_results = await self.analyze_web_content(filtered_results)
        
        return {
            "source": "Web Research",
            "content": analyzed_results,
            "confidence": "medium",  # Web content varies in quality
            "trends": self.identify_trending_techniques(analyzed_results)
        }
    
    async def research_video_content(self, topic, team_context):
        """Find relevant instructional videos"""
        
        video_queries = [
            f"{topic} hockey drill {team_context.age_group}",
            f"how to teach {topic} hockey kids",
            f"{topic} hockey tutorial coaching"
        ]
        
        video_results = []
        for query in video_queries:
            videos = await self.youtube.search_youtube_videos(
                search_term=query,
                num_videos=5
            )
            video_results.extend(videos)
        
        # Apply video curation criteria from Issue #4
        curated_videos = self.apply_video_curation(video_results, team_context)
        
        return {
            "source": "Video Content",
            "content": curated_videos,
            "instructional_value": "high",  # Videos provide visual learning
            "age_appropriate": self.validate_age_appropriateness(curated_videos, team_context.age_group)
        }
```

## Content Generation Process

### Structured Content Creation Pipeline
```python
class ContentGenerator:
    def __init__(self, research_orchestrator, ux_guidelines, team_context):
        self.research = research_orchestrator
        self.ux = ux_guidelines
        self.team = team_context
        
    async def generate_content(self, content_type, topic, specifications=None):
        """Main content generation workflow"""
        
        # 1. Comprehensive research phase
        research_data = await self.research.comprehensive_research(topic, self.team)
        
        # 2. Content planning and structure
        content_plan = self.create_content_plan(
            content_type, topic, research_data, specifications
        )
        
        # 3. Initial content generation
        draft_content = await self.generate_initial_draft(content_plan, research_data)
        
        # 4. UX guidelines application
        ux_compliant_content = self.apply_ux_guidelines(
            draft_content, content_type, self.team.age_group
        )
        
        # 5. Source integration and attribution
        final_content = self.integrate_sources(ux_compliant_content, research_data)
        
        return {
            "content": final_content,
            "metadata": {
                "content_type": content_type,
                "topic": topic,
                "age_group": self.team.age_group,
                "research_sources": len(research_data["synthesis"]["sources"]),
                "ux_compliance": True,
                "generation_timestamp": datetime.utcnow()
            }
        }
    
    def create_content_plan(self, content_type, topic, research_data, specifications):
        """Plan content structure based on type and research"""
        
        base_structures = {
            "drill": {
                "sections": ["overview", "setup", "execution", "coaching_points", "progressions"],
                "required_elements": ["diagram", "equipment_list", "safety_notes"],
                "optional_elements": ["video_demo", "variations", "troubleshooting"]
            },
            "concept": {
                "sections": ["definition", "demonstration", "breakdown", "application"],
                "required_elements": ["visual_example", "key_points", "game_situations"],
                "optional_elements": ["common_mistakes", "practice_drills", "advanced_applications"]
            },
            "practice_plan": {
                "sections": ["objectives", "warm_up", "skill_development", "application", "cool_down"],
                "required_elements": ["duration", "equipment", "safety_reminders"],
                "optional_elements": ["alternative_activities", "weather_modifications"]
            }
        }
        
        structure = base_structures.get(content_type, base_structures["concept"])
        
        # Customize based on research findings
        if research_data["synthesis"]["video_heavy"]:
            structure["required_elements"].append("video_integration")
        
        if research_data["synthesis"]["safety_critical"]:
            structure["required_elements"].append("detailed_safety_protocol")
        
        return {
            "structure": structure,
            "key_concepts": research_data["synthesis"]["key_concepts"],
            "age_adaptations": self.plan_age_adaptations(research_data, self.team.age_group),
            "source_integration_points": self.identify_source_integration_points(research_data)
        }
```

### Age-Appropriate Content Adaptation
```python
class AgeAdaptationEngine:
    def __init__(self, ux_guidelines):
        self.ux = ux_guidelines
        
    def adapt_content_for_age(self, content, source_age, target_age):
        """Adapt content between different age groups"""
        
        adaptations = {
            "language": self.adapt_language_complexity(content, source_age, target_age),
            "concepts": self.adapt_concept_complexity(content, source_age, target_age),
            "activities": self.adapt_activity_duration(content, source_age, target_age),
            "visual_ratio": self.adjust_visual_content_ratio(content, target_age),
            "safety_focus": self.adjust_safety_emphasis(content, target_age)
        }
        
        return self.apply_adaptations(content, adaptations)
    
    def adapt_language_complexity(self, content, source_age, target_age):
        """Adjust language complexity for target age group"""
        
        complexity_mappings = {
            "U8": {"reading_level": "grade_2", "vocabulary": "basic", "sentence_length": "short"},
            "U10": {"reading_level": "grade_4", "vocabulary": "intermediate", "sentence_length": "medium"},
            "U12": {"reading_level": "grade_6", "vocabulary": "advanced", "sentence_length": "varied"},
            "U14+": {"reading_level": "grade_8", "vocabulary": "technical", "sentence_length": "complex"}
        }
        
        target_specs = complexity_mappings[target_age]
        
        # Apply language transformations
        adapted_content = {
            "vocabulary": self.simplify_hockey_terms(content, target_specs["vocabulary"]),
            "explanations": self.adjust_explanation_depth(content, target_specs["reading_level"]),
            "instructions": self.modify_instruction_complexity(content, target_specs["sentence_length"])
        }
        
        return adapted_content
```

## Iterative Refinement System

### Multi-Turn Content Improvement
```python
class ContentRefinementEngine:
    def __init__(self, content_generator, quality_assessor):
        self.generator = content_generator
        self.assessor = quality_assessor
        
    async def iterative_refinement(self, initial_content, refinement_criteria, max_iterations=3):
        """Improve content through multiple refinement cycles"""
        
        current_content = initial_content
        refinement_history = []
        
        for iteration in range(max_iterations):
            # Assess current content quality
            quality_assessment = await self.assessor.evaluate_content(
                current_content, refinement_criteria
            )
            
            # Check if quality threshold met
            if quality_assessment["overall_score"] >= refinement_criteria["target_score"]:
                break
            
            # Generate improvement suggestions
            improvement_plan = self.create_improvement_plan(
                current_content, quality_assessment, refinement_criteria
            )
            
            # Apply improvements
            refined_content = await self.apply_improvements(
                current_content, improvement_plan
            )
            
            # Track refinement history
            refinement_history.append({
                "iteration": iteration + 1,
                "quality_score": quality_assessment["overall_score"],
                "improvements_made": improvement_plan["changes"],
                "content_version": refined_content
            })
            
            current_content = refined_content
        
        return {
            "final_content": current_content,
            "refinement_history": refinement_history,
            "iterations_used": len(refinement_history),
            "final_quality_score": quality_assessment["overall_score"]
        }
    
    def create_improvement_plan(self, content, assessment, criteria):
        """Create specific improvement plan based on quality assessment"""
        
        improvement_areas = []
        
        # Content structure improvements
        if assessment["structure_score"] < criteria["structure_threshold"]:
            improvement_areas.append({
                "area": "structure",
                "issues": assessment["structure_issues"],
                "fixes": self.generate_structure_fixes(assessment["structure_issues"])
            })
        
        # Content clarity improvements
        if assessment["clarity_score"] < criteria["clarity_threshold"]:
            improvement_areas.append({
                "area": "clarity",
                "issues": assessment["clarity_issues"],
                "fixes": self.generate_clarity_fixes(assessment["clarity_issues"])
            })
        
        # Age appropriateness improvements
        if assessment["age_appropriate_score"] < criteria["age_threshold"]:
            improvement_areas.append({
                "area": "age_appropriateness",
                "issues": assessment["age_issues"],
                "fixes": self.generate_age_fixes(assessment["age_issues"], criteria["target_age"])
            })
        
        return {
            "priority_order": self.prioritize_improvements(improvement_areas),
            "changes": improvement_areas,
            "estimated_impact": self.estimate_improvement_impact(improvement_areas)
        }
```

### Quality Assessment Framework
```python
class ContentQualityAssessor:
    def __init__(self, ux_guidelines, hockey_knowledge_base):
        self.ux = ux_guidelines
        self.knowledge = hockey_knowledge_base
        
    async def evaluate_content(self, content, criteria):
        """Comprehensive content quality evaluation"""
        
        evaluation_results = {
            "structure_score": self.evaluate_structure(content, criteria["content_type"]),
            "clarity_score": self.evaluate_clarity(content, criteria["target_age"]),
            "accuracy_score": await self.evaluate_hockey_accuracy(content),
            "age_appropriate_score": self.evaluate_age_appropriateness(content, criteria["target_age"]),
            "engagement_score": self.evaluate_engagement_potential(content, criteria["target_age"]),
            "safety_score": self.evaluate_safety_considerations(content),
            "completeness_score": self.evaluate_completeness(content, criteria["content_type"])
        }
        
        # Calculate weighted overall score
        weights = {
            "structure": 0.15,
            "clarity": 0.20,
            "accuracy": 0.20,
            "age_appropriate": 0.15,
            "engagement": 0.15,
            "safety": 0.10,
            "completeness": 0.05
        }
        
        overall_score = sum(
            evaluation_results[f"{key}_score"] * weight 
            for key, weight in weights.items()
        )
        
        evaluation_results["overall_score"] = overall_score
        evaluation_results["detailed_feedback"] = self.generate_detailed_feedback(evaluation_results)
        
        return evaluation_results
    
    def evaluate_hockey_accuracy(self, content):
        """Verify hockey techniques and information are accurate"""
        
        # Extract hockey-specific claims from content
        hockey_claims = self.extract_hockey_claims(content)
        
        accuracy_checks = []
        for claim in hockey_claims:
            # Cross-reference with Thunder Playbook knowledge base
            verification = self.verify_against_knowledge_base(claim, self.knowledge)
            accuracy_checks.append(verification)
        
        accuracy_score = sum(check["accurate"] for check in accuracy_checks) / len(accuracy_checks)
        
        return {
            "score": accuracy_score,
            "verified_claims": len([c for c in accuracy_checks if c["accurate"]]),
            "questionable_claims": [c for c in accuracy_checks if not c["accurate"]],
            "confidence_level": self.calculate_confidence_level(accuracy_checks)
        }
```

## Source Material Integration

### Thunder Playbook Repository Integration
```python
class ThunderPlaybookIntegrator:
    def __init__(self, repo_path="/Users/liammckendry/thunder_playbook"):
        self.repo_path = repo_path
        self.data_sources = {
            "drills": f"{repo_path}/chroma_load/data/drill_data",
            "ltad": f"{repo_path}/chroma_load/data/ltad_data",
            "tactics": f"{repo_path}/chroma_load/data/tactics_data",
            "conduct": f"{repo_path}/chroma_load/data/conduct_data",
            "insights": f"{repo_path}/chroma_load/data/insight_data"
        }
        
    def load_relevant_source_files(self, topic, content_type):
        """Load relevant source files for content generation"""
        
        # Map content types to relevant data sources
        source_mapping = {
            "drill": ["drills", "ltad"],
            "concept": ["ltad", "tactics", "insights"],
            "practice_plan": ["drills", "ltad", "tactics"],
            "team_guide": ["conduct", "insights"],
            "safety": ["conduct", "ltad"]
        }
        
        relevant_sources = source_mapping.get(content_type, ["insights"])
        loaded_files = {}
        
        for source in relevant_sources:
            source_path = self.data_sources[source]
            files = self.find_relevant_files(source_path, topic)
            loaded_files[source] = self.load_and_parse_files(files)
        
        return loaded_files
    
    def find_relevant_files(self, source_path, topic):
        """Find files related to the topic"""
        
        import os
        import re
        
        relevant_files = []
        topic_keywords = self.extract_keywords(topic)
        
        for root, dirs, files in os.walk(source_path):
            for file in files:
                if file.endswith(('.json', '.md', '.txt')):
                    file_path = os.path.join(root, file)
                    
                    # Check filename for topic keywords
                    filename_lower = file.lower()
                    if any(keyword.lower() in filename_lower for keyword in topic_keywords):
                        relevant_files.append(file_path)
                        continue
                    
                    # Check file content for topic keywords
                    content_match = self.check_file_content_relevance(file_path, topic_keywords)
                    if content_match:
                        relevant_files.append(file_path)
        
        return relevant_files[:10]  # Limit to most relevant files
```

### Multi-Source Citation System
```python
class SourceCitationManager:
    def __init__(self):
        self.citations = []
        
    def add_source_citation(self, content_section, source_info):
        """Add citation for content section"""
        
        citation = {
            "content_section": content_section,
            "source_type": source_info["type"],  # "thunder_playbook", "web", "video"
            "source_details": source_info["details"],
            "confidence_level": source_info.get("confidence", "medium"),
            "citation_id": self.generate_citation_id()
        }
        
        self.citations.append(citation)
        return citation["citation_id"]
    
    def generate_source_attribution_section(self, content):
        """Generate source attribution section for content"""
        
        attribution_section = "## Sources & References 📚\n\n"
        
        # Group citations by type
        grouped_citations = self.group_citations_by_type()
        
        for source_type, citations in grouped_citations.items():
            attribution_section += f"### {source_type.title()} Sources\n"
            
            for citation in citations:
                attribution_section += self.format_citation(citation)
                attribution_section += "\n"
            
            attribution_section += "\n"
        
        # Add disclaimer about source verification
        attribution_section += """
### Source Verification 🔍
All sources have been reviewed for accuracy and age-appropriateness. 
Thunder Playbook sources represent verified hockey coaching best practices.
Web sources are current as of the content creation date.
Video sources have been evaluated for instructional quality and safety.
"""
        
        return attribution_section
```

## Workflow Integration Points

### Slash Command Integration
```python
# Enhanced slash commands for content workflows

@slash_command("/generate-content")
async def generate_content_command(content_type, topic, age_group=None):
    """Generate content using full research and refinement workflow"""
    
    # Load team context
    team_context = await load_team_context()
    if age_group:
        team_context.age_group = age_group
    
    # Initialize workflow components
    orchestrator = ContentResearchOrchestrator(thunder_mcp, exa_mcp, youtube_mcp, notion)
    generator = ContentGenerator(orchestrator, ux_guidelines, team_context)
    refiner = ContentRefinementEngine(generator, quality_assessor)
    
    # Execute full workflow
    initial_content = await generator.generate_content(content_type, topic)
    
    refinement_criteria = {
        "target_score": 8.0,  # Out of 10
        "content_type": content_type,
        "target_age": team_context.age_group,
        "structure_threshold": 7.0,
        "clarity_threshold": 7.5,
        "age_threshold": 8.0
    }
    
    final_result = await refiner.iterative_refinement(
        initial_content["content"], 
        refinement_criteria
    )
    
    # Create Notion page with results
    notion_page = await create_notion_page(
        final_result["final_content"],
        initial_content["metadata"]
    )
    
    return {
        "notion_url": notion_page["url"],
        "quality_score": final_result["final_quality_score"],
        "iterations_used": final_result["iterations_used"],
        "source_count": len(orchestrator.get_used_sources())
    }

@slash_command("/refine-content")
async def refine_content_command(notion_url, feedback):
    """Refine existing content based on specific feedback"""
    
    # Load existing content from Notion
    current_content = await notion.fetch_page_content(notion_url)
    
    # Parse feedback into refinement criteria
    feedback_analysis = analyze_feedback(feedback)
    
    # Apply targeted improvements
    refiner = ContentRefinementEngine(content_generator, quality_assessor)
    
    refined_result = await refiner.apply_specific_feedback(
        current_content, 
        feedback_analysis
    )
    
    # Update Notion page
    await notion.update_page_content(notion_url, refined_result["content"])
    
    return {
        "updated_url": notion_url,
        "changes_made": refined_result["improvements_applied"],
        "quality_improvement": refined_result["quality_delta"]
    }
```

## Content Workflow Templates

### Practice Plan Generation Workflow
```yaml
practice_plan_workflow:
  name: "Comprehensive Practice Plan Generation"
  steps:
    1. team_context_loading:
        inputs: [team_id, date, focus_area]
        outputs: [team_preferences, player_count, equipment_available, ice_time]
    
    2. research_phase:
        thunder_playbook: 
          - search drill database for focus_area
          - retrieve LTAD progression guidelines
          - load safety protocols
        web_research:
          - search latest training methods for focus_area
          - find age-specific modifications
        video_research:
          - find demonstration videos
          - extract key teaching points
    
    3. plan_generation:
        structure: age_appropriate_template
        duration: team_preferences.practice_length
        activities: synthesize_research_findings
        progressions: create_skill_progressions
    
    4. refinement:
        safety_check: validate_all_activities
        age_appropriateness: verify_attention_spans
        equipment_check: match_available_equipment
        engagement_optimization: add_competitive_elements
    
    5. publication:
        notion_page: create_formatted_page
        sharing: generate_coach_and_parent_versions
        tracking: add_to_content_database
```

### Drill Instruction Creation Workflow
```yaml
drill_instruction_workflow:
  name: "Comprehensive Drill Documentation"
  steps:
    1. drill_analysis:
        video_source: extract_technique_breakdown
        thunder_playbook: verify_against_existing_drills
        safety_assessment: identify_risk_factors
    
    2. content_structuring:
        overview: create_purpose_statement
        setup: generate_detailed_diagram
        execution: break_into_clear_steps
        coaching_points: extract_key_techniques
        progressions: create_skill_ladder
    
    3. age_adaptation:
        u8_version: simplify_concepts_and_language
        u10_version: add_basic_strategy_elements
        u12_version: include_advanced_applications
    
    4. validation:
        hockey_accuracy: verify_techniques
        safety_compliance: check_protocols
        ux_guidelines: apply_age_standards
    
    5. enhancement:
        video_integration: embed_demonstrations
        related_content: link_to_concepts
        troubleshooting: add_common_problems
```

## Acceptance Criteria

### Research Integration
- [ ] All three data sources (Thunder Playbook, Exa, YouTube) integrate seamlessly
- [ ] Research synthesis provides comprehensive topic coverage
- [ ] Source attribution tracks all references automatically
- [ ] Research quality assessment filters unreliable sources

### Content Generation
- [ ] Generated content meets UX guidelines automatically
- [ ] Age-appropriate adaptations work correctly
- [ ] Content structure follows established templates
- [ ] Hockey accuracy validation prevents misinformation

### Refinement System
- [ ] Iterative refinement improves content quality measurably
- [ ] Quality assessment provides actionable feedback
- [ ] Multi-turn conversations maintain context
- [ ] Refinement history tracks all improvements

### Workflow Efficiency
- [ ] End-to-end content creation completes in <15 minutes
- [ ] Source integration happens automatically
- [ ] Quality checkpoints prevent substandard content
- [ ] Batch processing supports multiple content pieces

## Testing Requirements

### Integration Testing
- Test research orchestration across all data sources
- Verify content generation with different content types
- Validate refinement workflow with real feedback scenarios
- Test slash command integration with workflow components

### Quality Assurance Testing
- Verify age-appropriate content generation for all age groups
- Test hockey accuracy validation with known incorrect information
- Validate safety consideration integration
- Test source attribution accuracy and completeness

### Performance Testing
- Measure end-to-end content generation time
- Test concurrent content generation workflows
- Validate memory usage during multi-source research
- Test workflow performance with large datasets

## Timeline Estimate
**Total**: 2-3 hours
- Research orchestration implementation: 1 hour
- Content generation and refinement workflows: 1.5 hours
- Testing and validation: 30 minutes

## Dependencies
- Thunder Playbook ChromaDB collections and MCP server
- Exa MCP server configuration
- YouTube MCP server from Issue #4
- Notion database structure from Issue #3
- UX guidelines from Issue #2
- Slash commands from Issue #1

## Success Metrics
- Content generation time reduced to <15 minutes end-to-end
- Research coverage includes 3+ different source types per content piece
- Quality scores consistently above 8.0/10 after refinement
- 95% of generated content meets age-appropriateness standards
- Source attribution accuracy at 100%
- User satisfaction with generated content quality >90%