---
name: cook
description: Cooks the next phase of a recipe in docs/changes/ — one phase per run, one merge request per phase — with tests written alongside the code, a five-reviewer tasting, and a commit only after you approve it.
argument-hint: change folder
disable-model-invocation: true
---

# Cook

Turn the next uncooked phase of a recipe into a tasted, tested change.

## Input

<change>$ARGUMENTS</change>

Changes with a recipe:

```!
ls -1 "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"/docs/changes/*/plan.md 2>/dev/null || echo "(no recipes yet)"
```

## 1. Read the recipe

- **No argument and one recipe:** use it and say so.
- **No argument and several:** ask which with **AskUserQuestion**, one line each from its title and `Status:` line.
- **No recipes:** say "Nothing to cook yet: there is no plan.md in docs/changes/. Start with /prep or /recipe." and stop.

The phase to cook is the first one with unticked tasks. If an earlier phase is
cooked but its merge request hasn't reached the default branch yet (its commit
is missing from `git log origin/<default>`), say so and ask whether to wait or
to build this phase on top of the earlier branch.

Summarise the phase's tasks, files, tests and data risks, then ask:

1. **Start cooking (Recommended)**
2. **Let me read the recipe first**
3. **Change the scope**

## 2. Mise en place

1. On the default branch, propose `<type>/<slug>`, where the slug is the change folder's name without its date, and create it once the user agrees.
2. Read every file the phase names, their siblings, and the `CLAUDE.md` of each directory involved.
3. Take the format, format-check, lint, test and codegen commands from the "Key commands" table in AGENTS.md. Use no others; a missing one is a question for the user.

Don't explore the codebase again; the recipe already did. Grep for one example
only when a task names a pattern you haven't seen.

## 3. Cook each task

In recipe order:

1. **Write the code**, following the pattern the recipe cites.
2. **Write its tests in the same step:** the happy path, the failure paths, and whichever of the six edge states (empty, loading, error, offline, permission denied, first run) the recipe lists for it.
3. **Regenerate** once if the task changed sources of generated code. The hooks block hand edits to generated files.
4. **Check:** format, lint, then the tests nearest the change. On a failure, fix and rerun, three attempts at most. Then stop and show the user the error and each fix you attempted.
5. **Tick** the task in `plan.md`.

While cooking:

- The recipe is the scope. A missing piece that blocks you is a question for the user, not an improvisation.
- Act on every hook reminder (paired files, patterns) before you start the next task.
- Never weaken, skip or delete a test to make the suite pass.
- Never bypass hooks (`--no-verify`), and never silence a lint rule without a comment saying why.

## 4. Taste

Send the five tasters listed in `/taste` in one message, scoped to this phase's
changed files. Each prompt carries the file list, the recipe path and phase
(`docs/changes/<folder>/plan.md`, phase <n>), and the full text of
`${CLAUDE_PLUGIN_ROOT}/skills/taste/references/tasting-notes.md`. Then:

1. **Confirm** every blocker against the code; drop false alarms and say so.
2. **Fix** confirmed blockers and check again.
3. **Ask** about should-fix findings: fix them all, show the list, or leave them in the merge request description.
4. **Keep** the nits for the merge request description.

## 5. Serve

Follow the [serving steps](references/serving.md). They ask before anything is
committed, and they remove the change folder only inside the approved commit
for the last phase.
