#!/usr/bin/env python3
"""PreToolUse hook: refuse edits to protected files.

Rules live in `.claude/agent-workflow.json` under `protected`:

    {"glob": "**/*.g.dart", "reason": "Generated. Edit the source, then run build_runner."}
    {"glob": "db/migrations/**", "reason": "Applied migrations are immutable.", "allowCreate": true}

`allowCreate` permits writing a new file that matches the glob (a new
migration) while still refusing changes to existing ones.

Exit 2 blocks the tool call and shows stderr to Claude, so the reason is
written as an instruction to the model.
"""

from __future__ import annotations

import sys

from workflow_config import edited_path, first_match, load_config, project_root, read_payload


def main() -> int:
    payload = read_payload()
    root = project_root(payload)
    config = load_config(root)
    if not config:
        return 0

    path = edited_path(payload, root)
    if path is None:
        return 0

    rule = first_match(path, config.get("protected", []))
    if rule is None:
        return 0
    if rule.get("allowCreate") and not (root / path).exists():
        return 0

    reason = rule.get("reason") or "This file is protected in .claude/agent-workflow.json."
    print(f"Blocked: {path} is protected (matches `{rule['glob']}`). {reason}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
