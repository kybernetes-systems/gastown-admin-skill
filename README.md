# Gas Town Skill Refinery

The Wasteland has no shortage of agents. It has a shortage of agents
that know what they're doing.

A Gas Town Skill Refinery turns raw intent into distribution-ready
agent skill packages — validated, documented, multi-harness compatible.
There are many refineries. This is one. Fork it, deploy it, run it into
the ground; the spec doesn't care who owns the rig.

Built for the [agentskills.io](https://agentskills.io) open standard.

---

## What Comes Out the Other End

A skill directory. Specifically:

- `SKILL.md` with valid frontmatter and stage instructions
- `references/` with supporting documentation
- `scripts/` for validation and tooling
- `.source.json` provenance metadata

Validated. Ready to install. No promises about what you put in.

---

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- git

---

## Installation

Pick your harness. The skill does not care how it arrives.

### Claude Code

```sh
# Project-scoped (recommended)
cp -r gastown-admin-skill .claude/skills/

# User-global
cp -r gastown-admin-skill ~/.claude/skills/
```

### GitHub Copilot

```sh
cp -r gastown-admin-skill .github/skills/
```

### OpenCode

OpenCode needs the `AGENTS.md` shim included in this package.

```sh
cp -r gastown-admin-skill .opencode/skills/
```

### Goose

```sh
cp -r gastown-admin-skill .goose/skills/
```

### Global / Other

```sh
cp -r gastown-admin-skill ~/.config/agents/skills/
```

See `references/harness-compat.md` for the full compatibility map.

---

## Quick Start

Scaffold a skill, then find out what's wrong with it.

```sh
uv run scripts/scaffold.py --name my-skill --description "Does X. Use when Y."
uv run scripts/validate_skill.py ./my-skill --strict
```

Absent identification of problems, any solutions are left to chance.

Exit codes: 0 = clean, 1 = errors, 2 = warnings. Errors are errors.

---

## The Pipeline

Six stages. Each has a gate. Don't skip gates.

| Stage | Name | In | Out |
|---|---|---|---|
| 1 | Prospect | Human intent | Requirements manifest |
| 2 | Assay | Requirements | File tree plan |
| 3 | Refine | Plan | Skill directory (raw) |
| 4 | Harden | Raw skill | Validated skill |
| 5 | Ship | Validated skill | Distribution package |
| 6 | Maintain | Deployed skill | Updated versions |

Full stage instructions: `SKILL.md`.

---

## Scripts

Five scripts. All stdlib-only, all support `--help` and `--json`.

| Script | Does |
|---|---|
| `scaffold.py` | Bootstrap a new skill directory |
| `validate_skill.py` | Check compliance with agentskills.io spec |
| `token_estimate.py` | Count tokens per disclosure tier |
| `audit_disclosure.py` | Find orphans, oversized blocks, quality issues |
| `gen_source_json.py` | Generate provenance metadata |

---

## Blueprint

Architecture decisions and design rationale: [BLUEPRINT.md](./BLUEPRINT.md)

Harness compatibility: [references/harness-compat.md](./references/harness-compat.md)

---

## License

Apache-2.0. See [LICENSE.txt](./LICENSE.txt).
