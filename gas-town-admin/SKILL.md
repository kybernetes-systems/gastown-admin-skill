---
name: gas-town-admin
description: >
  Administers Gas Town (gt) multi-agent orchestration environments as an
  operator or infrastructure agent: initializes and configures workspaces and
  rigs, manages service lifecycle (daemon, deacon, mayor, witness, refinery),
  spawns and monitors crew and polecat agents, routes work via convoys and
  sling, and diagnoses system health. Use whenever an agent needs to set up,
  configure, operate, or troubleshoot a Gas Town installation, or when
  authoring software that drives gt commands programmatically. Also trigger on
  rig management, agent spawning, convoy administration, merge queue operations,
  or any multi-agent coordination infrastructure task involving the gt CLI.
compatibility: >
  Requires gt (Gas Town CLI) and bd (Beads CLI) in PATH. Also requires git,
  tmux, and a Claude Code installation accessible to the worker agents being
  managed. For platform-optimized invocation patterns, consult
  harness/claude-code.md (Claude Code) or harness/generic-shell.md (all other
  runtimes).
metadata:
  author: gas-town-admin skill
  version: "1.0"
  target-actor: admin-agent
  upstream-docs: https://docs.gastownhall.ai
---

# Gas Town Admin

This skill teaches an agent to operate Gas Town as an **administrator or
infrastructure orchestrator** — setting up the system, managing its services,
routing work to agents, and diagnosing problems. It does not cover the
worker-side (hook/done/handoff) lifecycle; that is a separate concern.

## Architecture in 90 seconds

Gas Town is a tmux-based multi-agent orchestration layer. The directory
`~/gt/` is the **town root** (HQ). Each managed repository is a **rig**,
living at `~/gt/<rig>/`.

**Infrastructure roles** (persistent, one per scope):

| Role | Scope | Responsibility |
|---|---|---|
| Mayor | Town | Global coordinator; receives escalations; human interface |
| Deacon | Town | Health watchdog; monitors Mayor and all Witnesses |
| Witness | Per-rig | Monitors polecats in one rig; handles failures |
| Refinery | Per-rig | Serializes merges to main for one rig |
| Daemon | Town | Dumb Go scheduler; sends heartbeats; no intelligence |

**Worker roles** (transient or persistent):

| Role | Lifecycle | Who controls |
|---|---|---|
| Polecat | Ephemeral — one task, then nuked | Witness |
| Crew | Persistent — survives indefinitely | Human or admin |
| Dog | Very short — single infrastructure task | Deacon |

**Critical distinctions:**
- Dogs are NOT workers. They are Deacon helpers for system-level tasks only.
- Polecats self-destruct via `gt done`. Never manually kill a working polecat.
- Identity is determined by `cwd`. An agent must be in its home directory
  for `GT_ROLE` and git identity to resolve correctly.

## Service startup order

When bringing up a town from cold:

```
gt up              # starts daemon → deacon → mayor → witnesses → refineries
```

This is idempotent. Run it multiple times safely. For a specific rig only:

```
gt rig start <rig>
```

To restore crew and polecats-with-hooks after a restart:

```
gt up --restore
```

## Quick-reference: which reference file to read

| Task | Read |
|---|---|
| Install, init workspace, add rigs, configure | `references/setup-and-config.md` |
| Start/stop services, manage daemon/deacon/mayor/witness/refinery | `references/service-lifecycle.md` |
| Spawn polecats, manage crew, dogs, sessions, identity | `references/agent-management.md` |
| Create convoys, sling work, merge queue, formulas, molecules | `references/work-routing.md` |
| Health checks, audit, logs, diagnostics, dashboard | `references/monitoring-diagnostics.md` |
| Mail, nudge, broadcast, escalation | `references/communication.md` |

## Common admin workflows

**Stand up a new rig:**
Read `references/setup-and-config.md` → `gt rig add` section.

**Dispatch a batch of issues to polecats:**
Read `references/work-routing.md` → convoy + sling section.

**Something is stuck or unhealthy:**
Read `references/monitoring-diagnostics.md` → start with `gt doctor`.

**Send a message to a running agent:**
Read `references/communication.md` → nudge vs mail decision.

**Perform a clean shutdown:**
Read `references/service-lifecycle.md` → down vs shutdown distinction.

## Harness-specific invocation

Before executing any `gt` commands, read the appropriate harness file for
your execution environment:

- Claude Code → `harness/claude-code.md`
- All other runtimes → `harness/generic-shell.md`

## Common mistakes (do not repeat these)

1. **Using dogs for project work.** Dogs are Deacon infrastructure. Use crew
   or polecats for anything touching a codebase.
2. **Killing a working polecat manually.** Always use `gt polecat nuke` after
   verifying state with `gt polecat git-state`. Never send SIGKILL directly.
3. **Running gt commands from the wrong directory.** Gas Town uses `cwd` for
   role detection. Always `cd` to the correct agent home first.
4. **Conflating `gt down` with `gt shutdown`.** `gt down` is a reversible
   pause. `gt shutdown` removes polecat worktrees. Use `gt down` unless you
   intend permanent cleanup.
5. **Slinging work before services are up.** Verify `gt status` shows daemon,
   deacon, and the target rig's witness and refinery running before dispatching.
