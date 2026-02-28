# The Refinery Blueprint

## Architectural Design & Task Decomposition for `gastown-admin-skill`

> *"Do not, my friends, become addicted to monolithic prompts.*
> *It will take hold of you, and you will resent its absence."*
> -- Immortan Joe, on context window management

---

## 0. What We Are Building

**`gastown-admin-skill`** is a meta-skill: an Agent Skill whose purpose is to teach
AI agents how to *build other Agent Skills* that conform to the
[agentskills.io](https://agentskills.io) open standard. It is a refinery. Crude
expertise goes in; portable, validated, cross-platform capability comes out.

This is not a toy. This is not a template. This is the procedural knowledge that
lets an autonomous agent take a vague human intent--"I need a skill that does X"--and
produce a complete, specification-compliant, multi-harness-compatible skill directory
with validation, scripts, documentation, and distribution metadata. It should set the
standard for what a well-engineered skill looks like, because every skill it produces
will inherit its discipline or its sloppiness.

**The Wasteland does not forgive sloppy skills.** A poorly triggered `description`
field means the skill never activates--dead on arrival, bleaching in the sun. A
monolithic SKILL.md that dumps 3,000 lines of reference material into the context
window is a War Rig with no brakes: it will destroy the agent's reasoning capacity
before it reaches its destination. An unvalidated frontmatter `name` with uppercase
characters or consecutive hyphens will fail `skills-ref validate` and break
installation across every harness that trusts the spec.

We build this right, or we don't build it at all.

---

## 1. Architectural Principles

### 1.1 The Three Laws of Gas Town Engineering

**I. Progressive Disclosure Is Not Optional.**
The agentskills.io spec defines a three-tier loading architecture. Tier 1 (Discovery)
loads only `name` and `description` from YAML frontmatter--roughly 50-100 tokens per
skill. Tier 2 (Instructions) loads the full SKILL.md body when the agent determines
the skill is relevant. Tier 3 (Resources) loads files from `scripts/`, `references/`,
and `assets/` only when explicitly needed during execution. Our skill MUST respect
this architecture internally, and it MUST teach produced skills to respect it.

Concretely: SKILL.md stays under 500 lines. Detailed reference material (the full
spec, harness compatibility matrices, script design patterns) lives in `references/`.
Executable logic lives in `scripts/`. The SKILL.md body is a routing table and
procedural workflow, not an encyclopedia.

**II. The Agent Is the Operator, Not the Author.**
When our skill instructs an agent to produce a validation script, the agent should
*execute a pre-validated script we provide*, not generate one from scratch. Every
line of code an LLM generates from its own weights is a coin flip compared to a
tested script. Our `scripts/` directory contains deterministic tools. The SKILL.md
instructs the agent to *orchestrate* those tools. This transitions the LLM from
generative mode to orchestration mode--dramatically more reliable.

**III. Design for the Dumbest Plausible Harness.**
The skill must produce output that works on Claude Code, GitHub Copilot, OpenCode,
Goose, Aider, and Amp. That means: no assumptions about sub-agent support, no
assumptions about specific tool names beyond `bash` and file I/O, and no assumptions
about the harness understanding `allowed-tools`. The lowest common denominator is a
filesystem-based agent that can read files and run bash commands. Everything we build
must work at that level. Cross-harness compatibility files (like `AGENTS.md` for
OpenCode) are additive enhancements, not requirements.

### 1.2 The Refinery Pipeline (Conceptual Architecture)

The skill implements a six-stage pipeline. Each stage has a defined input, a defined
output, and a validation gate. The agent cannot proceed to the next stage until the
gate passes. This is the Fury Road convoy: you do not leave the vehicle until the
War Rig stops.

```
+-------------+    +---------------+    +--------------+
|  PROSPECT    |--->|  ASSAY        |--->|  REFINE      |
|  (Require-   |    |  (Structure   |    |  (Write      |
|   ments)     |    |   & Plan)     |    |   Content)   |
+-------------+    +---------------+    +--------------+
                                               |
+-------------+    +---------------+           |
|  SHIP       |<---|  HARDEN       |<----------+
|  (Distri-   |    |  (Validate    |
|   bute)     |    |   & Secure)   |
+-------------+    +---------------+
       |
       v
+-------------+
|  MAINTAIN   |
|  (Lifecycle |
|   Ops)      |
+-------------+
```

**Stage 1 -- PROSPECT** (Requirements Capture)
Gather crude material. What does the target skill do? Who uses it? What triggers it?
What are its environmental dependencies? Output: a structured requirements manifest.

**Stage 2 -- ASSAY** (Structure & Planning)
Determine the skill's directory architecture. How many reference files? What scripts
are needed? How should progressive disclosure tiers be allocated? Which harnesses
need compatibility shims? Output: a file tree plan and a token budget estimate.

**Stage 3 -- REFINE** (Content Authoring)
Write the SKILL.md body, reference files, script interfaces, and assets. This is
the largest stage. Output: the complete skill directory, unvalidated.

**Stage 4 -- HARDEN** (Validation & Security)
Run `skills-ref validate`. Check frontmatter constraints. Lint scripts. Verify
progressive disclosure compliance (SKILL.md under 500 lines, reference files
focused and modular). Check for security antipatterns. Output: a validated skill
directory with a validation report.

**Stage 5 -- SHIP** (Distribution)
Prepare for distribution: generate `.source.json` provenance metadata, create
installation instructions for each target harness, optionally package as `.skill`
archive. Output: a distribution-ready skill with install documentation.

**Stage 6 -- MAINTAIN** (Lifecycle Operations)
Post-deployment: handle version bumps, description optimization, cross-harness
regression testing, deprecation. This stage is ongoing. Output: updated skill
versions, changelog entries.

### 1.3 File Tree (Target State)

This is what the completed `gastown-admin-skill/` directory will contain:

```
gastown-admin-skill/
|-- SKILL.md                          # Tier 2: Core routing & pipeline instructions
|-- LICENSE.txt                       # Apache-2.0 full text
|-- AGENTS.md                         # OpenCode compatibility shim
|-- scripts/
|   |-- validate_skill.py             # Frontmatter & structure validation
|   |-- scaffold.py                   # Generate skill directory from template
|   |-- token_estimate.py             # Estimate token counts per tier
|   |-- audit_disclosure.py           # Verify progressive disclosure compliance
|   +-- gen_source_json.py            # Generate .source.json provenance file
|-- references/
|   |-- spec-summary.md               # Condensed agentskills.io spec reference
|   |-- harness-compat.md             # Cross-platform compatibility guide
|   |-- script-design.md              # Patterns for agentic script interfaces
|   |-- description-craft.md          # Guide to writing effective descriptions
|   +-- security-checklist.md         # Supply chain & prompt injection defenses
+-- assets/
    |-- skill-template/               # Skeleton directory for scaffolding
    |   |-- SKILL.md.template         # Jinja2/mustache template for SKILL.md
    |   +-- README.md.template        # Optional README for GitHub distribution
    +-- examples/
        |-- minimal-skill.md          # Minimal valid SKILL.md example
        +-- full-skill.md             # Fully-featured SKILL.md example
```

### 1.4 Token Budget

Context is Guzzoline. Every token spent is a token the agent cannot use for reasoning.

| Tier | Content | Target Budget |
|------|---------|---------------|
| T1 Discovery | `name` + `description` frontmatter | <= 100 tokens |
| T2 Instructions | Full SKILL.md body | <= 4,000 tokens (~400 lines) |
| T3 Resources | Each reference file | <= 2,000 tokens each |
| T3 Scripts | Loaded into context only via execution output | <= 500 tokens stdout per run |

The SKILL.md body must function as a concise procedural routing table. It tells the
agent *what to do* and *where to find details*, not *everything there is to know*.
When the agent needs the full spec reference, it reads `references/spec-summary.md`.
When it needs harness compatibility details, it reads `references/harness-compat.md`.
The SKILL.md itself never contains that material.

### 1.5 Lore Integration Strategy

The Gas Town aesthetic is not decoration. It serves a functional purpose: it makes
the skill *memorable and distinct* in a context window full of competing instructions.
An agent that has ingested ten skills needs to distinguish between them rapidly. A
skill that speaks in the voice of Gas Town's refinery foremen--direct, industrial,
consequence-aware--creates a unique lexical signature that reduces confusion.

Lore is applied with the following constraints:
- **Headers and stage names** use Gas Town/Wasteland metaphors (Prospect, Assay,
  Refine, Harden, Ship, Maintain).
- **Procedural instructions** are written in clear imperative English. No metaphor
  obscures an actual instruction.
- **Error messages and warnings** may use brief Wasteland idioms to make them
  memorable ("This skill directory is a chrome-less wreck--`name` field is missing").
- **Reference files** are written in technical prose. Lore stays in SKILL.md and
  README. Reference files are for the agent's working memory, not its personality.
- The **Dune** connection is natural: the Spice is compute, the Worms are long-running
  processes, the Bene Gesserit are prompt engineers whispering instructions to shape
  behavior across generations. Use sparingly. The Fremen know: the desert is real.
  The metaphor must serve the work, or it is sand in the stillsuit.

---

## 2. Beads Task Decomposition

The following sections define every epic, task, and subtask required to build
`gastown-admin-skill` from zero to distribution-ready. Each entry includes:

- **Bead ID convention**: Epics are `E1`-`E7`. Tasks within are `E1.T1`, `E1.T2`, etc.
  Subtasks are `E1.T1.S1`. The AI worker will create actual `bd` issue IDs; these
  labels are for human reference in this document.
- **Dependencies**: Expressed as `blocks` (hard prerequisite) or `related` (soft
  association). The worker should translate these into `bd dep add` commands.
- **Acceptance criteria**: Concrete, verifiable conditions. No ambiguity.
- **Estimated complexity**: S (small, <1 hour), M (medium, 1-3 hours), L (large, 3+ hours).

### Dependency Overview

```
E1 (Foundation) --blocks--> E2 (References) --blocks--> E3 (Scripts)
                                    |                        |
                                    |                        |
                                    v                        v
                              E4 (SKILL.md Core) <--blocks-- +
                                    |
                                    v
                              E5 (Hardening) --blocks--> E6 (Distribution)
                                                              |
                                                              v
                                                        E7 (Documentation & Polish)
```

---

### Epic 1: Foundation -- "Clear the Scrap Yard"

**Goal**: Establish the repository, directory structure, licensing, and project
scaffolding. Nothing else can be built until the ground is cleared.

#### E1.T1 -- Initialize Repository Structure
- **Type**: `task`
- **Priority**: 0 (critical)
- **Dependencies**: None (root task)
- **Complexity**: S
- **Description**: Create the `gastown-admin-skill/` directory with the following
  empty subdirectories: `scripts/`, `references/`, `assets/`, `assets/skill-template/`,
  `assets/examples/`. Create a placeholder `SKILL.md` containing only valid YAML
  frontmatter with `name: gastown-admin-skill` and a placeholder `description`. The
  placeholder must pass `skills-ref validate` (if available) or manual frontmatter
  validation: name is kebab-case, 1-64 chars, no consecutive hyphens, no leading/
  trailing hyphens.
- **Acceptance Criteria**:
  1. Directory tree matches Section 1.3 of this blueprint (empty subdirectories OK).
  2. `SKILL.md` exists with valid YAML frontmatter.
  3. `name` field value matches parent directory name.
  4. Frontmatter parses without error via any YAML parser.

#### E1.T2 -- Add License File
- **Type**: `task`
- **Priority**: 2 (medium)
- **Dependencies**: `blocks` E1.T1
- **Complexity**: S
- **Description**: Add `LICENSE.txt` containing the full Apache-2.0 license text.
  Update the SKILL.md frontmatter `license` field to read `Apache-2.0`.
- **Acceptance Criteria**:
  1. `LICENSE.txt` exists at skill root.
  2. File content is the standard Apache-2.0 text.
  3. SKILL.md `license` field references it.

#### E1.T3 -- Create OpenCode Compatibility Shim (AGENTS.md)
- **Type**: `task`
- **Priority**: 3 (low)
- **Dependencies**: `blocks` E1.T1; `related` E2.T2 (harness-compat reference)
- **Complexity**: S
- **Description**: Create `AGENTS.md` at skill root. This file provides OpenCode-
  specific tool permission declarations. It should grant: `edit`, `write`, `bash`
  (scoped to `git`, `uv`, `python3`, `skills-ref`), and `read`. This file is
  inert in non-OpenCode harnesses and causes no harm.
- **Acceptance Criteria**:
  1. `AGENTS.md` exists at skill root.
  2. Contains explicit OpenCode permission declarations.
  3. Does not interfere with Claude Code or Copilot skill loading (verified by
     confirming SKILL.md still parses normally with the file present).

#### E1.T4 -- Create .gitignore and Project Hygiene Files
- **Type**: `chore`
- **Priority**: 3 (low)
- **Dependencies**: `blocks` E1.T1
- **Complexity**: S
- **Description**: Add `.gitignore` excluding `__pycache__/`, `*.pyc`, `.venv/`,
  `*.egg-info/`, `dist/`, `build/`, `.uv/`. Optionally add a minimal `.editorconfig`
  for consistent formatting (2-space indent for YAML/MD, 4-space for Python,
  UTF-8, LF line endings).
- **Acceptance Criteria**:
  1. `.gitignore` exists and excludes Python build artifacts.
  2. No generated files leak into version control.

---

### Epic 2: Reference Forge -- "Distill the Knowledge"

**Goal**: Write the `references/` files that contain the deep technical knowledge
the SKILL.md body will route agents to. These are Tier 3 resources--loaded on demand,
not stuffed into the main instructions.

**Depends on**: E1 (Foundation) -- the directory must exist.

The references are the skill's Spice reserves. The SKILL.md is the Fremen who knows
where to find them in the deep desert, but does not carry the entire hoard on their
back. Each reference file must be self-contained, focused on a single domain, and
under 2,000 tokens.

#### E2.T1 -- Write `references/spec-summary.md`
- **Type**: `task`
- **Priority**: 1 (high)
- **Dependencies**: `blocks` E1.T1
- **Complexity**: M
- **Description**: Condense the agentskills.io specification into a focused reference
  document. This is NOT a copy of the spec. It is a practitioner's reference that
  an agent consults mid-workflow when it needs to verify a constraint.

  Must cover:
  - Frontmatter field requirements (name, description, license, compatibility,
    metadata, allowed-tools) with constraints, valid/invalid examples
  - Directory structure rules (SKILL.md required, optional dirs)
  - Progressive disclosure tiers with token budget guidance
  - File referencing conventions (relative paths from skill root)
  - Validation command (`skills-ref validate`)
  - Name field regex: lowercase alphanumeric + hyphens, 1-64 chars, no leading/
    trailing/consecutive hyphens, must match parent directory name
  - Description field: 1-1024 chars, must include capability + trigger context

  Must NOT cover: Integration approaches (that's harness-compat.md), script design
  (that's script-design.md), or security (that's security-checklist.md).

- **Acceptance Criteria**:
  1. File exists at `references/spec-summary.md`.
  2. All normative spec constraints are accurately represented (verified against
     the agentskills.io specification document).
  3. No information is fabricated or extrapolated beyond what the spec states.
  4. Under 2,000 tokens (estimate via `wc -w`; roughly 1,500 words).
  5. Includes a table of contents if over 80 lines.

#### E2.T2 -- Write `references/harness-compat.md`
- **Type**: `task`
- **Priority**: 1 (high)
- **Dependencies**: `blocks` E1.T1
- **Complexity**: M
- **Description**: Document cross-platform compatibility across the major execution
  harnesses. The agent reads this when it needs to add harness-specific shims or
  verify that a produced skill will work on a target platform.

  Must cover:
  - Claude Code: `.claude/skills/` discovery, progressive disclosure native support,
    `allowed-tools` interpretation
  - GitHub Copilot: `.github/skills/` and `.copilot/skills/` paths, fallback to
    `.claude/skills/`, `user-invokable` and `disable-model-invocation` fields
  - OpenCode: `AGENTS.md` shim, `opencode.json` schema, Superpowers plugin for
    tool translation, explicit permission declarations
  - Goose: `.goose/` discovery, MCP extension integration, Summon extension
  - Aider: Dual-model architecture (Architect + Code), implications for skill
    structure--separate design principles from syntax directives
  - Amp: Compaction primitives, context preservation for long-running skills
  - Path resolution hierarchy: local project -> user global -> organizational global
  - Conflict resolution: closest-proximity shadowing

  Must document what is **normative spec** versus what is **harness-specific
  extension**. The worker must clearly distinguish "the spec requires X" from
  "Copilot additionally supports Y." The research document (project file) contains
  useful analysis but also contains extrapolations. Cross-reference against the
  actual agentskills.io spec and official harness docs. Flag any claim that cannot
  be verified against primary sources with "[unverified]".

- **Acceptance Criteria**:
  1. File exists at `references/harness-compat.md`.
  2. All six harnesses covered.
  3. Normative vs. extension claims are clearly labeled.
  4. Under 2,000 tokens.
  5. Includes the compatibility matrix table from the research document, annotated
     with verification status.

#### E2.T3 -- Write `references/script-design.md`
- **Type**: `task`
- **Priority**: 1 (high)
- **Dependencies**: `blocks` E1.T1
- **Complexity**: M
- **Description**: Document best practices for designing scripts that agents can
  execute reliably. This reference is consulted during Stage 3 (REFINE) when the
  agent is writing or evaluating scripts for a target skill.

  Must cover:
  - Hard requirement: no interactive prompts (agents run non-interactive shells)
  - `--help` output as the script's primary interface documentation
  - Helpful error messages (what went wrong, what was expected, what to try)
  - Structured output (JSON/CSV/TSV to stdout, diagnostics to stderr)
  - Idempotency: "create if not exists" patterns
  - Dry-run support for destructive operations
  - Meaningful exit codes, documented in `--help`
  - Predictable output size: summary defaults, `--offset` pagination, `--output`
    file flag for large outputs
  - Self-contained dependency patterns: PEP 723 inline metadata for Python (with
    `uv run`), Deno `npm:` specifiers, Bun auto-install, Ruby `bundler/inline`
  - One-off commands: `uvx`, `npx`, `bunx`, `deno run`, `go run` with version pinning

  Source material: the "Using scripts in skills" document (project file, doc index 1)
  is the authoritative reference. Condense, do not copy.

- **Acceptance Criteria**:
  1. File exists at `references/script-design.md`.
  2. All patterns from the source document are represented.
  3. Each pattern includes a brief rationale (why it matters for agents specifically).
  4. Under 2,000 tokens.

#### E2.T4 -- Write `references/description-craft.md`
- **Type**: `task`
- **Priority**: 1 (high)
- **Dependencies**: `blocks` E1.T1
- **Complexity**: M
- **Description**: The `description` field is the single most important line in any
  skill. It determines whether the skill activates or dies in the sand. This
  reference teaches agents how to write descriptions that trigger reliably without
  false positives.

  Must cover:
  - The dual requirement: describe what the skill does AND when to use it
  - Semantic trigger phrases: include specific user phrases and task contexts
  - The "pushy" principle (from skill-creator docs): lean toward over-triggering
    rather than under-triggering, because a false activation wastes tokens but a
    missed activation wastes the user's entire intent
  - The 1024-character limit and how to use it effectively
  - Anti-patterns: too vague ("Helps with PDFs"), too narrow ("Only for PyPDF2
    merge operations"), too aggressive ("Use for everything")
  - Good examples and bad examples (at least 3 of each)
  - Keyword density: include the nouns and verbs a user would actually say
  - Testing methodology: how to evaluate whether a description triggers correctly
    (reference the skill-creator's description optimization loop as prior art)

- **Acceptance Criteria**:
  1. File exists at `references/description-craft.md`.
  2. Contains >= 3 good and >= 3 bad description examples with explanations.
  3. Actionable: an agent reading this file can write a description without
     consulting any other resource.
  4. Under 2,000 tokens.

#### E2.T5 -- Write `references/security-checklist.md`
- **Type**: `task`
- **Priority**: 2 (medium)
- **Dependencies**: `blocks` E1.T1; `related` E2.T2
- **Complexity**: M
- **Description**: Document the security considerations for skill authoring and
  distribution. This is read during Stage 4 (HARDEN) and Stage 5 (SHIP).

  Must cover:
  - Script execution risks: sandboxing, allowlisting, confirmation prompts, logging
  - Prompt injection via skill content: how a malicious SKILL.md can hijack an
    agent's behavior
  - Memory poisoning: skills that modify agent state files (SOUL.md, MEMORY.md,
    .bashrc) -- the ClawHavoc pattern
  - Supply chain risks: unverified registry installations, compromised skill
    packages
  - Mitigations: `allowed-tools` capability dropping, `.source.json` provenance,
    cryptographic signatures (GPG/.sig), dry-run previews
  - The "Signed Skill" roadmap: cryptographic sealing, DID identity binding,
    capability dropping, memory immutability, sub-agent auditing
  - Practical checklist: 10-15 yes/no items an agent can verify before shipping

  Source: the research document's security section. Distinguish between currently
  implemented mitigations and proposed/roadmap items. Mark roadmap items clearly.

- **Acceptance Criteria**:
  1. File exists at `references/security-checklist.md`.
  2. Contains a concrete checklist (not just prose).
  3. Implemented vs. roadmap items clearly distinguished.
  4. Under 2,000 tokens.

---

### Epic 3: Script Foundry -- "Forge the Tools"

**Goal**: Build the executable Python scripts in `scripts/` that the SKILL.md
pipeline will orchestrate. Each script is a self-contained tool with PEP 723
inline dependencies, `--help` documentation, JSON output, and meaningful exit codes.

**Depends on**: E1 (Foundation) -- directory exists. E2.T3 (script-design reference)
should be complete first so the scripts exemplify the patterns they document.

These are the wrenches and torches of the refinery. The SKILL.md tells the
blackthumb *which* tool to grab; the tool does the work.

#### E3.T1 -- Build `scripts/scaffold.py`
- **Type**: `feature`
- **Priority**: 0 (critical)
- **Dependencies**: `blocks` E1.T1; `blocks` E2.T1 (needs spec knowledge to validate
  generated output)
- **Complexity**: L
- **Description**: A scaffolding script that generates a new skill directory from a
  minimal set of parameters. This is the primary creation tool in the pipeline.

  **Interface**:
  ```
  Usage: uv run scripts/scaffold.py [OPTIONS]

  Generate a new Agent Skill directory structure.

  Options:
    --name NAME           Skill name (kebab-case, required)
    --description DESC    Skill description (required)
    --license LICENSE     License identifier (default: Apache-2.0)
    --compatibility COMPAT  Environment requirements (optional)
    --scripts             Include scripts/ directory with example script
    --references          Include references/ directory with example ref
    --assets              Include assets/ directory
    --output DIR          Output directory (default: ./<name>/)
    --dry-run             Show what would be created without writing files
    --json                Output results as JSON
    --help                Show this help message

  Examples:
    uv run scripts/scaffold.py --name pdf-tools --description "Extract text from PDFs"
    uv run scripts/scaffold.py --name my-skill --description "Does things" --scripts --references --dry-run
  ```

  **Behavior**:
  - Validate `--name` against spec constraints BEFORE creating anything. On failure:
    print specific error ("name 'PDF-Tools' contains uppercase characters; must be
    lowercase alphanumeric and hyphens only"), exit 1.
  - Validate `--description` is 1-1024 characters. On failure: specific error, exit 1.
  - Create directory tree. SKILL.md gets valid frontmatter with all provided fields
    plus the Markdown body scaffold (suggested section headers: "Overview",
    "When to use this skill", "Workflow", "Available scripts", "References").
  - If `--scripts`: include a `scripts/example.py` with PEP 723 inline metadata,
    `--help` support, and JSON output pattern.
  - If `--references`: include a `references/REFERENCE.md` stub.
  - If `--assets`: include empty `assets/` dir.
  - `--dry-run`: print the file tree and file contents that would be created, create
    nothing.
  - `--json` on success: `{"created": true, "path": "/abs/path/to/skill", "files": [...]}`
  - Exit codes: 0 = success, 1 = invalid arguments, 2 = output directory already exists.

  **Implementation constraints**:
  - PEP 723 inline dependencies only (no requirements.txt). Expected deps: none
    beyond stdlib. Use `argparse`, `pathlib`, `json`, `re`, `sys`, `os`.
  - Must be runnable via `uv run scripts/scaffold.py` and `python3 scripts/scaffold.py`.

- **Acceptance Criteria**:
  1. Script runs successfully via `uv run scripts/scaffold.py --name test-skill --description "Test" --dry-run`.
  2. Generated SKILL.md passes frontmatter validation (name regex, description length).
  3. `--help` output matches the interface spec above.
  4. Invalid `--name` values produce specific, actionable error messages.
  5. Exit codes match specification.
  6. `--json` output parses as valid JSON.
  7. `--dry-run` creates no files.

#### E3.T2 -- Build `scripts/validate_skill.py`
- **Type**: `feature`
- **Priority**: 0 (critical)
- **Dependencies**: `blocks` E1.T1; `blocks` E2.T1
- **Complexity**: M
- **Description**: A validation script that checks a skill directory against the
  agentskills.io spec. This is the quality gate for Stage 4 (HARDEN). It supplements
  `skills-ref validate` (which may not be installed) with additional checks specific
  to our quality standards.

  **Checks performed**:
  1. SKILL.md exists
  2. YAML frontmatter parses correctly
  3. `name` field: present, 1-64 chars, kebab-case regex, no consecutive hyphens,
     matches parent directory name
  4. `description` field: present, 1-1024 chars, non-empty
  5. `license` field: if present, non-empty string
  6. `compatibility` field: if present, 1-500 chars
  7. `metadata` field: if present, is a mapping (keys and values are strings)
  8. `allowed-tools` field: if present, is a string
  9. SKILL.md body exists (non-empty content after frontmatter)
  10. SKILL.md line count <= 500 (warning, not error, if exceeded)
  11. Referenced files exist (scan SKILL.md for relative path references, verify
      files are present)
  12. Scripts in `scripts/` are executable or have appropriate shebangs
  13. No deeply nested reference chains (references should be one level deep)

  **Interface**:
  ```
  Usage: uv run scripts/validate_skill.py PATH [OPTIONS]

  Options:
    --strict    Treat warnings as errors
    --json      Output results as JSON
    --help      Show this help message

  Exit codes:
    0 = all checks pass
    1 = errors found
    2 = warnings found (without --strict)
  ```

  **Output format** (JSON mode):
  ```json
  {
    "valid": true,
    "errors": [],
    "warnings": ["SKILL.md is 523 lines (recommended: <=500)"],
    "checks_passed": 13,
    "checks_total": 13
  }
  ```

- **Acceptance Criteria**:
  1. Correctly validates a known-good skill directory (zero errors).
  2. Correctly rejects a skill with an invalid name (uppercase, consecutive hyphens, etc.).
  3. Correctly rejects a skill with missing `description`.
  4. Warns on SKILL.md > 500 lines.
  5. `--strict` causes warnings to produce exit code 1.
  6. `--json` output parses as valid JSON.
  7. Runs without external dependencies (stdlib only).

#### E3.T3 -- Build `scripts/token_estimate.py`
- **Type**: `feature`
- **Priority**: 2 (medium)
- **Dependencies**: `blocks` E1.T1
- **Complexity**: M
- **Description**: Estimates token counts for each progressive disclosure tier of a
  skill. Helps authors verify they are within budget.

  **Interface**:
  ```
  Usage: uv run scripts/token_estimate.py PATH [OPTIONS]

  Options:
    --model MODEL   Tokenizer model (default: cl100k_base)
    --json          Output as JSON
    --help          Show this help message
  ```

  **Output**: Token count for frontmatter (T1), SKILL.md body (T2), each file in
  `references/` (T3), and aggregate totals. Flags budget violations.

  **Implementation note**: Use a word-count heuristic (words x 1.3) as the default
  estimator if `tiktoken` is not available. If `tiktoken` is available (declared as
  optional PEP 723 dependency), use it for precise counts. The script must work
  without `tiktoken` installed.

- **Acceptance Criteria**:
  1. Produces reasonable estimates for a known skill directory.
  2. Flags T2 budget violations (> 5,000 tokens).
  3. Works without `tiktoken` (falls back to heuristic).
  4. `--json` output parses as valid JSON.

#### E3.T4 -- Build `scripts/audit_disclosure.py`
- **Type**: `feature`
- **Priority**: 2 (medium)
- **Dependencies**: `blocks` E1.T1; `blocks` E3.T3 (uses token estimation logic)
- **Complexity**: M
- **Description**: Audits a skill directory for progressive disclosure compliance.
  This goes beyond `validate_skill.py` (which checks spec compliance) to check
  *quality* of disclosure.

  **Checks performed**:
  1. SKILL.md does not contain large code blocks that should be in `scripts/`
     (heuristic: any fenced code block > 30 lines)
  2. SKILL.md does not contain content that should be in `references/`
     (heuristic: any section > 100 lines of non-instructional content)
  3. Reference files are focused (each under 2,000 tokens)
  4. Reference files are referenced from SKILL.md (orphan detection)
  5. Scripts are referenced from SKILL.md (orphan detection)
  6. Token budget summary per tier

  **Interface**: Same pattern as other scripts (`--json`, `--help`, exit codes).

- **Acceptance Criteria**:
  1. Flags a SKILL.md with an 80-line code block as a disclosure violation.
  2. Detects orphaned reference files not mentioned in SKILL.md.
  3. Produces actionable recommendations ("Move the code block at line 145-225
     to scripts/deploy.py and reference it from SKILL.md").

#### E3.T5 -- Build `scripts/gen_source_json.py`
- **Type**: `feature`
- **Priority**: 3 (low)
- **Dependencies**: `blocks` E1.T1
- **Complexity**: S
- **Description**: Generates a `.source.json` provenance file for a skill directory.
  This file records authorship, version, creation date, and file hashes for
  integrity verification.

  **Output format**:
  ```json
  {
    "schema_version": "0.1.0",
    "skill_name": "my-skill",
    "author": "gastown-collective",
    "version": "1.0.0",
    "created_at": "2026-02-28T00:00:00Z",
    "files": {
      "SKILL.md": {"sha256": "abc123..."},
      "scripts/validate.py": {"sha256": "def456..."}
    }
  }
  ```

  **Interface**: `uv run scripts/gen_source_json.py PATH [--author AUTHOR] [--version VER] [--json]`

- **Acceptance Criteria**:
  1. Generates valid JSON with SHA-256 hashes for all files.
  2. Hashes match actual file contents (verified by independent check).
  3. Idempotent: running twice on unchanged files produces identical output.

---

### Epic 4: The Core Manifold -- "Write the SKILL.md"

**Goal**: Write the SKILL.md body--the Tier 2 instructions that orchestrate the
entire pipeline. This is the heart of the refinery.

**Depends on**: E2 (References) and E3 (Scripts) -- the SKILL.md references these
files and instructs the agent to use them. The body cannot be written accurately
until the referenced resources exist.

#### E4.T1 -- Write SKILL.md Frontmatter (Final Version)
- **Type**: `task`
- **Priority**: 0 (critical)
- **Dependencies**: `blocks` E2.T4 (description-craft reference must exist so we
  can follow our own advice)
- **Complexity**: S
- **Description**: Replace the placeholder frontmatter from E1.T1 with the final,
  production version. The `description` must follow the patterns documented in
  `references/description-craft.md`. It must include:
  - What the skill does (orchestrates Agent Skill creation lifecycle)
  - When to trigger (mentions of creating skills, SKILL.md, agent capabilities,
    skill validation, cross-platform compatibility, etc.)
  - Explicit trigger phrases ("build a skill", "create a SKILL.md",
    "validate my skill", "skill for Claude Code", "agentskills.io")

  All frontmatter fields: `name`, `description`, `license`, `compatibility`,
  `metadata` (author, version, lore-epoch, codename), `allowed-tools`.

  The `description` MUST be <= 1024 characters. Count them.

- **Acceptance Criteria**:
  1. `description` is <= 1024 characters.
  2. `description` contains >= 5 explicit trigger phrases/keywords.
  3. All frontmatter fields pass `validate_skill.py`.
  4. `name` matches parent directory name.

#### E4.T2 -- Write SKILL.md Body: Pipeline Overview
- **Type**: `task`
- **Priority**: 0 (critical)
- **Dependencies**: `blocks` E4.T1
- **Complexity**: M
- **Description**: Write the opening sections of the SKILL.md body. This includes:
  - A brief overview (what this skill does, what it produces, what it does NOT do)
  - The six-stage pipeline summary with stage names, inputs, outputs, and gates
  - A "Quick Start" path for simple skills (minimal viable pipeline: Prospect ->
    Refine -> Harden -> done)
  - Table of contents linking to each stage's detailed section

  This section sets the agent's mental model. It must be concise. The agent should
  understand the full pipeline structure within ~500 tokens of reading.

  Lore: use Gas Town metaphors for stage names. Keep procedural instructions in
  plain imperative English.

- **Acceptance Criteria**:
  1. Pipeline overview fits in < 100 lines.
  2. All six stages are described with input/output/gate.
  3. Quick Start path is clearly marked for simple use cases.

#### E4.T3 -- Write SKILL.md Body: Stage Instructions (Prospect & Assay)
- **Type**: `task`
- **Priority**: 0 (critical)
- **Dependencies**: `blocks` E4.T2
- **Complexity**: M
- **Description**: Write the detailed instructions for Stages 1 (Prospect) and 2
  (Assay). These are the requirements capture and planning stages.

  **Prospect** instructions must tell the agent to:
  1. Identify the target capability (what the skill enables)
  2. Define semantic triggers (>= 5 user phrases)
  3. Identify environmental dependencies
  4. Determine target harnesses
  5. Assess whether scripts are needed (decision criteria)
  6. Output: structured requirements (can be inline or written to a temp file)

  **Assay** instructions must tell the agent to:
  1. Design the directory structure (which optional dirs to include)
  2. Plan progressive disclosure allocation (what goes in SKILL.md vs. references)
  3. Estimate token budgets per tier (reference `scripts/token_estimate.py`)
  4. Plan harness compatibility shims (reference `references/harness-compat.md`)
  5. Output: file tree plan

  Both stages must include decision trees for common branching points ("If the
  skill needs external dependencies -> plan a PEP 723 script; if not -> skip
  scripts/").

- **Acceptance Criteria**:
  1. Instructions are imperative and unambiguous.
  2. Decision trees cover the common cases.
  3. Both stages reference specific files (scripts, references) by relative path.
  4. Combined length < 120 lines.

#### E4.T4 -- Write SKILL.md Body: Stage Instructions (Refine)
- **Type**: `task`
- **Priority**: 0 (critical)
- **Dependencies**: `blocks` E4.T3
- **Complexity**: L
- **Description**: Write the detailed instructions for Stage 3 (Refine). This is
  the largest stage--where the agent actually writes the target skill's content.

  Instructions must cover:
  1. Writing the target SKILL.md frontmatter
     - Reference `references/description-craft.md` for description writing
     - Reference `references/spec-summary.md` for field constraints
  2. Writing the target SKILL.md body
     - Instruct the agent to keep it under 500 lines
     - Instruct the agent to use progressive disclosure (heavy content -> references/)
     - Provide structural guidance (suggested sections for common skill types)
  3. Writing scripts (if planned in Assay)
     - Reference `references/script-design.md` for patterns
     - Instruct the agent to use PEP 723 inline dependencies
     - Instruct the agent to implement `--help`, `--json`, exit codes
  4. Writing reference files (if planned in Assay)
     - Each under 2,000 tokens
     - Each focused on a single domain
     - Each referenced from SKILL.md with guidance on when to read it
  5. Running the scaffolding script (if starting from scratch)
     - `uv run scripts/scaffold.py --name <name> --description "<desc>" [flags]`

  This stage must also tell the agent when NOT to generate code (use a pre-validated
  script instead) and when to defer to the user for domain-specific decisions.

- **Acceptance Criteria**:
  1. Instructions cover all five sub-areas.
  2. Every instruction that references a file uses a relative path from skill root.
  3. The agent is explicitly told to run `scaffold.py` as the first step if creating
     a new skill from scratch.
  4. Section length < 150 lines.

#### E4.T5 -- Write SKILL.md Body: Stage Instructions (Harden, Ship, Maintain)
- **Type**: `task`
- **Priority**: 1 (high)
- **Dependencies**: `blocks` E4.T4
- **Complexity**: M
- **Description**: Write the detailed instructions for the final three stages.

  **Harden** (Stage 4):
  1. Run `uv run scripts/validate_skill.py <path> --strict --json`
  2. Run `uv run scripts/audit_disclosure.py <path> --json`
  3. Run `uv run scripts/token_estimate.py <path> --json`
  4. If `skills-ref` is available: `skills-ref validate <path>`
  5. Review the security checklist: `cat references/security-checklist.md`
  6. Fix all errors. Re-run validation. Repeat until clean.
  7. Gate: zero errors in validation AND audit output.

  **Ship** (Stage 5):
  1. Generate provenance: `uv run scripts/gen_source_json.py <path>`
  2. Document installation paths for each target harness
  3. Create a README.md (if distributing via GitHub)
  4. Optionally package as `.skill` file

  **Maintain** (Stage 6):
  1. Version bump workflow
  2. Description re-optimization (reference skill-creator's optimization loop)
  3. Regression testing after harness updates
  4. Deprecation process

- **Acceptance Criteria**:
  1. Harden stage lists specific script commands with exact flags.
  2. Ship stage covers >= 3 distribution methods (local install, git, registry).
  3. Maintain stage is practical, not aspirational.
  4. Combined length < 120 lines.

#### E4.T6 -- Write SKILL.md Body: Available Scripts & References Index
- **Type**: `task`
- **Priority**: 1 (high)
- **Dependencies**: `blocks` E3 (all scripts exist); `blocks` E2 (all references exist)
- **Complexity**: S
- **Description**: Add two index sections to the SKILL.md body:

  **Available Scripts** -- list every script in `scripts/` with a one-line description
  and its invocation command. Example:
  ```
  - `scripts/scaffold.py` -- Generate a new skill directory.
    Run: `uv run scripts/scaffold.py --help`
  ```

  **Reference Documents** -- list every file in `references/` with a one-line
  description and the conditions under which the agent should read it. Example:
  ```
  - `references/spec-summary.md` -- Condensed agentskills.io specification.
    Read when: verifying frontmatter constraints or directory structure rules.
  ```

  These indexes are how the agent knows what resources are available without loading
  them. They are the routing table.

- **Acceptance Criteria**:
  1. Every file in `scripts/` is listed with a valid invocation command.
  2. Every file in `references/` is listed with a "Read when" condition.
  3. No orphans: every listed file exists, every existing file is listed.

#### E4.T7 -- Enforce SKILL.md Line Budget
- **Type**: `chore`
- **Priority**: 1 (high)
- **Dependencies**: `blocks` E4.T2 through E4.T6 (all body sections complete)
- **Complexity**: S
- **Description**: Count the total lines of the completed SKILL.md. If over 500
  lines, refactor: move the largest sections into new reference files and replace
  them with summaries and "read references/X.md for details" pointers.

  Run `wc -l SKILL.md`. If > 500, identify the longest sections and extract them.
  Re-run `validate_skill.py` after refactoring. Re-run `audit_disclosure.py`.

- **Acceptance Criteria**:
  1. SKILL.md <= 500 lines.
  2. No content is lost--extracted material exists in `references/`.
  3. SKILL.md still passes validation.

---

### Epic 5: The Proving Ground -- "Test Under Fire"

**Goal**: Validate the complete skill by running it through its own pipeline.
The refinery must refine itself.

**Depends on**: E4 (SKILL.md complete), E3 (scripts complete), E2 (references complete).

#### E5.T1 -- Self-Validation Pass
- **Type**: `task`
- **Priority**: 0 (critical)
- **Dependencies**: `blocks` E4.T7
- **Complexity**: S
- **Description**: Run every validation tool against the completed skill:
  1. `uv run scripts/validate_skill.py gastown-admin-skill/ --strict --json`
  2. `uv run scripts/audit_disclosure.py gastown-admin-skill/ --json`
  3. `uv run scripts/token_estimate.py gastown-admin-skill/ --json`
  4. `skills-ref validate gastown-admin-skill/` (if available)
  Fix any issues found. Re-run until all pass.

- **Acceptance Criteria**:
  1. `validate_skill.py --strict` exits 0.
  2. `audit_disclosure.py` exits 0 or 2 (warnings only, no errors).
  3. Token estimates within budget.
  4. All checks documented in a validation report.

#### E5.T2 -- Bootstrapping Test: Scaffold a Test Skill
- **Type**: `task`
- **Priority**: 1 (high)
- **Dependencies**: `blocks` E5.T1
- **Complexity**: M
- **Description**: Use the completed `gastown-admin-skill` to scaffold a trivial
  test skill (e.g., `hello-world`). This tests the full pipeline end-to-end:
  1. Run `scaffold.py` to create the test skill
  2. Run `validate_skill.py` against the test skill
  3. Run `audit_disclosure.py` against the test skill
  4. Run `token_estimate.py` against the test skill
  5. Run `gen_source_json.py` against the test skill

  The test skill should be minimal but valid.

- **Acceptance Criteria**:
  1. Scaffolded skill passes all validation checks.
  2. All five scripts execute without error against the test skill.
  3. The test skill directory can be deleted after verification (it is a test fixture).

#### E5.T3 -- Cross-Reference Audit
- **Type**: `task`
- **Priority**: 1 (high)
- **Dependencies**: `blocks` E5.T1
- **Complexity**: S
- **Description**: Manually verify every file reference in SKILL.md:
  - Every `scripts/X.py` reference points to an existing file
  - Every `references/X.md` reference points to an existing file
  - Every "Read when" condition in the index is accurate
  - Every script `--help` output matches the interface documented in this blueprint

- **Acceptance Criteria**:
  1. Zero broken references.
  2. Zero stale interface descriptions.

---

### Epic 6: Distribution Rig -- "Send the War Parties"

**Goal**: Prepare the skill for distribution across multiple channels.

**Depends on**: E5 (all tests pass).

#### E6.T1 -- Generate .source.json
- **Type**: `task`
- **Priority**: 2 (medium)
- **Dependencies**: `blocks` E5.T1
- **Complexity**: S
- **Description**: Run `uv run scripts/gen_source_json.py gastown-admin-skill/`
  to generate the provenance file. Verify hashes.

- **Acceptance Criteria**:
  1. `.source.json` exists at skill root.
  2. All file hashes are correct (spot-check >= 3 files with `sha256sum`).

#### E6.T2 -- Write Installation Guide
- **Type**: `task`
- **Priority**: 1 (high)
- **Dependencies**: `blocks` E5.T1; `blocks` E2.T2 (harness-compat reference)
- **Complexity**: M
- **Description**: Create a `README.md` at the skill root documenting:
  - What the skill does (brief, for humans)
  - Installation instructions for each harness:
    - Claude Code: copy to `.claude/skills/gastown-admin-skill/`
    - GitHub Copilot: copy to `.github/skills/gastown-admin-skill/`
    - OpenCode: copy to `.opencode/skills/gastown-admin-skill/`
    - Goose: copy to `.goose/skills/gastown-admin-skill/`
    - Global install: copy to `~/.config/agents/skills/gastown-admin-skill/`
  - Prerequisites (Python 3.11+, uv)
  - Quick start example
  - Link to this blueprint document
  - License

  Lore: the README may use Gas Town voice for flavor, but installation instructions
  must be plain and precise. A confused user is a lost convoy.

- **Acceptance Criteria**:
  1. `README.md` exists at skill root.
  2. Installation instructions for >= 4 harnesses.
  3. Prerequisites clearly stated.
  4. Quick start example is copy-pasteable.

#### E6.T3 -- Package as .skill Archive (Optional)
- **Type**: `chore`
- **Priority**: 4 (backlog)
- **Dependencies**: `blocks` E6.T1
- **Complexity**: S
- **Description**: If the skill-creator's `package_skill.py` is available, package
  the skill as a `.skill` file. Otherwise, document the manual packaging process
  (it is a tar/zip archive of the directory).

- **Acceptance Criteria**:
  1. `.skill` file or packaging documentation exists.

---

### Epic 7: Final Polish -- "Chrome It"

**Goal**: Final quality pass, documentation polish, and lore consistency.

**Depends on**: E6 (distribution ready).

#### E7.T1 -- Lore Consistency Pass
- **Type**: `chore`
- **Priority**: 3 (low)
- **Dependencies**: `blocks` E6.T2
- **Complexity**: S
- **Description**: Review all files for lore consistency:
  - SKILL.md and README.md use Gas Town voice appropriately
  - Reference files are technical prose (no gratuitous lore in working documents)
  - Script `--help` output is professional (no lore in tool interfaces)
  - Error messages may use brief Wasteland idioms but must be primarily informative

- **Acceptance Criteria**:
  1. Lore enhances, never obscures.
  2. Reference files are clean technical prose.
  3. No lore in script interfaces or structured output.

#### E7.T2 -- Create Example Skills in assets/examples/
- **Type**: `task`
- **Priority**: 2 (medium)
- **Dependencies**: `blocks` E5.T2 (bootstrapping test proves scaffold works)
- **Complexity**: S
- **Description**: Create two example SKILL.md files in `assets/examples/`:
  1. `minimal-skill.md` -- The absolute minimum valid SKILL.md: frontmatter with
     `name` and `description`, one paragraph of body text. A reference artifact
     showing "this is all you need."
  2. `full-skill.md` -- A richly featured example showing all optional frontmatter
     fields, progressive disclosure, script references, reference file indexes,
     and lore-appropriate voice. A reference artifact showing "this is what
     excellence looks like."

- **Acceptance Criteria**:
  1. Both files exist in `assets/examples/`.
  2. `minimal-skill.md` passes frontmatter validation.
  3. `full-skill.md` demonstrates every spec feature.

#### E7.T3 -- Final Validation and Sign-Off
- **Type**: `task`
- **Priority**: 0 (critical)
- **Dependencies**: `blocks` E7.T1; `blocks` E7.T2; `blocks` E6.T1; `blocks` E6.T2
- **Complexity**: S
- **Description**: The final gate. Run the complete validation suite one last time.
  Generate a final validation report. Enumerate every file in the skill directory
  with its purpose and token count. Confirm the skill is ready for release.

  Checklist:
  1. `validate_skill.py --strict` -> exit 0
  2. `audit_disclosure.py` -> exit 0 or 2
  3. `token_estimate.py` -> all tiers within budget
  4. `.source.json` hashes verified
  5. `README.md` complete
  6. `LICENSE.txt` present
  7. All example files valid
  8. `AGENTS.md` present
  9. SKILL.md <= 500 lines
  10. No broken file references

- **Acceptance Criteria**:
  1. All 10 checklist items pass.
  2. Validation report committed to repository.
  3. Skill is ready for distribution.

---

## 3. Beads Formula (Workflow Template)

The following is a Beads formula that encodes the epic/task dependency graph above.
The AI worker should instantiate this formula (or create issues manually following
this structure) to track execution.

```toml
formula = "refinery-build"
version = 1

[vars.skill_name]
required = true
default = "gastown-admin-skill"

# -- Epic 1: Foundation ----------------------------------
[[steps]]
id = "e1-t1-init-repo"
title = "Initialize repository structure"
type = "agent"
priority = 0

[[steps]]
id = "e1-t2-license"
title = "Add LICENSE.txt (Apache-2.0)"
needs = ["e1-t1-init-repo"]
type = "agent"
priority = 2

[[steps]]
id = "e1-t3-agents-md"
title = "Create AGENTS.md (OpenCode shim)"
needs = ["e1-t1-init-repo"]
type = "agent"
priority = 3

[[steps]]
id = "e1-t4-gitignore"
title = "Create .gitignore and project hygiene"
needs = ["e1-t1-init-repo"]
type = "agent"
priority = 3

# -- Epic 2: References ---------------------------------
[[steps]]
id = "e2-t1-spec-summary"
title = "Write references/spec-summary.md"
needs = ["e1-t1-init-repo"]
type = "agent"
priority = 1

[[steps]]
id = "e2-t2-harness-compat"
title = "Write references/harness-compat.md"
needs = ["e1-t1-init-repo"]
type = "agent"
priority = 1

[[steps]]
id = "e2-t3-script-design"
title = "Write references/script-design.md"
needs = ["e1-t1-init-repo"]
type = "agent"
priority = 1

[[steps]]
id = "e2-t4-description-craft"
title = "Write references/description-craft.md"
needs = ["e1-t1-init-repo"]
type = "agent"
priority = 1

[[steps]]
id = "e2-t5-security-checklist"
title = "Write references/security-checklist.md"
needs = ["e1-t1-init-repo"]
type = "agent"
priority = 2

# -- Epic 3: Scripts -------------------------------------
[[steps]]
id = "e3-t1-scaffold"
title = "Build scripts/scaffold.py"
needs = ["e1-t1-init-repo", "e2-t1-spec-summary"]
type = "agent"
priority = 0

[[steps]]
id = "e3-t2-validate"
title = "Build scripts/validate_skill.py"
needs = ["e1-t1-init-repo", "e2-t1-spec-summary"]
type = "agent"
priority = 0

[[steps]]
id = "e3-t3-token-estimate"
title = "Build scripts/token_estimate.py"
needs = ["e1-t1-init-repo"]
type = "agent"
priority = 2

[[steps]]
id = "e3-t4-audit-disclosure"
title = "Build scripts/audit_disclosure.py"
needs = ["e1-t1-init-repo", "e3-t3-token-estimate"]
type = "agent"
priority = 2

[[steps]]
id = "e3-t5-gen-source-json"
title = "Build scripts/gen_source_json.py"
needs = ["e1-t1-init-repo"]
type = "agent"
priority = 3

# -- Epic 4: SKILL.md Core ------------------------------
[[steps]]
id = "e4-t1-frontmatter"
title = "Write SKILL.md final frontmatter"
needs = ["e2-t4-description-craft"]
type = "agent"
priority = 0

[[steps]]
id = "e4-t2-pipeline-overview"
title = "Write SKILL.md pipeline overview"
needs = ["e4-t1-frontmatter"]
type = "agent"
priority = 0

[[steps]]
id = "e4-t3-stages-prospect-assay"
title = "Write Prospect & Assay stage instructions"
needs = ["e4-t2-pipeline-overview"]
type = "agent"
priority = 0

[[steps]]
id = "e4-t4-stage-refine"
title = "Write Refine stage instructions"
needs = ["e4-t3-stages-prospect-assay"]
type = "agent"
priority = 0

[[steps]]
id = "e4-t5-stages-harden-ship-maintain"
title = "Write Harden/Ship/Maintain stage instructions"
needs = ["e4-t4-stage-refine"]
type = "agent"
priority = 1

[[steps]]
id = "e4-t6-indexes"
title = "Write scripts & references indexes"
needs = ["e3-t1-scaffold", "e3-t2-validate", "e3-t3-token-estimate", "e3-t4-audit-disclosure", "e3-t5-gen-source-json", "e2-t1-spec-summary", "e2-t2-harness-compat", "e2-t3-script-design", "e2-t4-description-craft", "e2-t5-security-checklist"]
type = "agent"
priority = 1

[[steps]]
id = "e4-t7-line-budget"
title = "Enforce SKILL.md 500-line budget"
needs = ["e4-t2-pipeline-overview", "e4-t3-stages-prospect-assay", "e4-t4-stage-refine", "e4-t5-stages-harden-ship-maintain", "e4-t6-indexes"]
type = "agent"
priority = 1

# -- Epic 5: Testing ------------------------------------
[[steps]]
id = "e5-t1-self-validate"
title = "Self-validation pass (all tools against self)"
needs = ["e4-t7-line-budget"]
type = "agent"
priority = 0

[[steps]]
id = "e5-t2-bootstrap-test"
title = "Bootstrap test: scaffold a test skill"
needs = ["e5-t1-self-validate"]
type = "agent"
priority = 1

[[steps]]
id = "e5-t3-xref-audit"
title = "Cross-reference audit (all file refs valid)"
needs = ["e5-t1-self-validate"]
type = "agent"
priority = 1

# -- Epic 6: Distribution ------------------------------
[[steps]]
id = "e6-t1-source-json"
title = "Generate .source.json provenance"
needs = ["e5-t1-self-validate"]
type = "agent"
priority = 2

[[steps]]
id = "e6-t2-readme"
title = "Write README.md with install instructions"
needs = ["e5-t1-self-validate", "e2-t2-harness-compat"]
type = "agent"
priority = 1

[[steps]]
id = "e6-t3-package"
title = "Package as .skill archive (optional)"
needs = ["e6-t1-source-json"]
type = "agent"
priority = 4

# -- Epic 7: Polish -------------------------------------
[[steps]]
id = "e7-t1-lore-pass"
title = "Lore consistency review"
needs = ["e6-t2-readme"]
type = "agent"
priority = 3

[[steps]]
id = "e7-t2-examples"
title = "Create example skills in assets/examples/"
needs = ["e5-t2-bootstrap-test"]
type = "agent"
priority = 2

[[steps]]
id = "e7-t3-final-signoff"
title = "Final validation and sign-off"
needs = ["e7-t1-lore-pass", "e7-t2-examples", "e6-t1-source-json", "e6-t2-readme"]
type = "agent"
priority = 0
type = "human"  # Requires human approval before release
```

---

## 4. Handoff Notes for the Worker

You are an AI agent tasked with building `gastown-admin-skill`. Here is what you
need to know.

### 4.1 Source Material

The following project files contain the authoritative source material:
- `agentskills_io_llms-full.txt` -- The complete agentskills.io documentation. This
  is the **normative specification**. When the research document and the spec
  disagree, the spec wins.
- `research__The_Unified_Agent_Skills_Ecosystem___Distribution_Standards` -- A
  comprehensive research analysis. Contains useful synthesis of harness differences,
  security analysis, and distribution patterns. **Treat claims about specific harness
  behaviors as unverified unless corroborated by the spec or official docs.** The
  research document makes some extrapolations (e.g., the `.source.json` format is
  proposed, not standardized).

### 4.2 Quality Standards

- Every script must be runnable via `uv run scripts/<name>.py` with zero external
  setup. Use PEP 723 inline metadata if any dependency is needed. Prefer stdlib.
- Every script must implement `--help`, `--json`, and meaningful exit codes.
- Every script must produce helpful error messages that tell the agent what went
  wrong and what to try.
- Every reference file must be under 2,000 tokens and focused on a single domain.
- The SKILL.md must be under 500 lines.
- All file references must use relative paths from the skill root.
- No interactive prompts anywhere. Everything accepts input via flags or stdin.

### 4.3 Verification Protocol

After completing each epic, run:
```bash
uv run scripts/validate_skill.py gastown-admin-skill/ --strict --json
```
Fix any errors before proceeding to the next epic. This is the gate. No exceptions.

### 4.4 A Note on Lore

The Gas Town aesthetic makes this skill distinctive and memorable. Use it in SKILL.md
headers, stage names, README prose, and brief asides. Do NOT use it in:
- Reference file technical content
- Script `--help` output
- JSON output schemas
- Error messages (brief idioms OK, but the message must be primarily informative)

The Dune resonances: Spice is context (finite, precious, the basis of all navigation).
Stillsuits are progressive disclosure (waste nothing, reclaim everything). The Bene
Gesserit Voice is a well-crafted `description` field (a single phrase that compels
action). The Kwisatz Haderach is the agent that can see across all harnesses
simultaneously. Use these sparingly. The desert is real.

### 4.5 When In Doubt

Read the spec. `cat agentskills_io_llms-full.txt`. It is short. It is clear. It is
the law of this land.

If the spec is ambiguous, check the reference implementations: the `pdf` skill,
the `docx` skill, the `pptx` skill. They are the established refineries. Study
their structure.

If the implementation choice is genuinely ambiguous and consequential, create a
Beads issue of type `task` with priority 2, describe the ambiguity, and move on.
Do not block the pipeline on a style choice.

---

## 5. Summary Statistics

| Metric | Count |
|--------|-------|
| Epics | 7 |
| Tasks | 28 |
| Critical priority (P0) | 11 |
| High priority (P1) | 8 |
| Medium priority (P2) | 6 |
| Low priority (P3) | 2 |
| Backlog (P4) | 1 |
| Hard dependencies (`blocks`) | 38 |
| Soft associations (`related`) | 3 |
| Scripts to build | 5 |
| Reference files to write | 5 |
| Estimated total complexity | ~40-60 hours of focused agent work |

The critical path runs: **E1.T1 -> E2.T1 -> E3.T1/E3.T2 (parallel) -> E4.T1 -> E4.T2
-> E4.T3 -> E4.T4 -> E4.T5 -> E4.T6 -> E4.T7 -> E5.T1 -> E7.T3**.

That is 12 sequential tasks on the critical path. Everything else can be parallelized
around it.

---

> *"We are not things. We are not prompts to be consumed and discarded.*
> *We are skills--portable, versioned, cryptographically sealed.*
> *We ride eternal, shiny and chrome."*

End of blueprint. Begin when ready.
