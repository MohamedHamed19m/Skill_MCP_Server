# MCP Skills Server - Clean Architecture Design

## Philosophy: "Definition vs. Executor" Pattern

This design follows the best practices from modern agentic frameworks:
- **Separation of Concerns**: Manager only manages state, doesn't make decisions
- **Protocol-Driven**: Tools return structured results, never throw exceptions to LLM
- **Result Objects**: Always return status + data, let caller decide what to do
- **Type Safety**: Pydantic models for all inputs/outputs

---

## Core Architecture

### 1. The Two-Tool Protocol

**Tool 1: `list_skills` (Discovery)**
- **Purpose**: Let AI discover what skills exist
- **Returns**: Lightweight metadata only (description, keywords, name)
- **Token Cost**: ~100 tokens total (all metadata)
- **When to call**: ALWAYS first, before loading anything

**Tool 2: `load_skill` (Activation)**
- **Purpose**: Load full skill content into context
- **Returns**: Result object with status ("loaded", "already_loaded", "error")
- **Token Cost**: ~5000 tokens per skill
- **When to call**: After analyzing metadata from list_skills

### 2. The Skills Manager (Single Responsibility)

```
SkillsManager
├── State Management
│   ├── _available_skills: Dict[name → SkillMetadata]
│   └── _loaded_skills: Dict[name → {content, tokens, loaded_at}]
├── Operations
│   ├── scan_directory() → void
│   ├── get_all_skills_metadata() → List[SkillMetadata]
│   ├── load_skill_content(name, force_reload) → SkillLoadResult
│   └── is_skill_loaded(name) → bool
```

**Key Design Decision**: The manager doesn't decide WHAT to load, only HOW to load.
The AI makes decisions based on metadata.

---

## Data Models (Pydantic)

### SkillMetadata (Lightweight)
```python
class SkillMetadata(BaseModel):
    name: str                    # Unique ID
    title: str                   # Human readable
    description: str             # For relevance matching
    keywords: List[str]          # For relevance matching
    version: str
    auto_activate: bool
    estimated_tokens: int
```

### SkillLoadResult (Protocol Result)
```python
class SkillLoadResult(BaseModel):
    status: str                  # "loaded" | "already_loaded" | "error"
    skill_name: str
    content: Optional[str]       # Only present if status="loaded"
    message: str                 # Human-readable explanation
    tokens_loaded: Optional[int]
    loaded_at: Optional[str]
```

**Why Optional[str] for content?**
If status="already_loaded", we don't return content again to save context tokens.
The AI should understand the skill is already in context.

---

## The Protocol: How AI Should Use This

### Phase 1: Discovery (REQUIRED)
```python
# Step 1: List all available skills
result = list_skills()

# Step 2: Analyze metadata
for skill in result.skills:
    # Check if relevant based on:
    # - skill.description
    # - skill.keywords  
    # - skill.name
```

### Phase 2: Selective Loading
```python
# Load only relevant skills
result = load_skill(skill_name="capl-arethil")

if result.status == "loaded":
    # New skill loaded, use result.content
    context = result.content
    
elif result.status == "already_loaded":
    # Skill already in context, don't load again
    # Continue without re-reading content
    
elif result.status == "error":
    # Skill doesn't exist or failed to load
    # Inform user
```

### Phase 3: Context Management
```python
# When switching domains, unload old skills
unload_skill(skill_name="capl-arethil")

# Load new domain skills
load_skill(skill_name="capl-database")
```

---

## Key Design Patterns Applied

### 1. Result Object Pattern
Instead of:
```python
def load_skill(name):
    if not exists(name):
        raise ValueError("Not found")  # ❌ Forces exception handling
    return content
```

We use:
```python
def load_skill(name) -> SkillLoadResult:
    if not exists(name):
        return SkillLoadResult(
            status="error",
            message="Skill not found"
        )  # ✅ Structured error
    return SkillLoadResult(
        status="loaded",
        content=content
    )
```

**Why?** The LLM can check `result.status` instead of handling exceptions.

### 2. Idempotent Loading
```python
# First call
result1 = load_skill("capl-arethil")
# status="loaded", content=full_text

# Second call (without force_reload)
result2 = load_skill("capl-arethil")  
# status="already_loaded", content=None, message="Already loaded"
```

**Why?** Prevents wasting context tokens by loading the same skill multiple times.

### 3. Type Safety (Pydantic)
All tool responses are validated:
```python
return SkillsListResult(
    skills=[...],          # Must be List[SkillMetadata]
    total_available=5,     # Must be int
    currently_loaded=[...] # Must be List[str]
)
```

**Why?** The LLM gets structured, predictable responses every time.

---

## Workflow Examples

### Example 1: Simple Query
```
User: "How do I send an ARETHIL frame?"

AI Agent Flow:
1. Call list_skills()
   → Gets: [{name: "capl-arethil", keywords: ["arethil", "capl"], ...}, ...]
   
2. Analyze: "arethil" matches user query
   
3. Call load_skill(skill_name="capl-arethil")
   → Gets: {status: "loaded", content: "# CAPL ARETHIL Expert\n..."}
   
4. Use content to generate accurate answer
```

### Example 2: Domain Switching
```
User: "Send ARETHIL frame"
AI: [Loads capl-arethil, answers]

User: "Now work with database"
AI Agent Flow:
1. Check get_loaded_skills_info()
   → Currently loaded: ["capl-arethil"]
   
2. User switched domains, so unload old skill
   Call unload_skill(skill_name="capl-arethil")
   
3. Load new skill
   Call load_skill(skill_name="capl-database")
   
4. Answer using database skill
```

### Example 3: Already Loaded (Efficient)
```
User: "Show me another ARETHIL example"

AI Agent Flow:
1. Check if capl-arethil is needed
   
2. Call load_skill(skill_name="capl-arethil")
   → Gets: {status: "already_loaded", content: None, message: "Already loaded"}
   
3. Understand skill is in context, proceed without re-loading
```

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Load Everything
```python
# Don't do this!
for skill in list_skills().skills:
    load_skill(skill.name)  # Wastes context on irrelevant skills
```

### ❌ Anti-Pattern 2: Ignore Status
```python
result = load_skill("capl-arethil")
# Using result.content without checking result.status
# Could be None if already_loaded or error!
```

### ❌ Anti-Pattern 3: Skip Discovery
```python
# Don't do this!
load_skill("capl-arethil")  # What if it doesn't exist?

# Do this instead:
skills = list_skills()
if "capl-arethil" in [s.name for s in skills.skills]:
    load_skill("capl-arethil")
```

---

## Implementation Checklist

### Phase 1: Core (✅ Implemented)
- [x] SkillsManager with state management
- [x] Pydantic models for all responses
- [x] list_skills tool (metadata only)
- [x] load_skill tool (with status checking)
- [x] Idempotent loading (already_loaded detection)

### Phase 2: Utility Tools (✅ Implemented)
- [x] unload_skill (free context)
- [x] get_loaded_skills_info (check state)
- [x] reload_skills_directory (rescan files)

### Phase 3: Documentation (✅ Included)
- [x] Usage patterns in code comments
- [x] Example workflows
- [x] Anti-patterns guide

---

## Token Efficiency Comparison

### Old Approach (Load Everything):
```
Context = [Skill1: 5000 tokens] + [Skill2: 5000 tokens] + 
          [Skill3: 5000 tokens] + [Skill4: 5000 tokens]
Total: 20,000 tokens consumed immediately
```

### New Approach (Protocol-Driven):
```
Phase 1 (Discovery):
  list_skills() → 500 tokens (all metadata)

Phase 2 (Selective Loading):
  load_skill("capl-arethil") → 5000 tokens
  
Total: 5,500 tokens (73% savings!)
```

---

## Why This Design is Better

1. **Efficient**: Only loads what's needed when it's needed
2. **Scalable**: Can have 100+ skills without context issues
3. **Type-Safe**: Pydantic ensures valid data every time
4. **Idempotent**: Safe to call load_skill multiple times
5. **Clear Protocol**: AI knows exactly what to do (list → analyze → load)
6. **Graceful Errors**: No exceptions, just status codes

---

## Summary

This design follows the "Definition vs. Executor" pattern where:

- **SkillsManager** = The Executor (manages state, does operations)
- **Skill Files** = The Definitions (YAML frontmatter + markdown)
- **MCP Tools** = The Protocol (how AI interacts with the system)

The AI acts as the "decision maker" using the protocol:
1. Discover (list_skills)
2. Analyze (check metadata)
3. Load (load_skill with status checking)
4. Manage (unload when switching domains)

This is exactly how modern agentic systems work - clean separation of concerns with protocol-driven interaction.