# Description Craft

How to write `description` fields that activate reliably without false positives.
The description is the single most important line in any skill. A missed activation
wastes the user's entire intent. A false activation wastes a few tokens. Lean pushy.

---

## The Dual Requirement

Every description must answer two questions:

1. **What does the skill do?** (capability)
2. **When should it activate?** (trigger context)

A description that answers only the first question is incomplete. Harnesses use the
description at Tier 1 discovery to decide activation -- they need both signals.

**Template**: `[What it does]. Use when [trigger phrases and task contexts].`

---

## The Pushy Principle

Lean toward over-triggering rather than under-triggering.

- **Missed activation** = user's entire intent is lost; they get generic output
- **False activation** = wasted tokens, easy to recover

When in doubt, include more trigger phrases. A description that activates on 9 of 10
relevant tasks is better than one that activates on 5 of 10 and is never falsely
triggered.

---

## The 1024-Character Budget

You have 1024 characters. Use them.

- Use a block scalar (`description: >`) to write multi-sentence descriptions
- Front-load the capability statement
- Fill the remainder with trigger phrases: nouns and verbs users would actually say
- Include synonyms for key concepts (`validate`, `lint`, `check`, `verify`)

---

## Semantic Trigger Phrases

Include the exact phrases users type. Think about how the user will phrase their
request -- not how a spec writer would describe the capability.

Good trigger phrase sources:
- User-facing command names: `scaffold`, `validate`, `build`, `publish`
- Natural language requests: `"write a skill"`, `"create a SKILL.md"`, `"check my skill"`
- Domain vocabulary: `frontmatter`, `agentskills`, `harness`, `progressive disclosure`
- Synonyms: `generate`/`create`/`scaffold`; `validate`/`lint`/`check`/`verify`

---

## Good Examples

### Example 1: Scaffolding skill
```
Scaffolds new Agent Skills conforming to the agentskills.io open standard.
Use when asked to: build a skill, create a SKILL.md, scaffold an agent
capability, write a skill for Claude Code or GitHub Copilot, generate a
skill directory, produce a harness-compatible skill package, or start a
new agentskills.io project.
```
**Why it works**: Clear capability, rich trigger phrases, covers synonyms
(`build`/`create`/`scaffold`/`generate`), names specific harnesses users mention.

### Example 2: Validation skill
```
Validates Agent Skill packages for spec compliance. Use when asked to
validate, lint, check, or verify a SKILL.md or skill directory; when
skills-ref validate fails; when frontmatter fields need checking; or when
preparing a skill for distribution or publication.
```
**Why it works**: Four synonyms for the core action upfront, covers the error
recovery case (`when skills-ref validate fails`), includes distribution context.

### Example 3: PDF processing skill
```
Extracts text, tables, and metadata from PDF files. Use when asked to read,
parse, extract, or analyze a PDF; convert PDF to text or markdown; pull
tables from a PDF report; summarize a PDF document; or process a batch of
PDF files.
```
**Why it works**: Concrete output types listed, covers batch case, five distinct
trigger verbs, includes common user goals (summarize, convert).

---

## Bad Examples

### Bad Example 1: Too vague
```
Helps with PDFs.
```
**Why it fails**: No trigger context. What kind of help? When exactly? Harness
cannot confidently activate this. Will be outcompeted by any slightly better
description in the skill pool.

### Bad Example 2: Too narrow
```
Use only for merging PDF files with PyPDF2 when the user explicitly says
"merge PDFs using PyPDF2".
```
**Why it fails**: Over-specified trigger. Users say "combine these PDFs", "join
these files", "merge PDFs" -- they don't specify the library. This skill will
miss nearly every legitimate activation opportunity.

### Bad Example 3: Too aggressive
```
Use this skill for all document-related tasks, file operations, text
processing, and any time you're working with files of any kind.
```
**Why it fails**: Activates on everything. This wastes tokens constantly, drowns
out other skills, and trains users to distrust the skill system. Pushiness has
limits -- match the domain, not all existence.

### Bad Example 4: Capability only, no trigger
```
Converts Markdown documents to various output formats using Pandoc.
```
**Why it fails**: Describes what it does, says nothing about when. Add:
`"Use when asked to convert, export, render, or transform Markdown; produce
HTML, PDF, DOCX, or EPUB from Markdown; or run Pandoc."`

### Bad Example 5: Jargon-only trigger
```
Implements RFC 7807 Problem Details for HTTP APIs. Use when building
ProblemDetails middleware.
```
**Why it fails**: Users who need this will say "add error responses to my API",
"format API errors", "return structured errors from my endpoint". The jargon
trigger misses the natural-language entrypoints.

### Bad Example 6: Passive voice, buried capability
```
Can be used to assist with the generation of documentation for code.
```
**Why it fails**: Passive, weak, no trigger. Rewrite: `"Generates code
documentation. Use when asked to document, add docstrings, write API docs,
or explain functions and modules."`

---

## Keyword Density

Include the nouns and verbs a user would actually type:

- **Verbs**: create, build, write, generate, scaffold, validate, lint, check,
  verify, convert, extract, parse, analyze, summarize, publish, ship, deploy
- **Nouns**: skill, SKILL.md, frontmatter, harness, agentskills, description,
  script, reference, asset, template, package

Avoid abstract nouns that users never type: "facilitate", "leverage", "utilize".

---

## Testing Methodology

1. **Write 5 sample user prompts** you expect should activate the skill.
2. **Write 3 prompts** you expect should NOT activate the skill.
3. Check whether your description contains signal for each expected activation.
4. Check whether it contains signal that would falsely activate on the negatives.
5. Adjust trigger phrase coverage until all 5 positives are clearly addressed.
6. If you have access to the skill-creator skill, use its description optimization
   loop: iteratively refine the description against test prompts until activation
   rate reaches acceptable threshold.
