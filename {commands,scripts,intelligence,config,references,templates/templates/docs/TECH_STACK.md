# Tech Stack & Coding Standards
**Project:** [Project Name]
**Last Updated:** [Date]

---

## Stack

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Framework | Next.js | 14.x | App Router |
| Language | TypeScript | 5.x | Strict mode |
| Styling | Tailwind CSS | 3.x | + shadcn/ui |
| Database | PostgreSQL | 15.x | via Prisma |
| Auth | [Clerk / NextAuth] | — | — |
| Deployment | Vercel | — | Edge functions |
| Testing | Vitest + RTL | — | — |

---

## Package Decisions

| Package | Use for | Don't use |
|---------|---------|-----------|
| `zod` | All validation | `joi`, `yup` |
| `react-hook-form` | Forms | Uncontrolled inputs |
| `@tanstack/react-query` | Server state (if SPA) | — |
| `date-fns` | Date manipulation | `moment` |
| `lucide-react` | Icons | `react-icons` (too large) |

---

## Coding Standards

### TypeScript
- **Never** use `any` — use `unknown` and narrow it
- Prefer `interface` for object shapes, `type` for unions/intersections
- All functions must have explicit return types on exported functions
- Use `satisfies` operator for object literals with known shapes

```typescript
// ✅ Good
const config = {
  timeout: 5000,
  retries: 3,
} satisfies RequestConfig

// ❌ Bad  
const config: any = { timeout: 5000 }
```

### React Components
- Server Components by default
- `use client` only when: event handlers, browser APIs, hooks that need client state
- Component files: `PascalCase.tsx`
- Utility files: `camelCase.ts`
- One component per file (except tiny sub-components)

```typescript
// ✅ Good — Server Component
async function UserProfile({ userId }: { userId: string }) {
  const user = await db.user.findUnique({ where: { id: userId } })
  return <div>{user?.name}</div>
}

// ❌ Bad — fetching in Client Component for no reason
"use client"
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState(null)
  useEffect(() => { fetch(`/api/users/${userId}`).then(...) }, [userId])
}
```

### Error Handling
```typescript
// ✅ All Server Actions return typed result
export async function createUser(data: CreateUserInput): Promise<ActionResult<User>> {
  try {
    const user = await db.user.create({ data })
    revalidatePath('/users')
    return { success: true, data: user }
  } catch (err) {
    console.error('[createUser]', err)
    return { success: false, error: 'Failed to create user. Please try again.' }
  }
}
```

### Database (Prisma)
- All queries through `lib/db.ts`
- Use `select` to fetch only needed fields
- Use transactions for multi-step operations
- Always paginate list queries (default: 20 items)

```typescript
// ✅ Good
const users = await db.user.findMany({
  select: { id: true, name: true, email: true },
  where: { active: true },
  take: 20,
  skip: page * 20,
  orderBy: { createdAt: 'desc' }
})
```

### Naming Conventions
| Type | Convention | Example |
|------|-----------|---------|
| Files (components) | PascalCase | `UserCard.tsx` |
| Files (utilities) | camelCase | `formatDate.ts` |
| Files (routes) | lowercase | `page.tsx`, `route.ts` |
| Variables | camelCase | `userName` |
| Constants | SCREAMING_SNAKE | `MAX_RETRIES` |
| Types/Interfaces | PascalCase | `UserProfile` |
| CSS classes | kebab-case | `user-card` |
| Env vars | SCREAMING_SNAKE | `DATABASE_URL` |

---

## Testing Standards

- Unit tests: `[filename].test.ts`
- Component tests: `[ComponentName].test.tsx`
- Coverage target: 80%+ on business logic
- Always test: happy path + error paths + edge cases
- Mock: all external services (DB, APIs, auth)

```typescript
// Test name format: describes behavior, not implementation
it("returns error when email is already in use", ...)
it("redirects to dashboard after successful login", ...)
// Not: it("calls setUser with the response data", ...)
```

---

## Git Conventions

### Commit Format
```
type(scope): description

Types: feat, fix, refactor, test, docs, chore, perf, style
```

### Branch Format
```
feature/[feature-name]
fix/[bug-description]
agent/[agent-name]
```

### Rules
- Never push directly to `main`
- Feature branches merge via PR
- Commit after each completed task
- Commit messages in present tense ("add" not "added")
