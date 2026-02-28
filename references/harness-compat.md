# Harness Compatibility

Cross-platform compatibility guide for Agent Skills across major execution harnesses.
Consult this when adding harness-specific shims or verifying a skill will work on a
target platform. For spec constraints see `spec-summary.md`.

**Notation**: Claims marked **[spec]** are normative agentskills.io requirements.
Claims marked **[harness]** are harness-specific extensions. Claims marked
**[unverified]** could not be confirmed against primary sources at time of writing.

---

## Compatibility Matrix

| Feature | Claude Code | GitHub Copilot | OpenCode | Goose | Aider | Amp |
|---------|-------------|----------------|----------|-------|-------|-----|
| `SKILL.md` discovery | yes | yes | via shim | [unverified] | [unverified] | [unverified] |
| Progressive disclosure | yes native | yes [unverified] | partial | [unverified] | manual | [unverified] |
| `allowed-tools` | yes | yes [unverified] | via shim | - | - | - |
| `user-invokable` field | yes | yes | [unverified] | - | - | - |
| Script execution | bash | bash | bash | bash | bash | bash |
| Global skill path | `~/.claude/skills/` | `~/.github/skills/` [unverified] | AGENTS.md | [unverified] | - | - |

---

## Claude Code

**Discovery path**: `.claude/skills/<skill-name>/` (project-local) or
`~/.claude/skills/<skill-name>/` (user-global) **[harness]**

**Progressive disclosure**: Natively supported. Harness loads `name` +
`description` at T1, full `SKILL.md` at T2, `references/` and `scripts/` on
explicit agent request at T3. **[spec]** architecture, **[harness]** implementation.

**`allowed-tools`**: Respected for permission gating. Skills can declare which
tools they require; Claude Code enforces these at activation. **[harness]**

**`user-invokable`**: Skills with `user-invokable: true` in frontmatter appear
as slash commands. **[harness]**

**`disable-model-invocation`**: Prevents automatic model-triggered activation;
skill only activates via explicit user command. **[harness]**

**Path resolution**: project `.claude/skills/` shadows user `~/.claude/skills/`
which shadows organizational global (if configured). Closest proximity wins.

**Minimum viable skill**: `SKILL.md` with valid `name` and `description`.
No additional shim files required.

---

## GitHub Copilot

**Discovery paths**: `.github/skills/<skill-name>/` or `.copilot/skills/<skill-name>/`
**[harness]** - falls back to `.claude/skills/` **[unverified]**

**`user-invokable`**: Supported; skills appear as `/skill-name` commands in
Copilot Chat when set to true. **[harness]**

**`disable-model-invocation`**: Supported; prevents automatic activation.
**[harness]**

**Progressive disclosure**: Tier architecture supported **[unverified]**. Copilot
may load more context than Claude Code at T2; keep `SKILL.md` body concise
regardless.

**`allowed-tools`**: Interpreted for Copilot's tool permission system.
**[unverified]**

**Shim needed**: No additional files required beyond `SKILL.md` for basic
compatibility. For project-local skills, `.github/skills/` is preferred path.

---

## OpenCode

**Discovery**: OpenCode does not natively parse `SKILL.md`. Compatibility is
achieved via an `AGENTS.md` shim at the skill root. **[harness]**

**`AGENTS.md` shim**: Place an `AGENTS.md` file at the project root (or skill
root) that declares tool permissions and loads skill context. OpenCode reads
`AGENTS.md` as its primary agent configuration file.

```markdown
# AGENTS.md

## Tools
edit, write, bash, read

## Context
See SKILL.md for skill instructions.
```

**`opencode.json`**: OpenCode supports a JSON configuration file for structured
tool declarations and plugin configuration. **[harness]** Schema: **[unverified]**
```json
{
  "tools": ["edit", "write", "bash", "read"],
  "skills": ["./SKILL.md"]
}
```

**Superpowers plugin**: OpenCode's plugin system can translate `allowed-tools`
declarations from SKILL.md frontmatter into OpenCode-native permissions.
**[unverified]**

**Minimum viable**: `SKILL.md` + `AGENTS.md` shim with tool permission declarations.

---

## Goose

**Discovery**: `.goose/` directory at project root. **[harness]**

**MCP extension integration**: Goose supports Model Context Protocol (MCP)
extensions. Skills that expose MCP-compatible interfaces integrate cleanly.
**[harness]**

**Summon extension**: Goose's Summon extension enables dynamic skill loading
from remote registries. **[unverified]**

**Progressive disclosure**: Tier architecture status **[unverified]**. Treat
`SKILL.md` as fully loaded at activation; keep it concise.

**Minimum viable**: `SKILL.md` in `.goose/` directory. Full compatibility
requires verification against current Goose documentation.

---

## Aider

**Architecture**: Dual-model (Architect + Code). The Architect model receives
high-level instructions; the Code model applies diffs. This has implications
for skill structure. **[harness]**

**Implications for skill design**:
- Separate **design principles** (for the Architect) from **syntax directives**
  (for the Code model)
- Architect-facing content: goals, constraints, architectural decisions
- Code-facing content: exact patterns, valid/invalid examples, regex constraints
- A skill that mixes both levels may confuse the model routing

**Discovery**: No native `SKILL.md` discovery mechanism confirmed. **[unverified]**
Skills are typically injected via `--read` flag or repository-level `CONVENTIONS.md`.

**Minimum viable**: Include skill instructions in `CONVENTIONS.md` or inject via
`aider --read SKILL.md`. Full skill compatibility **[unverified]**.

---

## Amp

**Compaction primitives**: Amp includes context compaction features for
long-running agent sessions. Skills designed for Amp should be robust to context
compression - critical information must be re-derivable or explicitly cached.
**[harness]**

**Context preservation**: For long-running skills, include checkpointing patterns:
emit progress state to files rather than relying on in-context memory. **[harness]**

**Discovery**: **[unverified]**. Progressive disclosure tier support: **[unverified]**.

**Minimum viable**: `SKILL.md` with compact, high-signal instructions. Avoid
skills that require large amounts of in-context state persistence.

---

## Path Resolution Hierarchy

**[spec]** - applies across all conformant harnesses:

1. **Project-local**: `<project-root>/.claude/skills/` (or harness equivalent)
2. **User-global**: `~/.claude/skills/` (or harness equivalent)
3. **Organizational global**: configured via harness-specific settings

**Conflict resolution**: Closest proximity wins. A project-local skill with the
same `name` as a user-global skill shadows the global skill for that project.
This enables project-specific overrides without modifying the global skill.

---

## Normative vs. Extension Summary

**Normative (all conformant harnesses must support)**:
- `SKILL.md` with `name` and `description` frontmatter **[spec]**
- Three-tier progressive disclosure architecture **[spec]**
- `name` field regex and constraints **[spec]**
- `description` field 1-1024 char limit **[spec]**
- `skills-ref validate` command **[spec]**
- Relative path file referencing **[spec]**

**Harness-specific extensions (not in core spec)**:
- `user-invokable`, `disable-model-invocation` - Claude Code, Copilot **[harness]**
- `AGENTS.md` shim - OpenCode **[harness]**
- `.goose/` discovery path - Goose **[harness]**
- Dual-model routing - Aider **[harness]**
- Compaction primitives - Amp **[harness]**
