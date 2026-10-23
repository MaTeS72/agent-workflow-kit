# functions/

Cloud Functions in TypeScript 5 (`strict`) on Node 22. Background in
[docs/firebase.md](../docs/firebase.md) and [docs/recipe-import.md](../docs/recipe-import.md).

## Commands (run in `functions/`)

| Task | Command |
| ---- | ------- |
| Build | `npm run build` — installs, compiles to `lib/`, copies `assets/*.json`. A bare `npx tsc` skips the assets. |
| Test | `npm test` — compiles, then runs `node --test` on the compiled `lib/**/*.test.js` |
| Replay the import corpus | `npm run eval:corpus` |

No linter or formatter is configured; match the surrounding style.

## Rules

- **`lib/` is build output.** Never edit it; the hooks block it. `lib/*.js` is git-ignored, and `lib/assets/*.json` are committed copies of `assets/`.
- **Deploys are the owner's.** When asked to deploy, deploy only the named functions (`firebase deploy --only functions:extractRecipe`), build first (`firebase.json` has no predeploy step), and run the `import-quality-live.yml` workflow afterwards when the import function changed. `npm run deploy` ships every function at once.
- **Admin scripts are dry-run first.** The one-off scripts in `src/` run with `npx ts-node` against production and write only with `--write` or `--send`. Never pass either without the owner's go-ahead for that run.
- **Old app versions keep calling these functions for months.** Change a callable's request or response shape additively, or version it.

## Mirrored logic

| Logic | App (Dart) | Here (TypeScript) | Native |
| ----- | ---------- | ----------------- | ------ |
| HTML entity decoding | `lib/utils/string_utils.dart` | `src/html_entities.ts` | `JsonLdParser.swift` (`decodeEntities`) |
| JSON-LD picking and normalization | `recipe_extractor.dart` | `src/extract_recipe.ts` (`pickBestRecipeJsonLd`, `normalizeAliases`) | `JsonLdParser.swift` (`normalizeAliases`, `normalize`) |
| Microdata, primary content | `microdata_extractor.dart`, `primary_content_extractor.dart` | `src/extract_recipe.ts` | — |
| Language detection | `lib/utils/language_resolver.dart` | `src/language_resolver.ts` | — |
| Empty-import naming | `lib/utils/import_naming.dart` (canonical) | `src/extract_recipe.ts` | `ExtractedRecipe.swift`, `ShareActivity.kt` |
| AI model id | `ai_model_factory.dart` | `AI_MODEL` in `src/extract_recipe.ts` | — |

Change every copy in the same pull request, then run
`./scripts/import_check/check.sh` from the repo root (after `npm run build`
here). It replays the frozen corpus through all three parsers and fails when
they disagree.
