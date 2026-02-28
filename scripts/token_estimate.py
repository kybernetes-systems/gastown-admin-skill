#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "tiktoken>=0.7.0",
# ]
# ///
"""
Estimate token counts for progressive disclosure tiers.

Usage:
    uv run scripts/token_estimate.py [--model MODEL] [--json] [--] PATH

Exit codes:
    0  Success
    1  Error (invalid path or arguments)
"""

import argparse
import json
import sys
from pathlib import Path

TOKENS_PER_WORD = 1.3
T2_BUDGET_LIMIT = 5000

TIKTOKEN_AVAILABLE = False
try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    pass


def count_tokens_word_heuristic(text: str) -> int:
    """Estimate tokens using word count heuristic."""
    words = len(text.split())
    return int(words * TOKENS_PER_WORD)


def count_tokens_tiktoken(text: str, model: str) -> int:
    """Count tokens using tiktoken."""
    if not TIKTOKEN_AVAILABLE:
        return count_tokens_word_heuristic(text)
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def parse_frontmatter(content: str) -> tuple[str, str]:
    """Parse YAML frontmatter from markdown file."""
    if not content.startswith("---"):
        return "", content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return "", content
    return parts[1], parts[2]


def analyze_skill_dir(path: Path, model: str, use_tiktoken: bool) -> dict:
    """Analyze a skill directory and return token estimates."""
    result = {
        "path": str(path),
        "tier1_frontmatter": 0,
        "tier2_body": 0,
        "tier3_references": {},
        "tier3_total": 0,
        "aggregate_total": 0,
        "violations": [],
    }

    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        result["error"] = "SKILL.md not found"
        return result

    content = skill_md.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)

    if use_tiktoken and TIKTOKEN_AVAILABLE:
        count = count_tokens_tiktoken
        result["method"] = f"tiktoken ({model})"
    else:
        count = count_tokens_word_heuristic
        result["method"] = "word-heuristic (1.3x)"

    result["tier1_frontmatter"] = count(frontmatter)
    result["tier2_body"] = count(body)

    references_dir = path / "references"
    if references_dir.exists() and references_dir.is_dir():
        for ref_file in sorted(references_dir.rglob("*.md")):
            rel_path = ref_file.relative_to(references_dir)
            ref_content = ref_file.read_text(encoding="utf-8")
            tokens = count(ref_content)
            result["tier3_references"][str(rel_path)] = tokens
            result["tier3_total"] += tokens

    result["aggregate_total"] = (
        result["tier1_frontmatter"] + result["tier2_body"] + result["tier3_total"]
    )

    if result["tier2_body"] > T2_BUDGET_LIMIT:
        result["violations"].append(
            {
                "tier": "T2",
                "limit": T2_BUDGET_LIMIT,
                "actual": result["tier2_body"],
                "message": f"T2 body exceeds {T2_BUDGET_LIMIT} token budget",
            }
        )

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estimate token counts for progressive disclosure tiers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Exit codes:
  0  Success
  1  Error

Token estimation methods:
  - word-heuristic (default): words × {TOKENS_PER_WORD}
  - tiktoken: precise count if available (use --model)

T2 budget: {T2_BUDGET_LIMIT} tokens

Examples:
  uv run scripts/token_estimate.py .
  uv run scripts/token_estimate.py ../my-skill --json
  uv run scripts/token_estimate.py . --model gpt-4
        """,
    )
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="Model for tiktoken encoding [default: gpt-4]",
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

    use_tiktoken = TIKTOKEN_AVAILABLE
    result = analyze_skill_dir(skill_path, args.model, use_tiktoken)

    if args.json:
        output = {"success": True, **result}
        print(json.dumps(output, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            return 1

        print(f"Token Estimate: {result['path']}")
        print(f"Method: {result['method']}")
        print()
        print(f"  Tier 1 (frontmatter): {result['tier1_frontmatter']:,} tokens")
        print(f"  Tier 2 (SKILL.md body): {result['tier2_body']:,} tokens")
        print(f"  Tier 3 (references):    {result['tier3_total']:,} tokens")
        print(f"  ─────────────────────────────────")
        print(f"  Aggregate total:      {result['aggregate_total']:,} tokens")
        print()

        if result["tier3_references"]:
            print("  Tier 3 breakdown:")
            for ref_path, tokens in result["tier3_references"].items():
                print(f"    {ref_path}: {tokens:,} tokens")
            print()

        if result["violations"]:
            print("  VIOLATIONS:")
            for v in result["violations"]:
                print(f"    - {v['message']}")
        else:
            print("  No budget violations.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
