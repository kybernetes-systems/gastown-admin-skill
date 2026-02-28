# Communication Reference

## Contents
- [Nudge vs mail — when to use which](#nudge-vs-mail--when-to-use-which)
- [gt nudge — synchronous messaging](#gt-nudge--synchronous-messaging)
- [gt mail — async messaging](#gt-mail--async-messaging)
- [gt broadcast — message all workers](#gt-broadcast--message-all-workers)
- [gt escalate — severity-routed alerts](#gt-escalate--severity-routed-alerts)
- [gt notify and gt dnd — notification control](#gt-notify-and-gt-dnd--notification-control)
- [gt peek — observe session output](#gt-peek--observe-session-output)

---

## Nudge vs mail — when to use which

| Use nudge when... | Use mail when... |
|---|---|
| You need immediate attention from a running agent | You can tolerate async delivery |
| The recipient must act now | The message is informational or queued |
| Real-time coordination | Handoff context, escalation routing |

Nudge delivers directly into a Claude session via tmux. Mail is stored in
beads and read by the agent on its next inbox check.

**Do not use raw tmux send-keys.** Only `gt nudge` uses the reliable delivery
pattern (literal mode + 500ms wait + Enter). Direct tmux usage will corrupt
Claude sessions.

---

## `gt nudge` — synchronous messaging

```
gt nudge <target> "<message>"              # send to any agent
gt nudge mayor "Check convoy hq-abc"
gt nudge witness "Polecat Toast is stuck"
gt nudge refinery "Priority MR incoming"
gt nudge gastown/Toast "Resume your work"
gt nudge channel:<n> "<message>"        # nudge all channel members
```

**Role shortcuts** (resolve automatically):
- `mayor` → `gt-mayor`
- `deacon` → `gt-deacon`
- `witness` → `gt-<current-rig>-witness`
- `refinery` → `gt-<current-rig>-refinery`

**Full address format:** `<rig>/<role>/<n>` or `<rig>/<polecat-name>`

---

## `gt mail` — async messaging

```
gt mail send <address> "<subject>" "<body>"   # send a message
gt mail inbox                                  # view inbox
gt mail read <id>                              # read a message
gt mail reply <id> "<body>"                    # reply to a message
gt mail thread <id>                            # view thread
gt mail search "<query>"                       # search messages
gt mail mark-read <id>                         # mark as read
gt mail mark-unread <id>                       # mark as unread
gt mail archive <id>                           # archive
gt mail delete <id>                            # delete
gt mail clear                                  # clear all from inbox
gt mail peek                                   # preview first unread message
gt mail check                                  # check for new mail (for hooks)

gt mail queue                                  # manage mail queues
gt mail claim <queue>                          # claim a message from a queue
gt mail release <id>                           # release a claimed queue message

gt mail channel                                # manage beads-native channels
gt mail announces                              # list or read announce channels
gt mail group                                  # manage mail groups
```

**Address formats:**
```
mayor/                       → Mayor inbox
<rig>/witness                → Rig's Witness
<rig>/refinery               → Rig's Refinery
<rig>/<polecat-name>         → e.g., gastown/Toast
<rig>/crew/<n>            → e.g., gastown/crew/max
--human                      → human overseer
```

---

## `gt broadcast` — message all workers

```
gt broadcast "<message>"                      # send to all polecats + crew
gt broadcast "<message>" --rig <n>         # limit to one rig
gt broadcast "<message>" --all                # include infrastructure agents
gt broadcast "<message>" --dry-run            # preview without sending
```

Use for system-wide announcements (maintenance windows, priority changes).
Does not include infrastructure agents (mayor, deacon, witnesses, refineries)
unless `--all` is specified.

---

## `gt escalate` — severity-routed alerts

```
gt escalate "<description>"                               # medium severity
gt escalate "<description>" --severity critical           # P0
gt escalate "<description>" --severity high               # P1
gt escalate "<description>" --reason "<details>"          # with context
gt escalate "<description>" --related <bead-id>           # link to bead

gt escalate list                                          # open escalations
gt escalate show <id>                                     # details
gt escalate ack <id>                                      # acknowledge
gt escalate close <id> --reason "<resolution>"            # close
gt escalate stale                                         # re-escalate stale ones
```

**Severity levels:** `critical` (P0), `high` (P1), `medium` (P2, default), `low` (P3)

Routing configured in `~/gt/settings/escalation.json`. Stale unacknowledged
escalations are automatically re-escalated after the configured threshold (default 4h).

---

## `gt notify` and `gt dnd` — notification control

```
gt notify                    # show current level
gt notify verbose            # all notifications
gt notify normal             # default
gt notify muted              # DND

gt dnd                       # toggle DND
gt dnd on                    # enable DND
gt dnd off                   # disable DND
gt dnd status                # current state
```

---

## `gt peek` — observe session output

```
gt peek <agent>              # view recent output from polecat or crew session
```

Read-only. Does not interact with the session. Useful for checking what an
agent is currently doing without attaching to its tmux session.
