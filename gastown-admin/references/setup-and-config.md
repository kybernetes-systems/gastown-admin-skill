# Setup and Configuration Reference

## Contents
- [Install a new HQ](#install-a-new-hq)
- [Initialize rigs](#initialize-rigs)
- [Add rigs to a running town](#add-rigs-to-a-running-town)
- [Shell integration](#shell-integration)
- [Git initialization](#git-initialization)
- [Configuration management](#configuration-management)
- [Account management](#account-management)
- [Polecat name pools](#polecat-name-pools)
- [Plugins](#plugins)
- [Uninstall](#uninstall)

---

## Install a new HQ

Creates the town root directory with CLAUDE.md, mayor/, and .beads/:

```
gt install ~/gt
gt install ~/gt --name my-workspace
gt install ~/gt --git                        # also init git + .gitignore
gt install ~/gt --github=owner/repo          # create private GitHub repo
gt install ~/gt --github=owner/repo --public # create public GitHub repo
gt install ~/gt --shell                      # install shell integration
gt install ~/gt --wrappers                   # install gt-codex/gt-opencode wrappers to ~/bin/
gt install . --force                         # overwrite existing HQ
```

Key flags: `--name`, `--owner` (email for entity identity), `--no-beads`,
`--public-name`.

After install, `gt doctor` will enumerate any remaining fixable issues.

---

## Initialize rigs

A rig is an existing git repository registered with the town. Initialize one:

```
cd /path/to/repo
gt init                  # creates polecats/, witness/, refinery/, mayor/ dirs
gt init --force          # reinitialize existing structure
```

Then register it with the town:

```
gt rig add <rig-name> /path/to/repo
```

---

## Add rigs to a running town

```
gt rig add <name>               # add and register a rig
gt rig list                     # show all registered rigs
gt rig status <name>            # detailed status for one rig
gt rig start <name>             # start witness + refinery for this rig
gt rig stop <name>              # stop rig agents (reversible)
gt rig restart <name>           # stop then start
gt rig reboot <name>            # restart witness and refinery
gt rig remove <name>            # remove from registry (does not delete files)
gt rig reset <name>             # reset rig state (handoff content, mail, stale issues)
gt rig dock <name>              # globally/persistently disable a rig
gt rig undock <name>            # re-enable a docked rig
gt rig park <name>              # stop agents, daemon won't auto-restart
gt rig unpark <name>            # allow daemon to auto-restart rig agents
gt rig config <name>            # view/manage rig configuration
gt rig boot <name>              # start witness and refinery (alias for rig start)
gt rig shutdown <name>          # gracefully stop all rig agents
```

---

## Shell integration

```
gt shell                         # manage shell integration
gt install ~/gt --shell          # installs GT_TOWN_ROOT and GT_RIG env var helpers
```

Shell integration sets `GT_TOWN_ROOT` and `GT_RIG` automatically based on cwd.
Agents relying on role detection from cwd require this to be configured.

---

## Git initialization

```
gt git-init                              # create .gitignore for Gas Town
gt git-init --github=owner/repo          # also create private GitHub repo
gt git-init --github=owner/repo --public # public repo
```

The generated `.gitignore` excludes polecat worktrees, rig clones, and runtime
state files, while tracking CLAUDE.md, .beads/ config, and rig configs.

---

## Configuration management

```
gt config                        # show current configuration
gt config get <key>              # get a specific config value
gt config set <key> <value>      # set a config value
gt hooks                         # list all Claude Code hooks in the workspace
gt theme                         # view current tmux theme
gt theme <name>                  # set tmux theme for current rig
```

Configuration follows a property-layers hierarchy: town-level → rig-level →
agent-level. More specific layers override less specific ones.

---

## Account management

```
gt account                       # manage Claude Code accounts
gt account list                  # list configured accounts
gt account set <account>         # set default account
```

Used when different agents should run under different Claude Code accounts
(e.g., different API keys per rig or per role).

---

## Polecat name pools

Polecats receive themed names from a pool. Default theme: Mad Max universe.

```
gt namepool                      # show current pool status
gt namepool --list               # list available themes
gt namepool themes               # show theme names and members
gt namepool set <theme>          # set theme (e.g., minerals, planets)
gt namepool add <name>           # add a custom name to the pool
gt namepool reset                # reset pool state (release all names)
```

---

## Plugins

```
gt plugin                        # plugin management
gt plugin list                   # list installed plugins
gt plugin install <path>         # install a plugin
gt plugin remove <name>          # remove a plugin
```

---

## Uninstall

```
gt uninstall                     # remove Gas Town from the system
```

Prompts for confirmation. Does not delete managed repositories, only Gas Town
infrastructure directories and configuration.
