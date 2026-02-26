# gas-town-admin

An [Agent Skills](https://agentskills.io) skill for administering
[Gas Town](https://gastownhall.ai) (`gt`) multi-agent orchestration
environments.

Targets an AI agent (an LLM harness) acting as a Gas Town **operator or
infrastructure orchestrator** — not a worker or other entity participating in
the system. It is what an LLM working on behalf of the creator of Gas Town
and/or of any of a number of other gas towns needs in order to do the job well.

In other words, use this when authoring software that drives `gt` commands
programmatically, or when an agent needs to set up, operate, or troubleshoot a
Gas Town installation.

---

## Contents

```
gas-town-admin/
├── SKILL.md                      Core instructions, architecture overview,
│                                 quick-reference decision table
├── references/
│   ├── setup-and-config.md       Install, init, rig management, configuration
│   ├── service-lifecycle.md      Daemon, deacon, mayor, witness, refinery
│   ├── agent-management.md       Polecats, crew, dogs, sessions, identity
│   ├── work-routing.md           Convoys, sling, merge queue, formulas
│   ├── monitoring-diagnostics.md Doctor, status, audit, feeds, dashboard
│   └── communication.md         Nudge, mail, broadcast, escalation
└── harness/
    ├── claude-code.md            Claude Code–specific tool invocation patterns
    └── generic-shell.md          Subprocess patterns for all other runtimes
```

Reference files are loaded on demand (progressive disclosure). An agent
reads only what each task requires.

---

## Prerequisites

- `gt` (Gas Town CLI) in `PATH`
- `bd` (Beads CLI) in `PATH`
- `git`, `tmux`
- Claude Code accessible to the worker agents being managed

---

## Installation

**Claude.ai** — upload `gas-town-admin.skill` via Settings → Features.

**Claude Code** — copy or symlink the skill directory:

```sh
cp -r gas-town-admin ~/.claude/skills/
# or for project-scoped installation:
cp -r gas-town-admin .claude/skills/
```

**Other Agent Skills-compatible runtimes** — place the directory wherever
your runtime's skill loader scans. Consult your runtime's documentation
for the skills path.

**Validation** (requires [skills-ref](https://github.com/agentskills/agentskills)):

```sh
skills-ref validate ./gas-town-admin
```

---

## Design notes

**Scope:** admin/operator only. Worker-side lifecycle (hook, done, handoff,
resume) is intentionally excluded — that belongs in a separate skill.

**Harness portability:** `SKILL.md` and all reference files use
harness-neutral language ("read", "run", "execute"). Platform-specific
optimizations (Claude Code `Bash` tool patterns, `--json` piping via `jq`)
are isolated in `harness/`. An agent on any runtime reads the neutral
baseline; Claude Code agents additionally read `harness/claude-code.md`
for optimized invocation.

**Spec compliance:** frontmatter conforms to the
[Agent Skills open standard](https://agentskills.io/specification) —
name matches directory, description under 1024 chars, no reserved words,
no `allowed-tools` (experimental/platform-specific).

---

## Upstream documentation

Full Gas Town documentation: <https://docs.gastownhall.ai>  
Gas Town source: <https://github.com/steveyegge/gastown>  
Agent Skills specification: <https://agentskills.io/specification>
