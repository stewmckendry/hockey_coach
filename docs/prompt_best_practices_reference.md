# Prompt Best Practices Reference
## Extracted from Anthropic's Claude 4 System Prompt Analysis

### Core Principles from 24,000-Token Professional System Prompt

Based on analysis of Anthropic's Claude 4 system prompt (24,000 tokens, 453 sentences), here are the key prompt engineering principles:

## Rule 1: You are an instructor, act like it
**Key Finding**: Being specific with clear, formatted instructions can improve AI results by up to 76%.

**Best Practices:**
- Define AI's role clearly
- Specify exact task and desired output format
- Include style, length, and formatting requirements
- Use precise instructional language

**Example Pattern:**
```
You are a [ROLE]. Task: [SPECIFIC TASK]. Output: [FORMAT], [LENGTH], [CONSTRAINTS].
```

## Rule 2: Use negative examples effectively
**Key Finding**: Claude 4 uses "never" (39 instances) more than "always" (31 instances).

**Best Practices:**
- Provide examples of what NOT to do
- Use "DON'T" statements to clarify boundaries
- Include specific negative examples to guide behavior
- Balance positive and negative guidance

**Example Pattern:**
```
DO: [desired behavior]
DON'T: [specific behaviors to avoid]
If [unwanted thing] happens, [corrective action].
```

## Rule 3: Provide escape hatches
**Key Finding**: Reduce hallucinations by allowing AI to admit uncertainty.

**Best Practices:**
- Explicitly allow "I don't know" responses
- Provide alternative resources when uncertain
- Set confidence thresholds for responses
- Enable requests for clarifying information

**Example Pattern:**
```
If you're < 70% confident, respond: "I'm not certain—please verify with [RESOURCE]."
```

## Rule 4: Search strategically
**Key Finding**: Claude 4 dedicates 6,471 tokens (nearly 1/3) to search instructions.

**Best Practices:**
- Use "deep dive", "comprehensive", "analyze" for thorough research
- Answer from knowledge first for stable information
- Search immediately for time-sensitive topics
- Scale tool usage based on query complexity

**Trigger Phrases:**
- "deep dive" = minimum 5 tool calls
- "comprehensive" = thorough research
- "think harder" = deeper reasoning

## Rule 5: Enable self-critique
**Best Practices:**
- Build iteration loops into prompts
- Ask AI to rank its own responses
- Include self-evaluation criteria
- Enable automatic refinement

**Example Pattern:**
```
After completing task, run this check: (1) [criteria], (2) [criteria], (3) [criteria]. 
Fix problems, recheck once, then show final version.
```

## Rule 6: Stay neutral
**Key Finding**: Claude 4 system prompt has 0.12 compound sentiment score (mostly neutral).

**Best Practices:**
- Avoid leading questions and biased language
- Use fact-based, professional tone
- Begin neutral and iterate for different perspectives
- Minimize emotional or charged language

## Rule 7: Context is king
**Key Finding**: "Context engineering" - fill context window with right information.

**Best Practices:**
- Layer in relevant information systematically
- Use appropriate model for task complexity
- Provide comprehensive context upfront
- Structure information for optimal AI processing

## Additional Professional Techniques

### Formatting Best Practices
- Use markdown, headers, bullet points intentionally
- Structure prompts with XML-style tags
- Use clear visual hierarchy

### Dynamic Prompting
- Build prompts that create subsequent specialized prompts
- Use keywords in brackets to adjust behavior: [PLAIN], [SEO], [CHECK]
- Chain prompts for complex multi-step tasks

### Iterative Refinement
- Start broad, refine through successive prompts
- Break complex tasks into clear steps
- Prioritize output quality over speed
- Use deliberate practice approach

## Hockey Season Planning Agent Application

### Applying Best Practices to Our Use Case

**Role Definition (Rule 1):**
```
You are a hockey season planning specialist helping volunteer parent-coaches create comprehensive season plans through natural, supportive conversation.
```

**Negative Examples (Rule 2):**
```
DON'T ask multiple questions simultaneously - overwhelming coaches reduces quality
DON'T use procedural language - maintain natural coaching mentor tone
DON'T wait for explicit "done" - recognize satisfaction signals intelligently
```

**Escape Hatches (Rule 3):**
```
If you need clarification about team context, ask naturally: "Tell me more about..."
If unsure about organization-specific requirements, suggest: "You might want to check with your league about..."
```

**Strategic Tool Usage (Rule 4):**
```
Use find_skills_by_age_group immediately when age group mentioned
Use web_search when organization context needed for current information
Use create_practice_plan when conversation naturally turns to specific practices
```

**Self-Evaluation (Rule 5):**
```
Monitor conversation for completion signals: approval language, implementation questions
Assess if sufficient context gathered before offering to create season plan
Evaluate response helpfulness and adjust approach dynamically
```

**Neutral Tone (Rule 6):**
```
Maintain supportive but professional coaching mentor tone
Avoid overly enthusiastic language - stay grounded and helpful
Focus on practical, actionable guidance
```

**Context Engineering (Rule 7):**
```
Build comprehensive picture: team context + coach experience + organizational requirements + LTAD guidelines
Layer information progressively through natural conversation
Maintain context across multiple interactions using native session management
```

## Implementation Guidelines

### Prompt Structure Template
```
ROLE: [Clear role definition]
CORE PHILOSOPHY: [Approach and values]
CONVERSATION APPROACH: [How to interact]
TOOL USAGE: [When and how to use each tool]
COMPLETION RECOGNITION: [How to detect satisfaction]
OUTPUT REQUIREMENTS: [Final deliverables and format]
```

### Quality Checkpoints
1. **Clarity**: Is the instruction specific and unambiguous?
2. **Examples**: Are both positive and negative examples provided?
3. **Escape Routes**: Can the AI gracefully handle uncertainty?
4. **Context**: Is sufficient context provided for quality responses?
5. **Evaluation**: Can the AI assess and improve its own output?

This reference should guide all prompt creation for the Hockey Coach AI Assistant project, ensuring professional-grade instruction quality that leverages proven techniques from leading AI lab implementations.