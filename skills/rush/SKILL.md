---
name: rush
description: The rush order for an urgent bug — root cause, a failing test that proves it, the smallest fix, and still a tasting before anything is committed. Skips prep and recipe.
argument-hint: bug description, error message, or issue link
disable-model-invocation: true
---

# Rush

A rush order skips the queue, never the tasting. Speed comes from skipping
documents, not from skipping the test or the review.

## Input

<bug>$ARGUMENTS</bug>

If empty, ask: "What's broken? Paste the error, the steps, or the issue link."

## 1. Say what's broken

In one sentence: what the user sees, and where it most likely lives. Don't read
code yet. If a monitoring MCP server is connected (Crashlytics, Sentry), pull
the real stack trace first.

## 2. Find the cause

Dispatch the **codebase-explorer** agent: "Find the code responsible for this
symptom. Stay narrow; return file:line pointers and the most likely root
cause. Symptom: <bug>."

Read what it points at, then give the user the root cause in two or three
sentences with `path:line`.

Stop and recommend `/prep` when the fix needs a design decision, a migration, or
changes to more than about three files. That's no longer a rush order.

## 3. Branch

On the default branch, propose `fix/<short-symptom>` and create it once the user
agrees. Never fix on the default branch.

## 4. Prove it

Write a test that reproduces the bug and run it. It must fail for the reason you
diagnosed. If you can't reproduce it in a test, you don't understand it yet: say
so and ask the user before patching.

## 5. Fix

Make the smallest change that turns the test green: no refactoring, no renaming,
no drive-by fixes. Run format, lint and the tests near the change (commands
from AGENTS.md), three attempts at most, then ask.

## 6. Taste

Send **rules-reviewer**, **test-reviewer** and **premerge-checker** in one
message, scoped to the changed files, each with the full text of
`${CLAUDE_PLUGIN_ROOT}/skills/taste/references/tasting-notes.md`. Add
**data-safety-reviewer** when the bug involves stored, cached or synced data.
Confirm and fix blockers; list the rest for the user.

## 7. Serve

Follow `${CLAUDE_PLUGIN_ROOT}/skills/cook/references/serving.md`, skipping the
change-folder steps. The merge request description gives the root cause, the
regression test, and how to verify the fix in production.
