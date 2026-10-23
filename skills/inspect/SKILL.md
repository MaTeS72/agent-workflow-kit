---
name: inspect
description: The kitchen inspection for agent docs — grades AGENTS.md, CLAUDE.md files, project skills, hooks and change folders against the 100-point rubric, A to D like a restaurant hygiene grade, with evidence for every point and fixes ranked by points recovered. Use when the user says "inspect", "grade our CLAUDE.md", "audit AGENTS.md", or "are our agent docs any good".
argument-hint: "[repo path, default: current]"
---

# Inspect

A health inspector doesn't take the chef's word for it. Grade the repo with the
rubric at `${CLAUDE_PLUGIN_ROOT}/docs/agent-docs-rubric.md`: facts first,
judgment second, and evidence for every point.

## Input

<repo>$ARGUMENTS</repo>

Use the current directory when no path is given. **Report-only mode:** when the
input contains `report-only`, or nobody can answer questions (a CI job, a
headless run), skip step 4: write the report to
`docs/changes/.tasting/inspection.md`, make it your final message, and change
nothing else.

## 1. Collect the facts

Run the checker that ships with this plugin:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/agent_docs_check.py" <repo>
```

It reports broken links, line budgets, a CLAUDE.md that doesn't import
`@AGENTS.md`, briefs and plans without a `Status:` line, and PostToolUse hooks
whose output never reaches Claude. Treat its findings as settled facts.

Then gather what it can't check:

1. Read `AGENTS.md`, the root `CLAUDE.md` and every file it imports, and every nested `CLAUDE.md`.
2. Read `.claude/settings.json`, `.claude/agent-workflow.json` if present, every hook script, and the project skills' frontmatter.
3. Read the CI configuration (`.github/workflows/`, `.gitlab-ci.yml`) and the scripts it calls.
4. For every change folder (and any older `docs/plan/` or `docs/brainstorm/` files), compare its `Status:` line with `git log --oneline` for the work it describes. A folder whose work has merged is stale, whatever its status says.
5. For every plugin, tool or script the docs name, confirm it exists: on disk, in `.claude/settings.json`, or in `claude plugin list`.

## 2. Grade

Give each criterion a level from 0 to 4 exactly as the rubric defines it, citing
`path:line`. Between two levels, give the lower one and say what would earn the
higher.

Never reward length. A short file that is accurate beats a long one that is
partly stale.

## 3. Report

Use the rubric's report format: the score and letter grade, the criteria table,
the strengths to keep, then fixes ranked by points recovered per minute of
work, each naming the exact file and line.

## 4. Offer to fix

Ask with **AskUserQuestion**:

1. **Fix the top items now (Recommended)**
2. **Stop here** (the report stays in this conversation)

When fixing, follow the repo's own rules: correct the doc instead of adding a
warning elsewhere, delete shipped change folders instead of ticking them, and
never commit without permission. Run the checker again afterwards and report the
new grade.
