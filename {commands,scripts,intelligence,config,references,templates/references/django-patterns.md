# Django Development Patterns

## Project Structure
```
myproject/
├── config/           # Settings, urls, wsgi (not app logic)
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   └── urls.py
├── apps/
│   ├── users/        # Each feature = its own app
│   ├── products/
│   └── orders/
├── templates/        # Project-level templates
├── static/
└── manage.py
```

## Models
```python
# Always use verbose_name, add __str__, Meta ordering
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["author", "is_published"])]

    def __str__(self) -> str:
        return self.title
```

## N+1 Prevention (Critical)
```python
# WRONG — N+1: 1 query for posts + N queries for authors
posts = Post.objects.filter(is_published=True)
for post in posts:
    print(post.author.username)  # N extra queries

# CORRECT — 2 queries total
posts = Post.objects.select_related("author").filter(is_published=True)

# For ManyToMany: use prefetch_related
posts = Post.objects.prefetch_related("tags").filter(is_published=True)

# Use only() to select needed columns
Post.objects.only("id", "title", "slug").filter(is_published=True)
```

## Views (prefer Class-Based for CRUD, function-based for one-offs)
```python
# DRF ViewSet — standard CRUD
class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Post.objects.select_related("author").filter(is_published=True)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

## Migrations
- Always run `python manage.py makemigrations --check` in CI
- Never edit migration files manually after they've been applied
- For data migrations, use `RunPython` with `apps.get_model()` — not direct imports
- Backwards-compatible: AddField before RemoveField, never rename directly

## Security
- Use `django-environ` for all settings — never hardcode secrets
- `ALLOWED_HOSTS` must be explicit in production — never `["*"]`
- Use `django-ratelimit` on auth endpoints
- Enable CSRF protection — never disable globally
- Use `django-csp` for Content Security Policy headers
