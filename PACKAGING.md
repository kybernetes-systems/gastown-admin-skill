# Packaging & Distribution

How to package `gastown-admin-skill` for distribution and installation across harnesses.

## Quick Package

Create a distributable archive:

```bash
# As tar.gz (Unix/Mac/Linux)
tar -czf gastown-admin-skill.tar.gz gastown-admin-skill/

# As zip (Windows/cross-platform)
zip -r gastown-admin-skill.zip gastown-admin-skill/
```

The resulting archive is ready to ship. Extract it in the target location per harness (see README.md Installation section).

## Archive Contents

The packaged skill includes:

```
gastown-admin-skill/
├── SKILL.md                     # Required: Skill metadata and instructions
├── README.md                    # Installation and overview
├── AGENTS.md                    # OpenCode tool permissions shim
├── BLUEPRINT.md                 # Architecture decisions
├── LICENSE.txt                  # Apache-2.0 license
├── PACKAGING.md                 # This file
├── .source.json                 # Provenance metadata
├── references/                  # T3 reference documentation
│   ├── spec-summary.md
│   ├── harness-compat.md
│   ├── description-craft.md
│   ├── script-design.md
│   └── security-checklist.md
├── scripts/                     # Executable tools
│   ├── scaffold.py
│   ├── validate_skill.py
│   ├── token_estimate.py
│   ├── audit_disclosure.py
│   └── gen_source_json.py
└── assets/examples/             # Example skills
    ├── minimal-skill/
    └── full-skill/
```

## Installation from Archive

### Claude Code

```bash
cd ~/.claude/skills
tar -xzf /path/to/gastown-admin-skill.tar.gz
# or
unzip /path/to/gastown-admin-skill.zip
```

### GitHub Copilot

```bash
mkdir -p .github/skills
cd .github/skills
tar -xzf /path/to/gastown-admin-skill.tar.gz
```

### OpenCode

```bash
mkdir -p .opencode/skills
cd .opencode/skills
tar -xzf /path/to/gastown-admin-skill.tar.gz
```

### Goose

```bash
mkdir -p .goose/skills
cd .goose/skills
tar -xzf /path/to/gastown-admin-skill.tar.gz
```

### Global

```bash
mkdir -p ~/.config/agents/skills
cd ~/.config/agents/skills
tar -xzf /path/to/gastown-admin-skill.tar.gz
```

## Verification After Installation

After extraction, verify the skill is valid using `agentskills`:

```bash
agentskills validate gastown-admin-skill
```

Should succeed with no output (exit code 0).

For detailed validation, use the built-in script:

```bash
uv run gastown-admin-skill/scripts/validate_skill.py gastown-admin-skill --strict --json
```

Should output:
```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

## Distribution Checklist

Before shipping:

- [ ] Run `uv run scripts/validate_skill.py . --strict` ✓ passes
- [ ] Run `uv run scripts/audit_disclosure.py .` ✓ no orphans or oversized blocks
- [ ] Run `uv run scripts/token_estimate.py . --model claude-haiku-4-5` ✓ T2 ≤ 5000 tokens
- [ ] Verify `.source.json` exists with author and version
- [ ] Check `SKILL.md` description is trigger-phrase rich
- [ ] Confirm all referenced files in `references/` exist
- [ ] Test extraction and validation in a clean directory

## Validation with agentskills CLI

The `agentskills` CLI can validate packaged skills:

```bash
agentskills validate gastown-admin-skill/
```

Exit codes:
- 0 = Valid
- Non-zero = Validation failed

## Future: Automated Packaging via skill-creator

When `skill-creator` package tooling becomes available, packaging will be fully automated. Currently, manual tar/zip packaging is the standard approach.

---

**Manual packaging is distribution-ready.** Validated by both `agentskills validate` and the built-in spec validator. No additional tooling required; tar and zip are universal across all platforms.
