# AGENTS.md — <Project name>

> Source of truth for every AI coding agent in this repo (Claude Code, Cursor,
> Codex, Copilot). Read this first; pull in the linked `docs/` files only when
> the task needs them.

## Project overview

<Two or three sentences: what the product does, who uses it, on which platforms.>

- **Core loop:** <the user journey that matters most>. When a trade-off comes up, protect this loop first.
- **Secondary features:** <what matters less, so agents don't over-invest there>.

## Tech stack

<Paste the "Tech stack" section from your stack pack (`stacks/<stack>/AGENTS.snippet.md`) and pin real versions.>

## Project structure

```text
<repo>/
├── AGENTS.md        # This file
├── CLAUDE.md        # Claude Code extras; imports this file
├── docs/            # Durable deep dives, plus changes/ for work in progress
└── <src>/           # <one line per top-level directory>
```

Directories with rules of their own carry a short `CLAUDE.md`: <list them>.

## Key commands

| Task | Command |
| ---- | ------- |
| Install dependencies | `<command>` |
| Format | `<command>` |
| Format check (reports, never rewrites) | `<command>` |
| Lint / static analysis | `<command>` |
| Run tests | `<command>` |
| Code generation | `<command, or delete the row>` |

CI runs `<the same commands | scripts/check.sh>` on every merge request.

## Architecture summary

<Five to eight headline rules: layers and dependency direction, state management,
how services are provided, offline/sync strategy, navigation. Link the deep dive.>

See [docs/architecture.md](docs/architecture.md) for the full picture.

## Conventions summary

<Paste "Conventions" from the stack pack, then add the project's own. Leave out
anything the formatter or linter already enforces.>

## Workflow

- **Non-trivial work:** `/prep` → `/recipe` → `/cook` (agent-workflow-kit). `/cook` has five reviewers taste every phase; `/taste` reviews any other diff on demand. Each step writes a file the next one reads, so clear the context between steps.
- **Urgent bugs:** `/rush` skips prep and recipe but keeps the regression test and the tasting.
- **Trivial work** (typo, one-line fix): edit directly.
- **Commits, pushes and merge requests** happen only after the user says so.

## Absolute rules

Each rule exists because breaking it cost something. Keep the reason next to it,
and say what enforces it.

1. **<Never/Always …>** — <why: the incident or cost>. *Enforced by <hook | CI job | review agent>.*
2. **Never commit, push or open a merge request without explicit permission.** Those are the owner's decisions; a pushed mistake reaches CI, reviewers and sometimes users. *Enforced by `ask` rules in `.claude/settings.json`.*
3. **Never add a dependency without asking.** Every package is an upgrade and supply-chain cost.
4. **One concern per change.** Unrelated refactors make reviews slow and reverts dangerous. *Rules reviewer.*
5. **Read before editing.** Verify APIs and surrounding patterns from source; a guessed API fails the build at best and misbehaves silently at worst.

## References

Read these on demand; none load by default.

- [docs/architecture.md](docs/architecture.md) — read when changing <layers, state, data flow>.
- [docs/testing.md](docs/testing.md) — read when adding tests.
- <docs/feature.md> — read whenever touching <the core feature>.

## Environmental quirks

<Traps a fresh checkout hits: git-ignored files that must exist, services that need
credentials, flaky or slow suites to exclude, settings that look wrong but are deliberate.>

## Docs hygiene

Markdown here is either **durable** or **disposable**.

- **Durable:** `AGENTS.md`, every `CLAUDE.md`, `README.md` files and `docs/*.md`. They describe the code as it is now and change in the same merge request as the behaviour they describe.
- **Disposable:** one folder per change in `docs/changes/` (`brief.md`, `plan.md`), plus review notes in `docs/changes/.tasting/` (git-ignored). Each brief and plan carries a `Status:` line near the top. Clean as you go: the merge request that ships a change's last phase deletes its folder.

Two rules for durable docs:

1. **Don't copy values that live in code** (colors, tokens, schedules, limits). Link to the source file.
2. **When a doc and the code disagree, the code is right.** Fix the doc in the same commit; never add a warning about it somewhere else.

## Keeping this file accurate

Update it in the same change when a top-level directory, a key command, the
stack or a major dependency changes, or when a mistake happens twice and earns
an absolute rule. Run `/inspect` before a release.
