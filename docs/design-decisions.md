# Design decisions

Why the kit is shaped the way it is. Where a decision came from a Claude Code
fact or a mistake made in production, it names the evidence.

## 1. AGENTS.md is the source of truth; CLAUDE.md imports it

Cursor and Codex read `AGENTS.md` natively; Claude Code reads `CLAUDE.md` and
follows `@` imports. One file of rules plus a thin Claude-only layer means no
rule can drift between tools. **Evidence:** Meally's CLAUDE.md repeated its
workflow section, the one place the two files could disagree.

## 2. Each step hands off through a file

Every step reads its input from a file and writes its output to one, so the
context can be cleared between steps without losing anything. It also makes the
work reviewable: the brief and the plan are documents a person can read and
correct before any code exists.

## 3. One folder per change, deleted when it ships

A change's brief and plan sit in one folder with one status line, and the
merge request that ships the last phase deletes the folder. **Evidence:**
Meally kept brainstorms and plans in two folders, each with its own status
note. For the sale-campaign feature they read "Live brainstorm" and "Live plan:
no phase has shipped yet", and the second was wrong: two of its pull requests
had already merged. On 2026-09-02 the repo carried 88 leftover plans,
brainstorms and review reports describing work that had merged months earlier.

## 4. A rule a machine can check becomes a hook

Prose asks; hooks enforce. **Evidence:** Meally's AGENTS.md told agents to keep
each plan's status current, and five of six plans and brainstorms in the tree
didn't. The kit's post-edit hook flags a missing `Status:` line the moment a
brief or plan is written, and CI fails on it. Code rules work the same way: a
`patterns` rule flags a new `Widget _buildX()` helper as it's written, checking
only the added text so existing code doesn't cause noise.

## 5. A hook's message must reach the model

On `PostToolUse`, plain stdout from a hook that exits 0 goes to the debug log,
not to Claude ([hooks docs](https://code.claude.com/docs/en/hooks)).
**Evidence:** Meally's ARB reminder hook printed to stdout for five months; the
reminder never reached the model. The kit sends reminders as
`additionalContext`, blocks with exit 2 and stderr, and tests both paths.

## 6. Hooks read data; stacks are data

Meally's original hooks had its paths and file types written into the scripts,
so they were useless in any other repository. What a hook needs to know about a
stack (which files are generated, how to format, what changes together) fits in
a few lines of JSON. One tested hook implementation now serves every stack, and
a new stack costs a JSON file and a Markdown snippet. **Evidence:** the same
test suite runs Flutter-shaped and Go-shaped configs.

## 7. No background work in hooks

Meally has a hook that starts `build_runner` in the background after each edit
to a Freezed source. Two quick edits start two concurrent runs, which delete
and regenerate the same files at the same time, so generated code vanishes
mid-session. Hooks in the kit finish synchronously; `/cook` regenerates code
once per task.

## 8. Five tasters in parallel, notes to files

Each reviewer has one narrow brief, all five run at once, and each writes full
notes to `docs/changes/.tasting/` while returning at most 12 lines. The main
context pays about 60 lines for a full tasting and opens a note only to fix
what it describes.

## 9. A reviewer just for user data

Data bugs are the ones users don't forgive, so one taster checks nothing else.
**Evidence:** three Meally incidents, each now a check in
`data-safety-reviewer`. An offline query that came back empty emptied a recipe
book. One malformed cached entry failed a whole restore, which then overwrote
the user's data. A guard that survived sign-out showed the next account an
empty book.

## 10. Blockers are confirmed before anyone acts

The main context opens the code behind every blocker before presenting it, and
drops what doesn't hold. A reviewer that cries wolf trains people to skip
tasting.

## 11. Labels that say what to do

**blocker**, **should-fix** and **nit** tell the reader what happens next.
Severity words such as "high" or "important" leave that to interpretation.

## 12. A model per job

`haiku` runs commands and greps (`premerge-checker`); `sonnet` reads and judges
code (tests, docs drift, exploration); `inherit` takes the calls where a miss is
expensive (project rules, data safety). Cost follows the stakes.

## 13. Questions in one round

`/prep` collects every decision only the user can make, strikes the ones the
code already answers, and asks the rest in a single round of at most four
multiple-choice questions, the choice of approach included, recommendation
first. The user answers in one
sitting instead of a slow back-and-forth; a second round happens only when an
answer opens something new.

## 14. One phase, one merge request

Recipes split work into phases that each merge and ship alone, and `/cook`
cooks one per run. Small merge requests get real reviews, and a bad phase
reverts cleanly. **Evidence:** Meally's larger features shipped as "PR A /
PR B" pairs that were planned that way up front.

## 15. Humans own the irreversible steps

Commit, push and merge request each need a yes in the current session.
`/cook`, `/rush` and `/adopt` set `disable-model-invocation`, so Claude can't
start them on its own, and `ask` rules in the template's settings hold
`git commit` and `git push` behind a prompt. **Evidence:** "Never commit without
explicit permission" is an absolute rule in Meally.

## 16. Bounded loops

Three attempts at a failing check, then the user gets the error and the fixes
already attempted. An agent that retries forever burns time and hides the
problem.

## 17. Every recipe covers edge states and data

`/recipe` requires acceptance criteria for the empty, loading, error, offline,
permission-denied and first-run states of each user-facing flow, and a
data-safety section that may say "none" but may not be missing.
**Evidence:** Meally's owner made it a standing rule to design and verify the
zero-data and edge states of every UI change, not only the happy path.

## 18. Kitchen names

Meally is a recipe app, and a professional kitchen maps onto this workflow
step for step: mise en place, recipe, cooking, tasting, rush orders, clean as
you go, inspection. The names are easy to remember, and every command still
carries a plain description of what it does.

## 19. The rubric grades in levels, calibrated on a real repo

The first draft scored each criterion full, half or zero. Run against Meally,
whose setup is genuinely good, it produced a D: partial credit at half weight
punished one gap as hard as five. Levels from 0 to 4 grade Meally at 60 (C),
which matches what the inspection found: strong structure with drift setting
in. The checker does the mechanical half, so two inspectors can't disagree
about facts.

## 20. Nothing is deleted before it's committed

The change folder is committed with a change's first phase and removed inside
the approved commit for its last. A user who chooses "leave it uncommitted"
loses nothing. **Evidence:** an independent review of this kit found that the
first draft of `/cook` deleted the folder before asking, the kind of bug the
data-safety reviewer exists to catch.

## 21. MCP: reads allowed, writes asked, destructive tools denied

MCP servers give agents the code host, the database and the crash reporter,
which is where most of their leverage is. Permission rules in the repo's
settings, not sentences in a prompt, decide what they may change. See
[mcp.md](mcp.md).

## 22. Mirrored logic gets a reminder on every copy

When the same logic lives in several languages, editing any copy reminds Claude
of the others, and one script proves they still agree. **Evidence:** Meally's
recipe parsing exists in Dart, TypeScript and Swift (import naming in Kotlin
too), and `scripts/import_check/check.sh` replays a frozen corpus through all
three parsers.

## 23. The prompts are tested too

Hooks and the checker have unit tests, but skills and agents are prompts, and a
prompt nobody measured is a hypothesis. A model release can change how one
behaves overnight. The [eval suite](../evals/README.md) sends realistic
requests into fixture repositories and grades the outcome, using free regex,
file and tool checks wherever possible and a judge model only where meaning
matters. Every case also runs without the plugin, so the score says what the
kit adds rather than what Claude would have done anyway.

## 24. In CI, agents advise and scripts gate

The free checker can block a merge: broken links and change folders without a
status are facts. The headless `/taste` posts its report and flags blockers,
but stays advisory until a team has seen enough of its findings to trust them
as a gate. Every unattended run has a budget ceiling and prints what it cost.
