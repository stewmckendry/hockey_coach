# Hockey Coaching MCP Resources Guide

## Overview

The Hockey Coaching MCP server provides structured access to hockey coaching content through MCP (Model Context Protocol) resources. These resources can be accessed in Claude Desktop by manually adding them to your prompts.

## Available Resources

### Skills Resources

#### List Available Age Groups
- **URI**: `hockey://skills/age-groups`
- **Description**: Returns all available age groups in the skills database
- **Example Response**:
```json
{
  "age_groups": ["U6", "U8", "U10", "U12", "U14", "U16", "U18"],
  "count": 7
}
```

#### Get Skills by Age Group
- **URI**: `hockey://skills/by-age/{age_group}`
- **Parameters**: 
  - `age_group`: One of U6, U8, U10, U12, U14, U16, U18
- **Description**: Returns all skills appropriate for the specified age group
- **Example**: `hockey://skills/by-age/U10`

### Drill Resources

#### List Drill Categories
- **URI**: `hockey://drills/categories`
- **Description**: Returns all available drill categories based on skills practiced
- **Example Response**:
```json
{
  "categories": [
    {"category": "Passing", "count": 45},
    {"category": "Shooting", "count": 38},
    {"category": "Skating", "count": 52}
  ],
  "total": 133
}
```

#### Get Drills by Category
- **URI**: `hockey://drills/by-category/{category}`
- **Parameters**:
  - `category`: URL-encoded drill category (e.g., "Passing", "Shooting")
- **Description**: Returns all drills for a specific skill/category
- **Example**: `hockey://drills/by-category/Passing`

### Tactics Resources

#### List Tactic Categories
- **URI**: `hockey://tactics/categories`
- **Description**: Returns all available tactical system categories
- **Example Response**:
```json
{
  "categories": [
    {"category": "Forechecking", "count": 15},
    {"category": "Power Play", "count": 12},
    {"category": "Penalty Kill", "count": 8}
  ],
  "total": 12
}
```

#### Get Tactics by Category
- **URI**: `hockey://tactics/by-category/{category}`
- **Parameters**:
  - `category`: URL-encoded tactic category (e.g., "Forechecking", "Power%20Play")
- **Description**: Returns all tactics for a specific category
- **Example**: `hockey://tactics/by-category/Power%20Play`

### Video Resources

#### List Video Categories
- **URI**: `hockey://videos/categories`
- **Description**: Returns all available video categories based on skill focus
- **Example Response**:
```json
{
  "categories": [
    {"category": "Puck Handling", "count": 25},
    {"category": "Shooting Technique", "count": 18},
    {"category": "Defensive Skills", "count": 22}
  ],
  "total": 353
}
```

#### Get Videos by Category
- **URI**: `hockey://videos/by-category/{category}`
- **Parameters**:
  - `category`: URL-encoded video category
- **Description**: Returns all videos for a specific category/skill focus
- **Example**: `hockey://videos/by-category/Shooting%20Technique`

### Dryland Training Resources

#### List Dryland Categories
- **URI**: `hockey://dryland/categories`
- **Description**: Returns all available off-ice training categories
- **Example Response**:
```json
{
  "categories": [
    {"category": "Balance & Coordination", "count": 42},
    {"category": "Stickhandling", "count": 38},
    {"category": "Core", "count": 45},
    {"category": "Flexibility", "count": 28},
    {"category": "Agility", "count": 31}
  ],
  "total": 5
}
```

#### Get Dryland Exercises by Category
- **URI**: `hockey://dryland/by-category/{category}`
- **Parameters**:
  - `category`: URL-encoded dryland category (e.g., "Balance%20%26%20Coordination")
- **Description**: Returns all dryland exercises for a specific category
- **Example**: `hockey://dryland/by-category/Stickhandling`

## Using Resources in Claude Desktop

### Important Note
Claude Desktop can access MCP resources, but they must be manually added to your prompts. The resources won't appear in the UI automatically.

### How to Use

1. **Copy the Resource URI**: Select the appropriate resource URI from the list above

2. **Add to Your Prompt**: Include the resource URI in your message to Claude. For example:
   ```
   Using the resource hockey://drills/by-category/Passing, can you create a practice plan for U10 players?
   ```

3. **Multiple Resources**: You can reference multiple resources in a single prompt:
   ```
   Using hockey://skills/by-age/U10 and hockey://drills/by-category/Skating, 
   create an age-appropriate skating development session.
   ```

### Tips for Effective Use

1. **Start with Categories**: First query the categories resource to see what's available:
   - `hockey://drills/categories`
   - `hockey://tactics/categories`
   - `hockey://videos/categories`
   - `hockey://dryland/categories`

2. **URL Encoding**: For categories with spaces or special characters, use URL encoding:
   - Space → `%20` (e.g., "Power Play" → "Power%20Play")
   - Ampersand → `%26` (e.g., "Balance & Coordination" → "Balance%20%26%20Coordination")

3. **Age-Appropriate Content**: Use the skills resources to ensure content matches player development:
   - First check: `hockey://skills/age-groups`
   - Then query: `hockey://skills/by-age/U12`

4. **Combine Resources**: Mix different resource types for comprehensive planning:
   ```
   Using these resources:
   - hockey://skills/by-age/U10
   - hockey://drills/by-category/Passing
   - hockey://videos/by-category/Passing
   - hockey://dryland/by-category/Core
   
   Create a complete training program for U10 players focusing on passing skills.
   ```

## Common Use Cases

### Practice Planning
```
Using hockey://drills/by-category/Skating and hockey://drills/by-category/Puck%20Handling,
create a 60-minute practice plan that balances both skills.
```

### Skill Development
```
Using hockey://skills/by-age/U12 and hockey://videos/by-category/Shooting%20Technique,
design a shooting progression for U12 players.
```

### Off-Ice Training
```
Using hockey://dryland/by-category/Balance%20%26%20Coordination and 
hockey://dryland/by-category/Core, create a 30-minute off-ice workout.
```

### System Implementation
```
Using hockey://tactics/by-category/Forechecking, explain different forechecking 
systems and when to use each one.
```

## Resource Response Format

All resources return JSON with consistent structure:

### Category Lists
```json
{
  "categories": [
    {"category": "Category Name", "count": 10},
    ...
  ],
  "total": 50
}
```

### Content by Category
```json
{
  "category": "Category Name",
  "count": 10,
  "items": [
    {
      "title": "Item Title",
      "description": "Item description",
      "metadata": {...}
    },
    ...
  ]
}
```

## Troubleshooting

### Resource Not Found
- Ensure the URI is correctly formatted
- Check that category names are properly URL-encoded
- Verify the age group is valid (U6, U8, U10, U12, U14, U16, U18)

### Empty Results
- Some categories may have no content
- Try listing categories first to see what's available
- Check different variations of category names

### Claude Desktop Integration
- Resources must be manually typed in prompts
- They won't appear in any UI menus
- Copy and paste URIs exactly as shown

## Support

For issues or questions about the Hockey Coaching MCP resources:
1. Check the MCP server logs: `mcp_server.log`
2. Verify the server is running: `python servers/hockey_mcp.py`
3. Test resources directly: `python test_new_resources.py`