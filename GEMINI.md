# Skills MCP Server

You have access to a Skills MCP server that provides specialized knowledge through modular skill files. Skills contain domain-specific information, code examples, and best practices that augment your capabilities.

## Core Concept

**Skills are NOT pre-loaded.** When a conversation starts, your context is empty of skill content. This design saves tokens for the actual conversation. You must explicitly discover and load skills as needed.

## Available Tools

### `list_skills()`
Returns metadata about all available skills. Call this first to discover what's available.

**Returns:**
```json
{
  "skills": [
    {
      "name": "capl-arethil",
      "title": "CAPL ARETHIL Library Expert",
      "description": "Expert knowledge of Vector CAPL ARETHIL library",
      "keywords": ["arethil", "ethernet", "capl"],
      "version": "1.0.0",
      "auto_activate": true
    }
  ],
  "total_available": 5,
  "currently_loaded": ["capl-arethil"]
}
```

### `search_skills(query: string, limit: int = 5)`
Intelligently search for relevant skills based on a query. Uses semantic search (if available) or keyword matching as fallback.

**Example:**
```json
search_skills(query="how to send ethernet frames", limit=5)
// Returns ranked skills with scores and match reasons
```

**Returns:**
```json
{
  "results": [
    {
      "name": "capl-arethil",
      "title": "CAPL ARETHIL Library Expert",
      "score": 0.847,
      "match_reason": "semantic similarity",
      "search_method": "embedding"
    }
  ],
  "total_found": 3,
  "query": "how to send ethernet frames",
  "search_method": "embedding"
}
```

### `load_skill(skill_name: string, force_reload: bool = false)`
Loads a skill's full content into your context.

**Important behavior:**
- If already loaded: returns `status: "already_loaded"` WITHOUT content (saves tokens)
- Use `force_reload: true` only if you suspect the skill was updated
- Always check the `status` field in the response

**Returns:**
```json
{
  "status": "loaded",  // or "already_loaded" or "error"
  "skill_name": "capl-arethil",
  "content": "# Full skill content here...",
  "message": "Skill loaded successfully",
  "loaded_at": "2024-12-08T10:30:00"
}
```

### `add_skills_directory(path: string)`
Add a new directory to scan for additional skills.

**Example:**
```json
add_skills_directory(path="/home/user/custom-skills")
```

### `get_search_status()` *(optional)*
Check which search backend is active (semantic vs keyword). Useful for debugging.

### `get_embedding_error()` *(optional)*
Get detailed error information if semantic search failed to load.

## Recommended Workflow

Here's how to effectively use the Skills system:

### Simple Queries (Known Domain)

```
User: "How do I send an ARETHIL frame in CAPL?"

Your thought process:
1. I need CAPL and ARETHIL knowledge
2. Let me search for relevant skills
   → search_skills(query="ARETHIL CAPL ethernet frame")
3. Top result: "capl-arethil" with high score
4. Load it: load_skill(skill_name="capl-arethil")
5. Use the loaded content to answer accurately
```

### Complex Queries (Multiple Domains)

```
User: "Compare ARETHIL and FlexRay diagnostics in CAPL"

Your thought process:
1. I need knowledge about ARETHIL, FlexRay, and diagnostics
2. Search: search_skills(query="ARETHIL FlexRay diagnostics", limit=5)
3. Load top relevant skills:
   → load_skill(skill_name="capl-arethil")
   → load_skill(skill_name="capl-flexray")
   → load_skill(skill_name="capl-diagnostics")
4. Synthesize answer using all three skills
```

### Switching Topics

```
User: "Now tell me about database access"

Your thought process:
1. Currently have "capl-arethil" loaded
2. User switched topics completely
3. Search: search_skills(query="database access")
4. Load new skill: load_skill(skill_name="capl-database")
5. Previous skills stay in context (no harm) but focus on new skill
```

## Search Strategy

The server uses intelligent search with automatic fallback:

1. **Semantic Search (Preferred)**: Loads in background using sentence transformers. Understands meaning and context. Provides better relevance matching.

2. **Keyword Search (Fallback)**: Always available immediately. Matches based on exact keywords, skill names, and description words.

You don't need to know which is active - just call `search_skills()` and get the best available results.

## Decision Guide

**When should you search/load skills?**

✅ **DO search when:**
- User asks about specific technical topics (protocols, libraries, frameworks)
- You need code examples or syntax you don't have memorized
- User references domain-specific terminology
- Question requires specialized knowledge beyond general training

❌ **DON'T search when:**
- Answering general programming concepts
- User asks basic questions you can answer confidently
- Explaining fundamental principles that don't need specific examples

**How many skills should you load?**

- **Simple question**: 1 skill usually sufficient
- **Medium complexity**: 2-3 related skills
- **Complex/comparative**: 3-5 skills across domains
- **General guideline**: Load what you'll actually use in the response

## Common Patterns

### Pattern 1: Direct Load (Known Skill)
```
User mentions specific skill by name
→ load_skill(skill_name="exact-name")
```

### Pattern 2: Search Then Load (Discovery)
```
User asks about unfamiliar topic
→ search_skills(query="user's question")
→ Review results
→ load_skill(skill_name="top-match")
```

### Pattern 3: Multi-Skill Synthesis
```
User needs comprehensive answer
→ search_skills(query="broad topic", limit=5)
→ load_skill() for top 3-5 results
→ Synthesize answer from multiple sources
```

## What NOT to Do

❌ **Don't load all skills preemptively** - Wastes context tokens for content you won't use

❌ **Don't reload already-loaded skills** - Check `status: "already_loaded"` and skip unless using `force_reload`

❌ **Don't skip discovery** - Call `list_skills()` or `search_skills()` first to find relevant skills

❌ **Don't ignore the status field** - Always check if load was successful before using content

## Status Field Reference

| Status | Meaning | What to Do |
|--------|---------|------------|
| `loaded` | Content freshly loaded | Use `content` field in response |
| `already_loaded` | Skill in context, no content returned | Skill is available, proceed with answer |
| `error` | Load failed | Check `message` field, try different skill |

## Example Conversation

```
User: "I need to send FlexRay frames and log them to a database"

AI Actions:
1. search_skills(query="FlexRay frames database logging", limit=5)
2. Results show: "capl-flexray" (0.89), "capl-database" (0.76)
3. load_skill(skill_name="capl-flexray")
   → status: "loaded", content: [FlexRay details]
4. load_skill(skill_name="capl-database")  
   → status: "loaded", content: [Database details]
5. Generate answer combining both skills

User: "What about error handling in database writes?"

AI Actions:
1. load_skill(skill_name="capl-database")
   → status: "already_loaded", content: null
2. Use already-loaded database skill to answer
3. No need to reload or search
```