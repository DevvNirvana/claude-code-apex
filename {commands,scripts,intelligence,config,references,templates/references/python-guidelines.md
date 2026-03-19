# Python Development Guidelines

## Code Style
- Follow PEP 8. Use `ruff` for linting (faster than flake8).
- Max line length: 88 chars (Black default). Use Black or Ruff formatter.
- Use f-strings over `.format()` or `%` formatting.
- Use `pathlib.Path` over `os.path` for file operations.

## Type Hints (required for any non-trivial code)
```python
# Always type function signatures
def process_user(user_id: int, options: dict[str, Any] | None = None) -> UserResult:
    ...

# Use TypedDict for structured dicts
from typing import TypedDict
class UserResult(TypedDict):
    id: int
    name: str
    email: str

# Use dataclasses or Pydantic models instead of plain dicts for domain objects
from dataclasses import dataclass
@dataclass
class Config:
    debug: bool = False
    db_url: str = ""
```

## Error Handling
```python
# Be specific — never bare except
try:
    result = fetch_user(user_id)
except UserNotFoundError:
    return None
except DatabaseError as e:
    logger.error("DB error fetching user %d: %s", user_id, e)
    raise  # re-raise after logging

# Use custom exceptions for domain errors
class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        super().__init__(f"User {user_id} not found")
        self.user_id = user_id
```

## Async Patterns
```python
# Use asyncio.gather for parallel I/O — never sequential awaits in a loop
async def load_dashboard(user_id: int):
    user, posts, notifications = await asyncio.gather(
        get_user(user_id),
        get_posts(user_id),
        get_notifications(user_id),
    )
    return {"user": user, "posts": posts, "notifications": notifications}

# Use async context managers for resources
async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        data = await resp.json()
```

## What NOT to Do
- Never use mutable default arguments: `def f(items=[])` → use `def f(items=None): items = items or []`
- Never import star: `from module import *`
- Never use `print()` in production — use `logging`
- Never catch `Exception` broadly without re-raising or specific handling
- Never use `time.sleep()` in async code — use `asyncio.sleep()`
- Never use `global` variables for state — use dependency injection
