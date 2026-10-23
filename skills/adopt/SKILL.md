---
name: adopt
description: Opens the kitchen in a new repository — writes AGENTS.md, CLAUDE.md, .claude/agent-workflow.json and docs/changes/, filled in from the real codebase and a stack pack, never from guesses.
argument-hint: "[stack pack: flutter, or leave empty to detect]"
disable-model-invocation: true
---

# Adopt

Give a repository the agent setup, written from what the code actually is.
The kit's files are at `${CLAUDE_PLUGIN_ROOT}/template/` and
`${CLAUDE_PLUGIN_ROOT}/stacks/`.

## Input

<stack>$ARGUMENTS</stack>

## 0. Check what's there

- Not a git repository: stop and say so.
- `AGENTS.md` or `CLAUDE.md` already exists: don't overwrite. Offer `/inspect` instead, or merging the template's missing sections into the existing files.

## 1. Pick the stack pack

Use the argument if given. Otherwise detect from marker files:

| Marker | Stack |
| ------ | ----- |
| `pubspec.yaml` | flutter |
| `go.mod` | go |
| `build.gradle.kts`, `build.gradle` | kotlin |
| `package.json` | typescript |
| `Package.swift`, `*.xcodeproj` | swift |
| `pyproject.toml`, `requirements.txt` | python |
| `build.sbt` | scala |

If `stacks/<stack>/` exists in the kit, use it. If not, start from an empty
`agent-workflow.json` and offer to draft a pack for that stack at the end
(see `stacks/README.md` in the kit). A repo with several stacks gets the
primary one; the others become nested `CLAUDE.md` files.

## 2. Learn the repo

Dispatch the **codebase-explorer** agent: "Survey this repository for an
AGENTS.md. Return: what the product does (from README and code), the top-level
directories with one-line purposes, the exact install / format / lint / test /
codegen commands (from CI, Makefile, package scripts, the stack pack),
architecture layers and state management, generated-file patterns, git-ignored
files the build needs, and existing docs worth linking. Cite file:line."

## 3. Write the files

1. **`AGENTS.md`** from `template/AGENTS.md`, merged with the pack's `AGENTS.snippet.md`. Fill every section with facts the explorer cited. Where a fact is unknown, write `TODO(owner): <question>` instead of a plausible guess. A wrong rule is worse than a missing one.
2. **`CLAUDE.md`** from `template/CLAUDE.md`.
3. **`.claude/agent-workflow.json`** from the pack, keeping only globs that match files in this repo.
4. **`.claude/settings.json`**: merge in the kit's marketplace and plugin, keeping existing keys:

   ```json
   {
     "extraKnownMarketplaces": {
       "agent-workflow-kit": { "source": { "source": "github", "repo": "MaTeS72/agent-workflow-kit" } }
     },
     "enabledPlugins": { "agent-workflow-kit@agent-workflow-kit": true }
   }
   ```

5. **`docs/changes/README.md`** from the template, and `docs/changes/.tasting/` appended to `.gitignore`. If the repo already keeps plans elsewhere (`docs/plan/`, `docs/brainstorm/`), list them for the user; moving live ones into change folders is their call.
6. **Nested `CLAUDE.md` files** only for directories with rules the explorer found evidence for. Suggest the rest; don't create empty ones.

## 4. Verify

1. Run each command in the new Key commands table that finishes quickly (format check, lint). Ask before starting a long test suite. Fix the table, not the repo, when a command is wrong.
2. Run `/inspect` on the result and report the grade.

## 5. Hand over

List the files written, every `TODO(owner)` question, and the inspection grade.
Remind the user that collaborators run
`claude plugin install agent-workflow-kit@agent-workflow-kit --scope project`
once after trusting the folder. Commit nothing.
