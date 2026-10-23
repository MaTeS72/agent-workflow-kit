"""Shared helpers for the kit's hooks.

Hooks read the tool call from stdin, find the project's
`.claude/agent-workflow.json`, and act on the file being edited. Every rule is
data in that file, so the same hooks work for Flutter, Go, Kotlin or any other
stack. A project without the file gets no behaviour at all.

Standard library only: hooks run on every edit and must not need a venv.
"""

from __future__ import annotations

import json
import os
import re
import sys
from functools import lru_cache
from pathlib import Path

CONFIG_PATH = Path(".claude") / "agent-workflow.json"


def read_payload() -> dict:
    """Return the hook payload Claude Code sends on stdin, or {} if unreadable."""
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def project_root(payload: dict) -> Path:
    """The project directory: CLAUDE_PROJECT_DIR, else the payload's cwd."""
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    return Path(root).resolve()


def load_config(root: Path) -> dict | None:
    """Load the project's workflow config. None means "no rules, do nothing"."""
    path = root / CONFIG_PATH
    if not path.is_file():
        return None
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        # A broken config must never block editing; say so once and move on.
        print(f"agent-workflow: ignoring unreadable {CONFIG_PATH}: {error}", file=sys.stderr)
        return None
    return config if isinstance(config, dict) else None


def edited_path(payload: dict, root: Path) -> str | None:
    """The edited file as a POSIX path relative to the project root.

    None when the tool call has no file, or the file is outside the project.
    """
    tool_input = payload.get("tool_input") or {}
    raw = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = root / path
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return None


@lru_cache(maxsize=256)
def _glob_regex(pattern: str) -> re.Pattern[str]:
    """Translate a gitignore-style glob into a regex.

    `**/` matches zero or more directories, `**` matches anything, `*` and `?`
    never cross a `/`. Patterns are anchored at the project root.
    """
    out = []
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def matches(path: str, pattern: str) -> bool:
    """True when the root-relative POSIX `path` matches the glob `pattern`."""
    return _glob_regex(pattern).match(path) is not None


def first_match(path: str, rules: list, key: str = "glob") -> dict | None:
    """The first rule whose glob matches `path`, skipping malformed entries."""
    for rule in rules or []:
        if isinstance(rule, dict) and isinstance(rule.get(key), str) and matches(path, rule[key]):
            return rule
    return None


def emit_context(event: str, message: str) -> None:
    """Hand `message` to Claude as additional context for this event.

    Plain stdout from a PostToolUse hook that exits 0 goes to the debug log,
    never to the model, so reminders must travel in `additionalContext`.
    """
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": message}}))
