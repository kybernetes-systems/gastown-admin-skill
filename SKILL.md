---
name: gastown-admin-skill
description: >
  Orchestrates the complete Agent Skill creation lifecycle: prospect requirements,
  design structure, refine content, validate compliance, and ship distribution-ready
  skills conforming to the agentskills.io open standard. Use when asked to build a
  skill, create a SKILL.md, validate my skill, write a skill for Claude Code or
  GitHub Copilot, publish to agentskills.io, scaffold an agent capability, produce
  a multi-harness-compatible skill package, check skill compliance, generate skill
  frontmatter, audit a skill for distribution, design progressive disclosure
  tiers, or apply the agentskills.io spec to a new capability.
license: Apache-2.0
compatibility: Designed for Claude Code and other agentskills.io-compatible harnesses
metadata:
  author: Kybernetes Systems
  version: "0.1.0"
  lore-epoch: The Wasteland
  codename: Gas Town
allowed-tools: Read Write Edit Bash Glob Grep
---

# Gas Town Skill Refinery

This skill guides an agent through building a complete, distribution-ready Agent
Skill conforming to the [agentskills.io](https://agentskills.io) open standard.

**Produces:** A validated skill directory containing `SKILL.md`, optional
reference files, optional scripts, and distribution metadata.

**Does NOT:** administer Gas Town infrastructure (see `gastown-admin`), write
application code, or manage deployment pipelines outside skill packaging.

## Table of Contents

- [Pipeline Overview](#pipeline-overview)
- [Quick Start](#quick-start)
- [Stage 1: Prospect](#stage-1-prospect)
- [Stage 2: Assay](#stage-2-assay)
- [Stage 3: Refine](#stage-3-refine)
- [Stage 4: Harden](#stage-4-harden)
- [Stage 5: Ship](#stage-5-ship)
- [Stage 6: Maintain](#stage-6-maintain)
- [Scripts](#scripts)
- [References](#references)

## Pipeline Overview

Six stages. Each has a defined input, output, and gate. Do not advance until
the gate passes.

| Stage | Name | Input | Output | Gate |
|---|---|---|---|---|
| 1 | **Prospect** | Human intent | Requirements manifest | Manifest confirmed |
| 2 | **Assay** | Requirements manifest | File tree plan + token budget | Plan finalized |
| 3 | **Refine** | File tree plan | Complete skill directory (unvalidated) | All planned files written |
| 4 | **Harden** | Skill directory | Validated skill + validation report | `validate_skill.py` passes |
| 5 | **Ship** | Validated skill | Distribution-ready skill + install docs | `.source.json` generated |
| 6 | **Maintain** | Deployed skill | Updated versions + changelog | Ongoing |

## Scripts

| Script | Description | Invocation |
|--------|-------------|------------|
| `scaffold.py` | Bootstrap new skill directories with SKILL.md, references/, scripts/ | `uv run scripts/scaffold.py --name <name> --description "<desc>" [--scripts] [--references] [--assets] --output <dir>` |
| `validate_skill.py` | Validate skill against agentskills.io spec | `uv run scripts/validate_skill.py <path> [--strict] [--json]` |
| `token_estimate.py` | Estimate token counts per progressive disclosure tier | `uv run scripts/token_estimate.py <path> [--model MODEL] [--json]` |
| `audit_disclosure.py` | Audit quality: large blocks, orphans, token budgets | `uv run scripts/audit_disclosure.py <path> [--json]` |
| `gen_source_json.py` | Generate .source.json provenance metadata | `uv run scripts/gen_source_json.py <path> [--author NAME] [--version VER] [--json]` |

## References

| Reference | Description | Read when |
|-----------|-------------|-----------|
| [spec-summary.md](references/spec-summary.md) | agentskills.io specification summary | Validating SKILL.md frontmatter or understanding spec requirements |
| [harness-compat.md](references/harness-compat.md) | Cross-harness compatibility guide | Adding support for OpenCode, GitHub Copilot, Goose, Aider, or Amp |
| [description-craft.md](references/description-craft.md) | Guide for writing skill descriptions and trigger phrases | Drafting or revising skill description field |
| [script-design.md](references/script-design.md) | Best practices for writing PEP 723 scripts | Writing any script in scripts/ directory |
| [security-checklist.md](references/security-checklist.md) | Security considerations for skill authoring/distribution | Preparing skill for distribution; auditing for risks |

## Quick Start

For simple, single-file skills (no reference files, no scripts), Assay is
optional:

1. **Prospect** — gather requirements; write a one-paragraph manifest.
2. **Refine** — write `SKILL.md` directly; skip Assay.
3. **Harden** — run `scripts/validate_skill.py`; fix any failures.
4. Stop here for local use. Advance to **Ship** only if distributing externally.

For complex skills (multiple reference files, scripts, multi-harness support),
run all six stages in order.

---

## Stage 1: Prospect

Gather crude material. Do not write any skill files yet.

1. **State the target capability** in one sentence: what will this skill enable
   an agent to do?

2. **Define semantic triggers.** List ≥ 5 phrases a user might say to invoke
   this skill. Consult `references/description-craft.md` for trigger patterns.

3. **Identify environmental dependencies.** List every tool, CLI, service, or
   runtime the skill requires. Mark each as required or optional.

4. **Determine target harnesses.**
   - Claude Code only → no shims needed; proceed.
   - Additional harnesses (Copilot, OpenCode, Goose, Aider, Amp) → flag each;
     plan compatibility shims in Assay. Consult `references/harness-compat.md`.

5. **Assess script need.**
   - Skill requires file generation, validation, or structured output → plan
     one or more scripts under `scripts/` using PEP 723 inline metadata.
   - Skill provides procedural instructions only → skip `scripts/`.

6. **Output:** a requirements manifest (in-context or written to a temp file)
   covering all five items above.

**Gate:** manifest answers capability, triggers, dependencies, harnesses, and
script need before advancing.

---

## Stage 2: Assay

Design the directory structure. Still no skill content writing.

1. **Design the directory tree.** Decide which optional components to include:
   - `references/` → include if content would exceed SKILL.md's 500-line budget
     or is material the agent loads on demand rather than every task.
   - `scripts/` → include if Prospect flagged script need.
   - `assets/` → include only if non-text assets (templates, examples) are
     needed.

2. **Plan progressive disclosure allocation.**
   - T1 (frontmatter): `name` + `description` only.
   - T2 (SKILL.md body): pipeline, routing tables, common workflows. Keep ≤ 500
     lines total.
   - T3 (`references/`): deep reference material, spec excerpts, edge cases.
   - Rule: consulted on every task → T2. Consulted occasionally → T3.

3. **Estimate token budgets.** Run:
   ```
   uv run scripts/token_estimate.py <skill-dir>
   ```
   T2 target: ≤ 5 000 tokens. If over budget, move reference material to T3.

4. **Plan harness compatibility shims.** Consult `references/harness-compat.md`:
   - Claude Code → no shim required.
   - OpenCode → plan `AGENTS.md` shim.
   - GitHub Copilot → no shim; verify discovery path.
   - Other harnesses → plan per `references/harness-compat.md`.

5. **Output:** a file tree listing every file to be created and which tier
   (T1/T2/T3) it serves.

**Gate:** file tree is complete and satisfies all Prospect requirements before
advancing to Refine.

---

## Stage 3: Refine

Write all skill content. Work through the file tree produced in Assay in order.

### Step 1: Scaffold (new skills only)

If creating a new skill from scratch, run scaffold before writing any files:

```
uv run scripts/scaffold.py --name <name> --description "<placeholder>" \
  [--scripts] [--references] [--assets] --output <parent-dir>
```

Pass `--scripts`, `--references`, `--assets` only for directories Assay
included. Edit the generated files; do not start from a blank directory.

### Step 2: Write target SKILL.md frontmatter

Consult `references/spec-summary.md` for all field constraints.

- `name` — kebab-case, 1-64 chars; must match the skill directory name exactly.
- `description` — 1-1024 chars. Draft it last, after the body is complete.
  Consult `references/description-craft.md` for trigger phrase patterns.
- `license`, `compatibility`, `metadata`, `allowed-tools` — fill as needed.

Verify frontmatter before continuing:
```
uv run scripts/validate_skill.py <path> --json
```

### Step 3: Write target SKILL.md body

- Keep the full file (frontmatter + body) under 500 lines.
- Progressive disclosure: detailed reference material → `references/`; only
  routing logic and common workflows belong in the body.
- Suggested structure for most skills:
  - One-paragraph overview (what it does, what it produces, what it does NOT do)
  - Table of contents (if more than three major sections)
  - Common workflows (imperative, step-by-step)
  - Quick reference table (commands, flags, or decision points)
  - Pointers to reference files with "Read when" conditions
- If body exceeds 500 lines → move sections to `references/` and link back.

### Step 4: Write scripts (if planned in Assay)

Consult `references/script-design.md` before writing any script.

- Use PEP 723 inline metadata (`# /// script` block) for Python dependencies.
- Implement `--help` with usage, all flags, exit codes, and example invocations.
- Support `--json` for structured output to stdout; diagnostics to stderr only.
- Never use interactive prompts. Support `--dry-run` for destructive operations.
- Exit non-zero on any error.

When NOT to write a script:
- A script in `scripts/` already covers the need → document its invocation in
  SKILL.md; do not duplicate it.
- The operation is a single shell one-liner → inline it in SKILL.md directly.
- The logic requires domain knowledge you cannot verify → defer to the user.

### Step 5: Write reference files (if planned in Assay)

Each reference file must:
- Cover exactly one domain or concern.
- Stay under 2 000 tokens (`uv run scripts/token_estimate.py <file>`).
- Open with a one-sentence description of its scope.
- Include a table of contents if over 100 lines.
- Be referenced from SKILL.md with a "Read when" condition, e.g.:
  > Consult `references/script-design.md` when writing scripts for a skill.

**Gate:** all planned files are written and the directory matches the Assay file
tree before advancing to Harden.

---

## Stage 4: Harden

Validate and secure the skill. Do not distribute until this stage is clean.

Run all checks in order. Fix errors before advancing to the next check.

1. Validate spec compliance:
   ```
   uv run scripts/validate_skill.py <path> --strict --json
   ```

2. Audit progressive disclosure:
   ```
   uv run scripts/audit_disclosure.py <path> --json
   ```

3. Check token budgets:
   ```
   uv run scripts/token_estimate.py <path> --json
   ```
   T2 must be ≤ 5 000 tokens. Move sections to `references/` if over budget.

4. Run the spec reference validator (if available):
   ```
   skills-ref validate <path>
   ```

5. Review the security checklist:
   ```
   cat references/security-checklist.md
   ```
   Address every item marked REQUIRED before shipping.

6. Fix all errors. Re-run affected checks. Repeat until all checks pass.

**Gate:** `validate_skill.py` and `audit_disclosure.py` both exit 0 before
advancing to Ship.

---

## Stage 5: Ship

Prepare the skill for distribution.

1. **Generate provenance:**
   ```
   uv run scripts/gen_source_json.py <path> --author "<name>" --version "<ver>"
   ```

2. **Install locally** (Claude Code): copy the skill directory to
   `~/.claude/skills/<skill-name>/` (user-global) or
   `.claude/skills/<skill-name>/` in the target project (project-local).

3. **Distribute via Git:** push the skill directory to a repository. Consumers
   clone and install per step 2. Include a `README.md` with install
   instructions and environment requirements.

4. **Publish to registry:** submit to the agentskills.io registry.
   `.source.json` provenance is required for submission.

5. **Package as `.skill` archive** (optional): zip the skill directory as
   `<skill-name>.skill` for offline or air-gapped distribution.

**Gate:** `.source.json` is present in the skill directory.

---

## Stage 6: Maintain

Ongoing operations after the skill is deployed.

**Version bumps:** increment `metadata.version` in frontmatter. Re-run Harden.
Update changelog. Notify consumers if a breaking change affects trigger phrases
or tool requirements.

**Description re-optimization:** if the skill is not triggering reliably,
revise `description` trigger phrases using `references/description-craft.md`.
Re-run `validate_skill.py` to verify character limits. Test against the target
harness.

**Regression testing after harness updates:** re-run `audit_disclosure.py` and
`validate_skill.py`. Check `references/harness-compat.md` for newly verified
or invalidated compatibility claims. Update shims as needed.

**Deprecation:** set `metadata.deprecated: "true"` and add
`metadata.successor: "<replacement-skill-name>"` in frontmatter. Leave the
skill in place for one release cycle before removing.
