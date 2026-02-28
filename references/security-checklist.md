# Security Checklist

Security considerations for skill authoring, distribution, and execution. Distinguishes implemented mitigations from roadmap items.

---

## Overview

Agent Skills are powerful because they can execute code, access files, and manipulate context. This creates security surface area that authors and users must understand.

**Key threats**:
- Script execution risks
- Prompt injection via skill content
- Memory poisoning (skills modifying SOUL.md/MEMORY.md)
- Supply chain risks

---

## Implemented Mitigations

### allowed-tools Capability Dropping

**Status**: Implemented

Skills declare required tools via `allowed-tools` in frontmatter. Harnesses enforce these permissions at activation. Users can audit what tools a skill requests before enabling.

```yaml
allowed-tools:
  - read
  - edit
  - write
  - bash: git
```

**Benefit**: Defense in depth. Even if a skill is compromised, tool access is limited to declared scope.

### .source.json Provenance

**Status**: Implemented

The scaffold generates `.source.json` metadata for each skill file:
- Original source file path
- Author/organization
- Timestamp
- Version

**Benefit**: Enables audit trails. Users can trace file origins and verify trustworthiness.

### Dry-Run Previews

**Status**: Implemented (via validate command)

`agentskills validate` performs static analysis without executing scripts. Authors and users can preview what a skill will do before activation.

**Benefit**: Transparency. Reduces risk of unexpected execution.

---

## Roadmap Mitigations

### Cryptographic Signatures

**Status**: Roadmap

Future: Skills will be signable by authors using Ed25519 or similar. Harnesses verify signatures before execution.

**Benefit**: Authenticity. Users can trust that skill content has not been tampered with.

### Signed Skill Registry

**Status**: Roadmap

Future: Central or distributed registry of signed skills with verified author identities. Similar to npm signed packages.

**Benefit**: Supply chain security. Reduces risk of malicious skill distribution via typosquatting or repo mirrors.

### Runtime Behavior Sandboxing

**Status**: Roadmap

Future: Execute skill scripts in isolated containers or VMs with minimal filesystem access and network restrictions.

**Benefit**: Blast radius reduction. Compromised skills cannot access sensitive data or escalate privileges.

### Memory Poisoning Detection

**Status**: Roadmap

Future: Harnesses detect and warn when skills attempt to modify SOUL.md/MEMORY.md context files without explicit user consent.

**Benefit**: Prevents context manipulation attacks.

---

## Security Checklist (Yes/No)

Review this checklist before publishing or enabling a skill:

| # | Question | Yes | No |
|---|----------|-----|-----|
| 1 | Does the skill declare all required tools in `allowed-tools`? | ☐ | ☐ |
| 2 | Are scripts audited via `agentskills validate` before use? | ☐ | ☐ |
| 3 | Does the skill include `.source.json` provenance metadata? | ☐ | ☐ |
| 4 | Have you reviewed all scripts for unsafe `bash` commands? | ☐ | ☐ |
| 5 | Does the skill avoid embedding untrusted user input in prompts? | ☐ | ☐ |
| 6 | Are external dependencies pinned to specific versions? | ☐ | ☐ |
| 7 | Does the skill document what data it accesses? | ☐ | ☐ |
| 8 | Have you verified the skill source (author, repo)? | ☐ | ☐ |
| 9 | Does the skill avoid modifying SOUL.md/MEMORY.md without consent? | ☐ | ☐ |
| 10 | Is the skill published from a trusted registry or repo? | ☐ | ☐ |
| 11 | Have you tested the skill in an isolated environment? | ☐ | ☐ |
| 12 | Does the skill avoid downloading/executing untrusted code? | ☐ | ☐ |
| 13 | Are sensitive operations logged and reviewable? | ☐ | ☐ |
| 14 | Do you understand the skill's behavior before enabling it? | ☐ | ☐ |
| 15 | Is the skill regularly updated for security patches? | ☐ | ☐ |

---

## Best Practices

1. **Least privilege**: Declare only tools the skill needs
2. **Audit scripts**: Run `agentskills validate` before each use
3. **Verify sources**: Check `.source.json` metadata
4. **Isolate testing**: Use separate workspace for skill testing
5. **Stay updated**: Pull latest versions from trusted sources
6. **Minimize external calls**: Reduce attack surface
7. **Document behavior**: Users must understand what the skill does
