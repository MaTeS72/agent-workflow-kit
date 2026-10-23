#!/usr/bin/env python3
"""Mechanical checks behind the agent docs rubric (docs/agent-docs-rubric.md).

Usage: python3 scripts/agent_docs_check.py [repo] [--exclude PREFIX ...] [--json] [--strict]

Reports facts, not grades: broken links, root and nested line budgets, a
CLAUDE.md that doesn't import AGENTS.md, change folders (and legacy plan or
brainstorm files) without a status line, and PostToolUse hooks whose output
never reaches Claude. The /inspect skill turns these into rubric grades.

--strict exits 1 when any error is found, for CI.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
from post_edit import CHANGE_DOCS, CHANGES_DIR, STATUS_LINE, STATUS_SCAN_LINES  # noqa: E402  (one rule for hooks and checker)

ROOT_BUDGET = 200
NESTED_BUDGET = 50
LEGACY_FOLDERS = ("docs/plan", "docs/brainstorm")  # where repos kept plans before adopting change folders
SKIP_DIRS = {".git", "node_modules", ".dart_tool", "build", "Pods", "vendor", ".venv", "worktrees"}
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMPORT = re.compile(r"^@(\S+)\s*$", re.MULTILINE)
EXIT_TWO = re.compile(r"exit\s*\(?\s*2\b|sys\.exit\(\s*2\s*\)|return\s+2\b")
REPO_SCRIPT = re.compile(r"(?:\$CLAUDE_PROJECT_DIR\"?/|\./)?(\.claude/\S+?\.(?:sh|py|js|ts|mjs))")


@dataclass
class Finding:
    severity: str  # "error" | "warning"
    check: str
    path: str
    message: str


def walk(root: Path, pattern: str, excludes: list[str]):
    for path in sorted(root.rglob(pattern)):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts[:-1]):
            continue
        if any(relative.as_posix().startswith(prefix) for prefix in excludes):
            continue
        yield path


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def check_links(root: Path, files: list[Path]) -> list[Finding]:
    findings = []
    for doc in files:
        text = doc.read_text(encoding="utf-8", errors="replace")
        # Ignore links inside fenced code blocks: they are examples, not references.
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for target in LINK.findall(text):
            if re.match(r"^(?:[a-z][a-z0-9+.-]*:|#)", target, re.IGNORECASE) or "<" in target or "${" in target:
                continue
            clean = re.sub(r"(#.*|:\d+(?:-\d+)?)$", "", target)
            if clean and not (doc.parent / clean).exists():
                findings.append(
                    Finding("error", "broken-link", doc.relative_to(root).as_posix(), f"link target `{target}` does not exist")
                )
    return findings


def check_budgets(root: Path, claude_files: list[Path]) -> list[Finding]:
    findings = []
    agents, claude = root / "AGENTS.md", root / "CLAUDE.md"
    root_files = {p.resolve() for p in (agents, claude) if p.is_file()}
    if claude.is_file():
        for target in IMPORT.findall(claude.read_text(encoding="utf-8")):
            imported = (root / target).resolve()
            if imported.is_file():
                root_files.add(imported)
    total = sum(line_count(p) for p in root_files)
    if total > ROOT_BUDGET:
        findings.append(
            Finding("warning", "root-budget", "AGENTS.md + CLAUDE.md", f"{total} always-loaded lines (budget {ROOT_BUDGET})")
        )
    if agents.is_file() and claude.is_file() and "@AGENTS.md" not in claude.read_text(encoding="utf-8"):
        findings.append(Finding("warning", "import", "CLAUDE.md", "CLAUDE.md does not import @AGENTS.md"))
    for nested in claude_files:
        if nested.parent == root:
            continue
        lines = line_count(nested)
        if lines > NESTED_BUDGET:
            findings.append(
                Finding("warning", "nested-budget", nested.relative_to(root).as_posix(), f"{lines} lines (budget {NESTED_BUDGET})")
            )
    return findings


def has_status(doc: Path) -> bool:
    head = "\n".join(doc.read_text(encoding="utf-8", errors="replace").splitlines()[:STATUS_SCAN_LINES])
    return STATUS_LINE.search(head) is not None


def check_change_folders(root: Path) -> list[Finding]:
    changes = root / CHANGES_DIR

    findings = []
    status_docs = []
    folders = sorted(p for p in changes.glob("*") if p.is_dir() and not p.name.startswith("."))
    for folder in folders:
        present = [folder / name for name in CHANGE_DOCS if (folder / name).is_file()]
        if not present:
            findings.append(
                Finding("error", "change-folder", folder.relative_to(root).as_posix(), "no brief.md or plan.md")
            )
        status_docs += present
    for legacy in LEGACY_FOLDERS:
        status_docs += [p for p in sorted((root / legacy).glob("*.md")) if p.name.lower() != "readme.md"]

    for doc in status_docs:
        if not has_status(doc):
            findings.append(
                Finding("error", "status-line", doc.relative_to(root).as_posix(), "no `Status:` line near the top")
            )
    return findings


def check_post_hooks(root: Path) -> list[Finding]:
    """Flag PostToolUse hook scripts that can only talk to the debug log."""
    findings = []
    for settings in (root / ".claude" / "settings.json", root / ".claude" / "settings.local.json"):
        if not settings.is_file():
            continue
        try:
            groups = json.loads(settings.read_text(encoding="utf-8")).get("hooks", {}).get("PostToolUse", [])
        except (json.JSONDecodeError, AttributeError):
            continue
        for group in groups:
            for hook in group.get("hooks", []):
                for script_path in REPO_SCRIPT.findall(hook.get("command", "")):
                    script = root / script_path
                    if not script.is_file():
                        findings.append(Finding("error", "hook-missing", script_path, "hook script does not exist"))
                        continue
                    source = script.read_text(encoding="utf-8", errors="replace")
                    talks = re.search(r"\b(echo|printf|print)\b", source)
                    if talks and "additionalContext" not in source and not EXIT_TWO.search(source):
                        findings.append(
                            Finding(
                                "warning",
                                "hook-visibility",
                                script_path,
                                "PostToolUse output on exit 0 goes to the debug log only; use additionalContext JSON or exit 2",
                            )
                        )
    return findings


def run(root: Path, excludes: list[str]) -> list[Finding]:
    claude_files = list(walk(root, "CLAUDE.md", excludes))
    linked = [root / "AGENTS.md", root / "README.md", *claude_files]
    linked += list(walk(root, "SKILL.md", excludes)) + list(walk(root / "docs", "*.md", excludes) if (root / "docs").is_dir() else [])
    linked += list(walk(root / "agents", "*.md", excludes)) if (root / "agents").is_dir() else []
    linked = [p for p in dict.fromkeys(linked) if p.is_file()]
    return (
        check_links(root, linked)
        + check_budgets(root, claude_files)
        + check_change_folders(root)
        + check_post_hooks(root)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--exclude", action="append", default=[], help="path prefix to skip (repeatable)")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    parser.add_argument("--strict", action="store_true", help="exit 1 when any error is found")
    args = parser.parse_args()

    root = Path(args.repo).resolve()
    findings = run(root, [prefix.rstrip("/") + "/" for prefix in args.exclude])

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        for finding in findings:
            print(f"{finding.severity.upper():7} {finding.check:16} {finding.path}: {finding.message}")
        errors = sum(f.severity == "error" for f in findings)
        print(f"\n{errors} error(s), {len(findings) - errors} warning(s) in {root.name}")

    return 1 if args.strict and any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
