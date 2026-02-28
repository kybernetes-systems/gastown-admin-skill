# Script Design for Agent Skills

Patterns for writing scripts that agents can execute reliably. Consult this during
Stage 3 (REFINE) when writing or evaluating scripts for a target skill. For
spec constraints see `spec-summary.md`.

---

## Core Requirement: No Interactive Prompts

**Agents run non-interactive shells.** Any script that pauses for input (`input()`,
`read`, `gets`, confirmation prompts) will hang indefinitely or crash.

- Never call `input()`, `readline()`, or equivalents
- Never use `--interactive` or `-i` flags that trigger prompts
- If confirmation is needed for destructive operations, require an explicit
  `--yes` / `--force` flag; default to dry-run or abort
- Test with `echo "" | uv run script.py` to verify non-interactive behavior

---

## `--help` as Primary Interface Documentation

The `--help` output is the script's contract with the agent. Agents read `--help`
to understand inputs, outputs, exit codes, and options -- not README files.

Requirements for `--help`:
- Usage line with all required and optional arguments
- Description of what the script does
- All flags documented with types and defaults
- Exit codes listed explicitly
- Output format described (JSON, TSV, plain text)
- Example invocations

```
Usage: uv run scripts/scaffold.py [OPTIONS]

Generate a new Agent Skill directory.

Options:
  --name TEXT       Skill name (kebab-case, 1-64 chars) [required]
  --output PATH     Output directory [default: .]
  --dry-run         Show what would be created without writing files
  --yes             Skip confirmation for destructive operations
  --format TEXT     Output format: json|text [default: text]
  --help            Show this message and exit.

Exit codes:
  0   Success
  1   Validation error (invalid name, path conflict)
  2   Filesystem error (permission denied, disk full)

Examples:
  uv run scripts/scaffold.py --name my-skill
  uv run scripts/scaffold.py --name my-skill --dry-run
```

---

## Helpful Error Messages

When a script fails, the agent needs three things to recover:

1. What went wrong (specific, not generic)
2. What was expected or valid
3. What to try next

```python
# Bad
raise ValueError("Invalid name")

# Good
raise ValueError(
    f"Invalid skill name '{name}': names must be lowercase alphanumeric "
    f"with hyphens (1-64 chars), no leading/trailing/consecutive hyphens. "
    f"Got {len(name)} chars. Example: 'my-skill'"
)
```

Always exit with a non-zero code on error so the agent can detect failure.

---

## Structured Output: JSON to stdout, Diagnostics to stderr

Agents parse script output programmatically. Mixed human-readable and machine-
parseable output breaks parsing.

- **stdout**: structured data only (JSON, CSV, TSV)
- **stderr**: progress messages, warnings, diagnostics, human-readable logs
- **Never** mix prose and JSON on stdout

```python
import json, sys

# Progress to stderr -- agent ignores unless debugging
print("Scaffolding skill directory...", file=sys.stderr)

# Result to stdout -- agent parses this
result = {"status": "ok", "path": str(output_path), "files_created": files}
print(json.dumps(result, indent=2))
```

For text-mode output (default for human review), structure is still expected:
use consistent line formats the agent can parse with simple string operations.

---

## Idempotency: Create If Not Exists

Scripts that create files or directories must be safe to run multiple times.
"Create if not exists" is the default behavior. Never silently overwrite without
`--force`.

```python
output_dir.mkdir(parents=True, exist_ok=True)  # Good: idempotent

if output_dir.exists() and not args.force:
    print(f"Error: {output_dir} already exists. Use --force to overwrite.",
          file=sys.stderr)
    sys.exit(1)
```

---

## Dry-Run Support

Destructive or generative operations must support `--dry-run`. Dry-run prints
what would happen without doing it. Essential for agent confidence before
committing to file system changes.

```python
if args.dry_run:
    print(json.dumps({"dry_run": True, "would_create": planned_files}))
    sys.exit(0)
```

Dry-run exit code is 0 (success) -- it completed its job of showing the plan.

---

## Exit Codes

Document all exit codes in `--help`. Use consistent conventions:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/input error (bad arguments, validation failure) |
| 2 | Environment error (file not found, permission denied) |
| 3+ | Script-specific codes (document in --help) |

Never exit 0 on partial failure. The agent uses exit codes to detect errors;
a silent exit 0 with error output on stderr will cause silent data loss.

---

## Predictable Output Size

Large stdout dumps break agent context windows. Default to summaries; provide
pagination for large result sets.

```
Options:
  --limit INT     Max results to return [default: 50]
  --offset INT    Skip first N results [default: 0]
  --output PATH   Write full output to file instead of stdout
```

```python
if len(results) > args.limit:
    truncated = results[args.offset:args.offset + args.limit]
    meta = {"total": len(results), "returned": len(truncated),
            "offset": args.offset, "limit": args.limit}
    print(json.dumps({"meta": meta, "results": truncated}))
```

---

## Self-Contained Dependency Patterns

Scripts must not require global package installation. Use inline dependency
declarations so agents can run scripts without setup steps.

### Python -- PEP 723 Inline Metadata (uv run)

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "click>=8.0",
#   "rich>=13.0",
# ]
# ///

import click
```

Invocation: `uv run scripts/scaffold.py --name my-skill`

`uv` resolves and caches dependencies automatically. No venv activation required.

### Deno -- npm: Specifiers

```typescript
import { parse } from "npm:yaml@2.3.1";
import { z } from "npm:zod@3.22.0";
```

Invocation: `deno run --allow-read --allow-write scripts/validate.ts`

### Bun -- Auto-install

```typescript
import yaml from "yaml"; // Bun installs from bun.lockb or package.json
```

Invocation: `bun run scripts/validate.ts`

### Ruby -- bundler/inline

```ruby
require "bundler/inline"
gemfile do
  source "https://rubygems.org"
  gem "yaml", "~> 0.2"
end
```

Invocation: `ruby scripts/scaffold.rb`

---

## One-Off Commands (No Project Setup)

For simple operations, use runner tools that fetch and execute without install:

| Runner | Language | Invocation |
|--------|----------|-----------|
| `uvx` | Python | `uvx ruff check .` |
| `npx` | Node.js | `npx --yes prettier --check SKILL.md` |
| `bunx` | Bun/Node | `bunx prettier --check SKILL.md` |
| `deno run` | Deno | `deno run --allow-net npm:cowsay "hello"` |
| `go run` | Go | `go run github.com/user/tool@v1.0.0 args` |

Pin versions explicitly in one-off commands to ensure reproducibility:
```bash
uvx ruff@0.4.4 check .
npx prettier@3.2.5 --check SKILL.md
```
