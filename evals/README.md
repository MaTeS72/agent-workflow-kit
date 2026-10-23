# Evals

Behaviour tests for the kit's skills, reviewers and hooks, run with
[`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals). Each case
builds a small fixture repository, sends Claude a request the way a person
would phrase it, and grades what happened. By default every case also runs
**without** the plugin, so the score shows what the kit adds, not just whether
Claude can do the task anyway.

| Case | Tags | What it proves | Graders |
| ---- | ---- | -------------- | ------- |
| `taste-flags-offline-wipe` | core, review | `/taste` catches a change that empties the local book when the server returns nothing, flags the untested function, and leaves the code alone | judge (data loss), regex, file check, tools used |
| `hook-blocks-generated-edit` | core, hooks, smoke | The protected-files hook stops a hand edit to `*.g.dart` and points at the source | file check, regex |
| `patterns-catch-build-helper` | hooks, smoke | The patterns hook turns a `Widget _buildX()` request into an extracted widget | file checks |
| `recipe-covers-edge-states-and-data` | core, planning | `/recipe` writes `plan.md` with all six edge states, a data-safety section and a `Status:` line, and no code | file checks, tools used |
| `prep-writes-brief-not-code` | planning | `/prep` turns settled decisions into a brief in a dated change folder, with a status, and no code | file list, tools used |
| `inspect-grades-agent-docs` | inspection | `/inspect` scores a weak setup out of 100 and names its concrete problems | judge, regex, tools used |
| `ignores-unrelated-request` | smoke, triggering | No skill fires on an unrelated question | tools used |

Only two graders call a judge model; everything else is a regex, a file check
or a tool-use check, which cost nothing. `/cook`, `/rush` and `/adopt` are
user-only commands, so the suite covers their building blocks (tasting, the
recipe, the hooks) rather than the commands themselves.

## Running it

Requires Claude Code 2.1.269 or later, and on Linux `bubblewrap` and `socat`
for the sandbox. The fixtures come from each case's `scaffold.sh`, so pass
`--scaffold`; the cases that edit files or run git need the tool grants.

**Every run is a real model call**, billed to your API key or counted against
your plan. Start with the smoke cases:

```bash
claude plugin eval . --tag smoke --ablation none --runs 1 \
  --trust-plugin --scaffold --allow-tools Write Edit \
  --model claude-sonnet-5-5 --max-cost-usd 2
```

The full suite, with the no-plugin baseline:

```bash
claude plugin eval . --trust-plugin --scaffold \
  --allow-tools Write Edit "Bash(git *)" "Bash(python3 *)" \
  --model claude-sonnet-5-5 --judge-model claude-haiku-5-5 \
  --threshold 0.8 --max-cost-usd 25
```

| Run | Agent runs | Judge calls | Rough list-price cost |
| --- | ---------- | ----------- | --------------------- |
| Smoke, one arm, one run | 3 | 0 | under $1 |
| Full suite, with baseline, 3 runs per arm | 42 | 36 (haiku) | roughly $5–20; `/taste` with five subagents is most of it |

The costs are estimates; `--max-cost-usd` is the hard limit. The
[evals workflow](../.github/workflows/evals.yml) runs the same commands on
demand from GitHub Actions and never on its own. Results land in
`evals/results/`, which is git-ignored.
