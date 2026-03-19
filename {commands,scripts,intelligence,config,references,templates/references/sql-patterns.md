# SQL & Database Patterns

## Query Safety (Critical — prevents injection)
```sql
-- WRONG — string interpolation = SQL injection
query = "SELECT * FROM users WHERE email = '" + email + "'"

-- CORRECT — parameterized queries (all languages/ORMs)
-- Python/psycopg2:
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
-- Go/database/sql:
db.QueryContext(ctx, "SELECT * FROM users WHERE email = $1", email)
-- Node/pg:
pool.query("SELECT * FROM users WHERE email = $1", [email])
```

## Index Strategy
```sql
-- Always index foreign keys
CREATE INDEX idx_posts_user_id ON posts(user_id);

-- Index columns in WHERE, ORDER BY, JOIN ON
CREATE INDEX idx_posts_published_at ON posts(published_at) WHERE is_published = true;

-- Composite index: order matters (most selective first, then sort column)
CREATE INDEX idx_posts_user_published ON posts(user_id, published_at DESC);

-- Covering index: includes all columns in SELECT (avoids table scan)
CREATE INDEX idx_posts_list ON posts(user_id, is_published) INCLUDE (title, slug, created_at);

-- Check for missing indexes
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;  -- Look for Seq Scan on large tables
```

## Migration Safety
```sql
-- SAFE: Always backwards compatible in this order
-- 1. Add nullable column (safe)
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- 2. Backfill data
UPDATE users SET avatar_url = '' WHERE avatar_url IS NULL;

-- 3. Add NOT NULL constraint (only after backfill)
ALTER TABLE users ALTER COLUMN avatar_url SET NOT NULL;

-- DANGEROUS patterns to avoid:
-- ✗ ALTER TABLE on large tables without CONCURRENTLY
-- ✗ DROP COLUMN without deprecation period
-- ✗ Adding NOT NULL without a DEFAULT on non-empty tables
-- ✗ Renaming columns (use add+copy+drop over multiple deploys)

-- SAFE index creation (non-blocking on PostgreSQL)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

## Common Anti-Patterns
```sql
-- SELECT * — always name columns
-- WRONG:
SELECT * FROM users JOIN posts ON posts.user_id = users.id

-- CORRECT:
SELECT users.id, users.name, posts.title, posts.created_at
FROM users JOIN posts ON posts.user_id = users.id

-- N+1 — fetch related data in joins, not loops
-- WRONG (in application code):
users = db.query("SELECT * FROM users")
for user in users:
    posts = db.query("SELECT * FROM posts WHERE user_id = %s", user.id)  # N+1

-- CORRECT:
SELECT u.id, u.name, p.title
FROM users u LEFT JOIN posts p ON p.user_id = u.id
```

## Connection Pooling
- Always use a connection pool — never new connection per request
- Set `pool_size` = (CPU cores × 2) + active disk spindles
- Set `max_overflow` = pool_size (allows burst)
- Set `pool_timeout` = 30s (fail fast, don't queue forever)
- PostgreSQL: use PgBouncer in front for high-concurrency apps
