# lib/services/

See [AGENTS.md § Architecture summary](../../AGENTS.md#architecture-summary) and [docs/firebase.md](../../docs/firebase.md) for background.

## Layout

- **`main_services/`** — core domain services. Examples: `analytics_service`, `catalog_service`, `meal_plan_service`, `recipe_import_service`, `recipe_search_service`, `user_preferences_service`.
- **`helper_services/`** — focused, narrowly-scoped utilities. Examples: `ai_ingredient_service`, `cloud_function_import_service`, `crash_reporting_service`, `feature_flags_service`, `image_service`, `ingredient_resolver_service`, `notification_service`, `ocr_service`, `recipe_extractor`, `storage_service`.
- **`services/cors_proxy_service.dart`** at the root is a one-off anomaly — leave it. Don't seed new files outside `main_services/` or `helper_services/`.

## Registration & access

- **No DI framework.** Register services in `MultiRepositoryProvider` in [`lib/main.dart`](../main.dart).
- Read in widgets / BLoCs via `context.read<ServiceType>()` (or constructor injection in BLoCs).
- Adding a new service? Update [docs/conventions.md "What to update when you add X"](../../docs/conventions.md) only if the placement rule changes.

## Patterns

- **Never call FirebaseAnalytics directly.** Use [`AnalyticsService`](main_services/analytics_service.dart).
- **Never call FirebaseRemoteConfig directly.** Use [`FeatureFlagsService`](helper_services/feature_flags_service.dart).
- **Firestore writes** are try/catch with `developer.log` + silent fallback. The local cache is authoritative.
- **AI calls** go through [`AiIngredientService`](helper_services/ai_ingredient_service.dart) or [`RecipeImportService`](main_services/recipe_import_service.dart). Respect the rate-limit guard in the import service.

## Tests

`test/services/` mirrors this directory. Test public methods, especially error paths.
