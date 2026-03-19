# Architecture & Design Document
**Project:** [Project Name]
**Last Updated:** [Date]

---

## System Overview

### Architecture Diagram (Text)
```
[Client Browser / Mobile App]
         ↓ HTTPS
[Next.js App — Vercel Edge]
    ↓ tRPC / REST       ↓ Server Actions
[API Routes]        [Server Components]
         ↓
[PostgreSQL via Prisma]  [Redis Cache]  [Object Storage]
         ↓
[External APIs: Stripe, Clerk, etc.]
```

### Key Architectural Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Framework | Next.js 14 App Router | SSR + RSC for performance |
| Database | PostgreSQL | ACID, relational, mature |
| Auth | [Clerk / NextAuth] | [reason] |
| State | [Zustand / Jotai / Server State only] | [reason] |
| Styling | Tailwind + shadcn/ui | Design system + velocity |

---

## Module Boundaries

### Frontend (src/app/, src/components/)
- Renders UI
- Calls Server Actions for mutations
- Uses Server Components for data fetching
- NO direct database access
- NO direct external API calls (goes through server layer)

### Server Layer (src/server/, src/app/api/)
- All database operations
- All external API calls
- Authentication/authorization checks
- Business logic

### Shared (src/lib/, src/types/)
- Utilities, constants, type definitions
- Can be imported by both layers

---

## Data Models

### [ModelName]
```typescript
type ModelName = {
  id: string
  // ...fields
  createdAt: Date
  updatedAt: Date
}
```

### Relationships
```
User (1) → (*) Posts
Post (1) → (*) Comments
```

---

## API Contracts

### Authentication
All protected endpoints require: `Authorization: Bearer <token>`

### [Endpoint Group]

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/[resource] | Yes | List all |
| POST | /api/[resource] | Yes | Create one |
| GET | /api/[resource]/:id | Yes | Get one |
| PUT | /api/[resource]/:id | Yes | Update one |
| DELETE | /api/[resource]/:id | Yes | Delete one |

---

## State Management

**Server State:** [React Query / SWR / Next.js cache]
**Client State:** [Zustand / Jotai / useState — keep minimal]
**Form State:** [React Hook Form]
**URL State:** [nuqs / Next.js searchParams]

Rule: Prefer server state. Client state should only hold UI state (open/closed, selected tab).

---

## Error Handling Strategy

All errors follow this shape:
```typescript
type ApiResponse<T> = 
  | { success: true; data: T }
  | { success: false; error: string; code?: string }
```

- User-facing errors: human-readable strings
- Server errors: logged with context, generic message to client
- Validation errors: field-level messages via Zod

---

## Performance Targets

| Metric | Target |
|--------|--------|
| LCP | < 2.5s |
| TTI | < 3.5s |
| API response (P95) | < 500ms |
| DB query (P95) | < 100ms |
| Bundle size (first load) | < 200KB |
