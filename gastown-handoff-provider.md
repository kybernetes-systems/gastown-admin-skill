# Claude Code Handoff: terraform-provider-gastown

## Skills to Load Before Starting

Read these skill files before writing any code. Consult the relevant skill at
the start of each phase — do not rely on memory for framework API details.

```
/mnt/skills/user/new-terraform-provider/SKILL.md    ← Phase 0 bootstrap
/mnt/skills/user/provider-resources/SKILL.md        ← Phases 3–5 CRUD patterns
/mnt/skills/user/terraform-test/SKILL.md            ← All test phases
/mnt/skills/user/terraform-style-guide/SKILL.md     ← All HCL files
```

---

## Purpose

A Terraform provider that manages Gas Town workspaces as declarative
infrastructure. The operator describes the desired state of a Gas Town
installation — its HQ, rigs, and crew workspaces — in HCL; the provider calls
the `gt` and `bd` CLIs to reconcile live state.

This is Phase 1 (Model B): thin wrappers over real `gt`/`bd` commands.
A governance layer (Model A: policy/role resources backed by `bd`) is planned
for a later phase and is explicitly out of scope here.

---

## Prerequisites — Verify Before Writing Any Code

```bash
gt version            # must be >= 0.5.0
bd version            # must be >= 0.44.0
git version           # must be >= 2.25
go version            # must be >= 1.23
git config user.name  # must be non-empty — required for commits in tests
git config user.email # must be non-empty — required for commits in tests
```

If any check fails, stop and resolve it. Do not proceed.

If `git config user.name` or `user.email` is empty, set them:

```bash
git config --global user.name "Kybernetes Systems"
git config --global user.email "operator@kybernetes.systems"
```

Tests that invoke `gt` or `bd` (which internally commit to Git) will fail
silently or produce confusing errors without a valid Git identity.

---

## Decisions Already Made — Do Not Revisit

| Decision | Value |
|---|---|
| Module path | `github.com/kybernetes-systems/terraform-provider-gastown` |
| License | Apache 2.0 |
| SDK | Terraform Plugin Framework (not SDKv2) |
| `gt`/`bd` integration | Shell out via `os/exec` — do NOT parse internal files directly |
| Delete behavior on `gastown_rig` | `gt rig stop` + `gt rig dock` — operational shutdown, not file removal |
| Git | Managed by `gt`/`bd` — provider never calls `git` directly |
| Commit convention | `feat:` `test:` `fix:` `docs:` `chore:` — one logical change per commit |
| Test command | `go test ./...` |
| Test isolation | Every test gets its own HQ in `t.TempDir()` |
| Gas Town in CI | Live `gt` and `bd` binaries — no mocking |

---

## Gas Town Concepts

### Workspace Hierarchy

```
~/gt/                          ← HQ (gt install ~/gt --git)
├── CLAUDE.md
├── AGENTS.md
├── mayor/
│   ├── town.json
│   ├── rigs.json
│   └── overseer.json
└── .beads/                    ← Town-level beads DB

~/gt/<rig-name>/               ← Rig (gt rig add <n> <repo>)
├── config.json
├── .repo.git/
├── .beads/
├── plugins/
├── mayor/rig/
├── crew/
└── polecats/

~/gt/<rig-name>/crew/<n>/      ← Crew workspace (gt crew add <n> --rig <rig>)
```

### Runtime Config Schema (`config.json`)

```json
{
  "runtime": {
    "provider": "claude",
    "command": "claude",
    "args": [],
    "prompt_mode": "none",
    "env": {}
  }
}
```

Valid built-in `provider` values: `claude`, `gemini`, `codex`, `cursor`,
`auggie`, `amp`.

### Rig Operational States

| State | Command | Scope |
|---|---|---|
| `operational` | default | — |
| `parked` | `gt rig park <rig>` | local only, ephemeral |
| `docked` | `gt rig dock <rig>` | all clones via git, permanent until undocked |

**Delete on `gastown_rig` = `gt rig stop` + `gt rig dock`.**
This is operational shutdown. Files are retained. The rig remains registered.

### What the Provider Does NOT Manage (Phase 1)

- Individual beads or issues — operational work, not infrastructure
- Convoys and polecats — ephemeral
- Formulas — future resource, out of scope
- Policy/role governance layer — Model A, planned for Phase 2

---

## Resource Model

```hcl
# 1. The HQ — one per workspace
resource "gastown_hq" "main" {
  path        = "/home/user/gt"
  owner_email = "phil@kybernetes.systems"
  git         = true
}

# 2. A Rig — one per project
resource "gastown_rig" "mirror" {
  hq_path      = gastown_hq.main.path
  name         = "mirror"
  repo         = "https://github.com/kybernetes-systems/rig-mirror.git"
  runtime      = "claude"
  max_polecats = 4
}

# 3. A Crew workspace
resource "gastown_crew" "deacon" {
  hq_path  = gastown_hq.main.path
  rig_name = gastown_rig.mirror.name
  name     = "deacon"
}
```

### CRUD Mapping

#### `gastown_hq`

| Operation | Command |
|---|---|
| Create | `gt install <path> --git --owner <email>` |
| Read | Parse `mayor/town.json`; confirm existence |
| Update | `path` and `git` are ForceNew — no in-place update |
| Delete | `gt uninstall --force` |

#### `gastown_rig`

| Operation | Command |
|---|---|
| Create | `gt rig add <n> <repo>` then `gt rig config set <n> runtime <val>` |
| Read | `gt rig status <n> --json` + `gt rig config show <n>` |
| Update | `gt rig config set <n> <key> <val>` for mutable fields |
| Delete | `gt rig stop <n>` + `gt rig dock <n>` |

`name` and `repo` are ForceNew. `runtime` and `max_polecats` are mutable.

#### `gastown_crew`

| Operation | Command |
|---|---|
| Create | `gt crew add <n> --rig <rig>` |
| Read | `gt crew list --rig <rig> --json` |
| Update | All fields are ForceNew |
| Delete | `gt crew remove <n> --rig <rig>` |

---

## TDD Workflow Protocol

Follow this cycle exactly, for every change:

1. Write a failing test
2. Run `go test ./...` — confirm it fails for the right reason
3. Write minimum code to make it pass
4. Run `go test ./...` — confirm green
5. Commit atomically with a scoped message
6. Refactor if needed, re-run, commit again

**Never commit red tests. Never skip the failing step.**

---

## Repository Layout

```
terraform-provider-gastown/
├── main.go
├── go.mod
├── go.sum
├── LICENSE
├── README.md
├── internal/
│   ├── provider/
│   │   ├── provider.go
│   │   └── provider_test.go
│   ├── exec/
│   │   ├── runner.go          # os/exec wrapper for gt and bd
│   │   └── runner_test.go
│   └── gastown/
│       ├── hq/
│       │   ├── resource.go
│       │   └── resource_test.go
│       ├── rig/
│       │   ├── resource.go
│       │   └── resource_test.go
│       └── crew/
│           ├── resource.go
│           └── resource_test.go
└── testdata/
    ├── hq_basic.tf
    ├── rig_basic.tf
    └── full_stack.tf
```

---

## Phase 0: Repository Bootstrap

Read `/mnt/skills/user/new-terraform-provider/SKILL.md` first.

```bash
mkdir terraform-provider-gastown && cd terraform-provider-gastown
git init
git config user.name "$(git config --global user.name)"
git config user.email "$(git config --global user.email)"
go mod init github.com/kybernetes-systems/terraform-provider-gastown
go get github.com/hashicorp/terraform-plugin-framework@latest
go mod tidy
go build -o /dev/null
```

Write `LICENSE` (Apache 2.0 full text) and `README.md` (see bottom of doc).

Commit: `chore: initialize go module and bootstrap repository`

**Exit criterion:** `go build -o /dev/null` succeeds with no errors.

---

## Phase 1: exec.Runner

Read `/mnt/skills/user/provider-resources/SKILL.md` before starting.

Build a testable wrapper around `os/exec` before any resource code. All
subsequent resource code calls this — never calls `os/exec` directly.

### Interface

```go
// internal/exec/runner.go
type Runner interface {
    GT(ctx context.Context, args ...string) (string, error)
    BD(ctx context.Context, args ...string) (string, error)
}
```

### Implementation Rules

- `GT` runs `gt <args>`; `BD` runs `bd <args>`
- Both capture stdout+stderr; on non-zero exit, return error containing full stderr
- Never use `/bin/sh` — explicit argument lists only
- Never call `git` directly — that is `gt`/`bd`'s responsibility

### TDD Sequence

**Test 1** — `GT` executes `gt version` and returns non-empty output:
```go
func TestRunner_GT_version(t *testing.T) { ... }
```
Red → implement → green → commit: `feat: implement exec runner`

**Test 2** — Non-zero exit returns error containing stderr:
```go
func TestRunner_GT_nonzeroExit_returnsStderr(t *testing.T) { ... }
```
Red → implement → green → commit: `test: runner surfaces stderr on failure`

**Exit criterion:** All runner tests pass.

---

## Phase 2: Provider Contract

Read `/mnt/skills/user/terraform-style-guide/SKILL.md` for HCL conventions.

### Provider Schema

```hcl
provider "gastown" {
  hq_path = "~/gt"   # required
}
```

### TDD Sequence

**Test 1** — Provider validates with `hq_path` set:
Red → implement `Provider()` → green → commit: `feat: provider schema`

**Test 2** — Provider rejects empty `hq_path`:
Red → add `stringvalidator.LengthAtLeast(1)` → green → commit: `test: provider rejects empty hq_path`

**Test 3** — Provider registers `gastown_hq`, `gastown_rig`, `gastown_crew`:
Red → register stubs → green → commit: `feat: register resource types`

**Exit criterion:** All three resource types registered. All tests pass.

---

## Phase 3: `gastown_hq` Resource

Read `/mnt/skills/user/provider-resources/SKILL.md` and
`/mnt/skills/user/terraform-test/SKILL.md` before starting.

### Schema

```hcl
resource "gastown_hq" "main" {
  path        = "/home/user/gt"     # required, ForceNew
  owner_email = "phil@example.com"  # optional
  git         = true                # optional, default true
}
```

Computed: `id` (= `path`), `name` (from `mayor/town.json`)

### TDD Sequence

**Test 1** — Create calls `gt install` and `mayor/town.json` exists:
```go
func TestHQResource_Create_callsGtInstall(t *testing.T) { ... }
func TestHQResource_Create_townJsonExists(t *testing.T) { ... }
```

**Test 2** — Read after Create returns identical state (idempotent):
```go
func TestHQResource_Read_idempotent(t *testing.T) { ... }
```

**Test 3** — Changing `path` triggers ForceNew:
```go
func TestHQResource_ForceNew_onPathChange(t *testing.T) { ... }
```

**Test 4** — Delete calls `gt uninstall --force`:
```go
func TestHQResource_Delete_callsUninstall(t *testing.T) { ... }
```

Each test gets its own HQ in `t.TempDir()`. Never reuse paths across tests.

**Exit criterion:** Full CRUD round-trip passes. No temp dirs leak.

---

## Phase 4: `gastown_rig` Resource

### Schema

```hcl
resource "gastown_rig" "mirror" {
  hq_path      = gastown_hq.main.path
  name         = "mirror"               # required, ForceNew
  repo         = "https://..."          # required, ForceNew
  runtime      = "claude"               # optional, default "claude"
  max_polecats = 4                      # optional, default 3
}
```

Computed: `id` (= `<hq_path>/<n>`), `status`, `prefix`

### TDD Sequence

**Test 1** — Create calls `gt rig add` and rig directory exists:
```go
func TestRigResource_Create_callsRigAdd(t *testing.T) { ... }
func TestRigResource_Create_rigDirExists(t *testing.T) { ... }
```

**Test 2** — Create sets runtime via `gt rig config set`:
```go
func TestRigResource_Create_setsRuntime(t *testing.T) { ... }
```

**Test 3** — Read reflects effective config from `gt rig config show`:
```go
func TestRigResource_Read_reflectsEffectiveConfig(t *testing.T) { ... }
```

**Test 4** — Update of `runtime` calls `gt rig config set`:
```go
func TestRigResource_Update_runtime(t *testing.T) { ... }
```

**Test 5** — `name` or `repo` change triggers ForceNew:
```go
func TestRigResource_ForceNew_onNameChange(t *testing.T) { ... }
func TestRigResource_ForceNew_onRepoChange(t *testing.T) { ... }
```

**Test 6** — Delete calls `gt rig stop` then `gt rig dock`; rig dir still exists:
```go
func TestRigResource_Delete_stopsAndDocks(t *testing.T) { ... }
func TestRigResource_Delete_doesNotRemoveFiles(t *testing.T) { ... }
```

**Test 7** — Drift: manually edit `config.json`; next plan shows a diff:
```go
func TestRigResource_DriftDetection(t *testing.T) { ... }
```

**Exit criterion:** Full CRUD passes. Rig directory exists after delete.

---

## Phase 5: `gastown_crew` Resource

### Schema

```hcl
resource "gastown_crew" "deacon" {
  hq_path  = gastown_hq.main.path
  rig_name = gastown_rig.mirror.name  # required, ForceNew
  name     = "deacon"                 # required, ForceNew
}
```

Computed: `id` (= `<hq_path>/<rig_name>/crew/<n>`), `path`

All attributes are ForceNew.

### TDD Sequence

**Test 1** — Create calls `gt crew add` and `crew/<n>/` exists:
```go
func TestCrewResource_Create_callsCrewAdd(t *testing.T) { ... }
func TestCrewResource_Create_dirExists(t *testing.T) { ... }
```

**Test 2** — Read detects workspace via `gt crew list --json`:
```go
func TestCrewResource_Read_detectsExistence(t *testing.T) { ... }
```

**Test 3** — Delete calls `gt crew remove`:
```go
func TestCrewResource_Delete_callsCrewRemove(t *testing.T) { ... }
```

**Test 4** — Create fails with descriptive error when rig does not exist:
```go
func TestCrewResource_Create_missingRig_returnsError(t *testing.T) { ... }
```

**Exit criterion:** Full CRUD passes. Dependency on rig enforced at apply time.

---

## Phase 6: Integration & Acceptance Suite

Read `/mnt/skills/user/terraform-test/SKILL.md` before writing acceptance tests.

```go
func TestAcc_FullLifecycle(t *testing.T) {
    // apply: creates HQ + rig + crew
    // plan: no diff (idempotency)
    // update runtime: apply succeeds, plan clean
    // destroy: rig is docked (not deleted), crew is removed
}

func TestAcc_DriftScenario(t *testing.T) {
    // apply, then manually edit rig config.json
    // next plan must show non-empty diff
}

func TestAcc_Concurrency(t *testing.T) {
    t.Parallel()
    // two separate HQ paths in t.TempDir(), apply simultaneously
    // verify no cross-contamination of state
}
```

Run with: `go test ./... -run TestAcc -v`

---

## Phase 7: Documentation & Release

Install tools before using them:

```bash
go install github.com/hashicorp/terraform-plugin-docs/cmd/tfplugindocs@latest
tfplugindocs generate

go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
golangci-lint run
```

Note: the golangci-lint module path is `github.com/golangci/golangci-lint` —
not `golangci-lint/golangci-lint`. Install will fail with the wrong path.

Add `.github/workflows/release.yml` with GoReleaser targeting:
`linux/amd64`, `linux/arm64`, `darwin/amd64`, `darwin/arm64`.

### Pre-Release Checklist

- [ ] `go test ./...` zero failures
- [ ] `go vet ./...` clean
- [ ] `golangci-lint run` clean
- [ ] `tfplugindocs generate` produces docs for all three resources
- [ ] All three resources have example HCL in `testdata/`
- [ ] No hardcoded paths outside test fixtures
- [ ] `LICENSE` and `README.md` present and complete

---

## README.md Content

```markdown
# terraform-provider-gastown

Terraform provider for managing Gas Town workspaces as infrastructure-as-code.

## Resources

- `gastown_hq` — Gas Town HQ (workspace root)
- `gastown_rig` — Project container wrapping a git repository
- `gastown_crew` — Persistent crew workspace within a rig

## Requirements

- Terraform >= 1.7
- `gt` >= 0.5.0 on PATH
- `bd` >= 0.44.0 on PATH
- `git` >= 2.25 on PATH
- `git config user.name` and `user.email` must be set globally

## Usage

\```hcl
provider "gastown" {
  hq_path = "/home/user/gt"
}

resource "gastown_hq" "main" {
  path        = "/home/user/gt"
  owner_email = "operator@kybernetes.systems"
}

resource "gastown_rig" "mirror" {
  hq_path  = gastown_hq.main.path
  name     = "mirror"
  repo     = "https://github.com/kybernetes-systems/rig-mirror.git"
  runtime  = "claude"
}

resource "gastown_crew" "deacon" {
  hq_path  = gastown_hq.main.path
  rig_name = gastown_rig.mirror.name
  name     = "deacon"
}
\```

## License

Apache 2.0
```

---

## Error Handling Standards

All CRUD errors must use `resp.Diagnostics.AddError()` with:
- A capitalized summary (e.g., `"Error creating rig"`)
- A detail string including the resource name and full stderr from `gt`/`bd`

Never swallow errors. Never panic. Never call `os.Exit`.

---

## Hard Constraints

- Call `gt` and `bd` via `os/exec` with explicit argument lists — never `/bin/sh`
- Parse internal Gas Town files (e.g., `config.json`, `mayor/town.json`) only
  where no `gt` command exposes the needed data
- All test HQ paths use `t.TempDir()` — no test writes to the real filesystem
- No global state — each resource operation is fully self-contained
- No shell intermediaries — direct exec only
