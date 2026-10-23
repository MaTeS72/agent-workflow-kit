---
name: taste
description: Has five specialist reviewers taste a change in parallel — project rules, tests, data safety, docs drift and pre-merge checks — then confirms every blocker against the code before anyone acts on it. Use when the user says "taste", "review", "look over my changes", or "can this merge?".
argument-hint: "[report-only] [paths, optional]"
---

# Taste

Nothing leaves a kitchen untasted. Five tasters check the change at the same
time, each for one thing; you confirm what they report before anyone acts.

## Input

<paths>$ARGUMENTS</paths>

**Report-only mode.** When the input starts with `report-only`, or nobody can
answer questions (a CI job, a headless run), taste the remaining paths, stop
after step 3, change no files except the tasting notes, and end with the
[CI report](#ci-report) instead of asking anything.

## 1. Decide what to taste

- **Paths given:** those files.
- **On a feature branch:** the base is `git symbolic-ref --short refs/remotes/origin/HEAD` (fallback `origin/main`, `origin/master`, then a local `main` or `master`). Taste `git diff --name-only <base>...HEAD` plus uncommitted and staged files, without duplicates.
- **Default branch, no paths:** ask whether to taste specific paths or the whole project.

Say how many files and which areas.

## 2. Five tasters at once

First make sure the notes can't be committed: if
`git check-ignore -q docs/changes/.tasting/x` fails, append
`docs/changes/.tasting/` to `.gitignore` and say so.

Find the recipe, if there is one: a branch named `<type>/<slug>` belongs to the
change folder `docs/changes/<date>-<slug>/`, and the phase being built is the
first one with unticked tasks.

Then send one message with five agent calls. Each gets the file list, the
recipe path and phase if you found them, and the full text of the
[tasting-notes contract](references/tasting-notes.md).

| Agent | Tastes for |
| ----- | ---------- |
| **rules-reviewer** | Regressions, the rules in AGENTS.md and nested CLAUDE.md files, layering, complexity and scope the change doesn't need |
| **test-reviewer** | Untested logic, weak assertions, missing failure-path and edge-state tests |
| **data-safety-reviewer** | Anything that can lose, corrupt or leak user data: stored formats, offline sync, sign-out resets, destructive writes |
| **docs-drift-reviewer** | Durable docs the change made false; the change folder's status |
| **premerge-checker** | Format, lint and tests, debug leftovers, secrets, commit messages |

A project can add tasters, or replace this set, under a "Tasters" heading in
its AGENTS.md or CLAUDE.md. An agent that errors out doesn't stop the tasting:
say which one, use the others' notes, and offer to rerun it at the end.

## 3. Confirm, then report

Open the code behind every blocker and confirm it. Drop what doesn't hold up and
say you dropped it; a false alarm costs the user more than it saves. Merge
findings that several tasters reported.

Show the counts and the one-line findings, blockers first.

## 4. Fix what the user picks

Ask with **AskUserQuestion**:

1. **Fix the blockers (Recommended when there are any)**
2. **Fix blockers and should-fix findings**
3. **Show me everything**
4. **Stop here**

When fixing, read only the notes behind the findings being fixed, change only
files in scope, then run format, lint and tests from AGENTS.md. One attempt per
finding; if a check still fails, report what you tried and move on.

## 5. Clean up

Delete `docs/changes/.tasting/` unless the user wants to keep the notes.
Nothing is committed here.

## CI report

In report-only mode, write this Markdown to `docs/changes/.tasting/report.md`
and make it your final message too, so a pipeline can post it as a merge
request comment:

```markdown
### Tasting: <merge as is | merge after fixes | rethink the approach>

**<n> blockers · <n> should-fix · <n> nits** across <n> files

#### Blockers
- `path:line` — <problem> (<agent>). Fix: <one line>

#### Should-fix
- `path:line` — <problem> (<agent>)

<details><summary>Nits</summary>

- `path:line` — <one line>
</details>
```

List only confirmed findings. With no blockers, say so in the first line.
