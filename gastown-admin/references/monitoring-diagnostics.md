# Monitoring and Diagnostics Reference

## Contents
- [Primary health check: gt doctor](#primary-health-check-gt-doctor)
- [Status overview](#status-overview)
- [Logs and activity feeds](#logs-and-activity-feeds)
- [Audit and provenance](#audit-and-provenance)
- [Dashboard](#dashboard)
- [Patrol](#patrol)
- [Session checkpoints](#session-checkpoints)
- [Binary and version checks](#binary-and-version-checks)

---

## Primary health check: `gt doctor`

Run first when diagnosing any problem:

```
gt doctor                        # run all checks on the workspace
gt doctor --rig <n>           # check a specific rig
gt doctor --fix                  # attempt automatic fixes for fixable issues
```

Checks performed include: town config validity, rig registry, mayor
directory structure, git protection, daemon status, database fingerprint,
orphan sessions and processes, clone divergence, crew state, session hooks,
and patrol wiring.

Fixable checks are noted in output. Most common issues (`gt doctor --fix`
handles): stale binary, daemon not running, orphan sessions, route mismatches,
crew state corruption.

---

## Status overview

```
gt status                        # overall town status (services + rigs)
gt rig status <n>             # detailed status for one rig
gt polecat status <n>         # status for one polecat
gt witness status [rig]          # Witness status
gt refinery status [rig]         # Refinery status
gt deacon status                 # Deacon status
gt mayor status                  # Mayor status
gt daemon status                 # daemon process status
gt agents list                   # all agent sessions
```

---

## Logs and activity feeds

```
gt feed                          # real-time activity feed (beads events + gt events)
gt log                           # view town activity log
gt daemon logs                   # daemon process logs
gt session capture <n>        # capture recent output from a session
gt peek <agent>                  # view recent output from polecat or crew session
gt trail                         # show recent agent activity (last touched beads)
```

`gt feed` is the primary real-time monitoring surface. `gt log` is the
persistent historical record.

---

## Audit and provenance

Every action is attributed. Query the full provenance record:

```
gt audit --actor=<rig>/crew/<n>        # all work by a specific actor
gt audit --actor=<rig>/polecats/<n>    # polecat work history
gt audit --actor=mayor                    # mayor activity
gt audit --since=24h                      # all activity in last 24h
gt audit --actor=<n> --since=1h        # combined filters
gt audit --json                           # output as JSON
gt audit -n 100                           # increase result limit (default 50)
```

Actor format: `<rig>/<role>/<name>` (e.g., `gastown/crew/joe`,
`gastown/polecats/toast`).

---

## Dashboard

Web-based convoy tracking dashboard:

```
gt dashboard                     # start on default port 8080
gt dashboard --port 3000         # specify port
gt dashboard --open              # start and open browser
```

Shows real-time convoy status with progress tracking and last-activity
indicators. Auto-refreshes every 30 seconds.

---

## Patrol

Patrol is the Deacon's recurring health-check cycle, triggered by the daemon.

```
gt patrol                        # patrol digest management
```

Patrol molecules exist for each role. `gt doctor` checks that patrol
molecules exist, hooks are wired, and no patrol is stuck (stale wisps > 1h).

---

## Session checkpoints

Polecats write checkpoints to `.polecat-checkpoint.json` for crash recovery.

```
gt checkpoint read               # read and display current checkpoint
gt checkpoint write              # write a checkpoint of current session state
gt checkpoint clear              # clear the checkpoint file
```

As admin, use `gt checkpoint read` to inspect a polecat's last known state
when diagnosing a crash.

---

## Binary and version checks

```
gt version                       # print version information
gt info                          # show Gas Town information and what's new
gt stale                         # check if gt binary is stale vs repo
```

`gt doctor` also checks binary staleness (`stale-binary` check). Run
`gt stale` to check independently without the full doctor suite.
