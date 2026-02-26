# Service Lifecycle Reference

## Contents
- [Startup and shutdown overview](#startup-and-shutdown-overview)
- [gt up — idempotent boot](#gt-up--idempotent-boot)
- [gt start — targeted start](#gt-start--targeted-start)
- [gt down — reversible pause](#gt-down--reversible-pause)
- [gt shutdown — permanent cleanup](#gt-shutdown--permanent-cleanup)
- [Daemon](#daemon)
- [Deacon](#deacon)
- [Mayor](#mayor)
- [Witness](#witness)
- [Refinery](#refinery)
- [Boot (Deacon watchdog)](#boot-deacon-watchdog)

---

## Startup and shutdown overview

| Command | Effect | Reversible? |
|---|---|---|
| `gt up` | Start all infrastructure agents | Yes — `gt down` |
| `gt start` | Start Deacon + Mayor only | Yes |
| `gt down` | Stop all infrastructure (pause) | Yes — `gt up` |
| `gt shutdown` | Stop everything + remove polecat worktrees | No (worktrees gone) |

**Cold start sequence (automatic via `gt up`):**
daemon → deacon → mayor → witnesses (per-rig) → refineries (per-rig)

Do not start individual services out of order. Use `gt up` unless targeting
a specific component for restart.

---

## `gt up` — idempotent boot

```
gt up                  # start all infrastructure agents
gt up --restore        # also restore crew (from settings) and polecats with hooks
gt up --quiet          # only show errors
```

Safe to run repeatedly. Only starts services that are not already running.
Polecats are NOT started by `gt up`; they are spawned on demand.

---

## `gt start` — targeted start

```
gt start               # start Deacon + Mayor only
gt start --all         # also start witnesses and refineries for all rigs
gt start crew <rig/n>  # start a specific crew workspace
```

Use `gt start` when you need Deacon and Mayor without bringing up per-rig
agents. Per-rig agents (witness, refinery) start lazily as needed by default.

---

## `gt down` — reversible pause

```
gt down                   # stop infrastructure agents only
gt down --polecats        # also stop all polecat sessions
gt down --all             # also stop bd daemons and verify shutdown
gt down --nuke            # kill entire tmux server (DESTRUCTIVE — kills non-GT sessions)
gt down --force           # force kill without graceful shutdown
gt down --dry-run         # preview without action
```

Infrastructure agents stopped by default: daemon, deacon, mayor, boot,
witnesses (all rigs), refineries (all rigs).

Polecats are NOT stopped by default. Use `--polecats` to include them.
`--nuke` kills the tmux server entirely; use only if non-GT sessions are
acceptable collateral.

---

## `gt shutdown` — permanent cleanup

```
gt shutdown               # stop everything + remove polecat worktrees/branches
gt shutdown --all         # also stop crew sessions
gt shutdown --polecats-only  # only stop polecats (leave infrastructure)
gt shutdown --graceful    # send ESC to agents, wait for handoff before killing
gt shutdown --force       # skip confirmation prompt
gt shutdown --nuclear     # force cleanup even with uncommitted polecat work (DANGEROUS)
gt shutdown --cleanup-orphans  # also kill orphaned Claude processes
```

**Use `gt down` for a reversible pause. Use `gt shutdown` only when done for
the day or performing a full reset.**

Polecats with uncommitted work are protected (skipped) by default.
`--nuclear` overrides this protection — data loss possible.

---

## Daemon

The daemon is a dumb Go process. All intelligence lives in agents.
Responsibilities: periodic heartbeats to agents, processing lifecycle
requests (cycle, restart, shutdown), restarting sessions when requested.

```
gt daemon start          # start the daemon
gt daemon stop           # stop the daemon
gt daemon status         # show daemon status
gt daemon logs           # view daemon logs
```

---

## Deacon

The Deacon ("daemon beacon") is the town-level health watchdog. It receives
heartbeats from the daemon and monitors all Witnesses and the Mayor.

```
gt deacon start          # start the Deacon session
gt deacon stop           # stop the Deacon session
gt deacon restart        # restart the Deacon session
gt deacon status         # check Deacon session status
gt deacon attach         # attach to the Deacon session (tmux)
gt deacon pause          # pause patrol actions
gt deacon resume         # resume patrol actions
gt deacon heartbeat      # update the Deacon heartbeat
gt deacon health-check <agent>    # send health check ping to an agent
gt deacon health-state            # show health state for all monitored agents
gt deacon stale-hooks             # find and unhook stale hooked beads
gt deacon zombie-scan             # find and clean zombie Claude processes
gt deacon cleanup-orphans         # clean up orphaned Claude subagent processes
gt deacon force-kill <session>    # force-kill an unresponsive agent session
gt deacon trigger-pending         # trigger pending polecat spawns (bootstrap mode)
```

The Deacon manages Dogs for cross-rig infrastructure tasks. Do not confuse
Deacon pause/resume with `gt down`; pausing the Deacon only suppresses its
patrol actions, it does not stop other services.

---

## Mayor

The Mayor is the global coordinator and the primary human-facing interface.
All escalations from Witnesses and Deacon route to the Mayor.

```
gt mayor start           # start the Mayor session
gt mayor stop            # stop the Mayor session
gt mayor restart         # restart the Mayor session
gt mayor status          # check Mayor session status
gt mayor attach          # attach to the Mayor session (tmux)
```

The Mayor runs from `~/gt/mayor/`. Address it as `"mayor"` in mail and nudge.

---

## Witness

One Witness per rig. Monitors polecats: detects stalls, nudges unresponsive
sessions, cleans up zombies, nukes sandboxes after completion.

```
gt witness start [rig]   # start the Witness for a rig
gt witness stop [rig]    # stop the Witness
gt witness restart [rig] # restart the Witness
gt witness status [rig]  # check Witness status
gt witness attach [rig]  # attach to Witness session (tmux)
```

Address as `"witness"` in mail/nudge (resolves to current rig's Witness).
The Witness does NOT force session cycles on working polecats; it handles
failures only. For per-rig start/stop, `gt rig start/stop` is the higher-level
interface.

---

## Refinery

One Refinery per rig. Serializes merges to main: receives MRs from polecats
via `gt done`, rebases onto latest main, runs validation, merges.
On conflict: spawns a fresh polecat to re-implement (original already gone).

```
gt refinery start [rig]       # start the Refinery
gt refinery stop [rig]        # stop the Refinery
gt refinery restart [rig]     # restart the Refinery
gt refinery status [rig]      # show Refinery status
gt refinery attach [rig]      # attach to Refinery session (tmux)
gt refinery queue [rig]       # show merge queue
gt refinery ready [rig]       # list MRs ready for processing
gt refinery unclaimed [rig]   # list unclaimed MRs
gt refinery blocked [rig]     # list MRs blocked by open tasks
gt refinery claim <mr>        # claim an MR for processing
gt refinery release <mr>      # release a claimed MR back to the queue
```

Address as `"refinery"` in mail/nudge.

---

## Boot (Deacon watchdog)

Boot is a special Dog that runs fresh on each daemon tick. It triages
Deacon health: observe → decide → act → exit.

```
gt boot spawn            # spawn Boot for triage
gt boot status           # show Boot status
gt boot triage           # run triage directly (degraded mode)
```

Boot lives at `~/gt/deacon/dogs/boot/`. Do not treat it as a persistent agent.
