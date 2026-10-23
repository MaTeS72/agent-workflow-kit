# lib/l10n/

See [docs/design-system.md § Localization workflow](../../docs/design-system.md#localization-workflow) for background. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for the known web-build "AppLocalizations isn't defined" issue.

## Hard rules

- **8 ARB files: `en`, `cs`, `de`, `es`, `fr`, `it`, `nl`, `pl`. All must be updated together.** Adding a key to `app_en.arb` without adding it to the other seven shows English to Czech, German, Spanish, French, Italian, Dutch and Polish users.
- **Run `fvm flutter gen-l10n` after every ARB change.** A paired-file hook (`.claude/agent-workflow.json`) hands Claude this reminder after every ARB edit.
- **Never hardcode user-facing strings.** Use `AppLocalizations.of(context)` (aliased to `l10n` in many files). It never returns null (`l10n.yaml` sets `nullable-getter: false`), so don't add `!`.

## Files

- `app_en.arb` — canonical. New keys land here first with their `@key` metadata block (description, placeholders).
- `app_cs.arb` / `app_de.arb` / `app_es.arb` / `app_fr.arb` / `app_it.arb` / `app_nl.arb` / `app_pl.arb` — translations.
- `generated/` — output of `flutter gen-l10n`. Committed. Don't hand-edit.
- `l10n_extensions.dart` — helper extensions on `AppLocalizations`.
- `category_vocabulary_l10n.dart` — every recipe category's name in all 8 languages, which recipe search uses for typed category names (`vegan`, `veganské`). Renaming a `category*` value in an ARB file changes the words search accepts for it.

## Adding a key

1. Add to `app_en.arb` (key + `@key` metadata).
2. Add a translation to each of `app_cs.arb`, `app_de.arb`, `app_es.arb`, `app_fr.arb`, `app_it.arb`, `app_nl.arb`, `app_pl.arb`.
3. Run `fvm flutter gen-l10n`.
4. Use via `AppLocalizations.of(context).<key>`.

## Adding a language

1. Create `app_<code>.arb`.
2. Run `fvm flutter gen-l10n`.
3. Update the ARB list in [AGENTS.md](../../AGENTS.md) (project structure + tech stack sections).
4. Update the ARB-file count in this file's rules and the file list above to the new total.
5. Add the language to the native strings, which live outside ARB (see below), plus `CFBundleLocalizations` in `ios/Runner/Info.plist` and `knownRegions` in `ios/Runner.xcodeproj/project.pbxproj`.

## Native strings (outside ARB)

`gen-l10n` never sees these, so keep them in step by hand:

- `ios/Runner/InfoPlist.xcstrings` — the iOS camera and photo-library permission prompts. Its language folders are also what the App Store lists as the app's languages. Its `en` value replaces `Info.plist`'s at runtime, so changing an `NS…UsageDescription` means changing the catalog too. `test/l10n/ios_info_plist_l10n_test.dart` fails until every prompt is translated into every ARB language.
- `ios/MeallyShareExtension/Localizable.xcstrings` — the iOS share sheet.
- `android/app/src/main/res/values-<code>/strings.xml` — the Android share sheet.
