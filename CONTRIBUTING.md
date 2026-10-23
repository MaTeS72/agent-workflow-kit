# Contributing

Read [AGENTS.md](AGENTS.md) first; its rules apply to people too. Work on the
kit with the kit: `claude --plugin-dir .`, then `/prep` → `/recipe` →
`/cook`, which tastes every phase.

## Adding a skill

1. Create `skills/<name>/SKILL.md`. Frontmatter:

   ```yaml
   ---
   name: <name>                     # matches the folder
   description: <what it does>. Use when the user says "<phrase>", "<phrase>".
   argument-hint: <what to pass>
   disable-model-invocation: true   # only if it commits, pushes or writes many files
   ---
   ```

   Don't set `effort` on a skill: it would override the user's own session level.
2. Structure the body as: H1, one-paragraph purpose, `## Input` with `$ARGUMENTS` and an empty-input guard, numbered steps, a hand-off, rules.
3. Put templates and long reference material in `skills/<name>/references/` and link them; the skill body stays readable in one sitting.
4. Add the skill to the tables in `README.md` and, if it is a phase, to `docs/workflow.md`.
5. Add an eval case in `evals/<case>/` that proves the skill's main promise, and update the table in `evals/README.md`. Prefer free graders (regex, file, tool use); use a judge only where meaning matters.

## Adding an agent

1. Create `agents/<name>.md` with `name`, `description` (what it does and when to use it), `tools`, `model`, and `effort` when the model is fixed (`haiku`, `sonnet`).
2. Pick the model by job: `haiku` for mechanical checks, `sonnet` for reading and judging code, `inherit` for architectural judgment.
3. Reviewers end with "Follow the tasting-notes contract in your prompt"; the dispatching command appends [the contract](skills/taste/references/tasting-notes.md).
4. Add it to the reviewer tables in `skills/taste/SKILL.md` and `README.md`.

## Changing a hook

1. Keep to the standard library and keep the rule from AGENTS.md: a hook blocks only on a matching `protected` rule, never because of its own problem.
2. Add a test to `hooks/tests/test_hooks.py` for the new behaviour, with fixtures from at least two stacks.
3. If the config shape changes, update [the schema](schema/agent-workflow.schema.json), every `stacks/*/agent-workflow.json` and [stacks/README.md](stacks/README.md) in the same change.

## Adding a stack pack

Create `stacks/<stack>/agent-workflow.json` and `stacks/<stack>/AGENTS.snippet.md`
as described in [stacks/README.md](stacks/README.md). Only include rules a real
project on that stack has needed.

## Before opening a pull request

```bash
python3 -m unittest discover -s hooks/tests
python3 -m unittest discover -s scripts/tests
python3 scripts/agent_docs_check.py . --exclude template --exclude examples --strict
npx markdownlint-cli2 "**/*.md"
claude plugin validate .
```

If you changed a skill, an agent or a hook, also run the evals for its tag
(see [evals/README.md](evals/README.md)). They cost money, so say in the pull
request which tags you ran and what they cost.

Use [Conventional Commits](https://www.conventionalcommits.org/):
`feat: add go stack pack`, `fix(hooks): resolve relative notebook paths`. One
concern per pull request.
