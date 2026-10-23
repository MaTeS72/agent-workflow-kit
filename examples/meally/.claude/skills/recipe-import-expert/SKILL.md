---
name: recipe-import-expert
description: "Use when working on Meally's recipe import pipeline — URL import (paste field, native share sheet, web deep link), photo OCR/AI extraction, JSON-LD/microdata/HTML parsing, the Cloud Function fallback for pages the app can't fetch, ingredient parsing, image re-hosting, or the AI stage via firebase_ai/Gemini. Imports are the most important feature: most recipes come through them. Triggers on phrases like recipe import, URL import, share sheet recipe, JSON-LD recipe, TikTok recipe, Instagram recipe, recipe extractor, AI fallback, Gemini recipe."
---

# Recipe import expert

Read [docs/recipe-import.md](../../../docs/recipe-import.md) for the full deep dive. This skill is the action-oriented summary you load when you're actively touching the import pipeline.

## Pipeline (in order)

1. **Route by host** — TikTok → Cloud Function directly. Instagram / Facebook → social path (`og:description` as caption → AI extraction).
2. **Fetch HTML** — a mobile browser user agent for most hosts; Facebook gets a desktop one.
3. **Detect a page the app can't read** — a bot-check interstitial, HTTP 403/429/503 or an empty body → fall back to the Cloud Function.
4. **JSON-LD parse** — preferred path. Look for `<script type="application/ld+json">` with `@type: Recipe` (or `@graph` / `mainEntity` containers).
5. **Microdata fallback** — `itemscope` + `itemtype="schema.org/Recipe"` blocks.
6. **AI fallback** — Gemini via `firebase_ai`, with a client-side rate-limit guard (`_AiRequestGuard`: a concurrency cap, a per-minute window and per-URL dedupe).
7. **Normalize** — `RecipeExtractor.fromJsonLd(...)` produces a `Recipe`. The image is re-hosted to Firebase Storage by `ImageService.uploadImageFromUrl(...)` in the app and again server-side by `onRecipeCreated` (`functions/src/index.ts`). Ingredients resolved through `IngredientResolverService`.

## File pointers

- Orchestrator: [`lib/services/main_services/recipe_import_service.dart`](../../../lib/services/main_services/recipe_import_service.dart).
- JSON-LD → Recipe: [`lib/services/helper_services/recipe_extractor.dart`](../../../lib/services/helper_services/recipe_extractor.dart).
- Cloud Function bridge: [`lib/services/helper_services/cloud_function_import_service.dart`](../../../lib/services/helper_services/cloud_function_import_service.dart).
- Web CORS proxy: [`lib/services/cors_proxy_service.dart`](../../../lib/services/cors_proxy_service.dart).
- AI ingredient parsing: [`lib/services/helper_services/ai_ingredient_service.dart`](../../../lib/services/helper_services/ai_ingredient_service.dart).
- Ingredient resolver (catalog + AI): [`lib/services/helper_services/ingredient_resolver_service.dart`](../../../lib/services/helper_services/ingredient_resolver_service.dart).
- Image re-hosting: [`lib/services/helper_services/image_service.dart`](../../../lib/services/helper_services/image_service.dart).
- Cloud Function (TypeScript): [`functions/src/extract_recipe.ts`](../../../functions/src/extract_recipe.ts).
- Share-sheet entry: [`lib/widgets/shared_url_handler.dart`](../../../lib/widgets/shared_url_handler.dart).
- Paste UI: [`lib/pages/recipe_import_page.dart`](../../../lib/pages/recipe_import_page.dart).

## AI prompt rules

- **Language is sacred, and the instruction must stay language-agnostic.** The prompt is a single `const languageInstruction` ("Preserve the EXACT original language… NEVER translate any field") in [`recipe_import_service.dart`](../../../lib/services/main_services/recipe_import_service.dart). **Never re-introduce a per-language "keep it in X" branch.** One existed and translated fr/de/es recipes to English whenever detection guessed the source language wrong (fixed and deployed 2026-06-16; the code carries a comment saying so). Detect language only to *tag* the recipe, never to *instruct* the model. Adding a new language therefore needs **no prompt change at all**.
- **Section headers (`# Dough`, `# Filling`)** are preserved verbatim so the downstream parser can render ingredient sub-groups.
- **Output is strict JSON** with keys `name, author, ingredients, steps, totalTime, servings`. The response cleaner strips ```json fences, CJK token-soup (for non-Asian responses), and trailing commas before parsing.

## Common failure modes

- **"Imported Recipe" default name** → `RecipeImportService.isRecipeComplete` rejected the JSON-LD, and the AI stage either failed or returned an empty `name`.
- **Broken image after a week** → the image was never re-hosted: check `ImageService.uploadImageFromUrl` in the app and the `onRecipeCreated` logs in Cloud Functions.
- **TikTok returns nothing** → Cloud Function failed; inspect `functions/src/extract_recipe.ts` logs, especially the Gemini-with-Search-grounding path.
- **Ingredients land as one string** → `recipeIngredient` was a String in the JSON-LD; widen the handling in `_extractIngredientStrings`.
- **"AI import is temporarily rate-limited"** → `_AiRequestGuard` hit its per-minute window.

## When you change the pipeline

- Update [docs/recipe-import.md](../../../docs/recipe-import.md) — pipeline order changes especially.
- If you add a new host carve-out (Twitter/X, Threads, Pinterest), update `_isSocialUrl` and docs/recipe-import.md.
- If the change touches JSON-LD parsing, entity decoding or import naming, change the TypeScript and Swift copies too ([functions/CLAUDE.md](../../../functions/CLAUDE.md) lists them).
- Run `./scripts/import_check/check.sh` — it replays the corpus through all three parsers; pipeline regressions in `RecipeExtractor` and the ingredient resolver are the most painful for users.
