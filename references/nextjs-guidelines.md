# Next.js Guidelines Reference

> Auto-loaded by `/design` when framework = nextjs. Covers Next.js 14+ App Router.

---

## 🔴 High Severity — Always Apply

### Rendering
| Rule | Do | Don't |
|------|----|-------|
| Server Components by default | Keep components server, no `'use client'` unless needed | Adding `'use client'` unnecessarily bloats client bundle |
| Mark Client Components | Add `'use client'` for hooks/events | Using `useState` in a Server Component crashes |
| Push Client Components down | `<InteractiveButton>` as leaf, page stays server | Marking entire page as `'use client'` |

### Images
```tsx
// ✅ Always use next/image
import Image from 'next/image'
<Image src={url} alt="Description" width={400} height={300} />
<Image src={hero} alt="Hero" fill className="object-cover" priority />

// ❌ Never use raw <img>
<img src={url} />  // No optimization, causes layout shift
```

### Data Fetching
```tsx
// ✅ Fetch in Server Components (Next.js 15: cache defaults to uncached)
export default async function Page() {
  const data = await fetch(url, { cache: 'force-cache' }) // explicit!
  return <div>{data.title}</div>
}

// ✅ Server Actions for mutations
async function createPost(formData: FormData) {
  'use server'
  const body = schema.parse(Object.fromEntries(formData)) // validate first
  await db.post.create({ data: body })
  revalidatePath('/posts')
}

// ❌ Never trust Server Action input without validation
async function deletePost(id: string) {
  'use server'
  await db.post.delete({ where: { id } }) // missing auth + validation!
}
```

### Environment Variables
```bash
# ✅ Client-accessible: NEXT_PUBLIC_ prefix required
NEXT_PUBLIC_API_URL=https://api.example.com

# ❌ Server-only vars must NEVER appear in client code
DATABASE_URL=...   # Fine in server, crashes if used in 'use client'
```

### Security
```tsx
// ✅ Sanitize user content
import DOMPurify from 'isomorphic-dompurify'
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />

// ❌ XSS vulnerability
<div dangerouslySetInnerHTML={{ __html: userContent }} />
```

---

## 🟡 Medium Severity — Best Practice

### Routing Structure
```
app/
├── (marketing)/          ← route group, no URL impact
│   ├── about/page.tsx
│   └── pricing/page.tsx
├── (app)/
│   ├── dashboard/
│   │   ├── page.tsx
│   │   ├── loading.tsx   ← streaming skeleton
│   │   └── error.tsx     ← error boundary
│   └── settings/page.tsx
└── layout.tsx
```

### Fonts — Always next/font
```tsx
// ✅ Zero layout shift, self-hosted
import { Inter, Outfit } from 'next/font/google'
const heading = Outfit({ subsets: ['latin'], weight: ['600','700','800'] })
const body = Inter({ subsets: ['latin'], weight: ['400','500'] })

// In layout.tsx
<body className={`${heading.variable} ${body.variable}`}>

// ❌ External font link causes FOUT
<link href="https://fonts.googleapis.com/css2?family=Inter..." />
```

### API Routes
```tsx
// ✅ App Router: named HTTP method exports
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

const schema = z.object({ name: z.string().min(1) })

export async function POST(request: NextRequest) {
  const body = schema.parse(await request.json())
  return NextResponse.json({ success: true })
}

// ❌ Pages Router style (don't use for new code)
export default function handler(req, res) { ... }
```

### Middleware
```ts
// middleware.ts (root level)
import { NextResponse } from 'next/server'
export function middleware(request) {
  const token = request.cookies.get('auth')
  if (!token) return NextResponse.redirect(new URL('/login', request.url))
}
export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*'] // specific paths only
}
```

---

## Performance Patterns

```tsx
// Dynamic import for heavy components
import dynamic from 'next/dynamic'
const HeavyChart = dynamic(() => import('./Chart'), { 
  ssr: false,
  loading: () => <Skeleton className="h-48" />
})

// Streaming with Suspense
export default function Page() {
  return (
    <main>
      <StaticHero />              {/* renders immediately */}
      <Suspense fallback={<Skeleton />}>
        <SlowDataComponent />     {/* streams in */}
      </Suspense>
    </main>
  )
}

// Parallel data fetching (not sequential)
const [user, posts] = await Promise.all([
  fetchUser(id),
  fetchPosts(id)
])
```

---

## Docs
- [App Router](https://nextjs.org/docs/app)
- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Server Actions](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)
- [next/image](https://nextjs.org/docs/app/building-your-application/optimizing/images)
- [next/font](https://nextjs.org/docs/app/building-your-application/optimizing/fonts)
