# Agent Management Reference

## Contents
- [Polecat management](#polecat-management)
- [Crew management](#crew-management)
- [Dogs](#dogs)
- [Sessions](#sessions)
- [Identity and role detection](#identity-and-role-detection)
- [Agents overview and session switching](#agents-overview-and-session-switching)
- [Callbacks](#callbacks)

---

## Polecat management

Polecats are ephemeral workers: spawned for one task, self-destruct via
`gt done` when complete. There is no idle state. States: Working, Stalled
(crashed), Zombie (finished but `gt done` failed).

Polecats are spawned by slinging work to them — see `references/work-routing.md`.
The Witness handles failure recovery automatically. Admin commands are for
inspection and manual cleanup only.

```
gt polecat list [rig]              # list polecats in a rig
gt polecat status <n> [rig]     # detailed status for one polecat
gt polecat stale [rig]             # detect stale polecats needing cleanup
gt polecat git-state <n>        # show git state (verify before nuke)
gt polecat check-recovery <n>   # check if needs recovery vs safe to nuke
gt polecat nuke <n>             # destroy polecat: session, worktree, branch, bead
gt polecat remove <n>           # remove polecat from rig
gt polecat gc [rig]                # garbage-collect stale polecat branches
gt polecat sync <n>             # sync beads for a polecat
gt polecat identity                # manage polecat identity pool
```

**Before nuking:** always run `gt polecat git-state <n>` and
`gt polecat check-recovery <n>` first. A polecat with uncommitted work should
be recovered, not nuked.

---

## Crew management

Crew workers are persistent full git clones for humans or long-running agents.
User-managed; not automatically cleaned up.

```
gt crew add <n>               # create workspace without starting session
gt crew start <n>             # start session (creates workspace if needed)
gt crew start --all           # start all crew sessions in current rig
gt crew stop <n>              # stop session
gt crew list                     # list workspaces with status
gt crew status <n>            # detailed workspace status
gt crew at <n>                # attach to session (tmux)
gt crew restart <n>           # kill and restart session fresh
gt crew refresh <n>           # context cycling with handoff mail
gt crew remove <n>            # remove workspace
gt crew rename <old> <new>    # rename a workspace
gt crew pristine              # sync crew workspaces with remote
```

Crew workers have recognizable names (dave, emma, fred) rather than ephemeral
pool names. They support mail, nudge, and handoff.

---

## Dogs

Dogs are Deacon-managed infrastructure workers, NOT project workers.
Use polecats or crew for codebase work.

```
gt dog list                  # list all dogs in the kennel
gt dog status <n>         # show detailed dog status
gt dog add <n>            # create a new dog in the kennel
gt dog remove <n>         # remove dogs from the kennel
gt dog call [<n>]         # wake idle dog(s) for work
gt dog dispatch <n>       # dispatch plugin execution to a dog
```

Dogs live at `~/gt/deacon/dogs/`. Each dog has worktrees into every configured
rig, enabling cross-rig infrastructure operations. Dogs return to idle after
completing work (unlike polecats).

---

## Sessions

Sessions are tmux sessions running Claude for each agent. Use `gt nudge`
to send messages to running sessions, not `gt session inject`.

```
gt session list              # list all sessions
gt session status <n>     # show session status details
gt session at <n>         # attach to a running session
gt session start <n>      # start a polecat session
gt session stop <n>       # stop a polecat session
gt session restart <n>    # restart a polecat session
gt session capture <n>    # capture recent session output
gt session check          # check session health for polecats
gt session inject <n> <msg>  # send message (prefer gt nudge instead)
```

---

## Identity and role detection

Gas Town derives an agent's identity from:
1. `GT_ROLE` environment variable (authoritative if set)
2. Current working directory (fallback)

If both are set and disagree, a warning is shown. An agent operating from
the wrong directory will have incorrect identity and broken git attribution.

```
gt role                      # show current role and detection source
gt role show                 # same
gt role detect               # force cwd-based role detection (debugging)
gt role env                  # print export statements for current role
gt role home                 # show home directory for a role
gt role list                 # list all known roles
gt role def                  # display role definition (session, health, env config)
gt whoami                    # show current identity for mail commands
```

Identity format in git commits and beads:
```
gastown/crew/joe → Author: gastown/crew/joe <joe@gastown.local>
```

The email domain is configurable in town settings (`agent_email_domain`).

---

## Agents overview and session switching

```
gt agents                    # display popup menu of core agent sessions (tmux)
gt agents list               # list agent sessions without popup
gt agents -a                 # include polecats in the menu
gt agents check              # check for identity collisions and stale locks
gt agents fix                # fix identity collisions and clean up stale locks
gt agents state <bead>       # get or set operational state on agent beads
```

---

## Callbacks

Callbacks are messages to the Mayor from Witnesses, Refineries, Polecats,
and external triggers. As an admin, you generally do not invoke these
directly; the Mayor processes them automatically. Exposed for debugging:

```
gt callbacks process         # process pending callbacks from Mayor's inbox
```
