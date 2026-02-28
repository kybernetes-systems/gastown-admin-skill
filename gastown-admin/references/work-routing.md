# Work Routing Reference

## Contents
- [Slinging work to agents](#slinging-work-to-agents)
- [Convoys — tracking batched work](#convoys--tracking-batched-work)
- [Merge queue](#merge-queue)
- [Formulas and molecules](#formulas-and-molecules)
- [Bead operations](#bead-operations)
- [Gates](#gates)
- [Orphan recovery](#orphan-recovery)

---

## Slinging work to agents

`gt sling` is the unified work dispatch command. It assigns a bead (issue)
to an agent, optionally spawning a polecat to work on it.

```
gt sling <bead-id> <rig>                  # sling to any available polecat in rig
gt sling <bead-id> <rig> --model=claude-sonnet   # specify model
gt sling mol-xxx <rig>                    # pour formula + sling molecule
gt unsling <bead-id>                      # remove work from an agent's hook
```

**Before slinging:** verify the target rig's witness and refinery are running
(`gt rig status <rig>`), and the bead is in a slингable state (`gt show <bead>`).

Polecats are spawned on demand by the Witness when work is slung. Do not
pre-spawn polecats and then try to assign work to them.

---

## Convoys — tracking batched work

A convoy tracks related issues across rigs. Create one whenever dispatching
a batch, even for a single issue.

```
gt convoy create "Feature X" gt-abc gt-def          # create tracking convoy
gt convoy create "Feature X" gt-abc --notify overseer  # with notification
gt convoy add <convoy-id> gt-ghi                    # add issues to existing convoy
gt convoy status <convoy-id>                        # show progress
gt convoy list                                      # dashboard view
gt convoy list --all                                # include completed
gt convoy close <convoy-id>                         # manually close
gt convoy check                                     # auto-close completed convoys
gt convoy stranded                                  # find stranded convoys with no workers
```

Convoy IDs use the `hq-cv-*` prefix. Convoys auto-close when all tracked
issues are complete and notify subscribers.

**Swarm vs convoy:** the swarm is ephemeral (current workers on a convoy's
issues). The convoy is the persistent tracking unit.

---

## Merge queue

Polecats submit to the merge queue via `gt done`. The Refinery processes
submissions. Admin commands for inspection and management:

```
gt mq list [rig]               # show the merge queue
gt mq status <mr>              # detailed MR status
gt mq next [rig]               # show highest-priority MR
gt mq submit                   # submit current branch (polecats use this via gt done)
gt mq reject <mr>              # reject an MR
gt mq retry <mr>               # retry a failed MR
gt ready                       # show work ready across all rigs
```

---

## Formulas and molecules

Formulas are TOML/JSON workflow templates. Molecules are instances of
formulas attached to a bead (issue).

**Search paths (in order):** `.beads/formulas/` → `~/.beads/formulas/` →
`$GT_ROOT/.beads/formulas/`

```
gt formula list                         # list all available formulas
gt formula show <n>                  # display formula steps and variables
gt formula run <n> --var=value       # execute: pour + dispatch formula
gt formula create <n>                # create new formula template

gt mol current                          # show what an agent should work on
gt mol progress                         # show execution progress
gt mol status                           # show hook status
gt mol step done                        # complete current step (auto-continues)
gt mol attach <mol-id>                  # attach molecule to hook
gt mol detach                           # detach molecule from hook
gt mol squash                           # compress to digest
gt mol burn                             # discard without record

gt synthesis                            # manage convoy synthesis steps
```

To dispatch a formula to a polecat: `gt sling mol-xxx <rig>`

---

## Bead operations

Beads are the atomic work units (issues, tasks, molecules). Most bead
operations go through the `bd` CLI, but `gt` provides convenience wrappers:

```
gt cat <bead-id>               # display bead content
gt cat <bead-id> --json        # output as JSON
gt show <bead-id>              # show bead details
gt close [bead-id]             # close bead (defaults to last-touched)
gt close <id> --reason "text"  # close with reason
gt release <bead-id>           # release stuck in_progress bead back to pending
gt trail                       # show recent agent activity

gt bead move <id> <repo>       # move a bead to a different repository
```

`gt release` is the recovery command for beads stuck in `in_progress` state
(e.g., after a polecat crash without cleanup).

---

## Gates

Gates are async coordination primitives. Most gate commands live in `bd`:

```
bd gate create <type>          # create a gate (timer, gh:run, human, mail)
bd gate show <id>              # show gate details
bd gate list                   # list open gates
bd gate close <id>             # close a gate
bd gate approve <id>           # approve a human gate
bd gate eval                   # evaluate and close elapsed gates

gt gate wake <gate-id>         # send wake mail to gate waiters after close
```

---

## Orphan recovery

```
gt orphans [rig]               # find orphaned polecat commits never merged to main
```

Orphans occur when a session is killed before merge, the Refinery fails,
or network issues interrupt a push. Review output and decide whether to
re-queue or discard.
