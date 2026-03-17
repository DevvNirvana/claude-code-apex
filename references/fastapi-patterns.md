# FastAPI Development Patterns

## Project Structure
```
myapi/
├── main.py           # App creation, router inclusion
├── routers/          # One file per domain
│   ├── users.py
│   ├── posts.py
│   └── auth.py
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas (request/response)
├── crud/             # Database operations
├── core/
│   ├── config.py     # Settings via pydantic-settings
│   ├── security.py   # JWT, password hashing
│   └── database.py   # DB session, engine
└── tests/
```

## Dependency Injection (core pattern)
```python
# Database session as dependency
async def get_db():
    async with AsyncSession(engine) as session:
        yield session

# Auth as dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    user = await crud.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

# Use in routes
@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
```

## Request/Response Schemas
```python
# Always separate create/update/response schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(max_length=100)

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)  # ORM mode

# Never return ORM objects directly — always use response_model
@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_user(db, user_data)
```

## Error Handling
```python
# Custom exception handlers
@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

# Use HTTPException for standard HTTP errors
raise HTTPException(status_code=400, detail="Email already registered")
```

## What NOT to Do
- Never use synchronous DB calls in async routes — always await
- Never put business logic in routes — extract to service/crud layer
- Never return raw exceptions — always use HTTPException or custom handlers
- Never skip `response_model` — it controls serialization and hides sensitive fields
