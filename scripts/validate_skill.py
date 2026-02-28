#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
Validate an Agent Skill directory against the agentskills.io specification.

Usage:
    uv run scripts/validate_skill.py <path> [--strict] [--json] [--help]

Exit codes:
    0  All checks passed
    1  One or more errors (spec violations)
    2  No errors but one or more warnings (inverted with --strict: warnings become errors)
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# YAML frontmatter parser (stdlib only -- no PyYAML)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter delimited by ---. Returns (fields, body).
    Raises ValueError if frontmatter is missing or malformed.
    """
    if not text.startswith("---"):
        raise ValueError("SKILL.md does not begin with --- (no frontmatter)")

    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("Frontmatter opening --- has no closing ---")

    raw = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")

    fields: dict = {}
    current_key: str | None = None
    current_lines: list[str] = []
    in_block_scalar = False
    block_indent: int = 0
    mapping_key: str | None = None  # key whose value is a mapping
    mapping: dict | None = None

    def flush_scalar():
        nonlocal current_key, current_lines, in_block_scalar, mapping_key, mapping
        if current_key is None:
            return
        if in_block_scalar:
            value = " ".join(l.strip() for l in current_lines if l.strip())
        else:
            value = current_lines[0].strip() if current_lines else ""
        if mapping_key is not None:
            # We were collecting a sub-mapping -- this flush is for a scalar
            # after the mapping, so close the mapping first.
            fields[mapping_key] = mapping
            mapping_key = None
            mapping = None
        fields[current_key] = value
        current_key = None
        current_lines = []
        in_block_scalar = False

    for line in raw.splitlines():
        # Detect top-level key: "key: value" or "key:" or "key: >"
        key_match = re.match(r'^([a-zA-Z0-9_-]+):\s*(.*)', line)
        if key_match and not line.startswith(" "):
            # Flush previous key
            if mapping_key is not None and mapping is not None:
                fields[mapping_key] = mapping
                mapping_key = None
                mapping = None
            elif current_key is not None:
                flush_scalar()

            current_key = key_match.group(1)
            rest = key_match.group(2).strip()
            current_lines = []
            in_block_scalar = False

            if rest == ">":
                in_block_scalar = True
            elif rest == "":
                # Could be a mapping block coming up -- defer
                mapping_key = current_key
                mapping = {}
                current_key = None
            else:
                current_lines = [rest]
            continue

        # Indented mapping entry (two-space or four-space indent)
        indent_match = re.match(r'^  ([a-zA-Z0-9_-]+):\s*(.*)', line)
        if indent_match and mapping_key is not None:
            if mapping is None:
                mapping = {}
            mapping[indent_match.group(1)] = indent_match.group(2).strip()
            continue

        # Continuation line for block scalar
        if in_block_scalar and line.startswith("  "):
            current_lines.append(line)
            continue

        # Continuation line for folded scalar (indented continuation)
        if current_key and line.startswith("  ") and not in_block_scalar:
            current_lines.append(line)
            continue

    # Flush final key
    if mapping_key is not None and mapping is not None:
        fields[mapping_key] = mapping
    elif current_key is not None:
        flush_scalar()

    return fields, body


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

NAME_RE = re.compile(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$')
SHEBANG_RE = re.compile(r'^#!')


def validate(skill_path: Path, strict: bool) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    skill_md = skill_path / "SKILL.md"

    # 1. SKILL.md exists
    if not skill_md.exists():
        errors.append("SKILL.md not found in skill directory")
        return errors, warnings  # can't continue without it

    text = skill_md.read_text(encoding="utf-8")

    # 2. Frontmatter parses
    try:
        fields, body = parse_frontmatter(text)
    except ValueError as exc:
        errors.append(f"Frontmatter parse error: {exc}")
        return errors, warnings

    # 3. name field
    name = fields.get("name", "")
    if not name:
        errors.append("Frontmatter missing required field: name")
    else:
        if len(name) < 1 or len(name) > 64:
            errors.append(f"name length {len(name)} is out of range 1-64: {name!r}")
        if not NAME_RE.match(name):
            errors.append(
                f"name {name!r} fails regex: must be lowercase alphanumeric + hyphens, "
                "no leading/trailing/consecutive hyphens"
            )
        if "--" in name:
            errors.append(f"name {name!r} contains consecutive hyphens")
        # Directory match
        if name != skill_path.name:
            errors.append(
                f"name {name!r} does not match parent directory {skill_path.name!r}"
            )

    # 4. description field
    desc = fields.get("description", "")
    if not desc:
        errors.append("Frontmatter missing required field: description")
    else:
        if len(desc) < 1 or len(desc) > 1024:
            errors.append(
                f"description length {len(desc)} is out of range 1-1024 chars"
            )

    # 5. license field (optional, no constraints beyond presence)
    # No errors; presence is recommended not required

    # 6. compatibility field (optional, string, max 500 chars)
    compat = fields.get("compatibility", "")
    if compat and len(compat) > 500:
        errors.append(f"compatibility exceeds 500 chars (got {len(compat)})")

    # 7. metadata field (optional, must be a mapping of string->string)
    meta = fields.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            errors.append("metadata field must be a mapping (key: value pairs)")
        else:
            for k, v in meta.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    errors.append(
                        f"metadata keys and values must be strings; "
                        f"got key={k!r} value={v!r}"
                    )

    # 8. allowed-tools field (optional, must be a string)
    allowed = fields.get("allowed-tools")
    if allowed is not None and not isinstance(allowed, str):
        errors.append("allowed-tools field must be a space-delimited string")

    # 9. Body exists
    if not body.strip():
        errors.append("SKILL.md body is empty (no content after frontmatter)")

    # 10. Line count warning
    total_lines = len(text.splitlines())
    if total_lines > 500:
        warnings.append(
            f"SKILL.md is {total_lines} lines; recommended maximum is 500. "
            "Move reference material to references/ directory."
        )

    # 11. Referenced files exist
    ref_pattern = re.compile(r'\[.*?\]\(([^)]+)\)|`((?:scripts|references|assets)/[^`]+)`')
    for m in ref_pattern.finditer(body):
        ref = m.group(1) or m.group(2)
        if ref and not ref.startswith("http") and not ref.startswith("#"):
            ref_path = skill_path / ref
            if not ref_path.exists():
                warnings.append(f"Referenced file does not exist: {ref}")

    # 12. Scripts have shebangs
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.iterdir():
            if script.is_file() and not script.name.startswith("."):
                first_line = ""
                try:
                    first_line = script.read_text(encoding="utf-8").splitlines()[0]
                except (IndexError, UnicodeDecodeError):
                    pass
                if not SHEBANG_RE.match(first_line):
                    warnings.append(f"Script missing shebang: scripts/{script.name}")

    return errors, warnings


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an Agent Skill directory against the agentskills.io spec.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0  All checks passed
  1  One or more spec errors
  2  Warnings present (only when --strict is set and no errors)

Examples:
  uv run scripts/validate_skill.py .
  uv run scripts/validate_skill.py ../my-skill --strict
  uv run scripts/validate_skill.py . --json
""",
    )
    parser.add_argument("path", nargs="?", default=".", help="Path to skill directory [default: .]")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of plain text")
    args = parser.parse_args()

    skill_path = Path(args.path).resolve()

    if not skill_path.is_dir():
        msg = f"Not a directory: {skill_path}"
        if args.json:
            print(json.dumps({"valid": False, "errors": [msg], "warnings": []}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 1

    errors, warnings = validate(skill_path, strict=args.strict)
    valid = len(errors) == 0

    if args.json:
        print(json.dumps({
            "valid": valid and (not warnings or not args.strict),
            "path": str(skill_path),
            "errors": errors,
            "warnings": warnings,
        }, indent=2))
    else:
        label = str(skill_path)
        if errors:
            print(f"FAIL {label}")
            for e in errors:
                print(f"  error: {e}")
        if warnings:
            for w in warnings:
                marker = "  error:" if args.strict else "  warn: "
                print(f"{marker} {w}")
        if not errors and not warnings:
            print(f"OK    {label}")
        elif not errors:
            print(f"{'FAIL' if args.strict else 'WARN'} {label}")

    if errors:
        return 1
    if warnings and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
