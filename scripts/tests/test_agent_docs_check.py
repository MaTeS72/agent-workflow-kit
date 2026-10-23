"""Tests for scripts/agent_docs_check.py.

Run: python3 -m unittest discover -s scripts/tests -v
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "agent_docs_check.py"


class Repo:
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def write(self, relative: str, content: str = "") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def check(self, *args: str):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.root), "--json", *args],
            capture_output=True,
            text=True,
        )
        return result.returncode, json.loads(result.stdout)

    def checks(self, *args: str) -> set[tuple[str, str]]:
        return {(f["check"], f["path"]) for f in self.check(*args)[1]}

    def cleanup(self):
        self._tmp.cleanup()


class AgentDocsCheckTest(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.repo.write("AGENTS.md", "# Agents\n")
        self.repo.write("CLAUDE.md", "@AGENTS.md\n")

    def tearDown(self):
        self.repo.cleanup()

    def test_clean_repo_has_no_findings(self):
        self.assertEqual(self.repo.check("--strict"), (0, []))

    def test_broken_link_is_an_error_and_fails_strict(self):
        self.repo.write("AGENTS.md", "See [arch](docs/architecture.md).\n")
        code, findings = self.repo.check("--strict")
        self.assertEqual(code, 1)
        self.assertEqual(findings[0]["check"], "broken-link")

    def test_anchors_line_suffixes_urls_and_code_fences_are_not_broken_links(self):
        self.repo.write("docs/architecture.md", "# Architecture\n")
        self.repo.write("lib/main.dart")
        self.repo.write(
            "AGENTS.md",
            "[a](docs/architecture.md#layers) [b](lib/main.dart:42) [c](https://example.com) [d](#top)\n"
            "```markdown\n[e](not/a/real/file.md)\n```\n",
        )
        self.assertEqual(self.repo.check("--strict"), (0, []))

    def test_nested_links_resolve_from_their_own_folder(self):
        self.repo.write("docs/testing.md", "# Testing\n")
        self.repo.write("test/CLAUDE.md", "Read [testing](../docs/testing.md).\n")
        self.assertEqual(self.repo.checks(), set())

    def test_plugin_root_variables_are_not_broken_links(self):
        self.repo.write("AGENTS.md", "Read [the contract](${CLAUDE_PLUGIN_ROOT}/skills/taste/references/tasting-notes.md).\n")
        self.assertEqual(self.repo.checks(), set())

    def test_root_budget_counts_imported_files(self):
        self.repo.write("AGENTS.md", "line\n" * 150)
        self.repo.write("CLAUDE.md", "@AGENTS.md\n@docs/extra.md\n")
        self.repo.write("docs/extra.md", "line\n" * 60)
        self.assertIn(("root-budget", "AGENTS.md + CLAUDE.md"), self.repo.checks())

    def test_claude_md_without_import_is_flagged(self):
        self.repo.write("CLAUDE.md", "# Claude\n")
        self.assertIn(("import", "CLAUDE.md"), self.repo.checks())

    def test_nested_budget(self):
        self.repo.write("lib/bloc/CLAUDE.md", "rule\n" * 51)
        self.assertIn(("nested-budget", "lib/bloc/CLAUDE.md"), self.repo.checks())

    def test_change_folders_need_a_brief_or_plan_with_a_status(self):
        self.repo.write("docs/changes/README.md", "# Changes\n")
        self.repo.write("docs/changes/2026-01-01-a/brief.md", "# a\n\n> **Status:** prepped\n")
        self.repo.write("docs/changes/2026-01-01-a/plan.md", "# feat: a\n")
        self.repo.write("docs/changes/2026-01-02-b/notes.md", "# loose notes\n")
        self.repo.write("docs/changes/.tasting/rules-reviewer.md", "# notes\n")
        self.assertEqual(
            self.repo.checks(),
            {("status-line", "docs/changes/2026-01-01-a/plan.md"), ("change-folder", "docs/changes/2026-01-02-b")},
        )

    def test_legacy_plan_and_brainstorm_folders_are_still_checked(self):
        self.repo.write("docs/plan/2026-01-01-feat-a-plan.md", "# feat: a\n")
        self.repo.write("docs/plan/2026-01-02-feat-b-plan.md", "# feat: b\n\n> **Status:** live\n")
        self.repo.write("docs/brainstorm/README.md", "# Brainstorms\n")
        self.assertEqual(self.repo.checks(), {("status-line", "docs/plan/2026-01-01-feat-a-plan.md")})

    def test_post_tool_use_hooks_that_only_print_are_flagged(self):
        settings = {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Edit",
                        "hooks": [
                            {"type": "command", "command": ".claude/hooks/stdout.sh"},
                            {"type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/context.py"},
                            {"type": "command", "command": ".claude/hooks/exit2.sh"},
                            {"type": "command", "command": ".claude/hooks/missing.sh"},
                        ],
                    }
                ]
            }
        }
        self.repo.write(".claude/settings.json", json.dumps(settings))
        self.repo.write(".claude/hooks/stdout.sh", 'echo "remember the ARB files"\nexit 0\n')
        self.repo.write(".claude/hooks/context.py", 'print(json.dumps({"additionalContext": "x"}))\n')
        self.repo.write(".claude/hooks/exit2.sh", 'echo "remember" >&2\nexit 2\n')
        self.assertEqual(
            self.repo.checks(),
            {("hook-visibility", ".claude/hooks/stdout.sh"), ("hook-missing", ".claude/hooks/missing.sh")},
        )

    def test_excluded_prefixes_are_skipped(self):
        self.repo.write("template/CLAUDE.md", "[x](nowhere.md)\n")
        self.assertIn(("broken-link", "template/CLAUDE.md"), self.repo.checks())
        self.assertEqual(self.repo.checks("--exclude", "template"), set())


if __name__ == "__main__":
    unittest.main()
