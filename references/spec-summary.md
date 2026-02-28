# agentskills.io Spec Summary

Practitioner reference for agents building or validating skills. Consult this
when verifying a constraint mid-workflow. For harness-specific integration
details see `harness-compat.md`. For script patterns see `script-design.md`.

## Table of Contents

1. [Directory Structure](#directory-structure)
2. [Frontmatter Fields](#frontmatter-fields)
3. [Name Field Constraints](#name-field-constraints)
4. [Description Field Constraints](#description-field-constraints)
5. [Progressive Disclosure Tiers](#progressive-disclosure-tiers)
6. [File Referencing](#file-referencing)
7. [Validation](#validation)

---

## Directory Structure

A skill is a directory containing at minimum a `SKILL.md` file.

```
skill-name/
  SKILL.md        # Required. YAML frontmatter + Markdown body.
  scripts/        # Optional. Executable code agents can run.
  references/     # Optional. Additional documentation agents can read.
  assets/         # Optional. Templates, images, data files.
```

Rules:
- `SKILL.md` is the only required file.
- The directory name must match the `name` frontmatter field exactly.
- Optional directories (`scripts/`, `references/`, `assets/`) are recognized
  by the spec but are not required.

---

## Frontmatter Fields

`SKILL.md` must open with YAML frontmatter delimited by `---`. Two fields are
required; all others are optional.

### `name` (required)

- **Type**: string
- **Constraints**: see [Name Field Constraints](#name-field-constraints) below

### `description` (required)

- **Type**: string
- **Constraints**: see [Description Field Constraints](#description-field-constraints) below

### `license` (optional)

- **Type**: string
- **Purpose**: Specifies the license applied to the skill.
- **Guidance**: Keep it short -- either the name of a license or the name of a
  bundled license file.
- **Example**:
  ```yaml
  license: Apache-2.0
  ```
  ```yaml
  license: Proprietary. LICENSE.txt has complete terms
  ```

### `compatibility` (optional)

- **Type**: string (max 500 characters if provided)
- **Purpose**: Indicates environment requirements such as intended product,
  required system packages, or network access needs. Most skills do not need
  this field.
- **Examples**:
  ```yaml
  compatibility: Designed for Claude Code (or similar products)
  ```
  ```yaml
  compatibility: Requires git, docker, jq, and access to the internet
  ```

### `metadata` (optional)

- **Type**: mapping (arbitrary key-value pairs, string keys to string values)
- **Purpose**: Stores additional properties not defined by the Agent Skills
  spec. Clients may use this field as needed. Use reasonably unique key names
  to avoid accidental conflicts.
- **Example**:
  ```yaml
  metadata:
    author: example-org
    version: "1.0"
  ```

### `allowed-tools` (optional, experimental)

- **Type**: space-delimited string of tool names
- **Purpose**: Lists tools that are pre-approved to run. Support varies between
  agent implementations.
- **Example**:
  ```yaml
  allowed-tools: Bash(git:*) Bash(jq:*) Read
  ```

---

## Name Field Constraints

The `name` field is required. All of the following must hold:

| Rule | Detail |
|------|--------|
| Character set | Lowercase alphanumeric and hyphens only: `a-z`, `0-9`, `-` |
| Length | 1 to 64 characters inclusive |
| No leading hyphen | Must not start with `-` |
| No trailing hyphen | Must not end with `-` |
| No consecutive hyphens | `--` anywhere in the value is invalid |
| Directory match | Must match the parent directory name exactly |

**Valid examples**:
```yaml
name: pdf-processing
name: data-analysis
name: code-review
```

**Invalid examples**:
```yaml
name: PDF-Processing  # uppercase not allowed
name: -pdf            # cannot start with hyphen
name: pdf-            # cannot end with hyphen
name: pdf--processing # consecutive hyphens not allowed
```

---

## Description Field Constraints

The `description` field is required. All of the following must hold:

| Rule | Detail |
|------|--------|
| Length | 1 to 1024 characters inclusive |
| Content | Must describe what the skill does AND when to use it |
| Specificity | Should include keywords that help agents identify relevant tasks |

The description is the primary signal used by agents at discovery time (Tier 1)
to decide whether a skill is relevant to a task. It is the only part of the
skill loaded during discovery -- make it count.

**Good example** (describes capability and trigger context):
```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and
  merges multiple PDFs. Use when working with PDF files or when the user
  mentions PDFs, forms, or document extraction.
```

**Poor example** (too vague, no trigger context):
```yaml
description: Helps with PDFs.
```

---

## Progressive Disclosure Tiers

Skills are loaded in three tiers to manage context costs.

| Tier | Name | What Loads | Token Budget |
|------|------|-----------|-------------|
| 1 | Discovery | `name` + `description` from frontmatter | ~100 tokens per skill |
| 2 | Instructions | Full `SKILL.md` body | < 5000 tokens recommended |
| 3 | Resources | Files in `scripts/`, `references/`, `assets/` | As needed |

**Design guidance**:
- Tier 1 metadata is loaded at agent startup for every available skill.
  Each skill adds roughly 50-100 tokens to the context.
- Tier 2: The agent reads the full `SKILL.md` body when it decides the skill
  is relevant. Keep the body under 500 lines. Move detailed reference material
  to separate files in `references/`.
- Tier 3: Individual files are loaded only when explicitly needed during
  execution. Keep reference files focused; smaller files mean less context use.

---

## File Referencing

When referencing other files in a skill, use paths relative to the skill root:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

**Keep file references one level deep from `SKILL.md`.** Avoid deeply nested
reference chains (e.g., `SKILL.md` -> `advanced.md` -> `details.md`). When
Claude encounters a nested reference, it may only partially read the
intermediate file, resulting in incomplete context.

For reference files longer than 100 lines, include a table of contents at the
top so Claude can see the full scope of available information even when
previewing with partial reads.

---

## Validation

The spec defines a reference CLI tool. On this system, the binary is at:

```
~/.local/share/uv/tools/skills-ref/bin/agentskills
```

To validate a skill directory:

```bash
agentskills validate <path>
```

This checks that:
- `SKILL.md` frontmatter is valid YAML
- `name` matches directory name and satisfies all naming constraints
- `description` is within character limits and non-empty
- Required fields are present
- Directory structure is conformant

The spec also documents the following alias:

```bash
skills-ref validate <path>
```
