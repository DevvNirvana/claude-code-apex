#!/usr/bin/env python3
"""
Universal Stack Detector — detects any project's tech stack and saves a
stack-profile.json that all APEX commands use to adapt their behavior.

Supports:
  JS/TS: Next.js, React, Vue, Svelte, Nuxt, SvelteKit, Vite, Gatsby, Remix
  Python: Django, FastAPI, Flask, plain Python
  Ruby:   Rails, Sinatra
  Go:     Standard Go modules
  PHP:    Laravel, Symfony, plain PHP
  Mobile: Flutter, React Native, SwiftUI
  Other:  Static sites, unknown

Usage:
  python3 .claude/intelligence/detect_stack.py
  python3 .claude/intelligence/detect_stack.py --save   # saves stack-profile.json
  python3 .claude/intelligence/detect_stack.py --json   # JSON only output
"""
import json, os, re, sys
from pathlib import Path

ROOT = Path.cwd()
CLAUDE_DIR = ROOT / ".claude"

# ── Rule set mapping ───────────────────────────────────────────────────────────
# Maps detected frameworks/libraries to which reference docs to load

RULE_SETS = {
    # JS/TS frontend
    "nextjs":      ["nextjs-guidelines", "react-guidelines", "ux-principles"],
    "react":       ["react-guidelines", "ux-principles"],
    "vue":         ["vue-svelte-guidelines", "ux-principles"],
    "nuxt":        ["vue-svelte-guidelines", "nextjs-guidelines", "ux-principles"],
    "svelte":      ["vue-svelte-guidelines", "ux-principles"],
    "sveltekit":   ["vue-svelte-guidelines", "ux-principles"],
    "remix":       ["react-guidelines", "ux-principles"],
    "gatsby":      ["react-guidelines", "ux-principles"],
    # Styling
    "tailwind":    ["shadcn-tailwind-guidelines"],
    "shadcn":      ["shadcn-tailwind-guidelines"],
    # Python backend
    "django":      ["python-guidelines", "django-patterns", "sql-patterns", "api-design", "security-checklist"],
    "fastapi":     ["python-guidelines", "fastapi-patterns", "api-design", "security-checklist"],
    "flask":       ["python-guidelines", "api-design", "security-checklist"],
    "python":      ["python-guidelines", "testing-patterns"],
    # Ruby
    "rails":       ["rails-guidelines", "sql-patterns", "api-design", "security-checklist"],
    "sinatra":     ["api-design", "security-checklist"],
    # Go
    "go":          ["go-guidelines", "api-design", "security-checklist"],
    # PHP
    "laravel":     ["api-design", "sql-patterns", "security-checklist"],
    "symfony":     ["api-design", "sql-patterns", "security-checklist"],
    # Mobile
    "flutter":     ["native-guidelines"],
    "react-native":["react-guidelines", "native-guidelines"],
    "swiftui":     ["native-guidelines"],
    # Universal
    "sql":         ["sql-patterns"],
    "api":         ["api-design"],
    "docker":      ["security-checklist"],
}

# Domain map templates per framework
DOMAIN_MAPS = {
    "nextjs": {
        "frontend": ["src/app/", "src/components/", "app/", "components/"],
        "api":      ["src/app/api/", "app/api/", "src/server/"],
        "db":       ["prisma/", "migrations/", "src/lib/db.ts", "drizzle/"],
        "auth":     ["src/app/(auth)/", "app/(auth)/", "src/lib/auth.ts"],
        "infra":    ["Dockerfile", ".github/", "scripts/"],
    },
    "react": {
        "frontend": ["src/components/", "src/pages/", "src/views/"],
        "api":      ["src/api/", "src/services/", "server/"],
        "db":       ["prisma/", "migrations/", "src/lib/db.ts"],
        "infra":    ["Dockerfile", ".github/", "scripts/"],
    },
    "django": {
        "frontend": ["templates/", "static/", "staticfiles/"],
        "api":      ["api/", "views.py", "urls.py", "serializers.py"],
        "db":       ["migrations/", "models.py"],
        "auth":     ["users/", "accounts/", "authentication/"],
        "infra":    ["Dockerfile", ".github/", "scripts/", "requirements.txt"],
    },
    "fastapi": {
        "api":      ["routers/", "api/", "endpoints/", "main.py"],
        "db":       ["models/", "migrations/", "database.py", "alembic/"],
        "auth":     ["auth/", "security.py"],
        "infra":    ["Dockerfile", ".github/", "requirements.txt"],
    },
    "rails": {
        "frontend": ["app/views/", "app/assets/", "app/javascript/"],
        "api":      ["app/controllers/", "app/serializers/", "config/routes.rb"],
        "db":       ["db/migrate/", "db/schema.rb", "app/models/"],
        "auth":     ["app/controllers/sessions_controller.rb", "app/models/user.rb"],
        "infra":    ["Dockerfile", ".github/", "config/"],
    },
    "go": {
        "api":      ["cmd/", "internal/handlers/", "internal/api/"],
        "db":       ["internal/store/", "migrations/", "internal/models/"],
        "auth":     ["internal/auth/", "internal/middleware/"],
        "infra":    ["Dockerfile", ".github/", "Makefile"],
    },
    "default": {
        "frontend": ["src/", "frontend/", "client/", "web/"],
        "api":      ["api/", "server/", "backend/"],
        "db":       ["migrations/", "database/", "db/"],
        "auth":     ["auth/", "authentication/"],
        "infra":    ["Dockerfile", ".github/", "scripts/"],
    },
}

def _extract_version(deps_lower: dict, key: str) -> str | None:
    """Extract semver major.minor from a dep like '^15.2.0' -> '15.2'."""
    raw = deps_lower.get(key, "")
    clean = raw.lstrip("^~>=<")
    parts = clean.split(".")
    if parts and parts[0].isdigit():
        return ".".join(parts[:2]) if len(parts) >= 2 else parts[0]
    return None


def detect():
    r = _build_profile()
    _print_profile(r)
    return r

def detect_and_save():
    """Detect stack and save to .claude/config/stack-profile.json"""
    r = _build_profile()
    _print_profile(r)
    _save_profile(r)
    return r

def _save_profile(profile: dict):
    """Save stack profile atomically — Windows-safe."""
    import os, tempfile
    config_dir = CLAUDE_DIR / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    out = config_dir / "stack-profile.json"
    fd, tmp_path = tempfile.mkstemp(dir=config_dir, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(json.dumps(profile, indent=2))
        os.replace(tmp_path, out)  # atomic on POSIX; replaces existing on Windows
    except Exception:
        try: os.unlink(tmp_path)
        except OSError: pass
        raise
    print(f"\n  ✓ Stack profile saved: .claude/config/stack-profile.json")

def load_profile() -> dict:
    """Load saved stack profile. Returns empty dict if not found."""
    path = CLAUDE_DIR / "config" / "stack-profile.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {}

def _build_profile() -> dict:
    r = {
        "language": "unknown",
        "framework": "unknown",
        "framework_version": None,
        "platform": "web",
        "router": None,
        "db": None,
        "db_orm": None,
        "auth_library": None,
        "package_manager": None,
        "test_framework": None,
        "deploy_target": None,
        "has_docker": False,
        "has_ci": False,
        "tailwind": False,
        "tailwind_version": None,
        "has_shadcn": False,
        "has_framer": False,
        "has_three": False,
        "has_typescript": False,
        "styling": [],
        "components": [],
        "src_dir": None,
        "rule_sets": [],
        "domain_map": {},
        "build_commands": {
            "dev": None,
            "build": None,
            "test": None,
            "lint": None,
        },
        "detected_at": None,
    }

    from datetime import datetime, timezone
    r["detected_at"] = datetime.now(timezone.utc).isoformat()

    # ── Infrastructure checks (universal) ────────────────────────────────────
    r["has_docker"] = (ROOT / "Dockerfile").exists() or (ROOT / "docker-compose.yml").exists()
    r["has_ci"] = (ROOT / ".github" / "workflows").exists() or (ROOT / ".gitlab-ci.yml").exists()

    # ── Python detection ──────────────────────────────────────────────────────
    if _is_python_project():
        return _detect_python(r)

    # ── Ruby detection ────────────────────────────────────────────────────────
    if (ROOT / "Gemfile").exists():
        return _detect_ruby(r)

    # ── Go detection ──────────────────────────────────────────────────────────
    if (ROOT / "go.mod").exists():
        return _detect_go(r)

    # ── PHP detection ─────────────────────────────────────────────────────────
    if (ROOT / "composer.json").exists():
        return _detect_php(r)

    # ── Flutter / Dart ────────────────────────────────────────────────────────
    if (ROOT / "pubspec.yaml").exists():
        return _detect_flutter(r)

    # ── SwiftUI ───────────────────────────────────────────────────────────────
    if list(ROOT.glob("*.xcodeproj")) or list(ROOT.glob("*.xcworkspace")):
        return _detect_swift(r)

    # ── JS/TS detection ───────────────────────────────────────────────────────
    if (ROOT / "package.json").exists():
        return _detect_js(r)

    # ── Fallback ──────────────────────────────────────────────────────────────
    r["rule_sets"] = ["security-checklist"]
    r["domain_map"] = DOMAIN_MAPS["default"]
    return r

def _is_python_project() -> bool:
    return any([
        (ROOT / "requirements.txt").exists(),
        (ROOT / "pyproject.toml").exists(),
        (ROOT / "setup.py").exists(),
        (ROOT / "Pipfile").exists(),
        (ROOT / "manage.py").exists(),
        bool(list(ROOT.glob("*.py"))[:1]),
    ])

def _detect_python(r: dict) -> dict:
    r["language"] = "python"
    r["platform"] = "backend"

    # Package manager
    if (ROOT / "poetry.lock").exists() or (ROOT / "pyproject.toml").exists():
        r["package_manager"] = "poetry"
        r["build_commands"]["dev"] = "poetry run python manage.py runserver"
    elif (ROOT / "Pipfile").exists():
        r["package_manager"] = "pipenv"
    else:
        r["package_manager"] = "pip"

    # Read all config files
    req_text = ""
    for req_file in ["requirements.txt", "requirements/base.txt", "requirements/local.txt"]:
        p = ROOT / req_file
        if p.exists():
            req_text += p.read_text(errors="ignore").lower()

    pyproject_text = ""
    if (ROOT / "pyproject.toml").exists():
        pyproject_text = (ROOT / "pyproject.toml").read_text(errors="ignore").lower()

    all_deps = req_text + pyproject_text

    # Django
    if (ROOT / "manage.py").exists() or "django" in all_deps:
        r["framework"] = "django"
        # Extract Django version from requirements
        m = re.search(r'django[>=<~!^]+([0-9]+\.[0-9]+)', all_deps, re.IGNORECASE)
        r["framework_version"] = m.group(1) if m else None
        r["build_commands"] = {
            "dev":   "python manage.py runserver",
            "build": "python manage.py collectstatic --noinput",
            "test":  "python manage.py test",
            "lint":  "flake8 . || ruff check .",
        }
        # Django sub-frameworks
        if "rest_framework" in all_deps or "djangorestframework" in all_deps:
            r["components"].append("django-rest-framework")
        if "ninja" in all_deps:
            r["components"].append("django-ninja")
        if "celery" in all_deps:
            r["components"].append("celery")
        if "channels" in all_deps:
            r["components"].append("django-channels")
        # DB
        if "psycopg" in all_deps or "postgresql" in all_deps:
            r["db"] = "postgresql"
        elif "mysqlclient" in all_deps or "pymysql" in all_deps:
            r["db"] = "mysql"
        else:
            r["db"] = "sqlite"
        r["db_orm"] = "django-orm"
        # Test
        if "pytest" in all_deps:
            r["test_framework"] = "pytest"
            r["build_commands"]["test"] = "pytest"
        else:
            r["test_framework"] = "django-test"
        _add_rule_sets(r, ["django"])

    # FastAPI
    elif "fastapi" in all_deps:
        r["framework"] = "fastapi"
        r["build_commands"] = {
            "dev":   "uvicorn main:app --reload",
            "build": "pip install -r requirements.txt",
            "test":  "pytest",
            "lint":  "ruff check . && mypy .",
        }
        r["test_framework"] = "pytest"
        if "sqlalchemy" in all_deps:
            r["db_orm"] = "sqlalchemy"
            r["components"].append("sqlalchemy")
        if "alembic" in all_deps:
            r["components"].append("alembic")
        if "pydantic" in all_deps:
            r["components"].append("pydantic")
        if "psycopg" in all_deps:
            r["db"] = "postgresql"
        _add_rule_sets(r, ["fastapi"])

    # Flask
    elif "flask" in all_deps:
        r["framework"] = "flask"
        r["build_commands"] = {
            "dev":   "flask run --debug",
            "build": "pip install -r requirements.txt",
            "test":  "pytest",
            "lint":  "ruff check .",
        }
        r["test_framework"] = "pytest"
        if "flask-sqlalchemy" in all_deps or "sqlalchemy" in all_deps:
            r["db_orm"] = "sqlalchemy"
        _add_rule_sets(r, ["flask", "python"])

    else:
        r["framework"] = "python"
        r["build_commands"] = {
            "dev":   "python main.py",
            "build": "pip install -r requirements.txt",
            "test":  "pytest",
            "lint":  "ruff check .",
        }
        r["test_framework"] = "pytest"
        _add_rule_sets(r, ["python"])

    _add_universal_rule_sets(r)
    r["domain_map"] = DOMAIN_MAPS.get(r["framework"], DOMAIN_MAPS["default"])
    return r

def _detect_ruby(r: dict) -> dict:
    r["language"] = "ruby"
    r["package_manager"] = "bundler"
    gemfile = (ROOT / "Gemfile").read_text(errors="ignore").lower()

    if "rails" in gemfile:
        r["framework"] = "rails"
        m = re.search(r"rails.*?([0-9]+\.[0-9]+)", gemfile)
        r["framework_version"] = m.group(1) if m else None
        r["platform"] = "fullstack"
        r["build_commands"] = {
            "dev":   "rails server",
            "build": "bundle exec rake assets:precompile",
            "test":  "bundle exec rspec",
            "lint":  "bundle exec rubocop",
        }
        r["test_framework"] = "rspec" if "rspec" in gemfile else "minitest"
        r["db_orm"] = "activerecord"
        if "pg" in gemfile:
            r["db"] = "postgresql"
        elif "mysql2" in gemfile:
            r["db"] = "mysql"
        else:
            r["db"] = "sqlite"
        if "devise" in gemfile:
            r["auth_library"] = "devise"
            r["components"].append("devise")
        if "sidekiq" in gemfile:
            r["components"].append("sidekiq")
        _add_rule_sets(r, ["rails"])
    else:
        r["framework"] = "sinatra"
        r["build_commands"] = {
            "dev":   "ruby app.rb",
            "build": "bundle install",
            "test":  "bundle exec rspec",
            "lint":  "bundle exec rubocop",
        }
        _add_rule_sets(r, ["sinatra"])

    _add_universal_rule_sets(r)
    r["domain_map"] = DOMAIN_MAPS.get(r["framework"], DOMAIN_MAPS["default"])
    return r

def _detect_go(r: dict) -> dict:
    r["language"] = "go"
    r["package_manager"] = "go-modules"
    r["platform"] = "backend"

    go_mod = (ROOT / "go.mod").read_text(errors="ignore")
    module_name = ""
    for line in go_mod.splitlines():
        if line.startswith("module "):
            module_name = line.split()[1]
            break

    r["framework"] = "go"
    r["build_commands"] = {
        "dev":   "go run ./cmd/...",
        "build": "go build ./...",
        "test":  "go test ./...",
        "lint":  "golangci-lint run",
    }
    r["test_framework"] = "go-test"

    # Detect popular Go frameworks/libs
    go_sum = ""
    if (ROOT / "go.sum").exists():
        go_sum = (ROOT / "go.sum").read_text(errors="ignore").lower()

    if "gin-gonic" in go_sum:
        r["components"].append("gin")
    if "echo" in go_sum:
        r["components"].append("echo")
    if "fiber" in go_sum:
        r["components"].append("fiber")
    if "chi" in go_sum:
        r["components"].append("chi")
    if "gorm" in go_sum:
        r["db_orm"] = "gorm"
        r["components"].append("gorm")
    if "sqlx" in go_sum:
        r["components"].append("sqlx")
    if "postgres" in go_sum or "pgx" in go_sum:
        r["db"] = "postgresql"

    _add_rule_sets(r, ["go"])
    _add_universal_rule_sets(r)
    r["domain_map"] = DOMAIN_MAPS["go"]
    return r

def _detect_php(r: dict) -> dict:
    r["language"] = "php"
    r["package_manager"] = "composer"
    r["platform"] = "fullstack"

    composer = {}
    try:
        composer = json.loads((ROOT / "composer.json").read_text(errors="ignore"))
    except Exception:
        pass
    deps = {**composer.get("require", {}), **composer.get("require-dev", {})}
    deps_lower = {k.lower(): v for k, v in deps.items()}

    if any("laravel" in k for k in deps_lower) or any("illuminate" in k for k in deps_lower):
        r["framework"] = "laravel"
        r["build_commands"] = {
            "dev":   "php artisan serve",
            "build": "composer install && npm run build",
            "test":  "php artisan test",
            "lint":  "./vendor/bin/phpstan analyse",
        }
        r["test_framework"] = "phpunit"
        r["db_orm"] = "eloquent"
        _add_rule_sets(r, ["laravel"])
    elif any("symfony" in k for k in deps_lower):
        r["framework"] = "symfony"
        r["build_commands"] = {
            "dev":   "symfony server:start",
            "build": "composer install",
            "test":  "php bin/phpunit",
            "lint":  "./vendor/bin/phpstan analyse",
        }
        _add_rule_sets(r, ["symfony"])
    else:
        r["framework"] = "php"
        _add_rule_sets(r, ["api"])

    _add_universal_rule_sets(r)
    r["domain_map"] = DOMAIN_MAPS["default"]
    return r

def _detect_flutter(r: dict) -> dict:
    r["language"] = "dart"
    r["framework"] = "flutter"
    r["platform"] = "cross-platform"
    r["package_manager"] = "pub"
    r["build_commands"] = {
        "dev":   "flutter run",
        "build": "flutter build apk",
        "test":  "flutter test",
        "lint":  "flutter analyze",
    }
    r["test_framework"] = "flutter-test"

    content = (ROOT / "pubspec.yaml").read_text(errors="ignore")
    for pkg in ["flutter_riverpod", "riverpod", "get_it", "bloc", "mobx", "go_router"]:
        if pkg in content:
            r["components"].append(pkg)

    _add_rule_sets(r, ["flutter"])
    _add_universal_rule_sets(r)
    r["domain_map"] = {
        "ui":     ["lib/screens/", "lib/widgets/", "lib/pages/"],
        "state":  ["lib/providers/", "lib/blocs/", "lib/cubits/"],
        "data":   ["lib/models/", "lib/repositories/", "lib/services/"],
        "infra":  ["android/", "ios/", "pubspec.yaml"],
    }
    return r

def _detect_swift(r: dict) -> dict:
    r["language"] = "swift"
    r["framework"] = "swiftui"
    r["platform"] = "ios"
    r["build_commands"] = {
        "dev":   "xcodebuild",
        "build": "xcodebuild -scheme MyApp",
        "test":  "xcodebuild test",
        "lint":  "swiftlint",
    }
    r["test_framework"] = "xctest"

    _add_rule_sets(r, ["swiftui"])
    _add_universal_rule_sets(r)
    r["domain_map"] = {
        "ui":    ["Views/", "Screens/"],
        "state": ["ViewModels/", "Stores/"],
        "data":  ["Models/", "Services/", "Repositories/"],
        "infra": ["Resources/", "Supporting Files/"],
    }
    return r

def _detect_js(r: dict) -> dict:
    try:
        pkg = json.loads((ROOT / "package.json").read_text())
    except Exception:
        r["rule_sets"] = ["react-guidelines", "ux-principles"]
        return r

    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    deps_lower = {k.lower(): v for k, v in deps.items()}
    scripts = pkg.get("scripts", {})

    # Package manager
    if (ROOT / "pnpm-lock.yaml").exists():
        r["package_manager"] = "pnpm"
    elif (ROOT / "yarn.lock").exists():
        r["package_manager"] = "yarn"
    elif (ROOT / "bun.lockb").exists():
        r["package_manager"] = "bun"
    else:
        r["package_manager"] = "npm"

    pm = r["package_manager"]

    # Language
    r["language"] = "typescript" if ("typescript" in deps_lower or (ROOT / "tsconfig.json").exists()) else "javascript"
    r["has_typescript"] = r["language"] == "typescript"

    # Framework detection
    if "next" in deps_lower:
        app_dirs = [ROOT / "app", ROOT / "src" / "app"]
        r["framework"] = "nextjs"
        r["framework_version"] = _extract_version(deps_lower, "next")
        r["router"] = "app-router" if any(d.exists() for d in app_dirs) else "pages-router"
        _add_rule_sets(r, ["nextjs"])
        r["platform"] = "fullstack"
    elif "remix" in deps_lower or "@remix-run/react" in deps_lower:
        r["framework"] = "remix"
        _add_rule_sets(r, ["remix"])
        r["platform"] = "fullstack"
    elif any(k in deps_lower for k in ["nuxt", "@nuxt/core"]):
        r["framework"] = "nuxt"
        _add_rule_sets(r, ["nuxt"])
    elif "vue" in deps_lower:
        r["framework"] = "vue"
        r["framework_version"] = _extract_version(deps_lower, "vue")
        _add_rule_sets(r, ["vue"])
    elif "@sveltejs/kit" in deps_lower:
        r["framework"] = "sveltekit"
        _add_rule_sets(r, ["sveltekit"])
    elif "svelte" in deps_lower:
        r["framework"] = "svelte"
        _add_rule_sets(r, ["svelte"])
    elif "gatsby" in deps_lower:
        r["framework"] = "gatsby"
        _add_rule_sets(r, ["gatsby"])
    elif "react-native" in deps_lower or "@react-native" in str(deps_lower):
        r["framework"] = "react-native"
        r["platform"] = "mobile"
        _add_rule_sets(r, ["react-native"])
    elif "react" in deps_lower:
        r["framework"] = "react-cra" if "react-scripts" in deps_lower else "react"
        r["framework_version"] = _extract_version(deps_lower, "react")
        _add_rule_sets(r, ["react"])
    elif "express" in deps_lower or "fastify" in deps_lower or "hono" in deps_lower:
        r["framework"] = "node-api"
        r["platform"] = "backend"
        _add_rule_sets(r, ["api"])

    # Styling
    if "tailwindcss" in deps_lower:
        ver = deps_lower.get("tailwindcss", "").lstrip("^~>=")
        r["tailwind"] = True
        r["tailwind_version"] = ver[0] if ver else "3"
        r["styling"].append(f"tailwind-v{r['tailwind_version']}")
        _add_rule_sets(r, ["tailwind"])
    if (ROOT / "components.json").exists():
        r["has_shadcn"] = True
        r["components"].append("shadcn/ui")
        _add_rule_sets(r, ["shadcn"])

    # Animation
    if "framer-motion" in deps_lower or "motion" in deps_lower:
        r["has_framer"] = True
        r["components"].append("framer-motion")
    if "three" in deps_lower or "three.js" in deps_lower:
        r["has_three"] = True
        r["components"].append("three.js")

    # DB / ORM
    if "prisma" in deps_lower or "@prisma/client" in deps_lower:
        r["db_orm"] = "prisma"
        r["components"].append("prisma")
        r["db"] = "postgresql"
    elif "drizzle-orm" in deps_lower:
        r["db_orm"] = "drizzle"
        r["components"].append("drizzle-orm")
    elif "@supabase/supabase-js" in deps_lower:
        r["db"] = "supabase/postgresql"
        r["components"].append("supabase")

    # Auth
    if "next-auth" in deps_lower or "@auth/core" in deps_lower:
        r["auth_library"] = "next-auth"
        r["components"].append("next-auth")
    elif "@clerk/nextjs" in deps_lower or "@clerk/clerk-react" in deps_lower:
        r["auth_library"] = "clerk"
        r["components"].append("clerk")

    # Test framework
    if "vitest" in deps_lower:
        r["test_framework"] = "vitest"
    elif "jest" in deps_lower or "@jest/core" in deps_lower:
        r["test_framework"] = "jest"
    elif "mocha" in deps_lower:
        r["test_framework"] = "mocha"

    # Build commands from package.json scripts
    r["build_commands"] = {
        "dev":   f"{pm} run dev" if "dev" in scripts else f"{pm} start",
        "build": f"{pm} run build" if "build" in scripts else None,
        "test":  f"{pm} {'run ' if pm != 'npm' else ''}test" if "test" in scripts else None,
        "lint":  f"{pm} run lint" if "lint" in scripts else None,
    }

    # Source directory
    for d in ["src", "app", "pages", "components"]:
        if (ROOT / d).exists():
            r["src_dir"] = d
            break

    # Deploy target hints
    if (ROOT / "vercel.json").exists() or (ROOT / ".vercel").exists():
        r["deploy_target"] = "vercel"
    elif (ROOT / "railway.json").exists() or (ROOT / "railway.toml").exists():
        r["deploy_target"] = "railway"
    elif (ROOT / "fly.toml").exists():
        r["deploy_target"] = "fly.io"
    elif (ROOT / "netlify.toml").exists():
        r["deploy_target"] = "netlify"
    elif r["has_docker"]:
        r["deploy_target"] = "docker"

    _add_universal_rule_sets(r)
    r["domain_map"] = DOMAIN_MAPS.get(r["framework"], DOMAIN_MAPS.get("react", DOMAIN_MAPS["default"]))
    return r

def _add_rule_sets(r: dict, keys: list):
    for key in keys:
        for rs in RULE_SETS.get(key, []):
            if rs not in r["rule_sets"]:
                r["rule_sets"].append(rs)

def _add_universal_rule_sets(r: dict):
    """Always add security and testing patterns."""
    for rs in ["security-checklist", "testing-patterns"]:
        if rs not in r["rule_sets"]:
            r["rule_sets"].append(rs)
    if r.get("db") or r.get("db_orm"):
        if "sql-patterns" not in r["rule_sets"]:
            r["rule_sets"].append("sql-patterns")

def _print_profile(r: dict):
    fw = r.get("framework", "unknown")
    lang = r.get("language", "unknown")
    platform = r.get("platform", "web")

    print(f"\n╔══════════════════════════════════════════════════════╗")
    print(f"║       APEX STACK ANALYSIS                            ║")
    print(f"╚══════════════════════════════════════════════════════╝\n")
    print(f"  Language:      {lang}")
    ver_str = f" v{r['framework_version']}" if r.get("framework_version") else ""
    print(f"  Framework:     {fw}{ver_str}" + (f" ({r['router']})" if r.get("router") else ""))
    print(f"  Platform:      {platform}")

    if r.get("db"):
        print(f"  Database:      {r['db']}" + (f" via {r['db_orm']}" if r.get("db_orm") else ""))
    if r.get("auth_library"):
        print(f"  Auth:          {r['auth_library']}")
    if r.get("test_framework"):
        print(f"  Tests:         {r['test_framework']}")
    if r.get("package_manager"):
        print(f"  Pkg manager:   {r['package_manager']}")
    if r.get("deploy_target"):
        print(f"  Deploy:        {r['deploy_target']}")
    if r.get("tailwind"):
        print(f"  Tailwind:      v{r['tailwind_version']}")
    if r.get("components"):
        print(f"  Components:    {', '.join(r['components'][:6])}")
    if r.get("has_docker"):
        print(f"  Docker:        ✓")
    if r.get("has_ci"):
        print(f"  CI/CD:         ✓")

    print(f"\n  Rule sets loaded ({len(r['rule_sets'])}):")
    for rs in r["rule_sets"]:
        print(f"    → {rs}")

    cmds = r.get("build_commands", {})
    if any(cmds.values()):
        print(f"\n  Build commands:")
        for k, v in cmds.items():
            if v:
                print(f"    {k:8} {v}")

    print()
    if "--json" in sys.argv:
        print("STACK_JSON:" + json.dumps(r))

if __name__ == "__main__":
    if "--save" in sys.argv:
        detect_and_save()
    elif "--json" in sys.argv:
        r = _build_profile()
        _print_profile(r)
    else:
        detect()
