---
name: prep
description: Mise en place for a change — settles what to build and why before any recipe or code, and writes the change's brief into a new change folder. Use when the user says "prep", "help me think about…", "what are our options for…", "is this a good idea", or describes a feature whose scope is still fuzzy.
argument-hint: idea, problem or feature to prep
---

# Prep

In a kitchen, mise en place means everything is decided, measured and within
reach before anyone turns on a burner. Here it means the user's decisions are
made and written down before anyone plans or codes. The output is a one-page
brief.

## Input

<idea>$ARGUMENTS</idea>

If the idea is empty, ask: "What do you want to prep? Describe the problem or
the feature you have in mind." Do not continue without it.

## 1. Decide whether prep is needed

When the request already says exactly what to build, which existing feature to
copy, and how to tell it works, say so and suggest `/recipe` directly.

## 2. Gather the facts

Dispatch the **codebase-explorer** agent: "Find the code, patterns and
AGENTS.md / CLAUDE.md rules related to: <idea>. Return file:line pointers."

Read AGENTS.md yourself for the core loop and the absolute rules. An idea that
breaks an absolute rule gets raised now, not at tasting.

## 3. Draft the approaches

Draft two or three approaches, recommended one first. Don't ask about them yet.

```markdown
### <Approach> (recommended | alternative)

<What it looks like in this codebase, in two sentences, naming the file it builds on.>

Costs: … · Risks: … · Pick it when: …
```

Cut any part that exists for a hypothetical future.

## 4. Ask once

Show the approaches, then list the decisions only the user can make:

- **Approach:** which of the drafts.
- **Done signal:** how the user will know it works.
- **Cut:** what is explicitly out.
- **Constraints:** platforms, deadline, money, privacy, stored data.
- **Edge states:** which of the six (empty, loading, error, offline, permission denied, first run) need designed behaviour.
- **Precedent:** an existing feature it should behave like.

Strike every decision the code or AGENTS.md already answers. Ask the rest in a
single **AskUserQuestion** call: at most four multiple-choice questions, the
approach among them, your recommendation first in each. Ask a second round only
when an answer raises a question you couldn't have foreseen.

## 5. Write the brief

Create `docs/changes/<YYYY-MM-DD>-<slug>/brief.md` from the
[brief template](references/brief.md). Keep it to one screen; the `Status:` line
is mandatory.

## 6. Next

Print one line and stop:

```text
Next: /clear, then /recipe docs/changes/<YYYY-MM-DD>-<slug>
```

## Rules

- No code and no plan in this step; it ends with decisions.
- Every decision carries its reason; a decision without one gets argued again in `/recipe`.
