# Go Development Guidelines

## Project Structure (Standard Go Layout)
```
myservice/
├── cmd/
│   └── server/
│       └── main.go     # Entry point — keep small
├── internal/           # Private packages — not importable externally
│   ├── handlers/       # HTTP handlers
│   ├── service/        # Business logic
│   ├── store/          # Database operations (repository pattern)
│   ├── models/         # Domain types
│   └── middleware/     # Auth, logging, rate limiting
├── pkg/                # Public packages — importable by others
├── migrations/
├── Makefile
└── go.mod
```

## Error Handling (Go's most important pattern)
```go
// WRONG — swallowing errors
result, _ := db.Query(...)

// CORRECT — always handle errors explicitly
result, err := db.QueryContext(ctx, query, args...)
if err != nil {
    return fmt.Errorf("querying users: %w", err)  // wrap with context
}
defer result.Close()

// Custom error types for domain errors
type NotFoundError struct {
    Resource string
    ID       int64
}
func (e *NotFoundError) Error() string {
    return fmt.Sprintf("%s with id %d not found", e.Resource, e.ID)
}

// Check error types in callers
var notFound *NotFoundError
if errors.As(err, &notFound) {
    // handle 404
}
```

## Context Usage (always propagate context)
```go
// Every function that does I/O takes context as first parameter
func (s *UserService) GetUser(ctx context.Context, id int64) (*User, error) {
    return s.store.FindByID(ctx, id)
}

// Set timeouts at the edge (handler level)
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
    defer cancel()
    user, err := h.service.GetUser(ctx, userID)
    ...
}
```

## Concurrency Patterns
```go
// Use channels for coordination, mutexes for state protection
type Cache struct {
    mu    sync.RWMutex
    items map[string]Item
}

func (c *Cache) Get(key string) (Item, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    item, ok := c.items[key]
    return item, ok
}

// errgroup for parallel operations with error handling
g, ctx := errgroup.WithContext(ctx)
g.Go(func() error { return fetchUser(ctx, id) })
g.Go(func() error { return fetchPosts(ctx, id) })
if err := g.Wait(); err != nil {
    return err
}
```

## What NOT to Do
- Never panic in library code — return errors
- Never use `interface{}` / `any` when a concrete type works
- Never start goroutines without a way to stop them (leaks)
- Never ignore the `ctx.Done()` channel in long operations
- Never use `init()` for complex initialization — use constructor functions
