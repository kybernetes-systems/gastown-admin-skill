#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
Audit skill directory for progressive disclosure QUALITY compliance.

Usage:
    uv run scripts/audit_disclosure.py [--json] [--] PATH

Exit codes:
    0  Success (no issues found)
    1  Error (invalid path or arguments)
    2  Issues found
"""

import argparse
import json
import re
import sys
from pathlib import Path


def count_lines(content: str) -> int:
    return len(content.splitlines())


def find_large_code_blocks(skill_md_path: Path) -> list[dict]:
    issues = []
    content = skill_md_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    in_code_block = False
    code_block_start = 0
    code_block_lines = []
    lang = ""

    code_block_re = re.compile(r"^```(\w*)$")

    for i, line in enumerate(lines, 1):
        if not in_code_block and code_block_re.match(line):
            in_code_block = True
            code_block_start = i
            lang = code_block_re.match(line).group(1)
            code_block_lines = []
        elif in_code_block and line == "```":
            block_height = len(code_block_lines)
            if block_height > 30:
                issues.append(
                    {
                        "type": "large_code_block",
                        "line": code_block_start,
                        "lines": block_height,
                        "message": f"Fenced code block ({block_height} lines) exceeds 30 line limit",
                    }
                )
            in_code_block = False
        elif in_code_block:
            code_block_lines.append(line)

    return issues


def find_large_sections(skill_md_path: Path) -> list[dict]:
    issues = []
    content = skill_md_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    in_section = False
    section_start = 0
    section_lines = []
    section_name = ""

    heading_re = re.compile(r"^(#{1,6})\s+(.+)$")

    for i, line in enumerate(lines, 1):
        match = heading_re.match(line)
        if match:
            if in_section and len(section_lines) > 100:
                issues.append(
                    {
                        "type": "large_section",
                        "line": section_start,
                        "lines": len(section_lines),
                        "section": section_name,
                        "message": f"Section '{section_name}' ({len(section_lines)} lines) exceeds 100 line limit; move to references/",
                    }
                )
            in_section = True
            section_start = i
            section_name = match.group(2).strip()
            section_lines = []
        elif in_section:
            section_lines.append(line)

    if in_section and len(section_lines) > 100:
        issues.append(
            {
                "type": "large_section",
                "line": section_start,
                "lines": len(section_lines),
                "section": section_name,
                "message": f"Section '{section_name}' ({len(section_lines)} lines) exceeds 100 line limit; move to references/",
            }
        )

    return issues


def find_large_references(references_dir: Path) -> list[dict]:
    issues = []
    if not references_dir.exists():
        return issues

    for ref_file in references_dir.rglob("*.md"):
        content = ref_file.read_text(encoding="utf-8")
        tokens = int(len(content.split()) * 1.3)
        if tokens > 2000:
            rel_path = ref_file.relative_to(references_dir)
            issues.append(
                {
                    "type": "large_reference",
                    "file": str(rel_path),
                    "tokens": tokens,
                    "message": f"Reference {rel_path} ({tokens} tokens) exceeds 2000 token limit",
                }
            )

    return issues


def find_orphaned_references(skill_md_path: Path, references_dir: Path) -> list[dict]:
    issues = []
    if not skill_md_path.exists() or not references_dir.exists():
        return issues

    content = skill_md_path.read_text(encoding="utf-8")
    referenced = set()

    ref_link_re = re.compile(r"\[([^\]]+)\]\((references/[^)]+)\)")
    for match in ref_link_re.finditer(content):
        ref_path = match.group(2)
        referenced.add(ref_path)

    for ref_file in references_dir.rglob("*.md"):
        rel_path = ref_file.relative_to(references_dir.parent)
        ref_str = str(rel_path)
        if ref_str not in referenced and str(ref_str) not in referenced:
            issues.append(
                {
                    "type": "orphaned_reference",
                    "file": ref_str,
                    "message": f"Reference {ref_str} is not referenced from SKILL.md",
                }
            )

    return issues


def find_orphaned_scripts(skill_md_path: Path, scripts_dir: Path) -> list[dict]:
    issues = []
    if not skill_md_path.exists() or not scripts_dir.exists():
        return issues

    content = skill_md_path.read_text(encoding="utf-8")
    referenced = set()

    script_link_re = re.compile(
        r"(?:run|call|execute|use)\s+[`]?scripts/([^]`]+\.py)[`]?", re.IGNORECASE
    )
    for match in script_link_re.finditer(content):
        script_name = match.group(1)
        referenced.add(f"scripts/{script_name}")

    for script_file in scripts_dir.rglob("*.py"):
        rel_path = script_file.relative_to(scripts_dir.parent)
        script_str = str(rel_path)
        if script_str not in referenced:
            issues.append(
                {
                    "type": "orphaned_script",
                    "file": script_str,
                    "message": f"Script {script_str} is not referenced from SKILL.md",
                }
            )

    return issues


def token_summary(skill_dir: Path) -> dict:
    result = {
        "tier1_frontmatter": 0,
        "tier2_body": 0,
        "tier3_total": 0,
    }

    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]
                result["tier1_frontmatter"] = int(len(frontmatter.split()) * 1.3)
                result["tier2_body"] = int(len(body.split()) * 1.3)

    references_dir = skill_dir / "references"
    if references_dir.exists():
        for ref_file in references_dir.rglob("*.md"):
            content = ref_file.read_text(encoding="utf-8")
            result["tier3_total"] += int(len(content.split()) * 1.3)

    return result


def audit_skill_dir(path: Path) -> dict:
    result = {
        "path": str(path),
        "issues": [],
        "token_summary": {},
    }

    skill_md = path / "SKILL.md"
    references_dir = path / "references"
    scripts_dir = path / "scripts"

    if not skill_md.exists():
        result["error"] = "SKILL.md not found"
        return result

    result["issues"].extend(find_large_code_blocks(skill_md))
    result["issues"].extend(find_large_sections(skill_md))
    result["issues"].extend(find_large_references(references_dir))
    result["issues"].extend(find_orphaned_references(skill_md, references_dir))
    result["issues"].extend(find_orphaned_scripts(skill_md, scripts_dir))
    result["token_summary"] = token_summary(path)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit skill directory for progressive disclosure QUALITY compliance.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0  Success (no issues found)
  1  Error (invalid path or arguments)
  2  Issues found

Checks performed:
  - Large code blocks in SKILL.md (>30 lines)
  - Large sections in SKILL.md (>100 lines)
  - Large reference files (>2000 tokens)
  - Orphaned reference files (not linked from SKILL.md)
  - Orphaned scripts (not linked from SKILL.md)
  - Token budget summary per tier

Examples:
  uv run scripts/audit_disclosure.py .
  uv run scripts/audit_disclosure.py ../my-skill --json
        """,
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

    result = audit_skill_dir(skill_path)

    if args.json:
        output = {"success": True, **result}
        print(json.dumps(output, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            return 1

        print(f"Audit: {result['path']}")
        print()

        if result["issues"]:
            print(f"Issues found: {len(result['issues'])}")
            print()
            for issue in result["issues"]:
                if "line" in issue:
                    print(f"  L{issue['line']}: {issue['message']}")
                elif "file" in issue:
                    print(f"  {issue['file']}: {issue['message']}")
                else:
                    print(f"  {issue['message']}")
            print()
            print(f"Token Summary:")
            print(
                f"  Tier 1 (frontmatter): {result['token_summary']['tier1_frontmatter']:,} tokens"
            )
            print(
                f"  Tier 2 (SKILL.md body): {result['token_summary']['tier2_body']:,} tokens"
            )
            print(
                f"  Tier 3 (references): {result['token_summary']['tier3_total']:,} tokens"
            )
            return 2
        else:
            print("No issues found.")
            print()
            print(f"Token Summary:")
            print(
                f"  Tier 1 (frontmatter): {result['token_summary']['tier1_frontmatter']:,} tokens"
            )
            print(
                f"  Tier 2 (SKILL.md body): {result['token_summary']['tier2_body']:,} tokens"
            )
            print(
                f"  Tier 3 (references): {result['token_summary']['tier3_total']:,} tokens"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
