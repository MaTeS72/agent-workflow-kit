#!/usr/bin/env python3
"""PostToolUse hook: format the edited file and hand Claude any reminders.

Driven by `.claude/agent-workflow.json`:

- `formatOnEdit`: run the first matching formatter on the edited file
  (`{"glob": "**/*.go", "command": "gofmt -w {file}"}`). A failure is reported
  to Claude, never blocking.
- `pairedFiles`: remind Claude of files that must change together
  (`{"glob": "lib/l10n/app_*.arb", "reminder": "Update all 8 ARB files."}`).
- `patterns`: flag text the edit *added* that breaks a rule
  (`{"glob": "lib/**/*.dart", "regex": "Widget _build", "message": "…"}`).
  Only the added text is checked, so existing code doesn't cause noise.
- A change folder's `brief.md` or `plan.md` without a status line gets a
  reminder, so shipped work can't pass for live work.
"""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
from pathlib import Path

from workflow_config import (
    edited_path,
    emit_context,
    first_match,
    load_config,
    matches,
    project_root,
    read_payload,
)

FORMAT_TIMEOUT_SECONDS = 45
STATUS_LINE = re.compile(r"^\s*(?:>\s*)?\**status\**\s*:", re.IGNORECASE | re.MULTILINE)
STATUS_SCAN_LINES = 30
CHANGES_DIR = "docs/changes"
CHANGE_DOCS = ("brief.md", "plan.md")


def format_file(root: Path, path: str, rule: dict) -> str | None:
    """Run the rule's formatter on `path`. Returns a message only on failure."""
    command = rule.get("command", "")
    if "{file}" not in command:
        return f"agent-workflow: formatOnEdit command for `{rule['glob']}` has no {{file}} placeholder; skipped."
    argv = shlex.split(command.replace("{file}", shlex.quote(path)))
    try:
        result = subprocess.run(
            argv, cwd=root, capture_output=True, text=True, timeout=FORMAT_TIMEOUT_SECONDS
        )
    except FileNotFoundError:
        return f"Formatter `{argv[0]}` is not installed, so {path} was not formatted. Format it before committing."
    except subprocess.TimeoutExpired:
        return f"Formatter timed out after {FORMAT_TIMEOUT_SECONDS}s on {path}. Format it before committing."
    if result.returncode != 0:
        output = (result.stderr or result.stdout).strip().splitlines()[:15]
        return f"Formatting {path} failed (`{command}`), which usually means a syntax error:\n" + "\n".join(output)
    return None


def added_text(payload: dict) -> str:
    """The text this tool call put into the file: Edit/MultiEdit replacements or Write content."""
    tool_input = payload.get("tool_input") or {}
    parts = [tool_input.get("new_string"), tool_input.get("content"), tool_input.get("new_source")]
    parts += [edit.get("new_string") for edit in tool_input.get("edits") or [] if isinstance(edit, dict)]
    return "\n".join(part for part in parts if isinstance(part, str))


def pattern_messages(path: str, text: str, rules: list) -> list[str]:
    """Messages for every `patterns` rule whose glob matches and whose regex hits the added text."""
    messages = []
    for rule in rules or []:
        if not (isinstance(rule, dict) and isinstance(rule.get("glob"), str) and matches(path, rule["glob"])):
            continue
        try:
            hit = re.search(rule.get("regex", ""), text, re.MULTILINE)
        except re.error as error:
            messages.append(f"agent-workflow: pattern `{rule.get('regex')}` is not a valid regex ({error}); skipped.")
            continue
        if hit:
            messages.append(f"{path}: `{hit.group(0).strip()}` — {rule.get('message', 'breaks a project rule.')}")
    return messages


def is_change_doc(path: str) -> bool:
    """True for `docs/changes/<folder>/brief.md` or `plan.md`; dot-folders hold scratch files."""
    parts = path.split("/")
    prefix = CHANGES_DIR.split("/")
    return (
        len(parts) == len(prefix) + 2
        and parts[: len(prefix)] == prefix
        and not parts[-2].startswith(".")
        and parts[-1] in CHANGE_DOCS
    )


def missing_status(root: Path, path: str) -> str | None:
    """A reminder when a change folder's brief or plan lacks a status line near its top."""
    if not is_change_doc(path):
        return None
    try:
        head = "\n".join((root / path).read_text(encoding="utf-8").splitlines()[:STATUS_SCAN_LINES])
    except OSError:
        return None
    if STATUS_LINE.search(head):
        return None
    return (
        f"{path} has no status line. Add one near the top, e.g. "
        "`> **Status:** phase 1 of 2 in review (merge request 42); phase 2 next.` "
        "A change folder without a status reads as unfinished work to the next agent."
    )


def main() -> int:
    payload = read_payload()
    root = project_root(payload)
    config = load_config(root)
    if not config:
        return 0

    path = edited_path(payload, root)
    if path is None or not (root / path).is_file():
        return 0

    messages = []

    format_rule = first_match(path, config.get("formatOnEdit", []))
    if format_rule:
        messages.append(format_file(root, path, format_rule))

    paired_rule = first_match(path, config.get("pairedFiles", []))
    if paired_rule and paired_rule.get("reminder"):
        messages.append(paired_rule["reminder"])

    messages += pattern_messages(path, added_text(payload), config.get("patterns", []))
    messages.append(missing_status(root, path))

    messages = [message for message in messages if message]
    if messages:
        emit_context("PostToolUse", "\n\n".join(messages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
