# /docs — Documentation Generation

You are generating documentation for: $ARGUMENTS

---

## Step 1: Detect What to Document

Parse `$ARGUMENTS`:
- `/docs [file]` → document that specific file/function/component
- `/docs api` → generate API reference from route files
- `/docs readme` → generate/update README.md
- `/docs arch` → generate architecture decision record
- `/docs component [name]` → generate component storybook-style docs

---

## Step 2: Load Context
Read: `CLAUDE.md` (project + stack)

---

## Step 3: Generate Documentation

### For a Function/Utility
```typescript
/**
 * [One sentence: what it does]
 *
 * [One sentence: when to use it / when NOT to use it]
 *
 * @param {Type} paramName - [description]
 * @param {Type} paramName - [description]
 * @returns {Type} [what it returns + when each case occurs]
 * @throws {ErrorType} [when it throws]
 *
 * @example
 * // [realistic example — not foo/bar]
 * const result = functionName(realValue, anotherRealValue)
 * // → result: { success: true, data: [...] }
 *
 * @example
 * // Error case
 * const result = functionName(invalidValue)
 * // → result: { success: false, error: "..." }
 */
```

### For a React Component
```typescript
/**
 * [ComponentName] — [one sentence describing what it renders]
 *
 * [One paragraph: when to use it, design system position]
 *
 * @component
 *
 * @example
 * // Basic usage
 * <ComponentName
 *   requiredProp="value"
 *   optionalProp={42}
 * />
 *
 * @example
 * // With all props
 * <ComponentName
 *   requiredProp="value"
 *   optionalProp={42}
 *   onAction={(result) => console.log(result)}
 * />
 */

interface ComponentNameProps {
  /** [What this prop does. When to use it. Default if omitted.] */
  requiredProp: string
  /** [Description] @default undefined */
  optionalProp?: number
  /** [Callback description — what triggers it, what it receives] */
  onAction?: (result: ActionResult) => void
}
```

### For an API Endpoint
```markdown
## POST /api/[endpoint]

**Purpose:** [One sentence]
**Auth required:** Yes / No
**Rate limit:** [N] requests per minute

### Request
\`\`\`typescript
// Headers
Content-Type: application/json
Authorization: Bearer [token]  // if required

// Body
{
  fieldName: string     // [description, required]
  optionalField?: number // [description, optional, default: N]
}
\`\`\`

### Response — 200 OK
\`\`\`typescript
{
  success: true
  data: {
    id: string
    // ...
  }
}
\`\`\`

### Error Responses
| Status | Code | When |
|--------|------|------|
| 400 | VALIDATION_ERROR | Invalid request body |
| 401 | UNAUTHORIZED | Missing or invalid token |
| 403 | FORBIDDEN | Valid token but insufficient permissions |
| 404 | NOT_FOUND | Resource doesn't exist |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Unexpected server error |

### Example
\`\`\`bash
curl -X POST https://api.example.com/api/[endpoint] \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"fieldName": "value"}'
\`\`\`
```

### For README.md
```markdown
# [Project Name]

[2 sentences: what it does, who it's for]

## Quick Start
\`\`\`bash
git clone [repo]
cd [project]
cp .env.example .env
# Fill in .env values
npm install
npm run dev
\`\`\`
Open: http://localhost:3000

## Stack
[Tech stack table]

## Project Structure
[File tree with annotations]

## Key Concepts
[3-5 most important things to understand about this codebase]

## Development
[Commands, conventions, workflow]

## Deployment
[How to deploy]

## Environment Variables
[Table: variable, description, required/optional, example value]
```

---

## Step 4: Output the Documentation

Deliver the complete documentation in the appropriate format. No placeholders.

---

> **Token Target:** ≤ 800 output tokens.
> **Quality Standard:** Documentation should answer the question before the reader asks it.
> **Rule:** Show examples for every concept. Abstract explanations without examples are useless.
