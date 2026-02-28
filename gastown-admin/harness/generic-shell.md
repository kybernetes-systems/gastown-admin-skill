# Generic Shell Harness

Patterns for executing `gt` commands from any shell-capable agent runtime
that is not Claude Code.

## Basic invocation

Execute `gt` and `bd` as standard subprocess calls via whatever shell
execution mechanism your runtime provides. All `gt` commands are synchronous
unless they spawn background agents (e.g., `gt start`, `gt up`).

Example in pseudocode:
```
result = shell.run("gt status")
stdout = result.stdout
returncode = result.returncode
```

A non-zero return code indicates failure. Check stderr for error messages.

## Structured output

Most `gt` commands accept `--json` for machine-readable output. Prefer
this over parsing human-formatted text:

```
gt status --json
gt convoy list --json
gt polecat stale --json
gt audit --json
gt cat <bead-id> --json
```

Pipe through `jq` or parse the JSON directly in your runtime.

## Checking prerequisites

Before dispatching work, verify the environment:

```sh
# Check gt is available
which gt || { echo "gt not in PATH"; exit 1; }

# Check critical services
gt status --json
```

## Working directory

Gas Town uses `cwd` for role detection. When running commands that need
a specific rig context, `cd` to the appropriate directory first:

```sh
cd ~/gt/<rig>/crew/<name>
gt status
```

For admin-level commands (not role-specific), running from `~/gt/` is safe.

## Sending messages to agents

Nudge requires tmux to be running (it delivers into Claude sessions):

```sh
gt nudge mayor "message text"
gt nudge gastown/Toast "message"
```

If tmux is not available or the target session is not running, nudge will
fail. Use mail as fallback:

```sh
gt mail send mayor/ "subject" "body"
```

## Long-running operations

Wrap in a timeout appropriate to your runtime. Suggested values:

- `gt up` / `gt down`: 30s
- `gt shutdown --graceful`: 90s
- `gt doctor --fix`: 60s

## Error handling pattern

```sh
output=$(gt convoy list --json 2>&1)
rc=$?
if [ $rc -ne 0 ]; then
  echo "gt convoy list failed (rc=$rc): $output"
  exit 1
fi
```

## Reading reference files

Reference files in this skill are plain Markdown. Read them directly from
the filesystem at their relative paths (e.g.,
`references/service-lifecycle.md` relative to the skill root).
