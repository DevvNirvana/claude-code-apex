# Security Checklist — Universal

## Secrets & Configuration
- [ ] No secrets in source code (API keys, passwords, tokens, connection strings)
- [ ] `.env` in `.gitignore` — only `.env.example` committed with placeholders
- [ ] Secrets loaded from environment variables — never hardcoded, never in config files
- [ ] Rotate secrets immediately if accidentally committed to git
- [ ] Use secret managers in production (AWS Secrets Manager, Vault, Doppler)

## Authentication
- [ ] Passwords hashed with bcrypt/argon2 (cost factor ≥ 12) — never MD5/SHA1
- [ ] JWT tokens have expiry (`exp` claim) — max 1 hour for access tokens
- [ ] Refresh tokens stored securely (httpOnly cookie or encrypted store)
- [ ] Session invalidation on logout (server-side session or token blacklist)
- [ ] Rate limiting on: login (5/min), register (3/min), password reset (3/hour)
- [ ] Account lockout after N failed attempts (or CAPTCHA challenge)
- [ ] Secure password reset: time-limited tokens, single use, emailed to verified address

## Authorization
- [ ] Every authenticated endpoint checks permissions — not just authentication
- [ ] Object-level authorization: user can only access their own resources
- [ ] Admin endpoints protected by role check — not just auth check
- [ ] Never trust user-supplied IDs without ownership verification

## Input Validation & Injection Prevention
- [ ] All user input validated and sanitized before use
- [ ] SQL queries parameterized — never string-interpolated
- [ ] File uploads: validate type (magic bytes, not just extension), size, and content
- [ ] HTML output escaped — never render raw user content as HTML
- [ ] XSS prevention: Content-Security-Policy header configured
- [ ] No `eval()`, `exec()`, or shell execution with user input

## API & Network Security
- [ ] HTTPS enforced — HTTP redirected to HTTPS
- [ ] CORS configured explicitly — never `Access-Control-Allow-Origin: *` in production
- [ ] CSRF protection on all mutation endpoints (POST/PUT/PATCH/DELETE)
- [ ] Security headers: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`
- [ ] Rate limiting on all public endpoints
- [ ] Error responses don't expose stack traces, SQL, or file paths

## Data Protection
- [ ] PII data identified and documented
- [ ] Sensitive data encrypted at rest (SSN, payment info, health data)
- [ ] Logs don't contain passwords, tokens, or full PII
- [ ] Database backups encrypted
- [ ] Principle of least privilege on DB credentials (app user ≠ admin user)

## Dependency Security
- [ ] `npm audit` / `pip-audit` / `bundle audit` — no high/critical vulnerabilities
- [ ] Dependencies pinned or locked (package-lock.json, Pipfile.lock, Gemfile.lock)
- [ ] Automated dependency updates configured (Dependabot, Renovate)

## Secrets Scanning Patterns
High-entropy strings that indicate leaked secrets:
```bash
# Run before every deploy
grep -rE \
  'sk-[A-Za-z0-9]{32,}|AKIA[A-Z0-9]{16}|ghp_[A-Za-z0-9]{36}|xox[baprs]-[A-Za-z0-9-]+|-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY|password\s*[:=]\s*["\x27][^"\x27]{8,}|secret\s*[:=]\s*["\x27][^"\x27]{8,}|api_key\s*[:=]\s*["\x27][^"\x27]{8,}' \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" \
  --include="*.rb" --include="*.go" --include="*.env" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor \
  . 2>/dev/null | grep -v ".env.example" | grep -v "# example"
```
