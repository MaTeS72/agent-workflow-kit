# AGENTS.md — agent-workflow-kit

> Source of truth for any AI agent working on this repository. The kit follows
> the same rules it asks other repositories to follow.

## Project overview

A Claude Code plugin plus a per-repository template. The plugin ships a
prep → recipe → cook workflow with tasting (skills), six subagents, and two
data-driven hooks. The template ships `AGENTS.md` / `CLAUDE.md` skeletons and
stack packs. The kit is stack-agnostic: everything about a language lives in
`stacks/`, never in skills, agents or hooks.

## Project structure

```text
agent-workflow-kit/
├── .claude-plugin/   # plugin.json + marketplace.json (the repo is its own marketplace)
├── skills/           # adopt, prep, recipe, cook, taste, rush, inspect
├── agents/           # codebase-explorer + five reviewers
├── hooks/            # hooks.json, pre_edit.py, post_edit.py, tests/
├── schema/           # JSON schema for a project's .claude/agent-workflow.json
├── stacks/           # stack packs (flutter/); data for hooks + prose for AGENTS.md
├── template/         # files /adopt copies into a repository, plus CI templates (ci/, .github/)
├── examples/meally/  # the production setup this kit was extracted from
├── scripts/          # agent_docs_check.py (+ tests): mechanical half of the rubric
├── evals/            # claude plugin eval cases with fixtures and a no-plugin baseline
└── docs/             # workflow, rubric, design decisions
```

## Key commands

| Task | Command |
| ---- | ------- |
| Hook tests | `python3 -m unittest discover -s hooks/tests` |
| Checker tests | `python3 -m unittest discover -s scripts/tests` |
| Agent docs check (this repo) | `python3 scripts/agent_docs_check.py . --exclude template --exclude examples --strict` |
| Markdown lint | `npx markdownlint-cli2 "**/*.md" --config .markdownlint-cli2.jsonc` |
| Plugin validation | `claude plugin validate .` |
| Behaviour evals (paid: ask before running) | `claude plugin eval . --tag smoke --ablation none --runs 1 --trust-plugin --scaffold --allow-tools Write Edit --max-cost-usd 2` |
| Try the plugin locally | `claude --plugin-dir /path/to/agent-workflow-kit` |

CI (`.github/workflows/ci.yml`) runs the free checks on every pull request. Evals run only on demand (`.github/workflows/evals.yml`), because every run is a model call.

## Writing skills and agents

- **Instructions, not hints.** Write "Run the tests", not "You might want to run the tests". An agent treats a hedge as optional.
- **Frontmatter:** `name` matches the folder (skills) or file (agents); `description` says what it does and lists the phrases that should trigger it.
- **Side effects are user-only.** A skill that commits, pushes or writes many files sets `disable-model-invocation: true`.
- **Model by job:** `haiku` for mechanical checks, `sonnet` for reviews and exploration, `inherit` for judgment calls about architecture.
- **Stop conditions.** Every loop has a limit (three attempts, then ask the user), and every phase ends by handing off to the next one through a file.
- **Keep the parent's context small.** Agents return summaries of at most about 40 lines; full reports go to files.
- **Claims about Claude Code behaviour cite the docs** at code.claude.com. Hook semantics in particular have surprised us before.

## Absolute rules

1. **Hooks use the Python standard library only.** They run on every edit, on every developer's machine; one missing package would break editing for everyone. *CI runs the tests on bare Python 3.9 and 3.13.*
2. **A hook never blocks because of its own problem.** A hook that fails closed stops all work. A missing or broken config means "do nothing", a failing formatter or a bad regex is reported, and only a matching `protected` rule blocks. *Tests cover each case.*
3. **Every hook behaviour has a test** in `hooks/tests/`, run against at least two unrelated stacks, because hooks run unattended. *CI.*
4. **No stack knowledge outside `stacks/`.** Otherwise every new language means editing skills. If a skill needs a command, it reads AGENTS.md. *Rules reviewer.*
5. **Skills never commit, push or open merge requests without asking.** Those steps are the user's. *`disable-model-invocation` on `/cook`, `/rush` and `/adopt`; the serving steps ask first.*

## Workflow

This repository uses its own plugin: run `claude --plugin-dir .`, then
`/prep` → `/recipe` → `/cook` for non-trivial changes (`/cook` tastes every
phase; `/taste` reviews any other diff). Edit trivial things directly.

## Environmental quirks

- **Python 3.9 is the floor**, because it's the `python3` that ships with macOS developer tools. No 3.10+ syntax at runtime (no `match`; `X | Y` only in annotations under `from __future__ import annotations`).
- **An old local `claude` CLI only checks manifests.** Validate with the latest one: `npx -y @anthropic-ai/claude-code@latest plugin validate .`.
- **`claude plugin validate .` shows two warnings by design:** this file's sibling `CLAUDE.md` (for working on the kit, not shipped as plugin context) and the missing directory icon.

## Docs hygiene

`README.md`, this file, `CONTRIBUTING.md` and `docs/*.md` are durable and change
with the behaviour they describe. Change folders in `docs/changes/` are
disposable: each brief and plan carries a `Status:` line, and the folder is
deleted when its work ships. When a doc and the code disagree, fix the doc in
the same commit.
