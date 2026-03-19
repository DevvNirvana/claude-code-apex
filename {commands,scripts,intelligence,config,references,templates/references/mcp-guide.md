# MCP Selection Guide

> Rule: fewer MCPs = better performance. 3-5 max per project.
> Each MCP added = more decisions Claude must make = more chances to pick wrong one.

---

## Selection Matrix

| Project Type | Core MCPs | Optional MCPs | Avoid |
|-------------|-----------|---------------|-------|
| Any | `filesystem` | — | Everything else unless needed |
| Web App (Next.js) | `filesystem`, `playwright` | `supabase` | Don't add database MCPs unless actually using them |
| API-only | `filesystem` | `postgres`, `sqlite` | `figma`, `playwright` |
| Design-heavy | `filesystem`, `figma` | — | Database MCPs unless needed |
| Full-stack SaaS | `filesystem`, `supabase`, `playwright` | — | Adding more than 5 |
| Data / Analytics | `filesystem`, `postgres` or `sqlite` | — | UI-focused MCPs |

---

## Install Commands

```bash
# Always install filesystem first
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem .

# Browser automation / E2E testing
claude mcp add playwright -- npx -y @playwright/mcp@latest

# Supabase (database + auth + storage)
claude mcp add supabase -- npx -y @supabase/mcp-server-supabase@latest --project-ref YOUR_REF

# Figma (design tokens, component specs)
claude mcp add figma -- npx -y @figma/mcp

# SQLite (local/embedded database)
claude mcp add sqlite -- npx -y mcp-server-sqlite --db-path ./data.db

# Postgres (external database)
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres postgresql://user:pass@host/db

# GitHub (repo management)
claude mcp add github -- npx -y @modelcontextprotocol/server-github

# Fetch (HTTP requests, API exploration)
claude mcp add fetch -- npx -y @modelcontextprotocol/server-fetch
```

---

## Managing MCPs

```bash
# List installed
claude mcp list

# Remove an MCP
claude mcp remove [name]

# Set scope (local = this project only, user = all projects)
claude mcp add --scope project [name] -- [command]
claude mcp add --scope user [name] -- [command]
```

---

## The Candy Shop Trap

> "15 tools = Claude picks the wrong one. More options, worse decisions."

Signs you have too many MCPs:
- Claude keeps trying the wrong tool for a task
- Sessions feel slow and unfocused
- Claude asks clarifying questions about which tool to use

Fix: `claude mcp list` → remove anything you haven't used in 2 weeks.

---

## Per-Project MCP Configuration

Store MCP config in `.claude/mcp-config.json` (committed to repo):

```json
{
  "project": "my-app",
  "mcps": ["filesystem", "playwright", "supabase"],
  "rationale": "Web app with E2E tests and Supabase backend"
}
```

This helps new team members (and agents) understand what's available.
