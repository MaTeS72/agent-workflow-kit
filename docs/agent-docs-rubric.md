# Agent docs rubric

How `/inspect` grades a repository's instructions for AI agents, A to D like a
restaurant hygiene inspection: `AGENTS.md`, `CLAUDE.md` (root and nested),
project skills, and the hooks that back them. No public standard grades these files, so this rubric is built from
two sources and says which one each criterion comes from:

- **Docs** — Anthropic's Claude Code documentation on memory files, skills and hooks.
- **Production** — what building Meally with AI agents taught, much of it the hard way. Meally is a Flutter app shipping on iOS, Android and the web (see [the worked example](../examples/meally/README.md)).

## Scoring

Ten criteria, 100 points. Each criterion gets a level from 0 to 4, and earns
`weight × level ÷ 4` points. Every level cites evidence as `path:line`.

| Level | Meaning |
| ----- | ------- |
| **4** | Meets the criterion fully. |
| **3** | One minor gap. |
| **2** | The practice is in place, with clear gaps. |
| **1** | The practice exists on paper only. |
| **0** | Absent. |

| Grade | Score | Meaning |
| ----- | ----- | ------- |
| **A** | 90–100 | Agent-ready. A new agent can work safely from a cold start. |
| **B** | 75–89 | Solid. Fix the listed gaps before rolling out to more repos. |
| **C** | 60–74 | Agents work, but drift and silent rule-breaking have started. |
| **D** | < 60 | Agents are guessing. Run `/adopt` and rebuild from the template. |

Run `python3 scripts/agent_docs_check.py <repo>` first: it settles the
mechanical parts of criteria 1 and 5–8, so the judgment calls start from facts.

## Criteria

### 1. One source of truth — 5 points

`AGENTS.md` holds the project rules every agent reads (Cursor and Codex read it
natively). `CLAUDE.md` starts with `@AGENTS.md` and adds only Claude Code
tooling: plugins, hooks, project skills. No rule appears in both. *(Docs)*

Deduct for: a rule or workflow stated in both files; CLAUDE.md not importing AGENTS.md.

### 2. Exact commands — 10 points

A "Key commands" table gives copy-pasteable install, format, lint, test and
code-generation commands, including version-manager prefixes (`fvm`, `nvm`),
and they match what CI runs. *(Docs)*

Deduct for: paraphrased commands ("run the tests"); a missing format or lint command; commands that differ from CI.

### 3. A map of the codebase — 10 points

The stack with versions, a directory tree with one-line purposes, the layers
and their dependency direction, and the state-management pattern. Review
agents read exactly these to judge a change. *(Production)*

Deduct for: any of the four missing or only implied; known exceptions to the layering left unstated.

### 4. Few rules, each with a reason — 15 points

At most about ten absolute rules, each a directive ("Never…", "Always…"), each
carrying the reason or incident behind it, and none that a formatter or linter
already enforces. A rule without a reason gets argued with; a style rule wastes
the instruction budget. *(Docs, Production)*

Deduct for: rules without reasons; hedged wording ("try to", "where possible", "ideally"); formatter territory.

### 5. Rules that can be checked are enforced — 15 points

Every rule a machine can check has a hook or a CI job, and the hook's message
reaches the model. On `PreToolUse`, exit 2 blocks and shows stderr to Claude.
On `PostToolUse`, plain stdout on exit 0 goes only to the debug log; a reminder
must use `additionalContext` JSON or exit 2. Every plugin, hook or script the
docs mention is actually configured. Prose asks; hooks enforce. *(Docs, Production)*

Deduct for: checkable rules left to prose; hook output that never reaches Claude; tooling the docs claim but nobody installed.

### 6. Progressive disclosure — 10 points

The always-loaded root (AGENTS.md plus CLAUDE.md, imports included) stays within
about 200 lines and holds only what every session needs. Deep dives are linked
with "read when…" triggers; directory rules sit in nested `CLAUDE.md` files of
at most about 50 lines; large subsystems get a project skill. *(Docs)*

Deduct for: a root over budget; backlog, changelog or metrics in the root; nested files over budget.

### 7. Accurate — 15 points

Every relative link resolves, every named file, command, plugin and script
exists, numbers are current, and no value is copied from code (colors, token
scales, schedules, limits). When a doc and the code disagree, the doc was fixed,
not footnoted elsewhere. *(Production)*

Deduct for: each stale fact, copied value or "this is stale" footnote. More than three caps the level at 2.

### 8. Clean as you go — 10 points

Work in progress has one home per change (a brief and a plan side by side), each
carries a `Status:` line, none describes work that has already shipped, and
review notes are git-ignored or deleted. *(Production)*

Deduct for: a brief or plan without a status; a status that contradicts `git log`; shipped work still in the tree; one change's documents scattered across folders with separate statuses.

### 9. A defined workflow — 5 points

The path for non-trivial work, the fast path for urgent fixes, the trivial-edit
exception, and who may commit, push or open merge requests. *(Production)*

Deduct for: any of the four missing.

### 10. Environment and safety — 5 points

The traps a fresh checkout hits (git-ignored files that must exist, slow or
flaky suites, deliberate oddities that look like bugs), and what an agent must
never touch: production data, deploys, secrets, force-pushes. MCP servers are
listed with what they can read, and their write tools are held by `ask` or
`deny` permission rules rather than by a sentence in a prompt. *(Docs, Production)*

Deduct for: missing traps; no boundary around production access the developer's credentials allow; MCP write tools left on allow.

## Report format

```markdown
# Agent docs audit — <repo> — <date>

**Score: <n>/100 (<grade>)**

| # | Criterion | Weight | Level | Points | Evidence |
| - | --------- | ------ | ----- | ------ | -------- |
| 1 | One source of truth | 5 | 3 | 3.75 | CLAUDE.md:5 repeats the workflow from AGENTS.md:146 |

## Strengths to keep

- <what works, with evidence>

## Fixes, ranked by points recovered per minute

1. <fix> — +<n> points — <files>
```
