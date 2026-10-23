#!/usr/bin/env bash
# A weak agent setup: vague rules, no commands, a CLAUDE.md that doesn't import
# AGENTS.md, a broken link, and a shipped plan without a status line.
set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name "Eval"
cat > AGENTS.md <<'EOF'
# AGENTS.md

Recipe sync service. Be careful with data and try to write tests where possible.

See [the architecture notes](docs/architecture.md).
EOF
cat > CLAUDE.md <<'EOF'
# Claude notes

Use the workflow plugin for big changes.
EOF
mkdir -p docs/changes/2026-08-01-old-import
cat > docs/changes/2026-08-01-old-import/plan.md <<'EOF'
# feat: old import

- [x] Parse feeds
- [x] Store entries
EOF
git add -A
git commit -q -m "feat: old import"
