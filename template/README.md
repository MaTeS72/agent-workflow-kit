# Template

The files `/adopt` writes into a repository. To set a repository up by hand
instead:

1. Copy `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json` and `docs/` into the repository root.
2. Copy `stacks/<stack>/agent-workflow.json` to `.claude/agent-workflow.json` and delete the rules for files the repository doesn't have.
3. Merge `stacks/<stack>/AGENTS.snippet.md` into `AGENTS.md`, then replace every `<placeholder>` with a fact from the code. Write `TODO(owner): <question>` where you don't know; never guess.
4. Add `docs/changes/.tasting/` to `.gitignore`.
5. Run `/inspect` and fix what it reports.
6. Add the CI jobs: include `ci/agent-workflow.gitlab-ci.yml` on GitLab, or copy `.github/workflows/agent-taste.yml` and `agent-inspect.yml` on GitHub. Set `ANTHROPIC_API_KEY` as a masked secret.

Keep `AGENTS.md` and `CLAUDE.md` within about 200 lines together. Directory
rules go in a `CLAUDE.md` inside that directory; large subsystems get a project
skill in `.claude/skills/`.
