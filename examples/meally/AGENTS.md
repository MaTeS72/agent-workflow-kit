# AGENTS.md — Meally

> Source of truth for any AI coding agent working on this repo (Claude Code,
> Cursor, Codex). Read this first; pull in the linked `docs/` files only when
> the task needs them.

## Project overview

**Meally** is a cross-platform recipe app: users save recipes (mostly by URL
import), organize them, plan meals, and generate shopping lists.

- **Platforms:** iOS, Android and web from one Flutter codebase, plus a native share extension on iOS (Swift) and a share activity on Android (Kotlin).
- **Core loop:** import → collection → cooking. Meally is a recipe keeper with the best import engine possible; protect this loop first in every trade-off.
- **Secondary:** the meal planner and the shopping list. Don't over-invest there.

## Tech stack

- **App:** Flutter 3.38.5 (FVM) on Dart `^3.9.0`. Prefix every command with `fvm`.
- **State:** `flutter_bloc` 8.1.3 + `hydrated_bloc` 9.1.2 for persistence.
- **Immutability:** Freezed in `lib/bloc/` and `lib/models/`. New code uses Freezed.
- **Navigation:** `go_router` 13.2.2 with `StatefulShellRoute.indexedStack`.
- **Backend:** Firebase — Firestore, Auth, Storage, Cloud Functions (TypeScript 5, Node 22), Remote Config, App Check, Firebase AI, Messaging, Crashlytics, Analytics.
- **Localization:** 8 ARB files — `en`, `cs`, `de`, `es`, `fr`, `it`, `nl`, `pl`.
- **Linting:** `very_good_analysis` ^7.0.0 for Dart; `strict` TypeScript and no linter in `functions/`.

## Project structure

```text
meal_planner/
├── AGENTS.md / CLAUDE.md      # agent instructions (this file is the source of truth)
├── docs/                      # deep dives (see References); changes/ for work in progress
├── functions/src/             # Cloud Functions: recipe extraction, saving + image re-hosting,
│                              #   social fetchers, scheduled pushes, store webhook, admin scripts
├── ios/MeallyShareExtension/  # Swift share extension: parses JSON-LD on the device
├── android/app/src/main/kotlin/…/ShareActivity.kt  # Kotlin share activity
├── scripts/import_check/      # import corpus replay, cross-language parity, quality gate
├── lib/
│   ├── main.dart              # Firebase init, Repository/Bloc providers
│   ├── router.dart            # GoRouter shell: Recipes, Meal Plan, Shopping List, More
│   ├── bloc/  design_system/  services/  l10n/   # each has its own CLAUDE.md
│   ├── models/                # Freezed data models
│   ├── pages/                 # pages with co-located widgets/
│   └── utils/                 # pure functions (ingredient pipeline, import naming)
└── test/                      # mirrors lib/; has its own CLAUDE.md
```

`functions/` has its own `CLAUDE.md` too.

## Key commands

| Task | Command |
| ---- | ------- |
| Install dependencies | `fvm flutter pub get` |
| Format | `fvm dart format <changed files>` (touched files only; see quirks) |
| Format check | `fvm dart format --output=none --set-exit-if-changed <changed files>` |
| Static analysis | `fvm flutter analyze` |
| Run tests | `fvm flutter test $(find test -name '*_test.dart' -not -path 'test/widgets/timer/*')` |
| Code generation | `fvm dart run build_runner build --delete-conflicting-outputs` |
| Localization | `fvm flutter gen-l10n` |
| Import quality, all surfaces (local CI mirror) | `./scripts/import_check/check.sh` |
| Cloud Functions build / test | `npm run build` / `npm test` in `functions/` |

**CI.** `import-quality.yml` runs on every pull request: the import tests, the
Cloud Function tests and corpus replay, and a per-language quality gate against
`main`'s committed baseline (the `quality-regression-accepted` label lets an
intended regression through). `import-quality-live.yml` runs weekly against the
production `extractRecipe` and opens an issue when results drift. Neither runs
`flutter analyze`, the full suite or Swift, so run those before asking for review.

## Architecture summary

See [docs/architecture.md](docs/architecture.md).

- **Layers:** pages and widgets → BLoCs → services → Firebase. Known exceptions: some pages and HydratedBlocs still call `FirebaseFirestore.instance` or `FirebaseAuth.instance` directly. New code goes through a service; don't copy the exceptions.
- **State:** HydratedBloc / HydratedCubit for persisted state, Bloc for transient flows with events, Cubit when there are none. Match the file you're in; `lib/bloc/CLAUDE.md` says which is which.
- **No DI framework.** Services come from `RepositoryProvider` in `lib/main.dart` via `context.read<T>()`.
- **Offline-first.** HydratedBloc is the local cache; Firestore writes are try/catch with silent fallbacks. Firestore persistence stays disabled (see quirks).
- **Mirrored logic.** Recipe parsing exists in Dart (app), TypeScript (Cloud Function) and Swift (share extension); import naming also in Kotlin. `functions/CLAUDE.md` lists the pairs, and `check.sh` proves they agree.
- **Navigation:** route paths are `static const` on page classes; the auth guard lives in the router's `redirect`.

## Conventions summary

See [docs/conventions.md](docs/conventions.md).

- **Files:** `snake_case.dart`; pages end in `_page.dart`, services in `_service.dart`.
- **Widgets:** decompose pages into co-located `widgets/`; `const` constructors wherever possible.
- **Async:** check `context.mounted` after `await`; dispose controllers and subscriptions.
- **Logging:** `log()` from `dart:developer` with a `name:` tag. Old `print()` calls stay; new code doesn't add any.
- **Read before editing:** verify APIs and constructors from source. A guessed API fails the build at best and misbehaves silently at worst.

## Workflow

- **Non-trivial work:** `/prep` → `/recipe` → `/cook` ([agent-workflow-kit](https://github.com/MaTeS72/agent-workflow-kit)). `/cook` has five reviewers taste every phase, plus Meally's import-quality taster when import code changes; `/taste` reviews any other diff.
- **Urgent bugs:** `/rush` — start from the Crashlytics trace, regression test first, then a shorter tasting.
- **Trivial work** (typo, one-line fix): edit directly.

## Absolute rules

Each rule is here because breaking it cost us something. The italics say what catches it.

1. **Never edit generated files:** Freezed and json_serializable output, `lib/l10n/generated/`, `lib/firebase_options.dart`, `functions/lib/`, the import goldens and the quality baseline. They're overwritten on the next run, and a hand-edited golden hides a real regression. *Blocked by hook.*
2. **Never write `Widget _buildX()` helpers.** Extract a `StatelessWidget`: helpers rebuild with their parent and can't be `const`. *Patterns hook; rules reviewer.*
3. **Never commit, push or open a pull request without explicit permission.** Those are the owner's decisions; a pushed mistake reaches CI, reviewers and sometimes the stores. *`ask` rules in `.claude/settings.json`.*
4. **Never add a dependency without asking.** Every package is an upgrade and supply-chain cost. *Reminder on `pubspec.yaml`.*
5. **Update all 8 ARB files together.** A key missing from a language falls back to English for those users. *Reminder on every ARB file.*
6. **Navigate with GoRouter** (`context.push/pop/go`). Raw `Navigator` pushes break deep links and the tab shell's back stack; use them only for dialog flows GoRouter can't express. *Patterns hook.*
7. **Use design-system tokens.** Never hardcode colors, spacing or text styles; dark mode and redesigns depend on it. *Patterns hook for raw colors; rules reviewer.*
8. **Change mirrored logic in every language at once.** A parser fixed in Dart but not in Swift imports the same recipe differently from the share sheet. *Reminder on every copy; `check.sh` parity.*
9. **Match the surrounding pattern.** Don't force a migration on a file you're only modifying; a file mixing two patterns is harder to review than either. *Rules reviewer.*
10. **One concern per change.** Unrelated refactors make reviews slow and reverts dangerous. *Rules reviewer.*

## References

Read on demand; none load by default.

- [docs/architecture.md](docs/architecture.md) — when designing BLoCs, navigation, models or Firebase integration.
- [docs/testing.md](docs/testing.md) — when adding tests; the ingredient pipeline is the highest-value area.
- [docs/recipe-import.md](docs/recipe-import.md) — **whenever touching URL, photo or share-sheet import.** The #1 feature.
- [docs/firebase.md](docs/firebase.md) — Firestore, Cloud Functions, security rules, Firebase AI.
- [docs/design-system.md](docs/design-system.md) — when building UI.

## Environmental quirks

- **A plain `fvm flutter test` hangs.** The five tests in `test/widgets/timer/` call `HydratedStorage.build`; use the test command above. Two failures in `recipe_ingredients_section_test.dart` are known.
- **`assets/env`** is git-ignored but declared as an asset. A fresh checkout or worktree needs an empty `assets/env` before tests load the asset bundle.
- **Firestore local persistence is disabled on purpose** (`persistenceEnabled: false` in `lib/main.dart`). Enabling it causes iOS `0xdead10cc` watchdog kills while LevelDB holds file locks during suspension.
- **App Check** sits behind a 5-second timeout with a fallback; a missing `RECAPTCHA_SITE_KEY` only breaks web App Check.
- **TikTok imports go straight to the Cloud Function**, because TikTok's mobile web blocks unauthenticated clients.
- **Format touched files only.** `dart format .` would reformat 78 files nobody is working on.
- **Production is off-limits.** Cloud Function admin scripts are dry-run by default; `--write`, `--send` and every deploy touch production and need the owner's go-ahead for that run. Database writes through MCP are denied.

## Docs hygiene

- **Durable:** `docs/*.md`, every `CLAUDE.md`, `README.md` files and this file. They describe the code as it is now and change in the same pull request as the behaviour.
- **Disposable:** one folder per change in `docs/changes/` (brief and plan, each with a `Status:` line) and review notes in `docs/changes/.tasting/`. The pull request that ships a change's last phase deletes its folder.

On 2026-09-02 this repo carried 88 leftover plans, brainstorms and reviews, each
one a false statement about the codebase. Hence two rules for durable docs:

1. **Don't copy values that live in code** (hex codes, token scales, cron schedules). Link to the source file.
2. **When a doc and the code disagree, the code is right.** Fix the doc in the same commit.

## Keeping this file accurate

Update it in the same change when a language, a top-level directory, a service
category, the lint set, the Flutter version or a major dependency changes, or
when a mistake happens twice and earns an absolute rule. Run `/inspect` before
each release.
