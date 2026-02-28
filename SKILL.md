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
  author: kybernetes-systems
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

## Quick Start

For simple, single-file skills (no reference files, no scripts), Assay is
optional:

1. **Prospect** — gather requirements; write a one-paragraph manifest.
2. **Refine** — write `SKILL.md` directly; skip Assay.
3. **Harden** — run `scripts/validate_skill.py`; fix any failures.
4. Stop here for local use. Advance to **Ship** only if distributing externally.

For complex skills (multiple reference files, scripts, multi-harness support),
run all six stages in order.
