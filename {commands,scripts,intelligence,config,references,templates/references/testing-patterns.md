# Testing Patterns — Universal

## Test Pyramid (target ratios)
```
        /\
       /E2E\          5%  — critical user flows only
      /------\
     /Integration\   20%  — API contracts, DB operations
    /------------\
   /  Unit Tests  \  75%  — pure functions, business logic
  /--------------/
```

## What to Test
**Always test:**
- Business logic and domain rules (the "why" of your app)
- Edge cases: null, empty, max values, invalid input
- Error paths: what happens when the DB is down, API times out
- Security boundaries: auth checks, permission checks
- Data transformations: input → output with known values

**Skip or defer:**
- Implementation details (test behavior, not internal structure)
- Framework code (don't test that Rails/Django/Express works)
- Simple getters/setters with no logic
- Generated code

## Unit Test Patterns
```python
# Python / pytest
def test_user_cannot_access_other_users_posts(user_factory, post_factory):
    alice = user_factory.create()
    bob = user_factory.create()
    alice_post = post_factory.create(author=alice)
    
    # Act
    result = can_access_post(user=bob, post=alice_post)
    
    # Assert
    assert result is False

# Name tests: test_[subject]_[condition]_[expected]
# Arrange / Act / Assert structure — one assertion per test (preferred)
```

```typescript
// TypeScript / Jest / Vitest
describe("UserService", () => {
  describe("createUser", () => {
    it("should hash password before saving", async () => {
      const repo = { save: jest.fn().mockResolvedValue({ id: 1 }) };
      const service = new UserService(repo);
      
      await service.createUser({ email: "a@b.com", password: "plain123" });
      
      const savedUser = repo.save.mock.calls[0][0];
      expect(savedUser.password).not.toBe("plain123");
      expect(savedUser.password).toMatch(/^\$2[aby]/);  // bcrypt pattern
    });
  });
});
```

## Integration Test Patterns
```python
# Test API endpoints against real DB (use test DB)
def test_create_post_returns_201_with_auth(client, authenticated_user):
    response = client.post("/api/v1/posts", json={
        "title": "My Post",
        "content": "Content here",
    }, headers=authenticated_user.auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Post"
    assert data["author_id"] == authenticated_user.id
    assert "id" in data
```

## Mocking Guidelines
- Mock at the boundary (external services, file system, clock)
- Don't mock your own code — if you need to, the code is too coupled
- Use factories/fixtures for test data — never hardcode IDs or emails
- Reset mocks between tests — never share state

## Test File Conventions
```
# Co-locate tests with source:
src/services/user_service.py
src/services/test_user_service.py  (or tests/services/test_user_service.py)

# Naming
test_[module].py          (Python)
[module].test.ts          (TypeScript)
[module]_spec.rb          (Ruby)
[Module]_test.go          (Go)
```

## CI Requirements
- All tests must pass before merge (zero tolerance)
- Coverage: aim for 80%+ on business logic, not framework boilerplate
- Flaky tests must be fixed immediately — never skip and ignore
