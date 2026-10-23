# Worked example: Meally

Meally is a recipe app built with Flutter and Firebase, shipping on iOS,
Android and the web, with a Swift share extension, a Kotlin share activity and
TypeScript Cloud Functions. Its agent setup is where this kit came from.

This folder is Meally's agent layer **as it looks once Meally runs on the
kit**: corrected, extended, and checked line by line against the real
repository. The live repo still uses its older setup (plans in `docs/plan/`,
three hand-written hooks). Only the agent layer is here, so links into Meally's
code and docs don't resolve in this repository.

## What's in the folder

| File | Role |
| ---- | ---- |
| [`AGENTS.md`](AGENTS.md) | Source of truth for every agent: stack, map, exact commands, ten rules with reasons and enforcers, quirks, docs hygiene. 148 lines. |
| [`CLAUDE.md`](CLAUDE.md) | Imports AGENTS.md; adds only the plugin, hooks, tasters, MCP servers and skills. 44 lines. |
| [`.claude/agent-workflow.json`](.claude/agent-workflow.json) | Hook data: 7 protected globs, a formatter, 13 paired-file reminders (8 of them for logic mirrored across Dart, TypeScript, Swift and Kotlin), 4 code patterns. |
| [`.claude/settings.json`](.claude/settings.json) | Enables the kit; allows the safe commands and MCP reads; asks before commit, push and deploy; denies database writes and Remote Config publishes. |
| [`.mcp.json`](.mcp.json) | The Firebase MCP server, limited to Firestore, Crashlytics and Remote Config. |
| [`.claude/agents/import-quality-taster.md`](.claude/agents/import-quality-taster.md) | Meally's own taster: corpus replay, cross-language parity and the per-language quality gate. |
| [`functions/CLAUDE.md`](functions/CLAUDE.md) and five more directory files | Local rules, 14–41 lines each, loaded only when Claude works there. |
| [`.claude/skills/recipe-import-expert/`](.claude/skills/recipe-import-expert/SKILL.md) | A domain skill for the import pipeline, the product's most important feature. |

## The inspection: before

The live repository on 2026-10-22, graded with the
[rubric](../../docs/agent-docs-rubric.md). Mechanical findings come from
`scripts/agent_docs_check.py`; the rest were checked against the code by an
independent review.

| # | Criterion | Weight | Level | Points | Evidence |
| - | --------- | ------ | ----- | ------ | -------- |
| 1 | One source of truth | 5 | 3 | 3.75 | CLAUDE.md imports AGENTS.md, but repeats the workflow section (CLAUDE.md:7 and AGENTS.md:103). |
| 2 | Exact commands | 10 | 3 | 7.5 | Exact `fvm` commands and a local CI mirror script (AGENTS.md:63), but no format command. |
| 3 | Map of the codebase | 10 | 3 | 7.5 | Stack, tree and BLoC patterns are explicit; the layer direction is only implied, and `functions/`, the share extension and the share activity barely appear. |
| 4 | Rules with reasons | 15 | 2 | 7.5 | Ten directives (AGENTS.md:116–129), but no rule carries its own reason, and rule 6 says "Prefer". |
| 5 | Enforcement | 15 | 2 | 7.5 | The generated-file hook blocks correctly. Both PostToolUse hooks print to stdout on exit 0, which only reaches the debug log, so the ARB reminder never reached Claude. The docs promise `dart analyze` / `dart format` hooks from a plugin that isn't installed. The plan-status rule has no check. |
| 6 | Progressive disclosure | 10 | 3 | 7.5 | Good layering (five directory files, three skills, "read when" links), but the root is 230 lines including a backlog section. |
| 7 | Accurate | 15 | 2 | 7.5 | All 17 links resolve, but more than ten facts were stale, among them: the plugin's name and "installed" claim; the user numbers; `MealPlanSettingsBloc` listed as a plain Bloc (it's a HydratedBloc) and four persisted BLoCs missing; a stale footnote about the design-system README; token values copied into a skill; `AppLocalizations.of(context)!` (the getter is non-nullable); `untranslated.json` described as working (it isn't wired up); and a YAML bug that cut the import skill's description off at "#1", losing every trigger phrase. |
| 8 | Clean as you go | 10 | 2 | 5 | The lifecycle is written down, but 5 of 6 plans and brainstorms had no `Status:` line (two had an informal "Live" note), and one said "no phase has shipped yet" after two of its pull requests had merged. |
| 9 | Workflow | 5 | 3 | 3.75 | Non-trivial path, trivial exception and commit permission are defined; no fast path for urgent fixes. |
| 10 | Environment and safety | 5 | 2 | 2.5 | Four real traps documented, but not the one that bites first: a plain `fvm flutter test` hangs on `test/widgets/timer/`. And no rule keeps agents away from production data. |
| | **Total** | **100** | | **60 (C)** | Strong structure, with drift and silent rule-breaking already started. |

The biggest losses share a cause: rules that lived only in prose, and facts
nobody re-checked. The docs said to keep plan status current and to update all
ARB files together, and nothing checked either. That's why the kit turns every
checkable rule into a hook and tests that the hook's message reaches the model.

## What changed

| Change | Criterion | Points |
| ------ | --------- | ------ |
| CLAUDE.md keeps only Claude tooling; the workflow lives in AGENTS.md | 1 | +1.25 |
| Format and format-check commands; a test command that skips the hanging timer tests; `functions/` commands | 2 | +2.5 |
| Layer direction with its real exceptions; `functions/`, the share extension, the share activity and the mirrored logic on the map | 3 | +2.5 |
| Every rule carries its reason and names what catches it; "Prefer" became a directive; mirrored logic earned a rule | 4 | +7.5 |
| Reminders reach Claude as `additionalContext`; `patterns` catch `_buildX()` helpers, raw `Navigator` pushes and hardcoded colors; `ask` rules hold commit, push and deploy; the auto-`build_runner` hook is replaced by one regeneration per task | 5 | +7.5 |
| Root cut to 192 lines; backlog moved to the issue tracker; user numbers removed | 6 | +2.5 |
| Every stale fact above fixed in this folder, the skill's YAML included | 7 | +3.75 |
| `/rush` added for urgent fixes | 9 | +1.25 |
| Hanging-tests trap documented; production boundary added; MCP writes denied | 10 | +2.5 |
| **Score of this folder** | | **91.25 (A)** |
| Move live plans into change folders with a true `Status:` line; delete those whose work has shipped | 8 | +5 |
| Replace the token values copied into the design-system skill with links | 7 | +3.75 |
| **Projected once both are done in the repo** | | **100** |

A perfect score says the hygiene is in place: commands that run, facts that are
true, rules that are enforced. It can't say whether the rules are the right
ones. That still takes someone who knows the product.

The production boundary, the MCP setup, the mirrored-logic rule and the
import-quality taster are new; the rest is Meally's own content, corrected.
