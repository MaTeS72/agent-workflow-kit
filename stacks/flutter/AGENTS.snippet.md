# Flutter stack pack: AGENTS.md sections

Paste the sections below into the repo's AGENTS.md, replacing the matching
placeholder sections, then delete whatever the project doesn't use. Drawn from
Meally's production setup; pin your own versions.

## Tech stack

- **Framework:** Flutter `<version>` on Dart `<sdk constraint>`, pinned with FVM. Prefix every command with `fvm`.
- **State management:** `<flutter_bloc | riverpod | …>`. Match the pattern of the file you are editing.
- **Immutability:** Freezed for events, states and models. New code uses Freezed.
- **Navigation:** GoRouter. Route paths are `static const` on the page class.
- **Linting:** `very_good_analysis`. Fix warnings; never suppress one without a comment saying why.

## Key commands

| Task | Command |
| ---- | ------- |
| Install dependencies | `fvm flutter pub get` |
| Format | `fvm dart format <changed files>` |
| Format check | `fvm dart format --output=none --set-exit-if-changed <changed files>` |
| Static analysis | `fvm flutter analyze` |
| Run tests | `fvm flutter test` |
| Code generation | `fvm dart run build_runner build --delete-conflicting-outputs` |
| Localization | `fvm flutter gen-l10n` |

## Conventions

- **Files:** `snake_case.dart`. Pages end in `_page.dart`, services in `_service.dart`.
- **Widgets:** never write `Widget _buildX()` helpers. Extract a `StatelessWidget`; it gets its own element, `const` support and a test seam. *Flagged by the `patterns` hook.*
- **Async:** check `context.mounted` before using a `BuildContext` after `await`. Dispose controllers and subscriptions in `dispose()` / `close()`.
- **Logging:** `log()` from `dart:developer` with a `name:` tag. No `print()` in new code. *Flagged by the `patterns` hook.*
- **Strings:** every user-facing string is localized, and every ARB file changes in the same commit.
- **Design tokens:** never hardcode colors, spacing or text styles. Import the design-system barrel.

## Absolute rules

1. **Never edit generated files** (`*.freezed.dart`, `*.g.dart`, `*.mocks.dart`). Edit the source and run code generation. *Enforced by the `protected` hook.*
2. **Never add a dependency without asking.** Every package is a supply-chain and upgrade cost. *Reminded by the `pubspec.yaml` paired-file hook.*
3. **Update every ARB file together.** A key missing from a language falls back to English for those users. *Reminded by the ARB paired-file hook.*

## Suggested nested CLAUDE.md files

Add a short `CLAUDE.md` (15–40 lines) to a directory when it has rules that
only matter there. They load only when Claude works in that directory.

- `lib/bloc/` — which state pattern each BLoC uses, the sync pattern, where to register new ones.
- `lib/l10n/` — the language list, how to add a key, how to add a language, strings that live outside ARB.
- `lib/design_system/` — the token files and the component catalogue.
- `test/` — mirroring rules, test priorities, fixture and asset gotchas.
