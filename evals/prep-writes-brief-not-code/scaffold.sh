#!/usr/bin/env bash
# The same small recipe-book library, with no change folders yet.
set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name "Eval"
cat > AGENTS.md <<'EOF'
# AGENTS.md — recipe-book

A small Python library behind a recipe app: it loads and saves a user's recipe
book as JSON on the device.

## Key commands

| Task | Command |
| ---- | ------- |
| Run tests | `python3 -m unittest discover -s tests` |

## Absolute rules

1. **Never lose a user's recipes.** The book on the device is the only copy for offline users.
2. **New logic ships with tests.**
EOF
cat > storage.py <<'EOF'
"""Load and save the recipe book as JSON."""

import json
from pathlib import Path


def load_book(path: Path) -> dict:
    """The saved book, or an empty one on first run."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_book(path: Path, book: dict) -> None:
    path.write_text(json.dumps(book, ensure_ascii=False, indent=2), encoding="utf-8")
EOF
git add -A
git commit -q -m "feat: recipe book storage"
