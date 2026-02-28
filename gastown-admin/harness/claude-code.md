# Claude Code Harness

Optimizations and patterns for executing `gt` commands from within a
Claude Code agent session.

## Tool invocation

Use the `Bash` tool for all `gt` and `bd` commands:

```
Bash("gt status")
Bash("gt up --quiet")
Bash("gt convoy list --json | jq '.[] | select(.status==\"active\")'")
```

For commands that produce structured output, prefer `--json` and pipe
through `jq` rather than parsing human-formatted text.

## Reading reference files

Use the `Read` tool with the skill's base directory:

```
Read("{baseDir}/references/service-lifecycle.md")
Read("{baseDir}/references/work-routing.md")
```

## Checking service state before acting

Before dispatching work, verify services in a single compound command:

```
Bash("gt status --json 2>/dev/null | jq '{daemon: .daemon.running, deacon: .deacon.running}'")
```

## Attaching to sessions

Do not use `gt session at` or `gt agents` (those open interactive tmux
sessions). For inspection, use:

```
Bash("gt session capture <name>")
Bash("gt peek <agent>")
```

## Sending messages

For nudge from within Claude Code, use Bash directly:

```
Bash("gt nudge mayor 'Convoy hq-abc complete'")
Bash("gt broadcast 'System maintenance in 5 minutes' --all")
```

## Long-running commands

For commands that may take time (e.g., `gt shutdown --graceful`), use a
timeout wrapper:

```
Bash("timeout 60 gt shutdown --graceful --yes")
```

## Parsing convoy status

```
Bash("gt convoy list --json | jq '.[] | {id: .id, title: .title, status: .status, progress: .progress}'")
```

## Checking for stale polecats

```
Bash("gt polecat stale --json 2>/dev/null")
```
