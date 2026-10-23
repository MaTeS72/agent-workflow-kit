---
name: recipe
description: Writes the recipe for a prepped change — tasks with their files and tests, the edge states, the data risks, and phases sized to one merge request each — as plan.md next to the brief, ready for /cook. Use when the user says "write the recipe", "turn this into a plan", "break this into tasks", or hands over a brief.
argument-hint: change folder, or the change to plan
---

# Recipe

A recipe someone else can cook from a cold start: every step, every
ingredient, and no question left that the recipe should have answered.

## Input

<change>$ARGUMENTS</change>

Open changes:

```!
ls -1d "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"/docs/changes/*/ 2>/dev/null || echo "(no change folders yet)"
```

## 1. Find the change

- **A folder was given:** read its `brief.md`.
- **Nothing given, and exactly one change folder has no `plan.md`:** use it and say so.
- **Several candidates:** ask which with **AskUserQuestion**.
- **No brief and a fuzzy request:** recommend `/prep` and stop.
- **No brief but a precise request:** create the change folder and write only `plan.md`.

## 2. Read only what the recipe touches

1. AGENTS.md, then the `CLAUDE.md` of every directory the change touches.
2. Grep and Glob in those areas only. For each pattern the recipe reuses, record one `file:line` example.
3. The deep-dive docs AGENTS.md points to for this area.
4. **Risk check.** When the change touches money, authentication, personal data, stored or synced data, or an external API, read the current official docs for what it touches and cite them in the recipe. Say in one line whether you did and why.

## 3. Shape it

- **Title:** conventional-commit form, e.g. `feat: export transactions as CSV`.
- **Phases:** one phase unless more than one layer changes *and* the diff will pass ~400 lines, a refactor is mixed with a feature, or a one-way step is involved (migration, data backfill, public API change). Each phase merges and ships on its own, in order.
- **Edge states:** for every user-facing flow, an acceptance criterion for each of the six edge states: empty, loading, error, offline, permission denied, first run. Mark one "not applicable" only with a reason.
- **Data safety:** every stored, cached or synced shape the change alters and how existing data still loads; every destructive write and its guard; what must reset on sign-out. "None" is a fine answer; a missing section is not.
- **Docs:** the durable docs this change makes stale. Updating them is a task.

## 4. Write plan.md

Write `<change folder>/plan.md` from the [plan template](references/plan.md).
Every task names its files and the tests that prove it. Then set the brief's
`Status:` line to `see plan.md`, so the change has one status, kept in one place.

## 5. Check before you hand it over

- [ ] Every acceptance criterion is observable: a test, a command, a screen state.
- [ ] Every task lists files and tests.
- [ ] Every reused pattern has a `file:line` example.
- [ ] The data-safety section is answered.
- [ ] Each phase can ship alone and leaves the product releasable.
- [ ] No task exists for a hypothetical need.

## 6. Next

Print one line and stop:

```text
Next: /clear, then /cook docs/changes/<folder>
```

## Rules

- No code in this step.
- Decisions in the brief are settled. Raise a real blocker; don't quietly redesign.
