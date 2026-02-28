# Commit Message Reference

Detailed reference for composing effective Git commit messages.

## Chris Beames' Seven Rules

### Rule 1: Separate Subject from Body

Always separate the subject line from the body with a blank line.

```
feat(auth): add login endpoint

Implement the /login endpoint with JWT token generation.
This is the body of the commit message.
```

Without the blank line, many Git tools cannot display correctly.

### Rule 2: Subject Line Under 50 Characters

Keep it concise. If you can't summarize in 50 chars, your commit is
likely doing too much.

**Good:** `feat(auth): add OAuth2 login`
**Bad:** `feat(auth): add OAuth2 login flow using GitHub as identity provider`

### Rule 3: Capitalize Subject Line

Start with a capital letter.

**Good:** `Add new feature`
**Bad:** `add new feature`

### Rule 4: No Period at End

Don't punctuate the subject line.

**Good:** `Add user authentication`
**Bad:** `Add user authentication.`

### Rule 5: Imperative Mood

Write as if giving a command. The commit should complete the sentence:
"If applied, this commit will __ your codebase."

**Good:** `Add user authentication`
**Bad:** `Added user authentication` / `Adding user authentication`

### Rule 6: Wrap Body at 72 Characters

Git does this automatically for you if you configure it:

```bash
git config --global core.wrap 72
```

Or use `git commit` without `-m` to open an editor.

### Rule 7: Explain What and Why

The diff shows what changed. The commit message explains why.

**Don't:**
```python
# Changed variable name from x to user_id
```

**Do:**
```python
# Rename x to user_id for clarity
# The previous name was ambiguous in the context of
# multi-user authentication flows
```

## Conventional Commits Spec

Format: `<type>(<scope>): <subject>`

### Type Enum

- `feat`: New feature for the user
- `fix`: Bug fix for the user
- `docs`: Documentation changes only
- `style`: Formatting, no code change (white-space, etc.)
- `refactor`: Code change that neither fixes nor adds
- `perf`: Code change that improves performance
- `test`: Adding or correcting tests
- `build`: Changes to build system or dependencies
- `ci`: Changes to CI configuration
- `chore`: Other changes that don't modify src/test files
- `revert`: Reverts a previous commit

### Scope

Optional. Use to add context:

- File or module: `feat(auth):`, `fix(api):`
- Component: `feat(ui):`, `fix(docs):`
- Process: `feat(ci):`, `refactor(tests):`

### Breaking Changes

In body or footer:

```
BREAKING CHANGE: API endpoint /v1/users is removed
Use /v2/users instead
```

Or with footer:

```
feat(auth)!: change token format

BREAKING CHANGE: Tokens are now JWT instead of opaque
```

## Task ID Integration

Extract task IDs from beads:

```bash
# List in-progress tasks
bd list --status=in_progress

# Get task ID
bd show <task-id>
```

Include in commit:

- Subject: `feat(gtas-123): add feature`
- Footer: `Closes gtas-123`

## Validation Scripts

### Subject Length Check

```bash
subject_len() {
  local msg="$1"
  local subject
  subject=$(echo "$msg" | head -1)
  if [ ${#subject} -gt 50 ]; then
    echo "Subject exceeds 50 chars: ${#subject}"
    return 1
  fi
}
```

### Body Wrap Check

```bash
body_wrap_check() {
  local msg="$1"
  echo "$msg" | tail -n +3 | while IFS= read -r line; do
    if [ ${#line} -gt 72 ]; then
      echo "Line exceeds 72 chars: $line"
      return 1
    fi
  done
}
```

### Full Validation

```bash
validate_commit_msg() {
  local file="$1"
  local lines
  lines=$(wc -l < "$file")
  
  # Check blank line separation
  if [ "$lines" -gt 1 ]; then
    if ! sed -n '2p' "$file" | grep -q '^$'; then
      echo "Error: Subject and body not separated by blank line"
      return 1
    fi
  fi
  
  # Check subject length
  subject=$(head -1 "$file")
  if [ ${#subject} -gt 50 ]; then
    echo "Error: Subject exceeds 50 chars"
    return 1
  fi
  
  # Check imperative mood (basic heuristic)
  if echo "$subject" | grep -qE '^(Add|Update|Fix|Remove|Change|Revert)'; then
    :  # Good
  else
    echo "Warning: Subject may not be imperative"
  fi
  
  return 0
}
```

## Good Examples

### Minimal (trivial change)
```
fix typo in README
```

### Standard
```
feat(auth): implement JWT token refresh

Add automatic token refresh before expiration.
Improves UX by preventing login interruptions.

Closes gtas-456
```

### With scope and breaking change
```
feat(auth)!: migrate to OAuth2

BREAKING CHANGE: Local authentication is removed.
All users must use OAuth2 providers.

Closes gtas-123
Refs gtas-456
```

## Bad Examples

### Too long
```
feat: add ability for users to authenticate using their GitHub
accounts through OAuth2 flow with proper token handling and refresh
```

### Not imperative
```
Added user authentication
```

### No blank line separation
```
feat(auth): add login
This commit adds login functionality.
```

### Explains how
```
refactor: changed the for loop to use map() because
it's more Pythonic and efficient
```

### Missing context
```
fix: null pointer
```

## Tools

- `commitlint`: Validate conventional commits
- `gitlint`: Git hook for commit message validation
- `cz-cli`: Interactive commitizen prompts
