#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
Generate .source.json provenance file for skill directory.

Usage:
    uv run scripts/gen_source_json.py [--author AUTHOR] [--version VER] [--json] [--] PATH

Exit codes:
    0  Success
    1  Error (invalid path or arguments)
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0"


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of file contents."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def generate_source_json(
    skill_dir: Path,
    author: str | None,
    version: str | None,
) -> dict:
    """Generate .source.json provenance data."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    content = skill_md.read_text(encoding="utf-8")
    skill_name = None
    for line in content.splitlines():
        if line.startswith("name:"):
            skill_name = line.split(":", 1)[1].strip()
            break

    if not skill_name:
        raise ValueError("Could not find skill name in SKILL.md frontmatter")

    files: dict[str, str] = {}
    for f in sorted(skill_dir.rglob("*")):
        if f.is_file() and not f.name.startswith("."):
            rel_path = f.relative_to(skill_dir)
            files[str(rel_path)] = sha256_file(f)

    result = {
        "schema_version": SCHEMA_VERSION,
        "skill_name": skill_name,
        "author": author or "",
        "version": version or "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate .source.json provenance file for skill directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0  Success
  1  Error

Output schema:
  {
    "schema_version": "1.0",
    "skill_name": "<name from SKILL.md>",
    "author": "<author>",
    "version": "<version>",
    "created_at": "<ISO timestamp>",
    "files": {"filename": "sha256", ...}
  }

Idempotent: same files produce same output.

Examples:
  uv run scripts/gen_source_json.py .
  uv run scripts/gen_source_json.py . --author "Phil Mocek" --version "1.0.0"
  uv run scripts/gen_source_json.py ../my-skill --json
        """,
    )
    parser.add_argument(
        "--author",
        default="",
        help="Author name",
    )
    parser.add_argument(
        "--version",
        default="",
        help="Version string",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to skill directory [default: .]",
    )
    args = parser.parse_args()

    skill_path = Path(args.path).resolve()
    if not skill_path.exists():
        if args.json:
            print(
                json.dumps({"success": False, "error": f"Path not found: {skill_path}"})
            )
        else:
            print(f"Error: Path not found: {skill_path}", file=sys.stderr)
        return 1

    try:
        result = generate_source_json(
            skill_path,
            args.author or None,
            args.version or None,
        )
    except Exception as e:
        if args.json:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1

    output_path = skill_path / ".source.json"
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps({"success": True, "path": str(output_path)}, indent=2))
    else:
        print(f"Created: {output_path}")
        print(f"  Skill: {result['skill_name']}")
        print(f"  Files: {len(result['files'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
