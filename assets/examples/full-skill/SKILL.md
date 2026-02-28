---
name: full-skill
description: >
  A richly featured skill example demonstrating progressive disclosure, script
  integration, reference indexes, and multi-harness support. Use when building
  complex skills that require a three-tier architecture, auxiliary reference
  materials, and procedural orchestration across tools.
license: Apache-2.0
compatibility: Designed for Claude Code and other agentskills.io-compatible harnesses
metadata:
  author: Kybernetes Systems
  version: "0.2.0"
  lore-epoch: The Wasteland
allowed-tools: Read Write Edit Bash Glob Grep
---

# Full Skill: Progressive Architecture

This skill demonstrates the complete agentskills.io pattern: YAML frontmatter, bounded SKILL.md body, reference materials for depth, and executable scripts for deterministic logic. The agent orchestrates pre-validated tools rather than generating code from scratch.

**Produces:** A validated skill directory with distribution metadata, progressive disclosure tiers (T1/T2/T3), and cross-harness compatibility.

**Does NOT:** Attempt operations outside the declared scope. Monolithic prompts are the enemy of agent reasoning. We separate concerns and respect tier boundaries.

## Table of Contents

- [Essential Workflows](#essential-workflows)
- [Decision Matrix](#decision-matrix)
- [Quick Reference](#quick-reference)
- [Scripts & Tools](#scripts--tools)
- [Reference Materials](#reference-materials)

## Essential Workflows

### Workflow 1: Single-File Skill

For capabilities that fit in SKILL.md with no auxiliary files:

1. Write YAML frontmatter: `name`, `description`, `license` (required).
2. Write body text. Keep total file under 500 lines.
3. Run: `uv run scripts/validate_skill.py <path>`
4. Stop if validation passes. No T3 overhead needed.

### Workflow 2: Multi-Tier Skill with References and Scripts

For capabilities requiring progressive disclosure and tooling:

1. **Design the file tree.** Decide what goes in SKILL.md body (T2, loaded every task) versus `references/` (T3, loaded on demand).
2. **Write frontmatter.** Include optional fields: `compatibility`, `metadata`, `allowed-tools`.
3. **Write body as routing table.** Keep ≤ 500 lines. Pointer to `references/` with "Read when" conditions.
4. **Write reference files.** Each under 2000 tokens. One domain per file. Include scope statement and table of contents if over 100 lines.
5. **Write scripts.** Use PEP 723 inline metadata. No interactive prompts. Support `--json` for output and `--dry-run` for risk operations.
6. **Validate and audit.** Run the complete gate sequence (see Quick Reference below).
7. **Generate provenance.** Create `.source.json` with author and version.
8. Ship.

## Decision Matrix

| Question | Answer | Destination |
|----------|--------|-------------|
| Will the agent need this on every task? | Yes | SKILL.md body (T2) |
| | No | `references/` (T3) |
| Is the body approaching 500 lines? | Yes | Move sections to `references/` |
| | No | Keep in body |
| Does this operation need to be deterministic? | Yes | Write a script in `scripts/` |
| | No | Document as inline instructions |
| Can this be interactive? | No. Never. Support `--json` and `--dry-run`. Exit non-zero on error. | `scripts/` |

## Quick Reference

### Frontmatter Fields

```yaml
---
name: <kebab-case, 1-64 chars>
description: >
  <1-1024 chars; multiline; include trigger phrases>
license: <SPDX identifier, e.g., Apache-2.0>
compatibility: <optional; e.g., "Claude Code and GitHub Copilot">
metadata: <optional; author, version, lore-epoch>
allowed-tools: <optional; list of available tools>
---
```

### File Tree

```
my-skill/
├── SKILL.md                 (required; ≤ 500 lines)
├── scripts/                 (optional; PEP 723)
│   ├── main-tool.py
│   └── validator.py
├── references/              (optional; ≤ 2000 tokens each)
│   ├── spec.md
│   ├── design.md
│   └── faq.md
└── assets/                  (optional; non-text)
    └── templates/
```

### Validation Gates (Run in Order)

```bash
# Gate 1: Frontmatter compliance
uv run scripts/validate_skill.py <path> --json

# Gate 2: Progressive disclosure audit
uv run scripts/audit_disclosure.py <path>

# Gate 3: Token budgets per tier
uv run scripts/token_estimate.py <path> --model claude-haiku-4-5

# Gate 4: Strict mode (no warnings)
uv run scripts/validate_skill.py <path> --strict --json
```

## Scripts & Tools

Read when: Your skill requires executable logic—file generation, validation, structured output, or deterministic orchestration.

| Script | Invocation | Purpose |
|--------|-----------|---------|
| `scaffold.py` | `uv run scripts/scaffold.py --name <name> --description "<desc>" [--scripts] [--references] --output <dir>` | Bootstrap skill directory with templates |
| `validate_skill.py` | `uv run scripts/validate_skill.py <path> [--strict] [--json]` | Validate frontmatter against agentskills.io spec |
| `audit_disclosure.py` | `uv run scripts/audit_disclosure.py <path> [--json]` | Check progressive disclosure: orphaned sections, large blocks, budget compliance |
| `token_estimate.py` | `uv run scripts/token_estimate.py <path> [--model MODEL] [--json]` | Count tokens per tier (T1/T2/T3) and file |
| `gen_source_json.py` | `uv run scripts/gen_source_json.py <path> [--author NAME] [--version VER] [--json]` | Generate `.source.json` provenance metadata |

## Reference Materials

Read these when you need authoritative guidance on a specific domain. Each is a T3 resource—loaded on demand, not on every task.

### [spec-summary.md](references/spec-summary.md)

Read when: Writing or validating frontmatter, understanding agentskills.io requirements.

**Scope:** Core specification with field constraints, valid values, examples, and validation rules.

### [harness-compat.md](references/harness-compat.md)

Read when: Adding support for OpenCode, GitHub Copilot, Goose, Aider, or Amp.

**Scope:** Cross-harness compatibility patterns, shim design, discovery paths, and tool availability per harness.

### [script-design.md](references/script-design.md)

Read when: Writing PEP 723 scripts for the `scripts/` directory.

**Scope:** Python script best practices, inline metadata format, argument parsing, error handling, and output validation.

### [security-checklist.md](references/security-checklist.md)

Read when: Auditing skills for distribution or supply chain security.

**Scope:** Input validation, shell injection prevention, dependency vetting, hardening for untrusted execution environments.

---

**Build to the standard, or do not build.**
