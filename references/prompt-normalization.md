# Prompt Normalization Guide

> How the adapter formats context differently for each model family.
> Same information — different packaging — consistent outputs.

---

## Why Normalization Matters

Each model family has different strengths in how it parses instructions:

| Model | Parses best | Struggles with |
|-------|-------------|----------------|
| Gemini 3.1 Pro | XML structure, explicit role framing, large context | Overly casual tone, implicit conventions |
| Gemini 3 Flash | Short, direct instructions | Long system prompts, complex XML |
| Claude Opus/Sonnet | Rich markdown, nuanced prose instructions | Poorly structured XML, ambiguous priorities |
| Claude Haiku | Concise markdown, direct tasks | Long context, many competing instructions |

---

## The 4 Normalization Rules

### Rule 1: Role Framing
Every context injection starts with an explicit role statement.

**For Gemini models:**
```xml
<role>Expert Frontend Developer on ProjectName. You are currently assigned to agent-frontend with task TASK-002.</role>
```

**For Claude models:**
```markdown
You are an expert frontend developer working on ProjectName. Your current assignment: agent-frontend, task TASK-002.
```

### Rule 2: Convention Priority
Conventions must have explicit priority signals.

**For Gemini models:**
```xml
<rule priority="high">Use Server Components by default</rule>
<rule priority="medium">Prefer named exports over default exports</rule>
```

**For Claude models:**
```markdown
**MUST** (never violate): Use Server Components by default  
**PREFER**: Named exports over default exports
```

### Rule 3: Context Density
Gemini 3.1 Pro handles high context density well.  
Flash and Haiku need ruthless compression.

**Full context (Gemini 3.1 Pro / Claude Opus):**
```xml
<conventions>
  <rule priority="high">Use Server Components by default; add "use client" 
  only when you need event handlers, browser APIs, or React hooks that require 
  client-side rendering</rule>
  <rule priority="high">All database queries must go through lib/db.ts — 
  never import Prisma directly in route handlers or components</rule>
</conventions>
```

**Compressed context (Gemini Flash / Claude Haiku):**
```
Rules: Server Components default. DB via lib/db.ts only. No direct Prisma.
```

### Rule 4: Example Format
Few-shot examples dramatically improve output quality for all models.

**Best format (works for all models):**
```typescript
// ✅ Good — how we write API routes in this project
export async function GET(req: Request) {
  try {
    const data = await db.query.users.findMany();
    return Response.json(data);
  } catch (err) {
    return Response.json({ error: 'Failed to fetch' }, { status: 500 });
  }
}

// ❌ Bad — what NOT to do
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient(); // Never create instances like this
```

---

## Model-Specific Profiles

The adapter ships model profiles at `.antigravity/model-profiles/`. Each profile wraps your project's rules.md content in the optimal format for that model.

### `gemini-3.1-pro.md`
- Full XML structure
- Verbose role framing
- All conventions with explicit priorities
- Extended context window used fully

### `gemini-3-flash.md`  
- Compressed rules (< 30 lines)
- Direct task instructions only
- No verbose explanations
- Skip conventions that aren't critical

### `claude-sonnet.md`
- Markdown format
- Nuanced prose for complex conventions
- Few-shot examples
- Moderate length (50-80 lines)

### `claude-opus.md`
- Full markdown
- Philosophical reasoning about WHY each convention exists
- Detailed few-shot examples
- Can handle up to 150 lines effectively

### `claude-haiku.md`
- Ultra-compressed markdown
- Rules as bullet points only
- < 25 lines total
- Only critical prohibitions

---

## How the Adapter Uses This

When `workspace.json` assigns a model to an agent, the adapter automatically selects the matching profile and injects it as the context header for that agent's session.

This happens transparently — you configure model assignments in `workspace.json` and the normalization is handled automatically.

```json
{
  "id": "agent-frontend",
  "model": { "primary": "claude-sonnet-4-6" }
}
```

→ Agent session starts with `model-profiles/claude-sonnet.md` + project rules.  
→ If model limit is hit and it falls back to `gemini-3.1-pro`:  
→ Session restarts with `model-profiles/gemini-3.1-pro.md` + same project rules.

Same context. Same conventions. Different packaging. Consistent outputs.
