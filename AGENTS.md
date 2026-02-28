# AGENTS.md -- gastown-admin-skill

## OpenCode Tool Permissions

This file declares tool permissions for OpenCode (and compatible harnesses).
Other harnesses (Claude Code, GitHub Copilot, Goose, Aider, Amp) ignore this file.

```yaml
allowed-tools:
  - read
  - edit
  - write
  - bash: git
  - bash: uv
  - bash: python3
  - bash: agentskills
```

The bash tools are scoped to specific commands:
- `git` -- read repo state, commit changes (no push; no remote configured)
- `uv` -- run scripts via `uv run scripts/<name>.py`
- `python3` -- run scripts directly via `python3 scripts/<name>.py`
- `agentskills` -- validate skill directories via `agentskills validate`

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status=in_progress  # Claim work
bd close <id>         # Complete work
bd sync --flush-only  # Export beads to JSONL
```

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below.
Work is NOT complete until `bd sync --flush-only` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** -- Create bd issues for anything needing follow-up
2. **Run quality gates** (if code changed) -- Validate scripts, check SKILL.md line count
3. **Update issue status** -- Close finished work, update in-progress items
4. **Export beads** -- This is MANDATORY:
   ```bash
   bd sync --flush-only
   ```
5. **Verify** -- All changes committed locally

**CRITICAL RULES:**
- Work is NOT complete until `bd sync --flush-only` succeeds
- NEVER stop before syncing -- that leaves issue state unexported
- NEVER say "ready to sync when you are" -- YOU must sync
- No git remote is configured -- do NOT attempt `git push`
- Use beads for ALL task tracking -- do NOT use TodoWrite, TaskCreate, or markdown task lists
- Create a beads issue BEFORE writing code -- issue first, then work
