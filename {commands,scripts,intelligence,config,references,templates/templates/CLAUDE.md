# CLAUDE.md
<!-- Keep under 80 lines — lean context outperforms bloated in every benchmark -->

## Project
[1-2 sentences: what it does, who uses it, core value proposition]

## Commands
```bash
[dev command]       # start dev server
[build command]     # production build
[test command]      # run tests
[lint command]      # lint + type check
```
<!-- Examples by stack:
  Next.js:   npm run dev / npm run build / npm test / npm run lint
  Django:    python manage.py runserver / collectstatic / pytest / ruff check .
  Rails:     rails server / rake assets:precompile / rspec / rubocop
  Go:        go run ./cmd/... / go build ./... / go test ./... / golangci-lint run
  Flutter:   flutter run / flutter build apk / flutter test / flutter analyze
-->

## Stack
- Language:  [Python 3.12 / TypeScript 5 / Ruby 3.3 / Go 1.21 / Dart 3]
- Framework: [Django 5 / Next.js 15 App Router / Rails 7 / Gin / Flutter]
- Database:  [PostgreSQL via [ORM] / Supabase / MongoDB / SQLite]
- Auth:      [library or approach]
- Deploy:    [Vercel / Railway / Fly.io / Heroku / VPS + Docker]

## Architecture
```
[actual project folder structure — fill from your project]
[e.g.:]
src/
├── app/           # Pages (Next.js App Router)
├── components/    # Shared UI
├── lib/           # Utilities
└── server/        # Server actions / API

[or:]
myproject/
├── apps/          # Django apps
├── config/        # Settings, urls
└── templates/     # HTML templates
```

## Critical Conventions
[Project-specific rules that override general best practices]
[Keep to 4-6 bullet points — only things that would trip up a new developer]
- [e.g.] No API routes — all data via Supabase client directly in components
- [e.g.] All DB queries through `lib/db.ts` — never ORM directly in components
- [e.g.] Errors must be user-readable strings — never surface raw Error objects

## Hard Rules (Never Violate)
- Never commit `.env` — use `.env.example` with placeholder values
- Never push to `main` directly — feature/agent branches only
- Never hardcode secrets, API keys, or credentials
- [Stack-specific hard rule — e.g., "Never use `any` in TypeScript"]
- [Stack-specific hard rule — e.g., "Never call `.save()` outside of service objects"]

## Good Pattern
```[language]
[One canonical example of how to do the most common thing in this project]
[e.g., a server action, a Django view, a Rails service object, a Go handler]
[This is the pattern that should be replicated across the codebase]
```

## Docs
- Context & Architecture: [path e.g., docs/AI_CONTEXT.md]
- Rules & Conventions:    [path e.g., docs/AI_RULES.md]
- Tasks & Roadmap:        [path e.g., docs/AI_TASKS.md or TODO.md]
- Session History:        [path e.g., docs/SESSION_LOG.md]
