---
name: commit-msg-craft
description: >
  Helps agents compose Git commit log messages following Chris Beames'
  seven rules and conventional commits format. Use when writing commit
  messages, validating commit log format, extracting task IDs from
  beads, formatting commit bodies, or enforcing commit conventions.
license: Apache-2.0
---

# Commit Msg Craft

This skill helps agents write effective Git commit messages following Chris
Beames' seven rules and conventional commits format.

**Produces:** Well-structured commit messages that communicate intent clearly.

## The Seven Rules

Every commit message must follow these rules:

1. **Separate subject from body with a blank line**
2. **Subject line under 50 characters**
3. **Capitalize the subject line**
4. **No period at end of subject line**
5. **Use imperative mood** ("add" not "added" or "adds")
6. **Wrap body at 72 characters**
7. **Explain what and why, not how**

## Conventional Commits Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code change that neither fixes nor adds |
| `test` | Adding or updating tests |
| `chore` | Maintenance, deps, build changes |
| `perf` | Performance improvement |
| `ci` | CI configuration changes |
| `revert` | Revert a previous commit |

### Scopes

Optional but recommended. Common scopes: `api`, `ui`, `auth`, `db`, `docs`.

### Subject Line Rules

- Imperative mood: "add feature" not "added feature"
- Lowercase after type/scope
- No trailing period
- Under 50 characters

### Body Rules

- Explain **what** and **why**, not **how**
- Wrap at 72 characters
- Use present tense: "change" not "changed"

### Footer Rules

Breaking changes: `BREAKING CHANGE: <description>`
Issue references: `Closes #123`, `Refs #456`

## Task ID Extraction

Extract task IDs from beads for commit scope:

```bash
bd list --status=in_progress
```

Include task ID in commit: `feat(gtas-123): add feature`

## Validation

Validate commit message format:

```bash
# Check subject length
echo "$msg" | head -1 | wc -c  # <= 51 (including newline)

# Check body wrap
echo "$msg" | tail -n +3 | while read -r line; do
  [ ${#line} -le 72 ] || echo "line too long: $line"
done
```

## Examples

### Feature commit
```
feat(auth): add OAuth2 login flow

Implement OAuth2 authentication using GitHub as provider.
Includes token refresh and secure session management.

Closes gtas-123
```

### Bug fix
```
fix: resolve nil pointer in user service

The user service was dereferencing nil when the user ID
was not found in the database. Added proper error handling
and return early pattern.

Fixes gtas-456
```

### Documentation
```
docs: update API endpoints reference

Add new /v2/users endpoint to the API documentation.
Includes request/response examples for each method.
```

### Refactor
```
refactor(db): extract query builder

Move SQL query construction to separate module for
reusability. No functional changes.
```

## When NOT to Use

- Commit message is trivial (typo fix, whitespace) → keep it short
- Large rewrite → split into smaller, logical commits
- Multi-topic change → separate into distinct commits
