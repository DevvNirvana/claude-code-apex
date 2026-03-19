# API Design Guidelines

## REST Conventions
```
# Resource naming — nouns, plural, lowercase
GET    /api/v1/users           # list
POST   /api/v1/users           # create
GET    /api/v1/users/:id       # read
PATCH  /api/v1/users/:id       # partial update (prefer over PUT)
DELETE /api/v1/users/:id       # delete

# Nested resources (max 2 levels)
GET    /api/v1/users/:id/posts      # user's posts
POST   /api/v1/users/:id/posts      # create post for user

# Actions that don't fit CRUD (use verb after resource)
POST   /api/v1/users/:id/activate
POST   /api/v1/orders/:id/cancel
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
```

## Response Shapes
```json
// Success — always include id and timestamps
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "name": "Alex",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}

// List — always paginate, always include meta
{
  "data": [...],
  "meta": {
    "total": 150,
    "page": 1,
    "per_page": 20,
    "total_pages": 8
  }
}

// Error — consistent shape across all errors
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is invalid",
    "details": [
      { "field": "email", "message": "Must be a valid email address" }
    ]
  }
}
```

## HTTP Status Codes
```
200 OK            — successful GET, PATCH
201 Created       — successful POST (include Location header)
204 No Content    — successful DELETE
400 Bad Request   — invalid input, validation error
401 Unauthorized  — not authenticated
403 Forbidden     — authenticated but not authorized
404 Not Found     — resource doesn't exist
409 Conflict      — duplicate, state conflict
422 Unprocessable — semantic validation error
429 Too Many      — rate limit exceeded (include Retry-After header)
500 Server Error  — unexpected error (never expose stack traces)
```

## Versioning
- Always version APIs: `/api/v1/`, `/api/v2/`
- Never break backwards compatibility within a version
- Deprecation path: add header `Deprecation: true` + `Sunset: [date]`

## Security
- Always validate Content-Type: `application/json`
- Always set CORS explicitly — never `*` in production
- Always rate limit: auth endpoints (5/min), general API (100/min)
- Always sanitize error messages — never expose stack traces or SQL
- Use `Authorization: Bearer <token>` — never pass tokens in URLs
