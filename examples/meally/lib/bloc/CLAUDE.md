# lib/bloc/

See [AGENTS.md § Architecture summary](../../AGENTS.md#architecture-summary) and [docs/architecture.md](../../docs/architecture.md) for background. Rules below are the only project-specific things you need before editing in this directory.

## Patterns

Three coexist — match the file you're modifying:

- **HydratedBloc / HydratedCubit** — state persisted to disk. Override `fromJson` / `toJson`, never throw from them, and parse list entries one at a time so one bad entry can't cost the rest.
  - HydratedBloc: `RecipeBloc`, `ShoppingListBloc`, `MealPlanBloc`, `RecipeFolderBloc`, `MealPlanSettingsBloc`, `TimerBloc`.
  - HydratedCubit: `CookingProgressCubit`, `ReviewPromptCubit`, `SubscriptionCubit`; `RecentSearchesCubit` (device-local and bound to one account: `bindUser`, wired in `main.dart`'s auth listener, drops another account's searches, and sign-out and account deletion call `clearQueries`); `UnitSystemCubit` (the As written / Metric / US choice, device-local; a launch-time flag can pin it to As written, and `toJson` then returns null so the saved choice survives).
- **Bloc** — transient flows with events: `AuthBloc`, `RecipeImportBloc`.
- **Cubit** — no event hierarchy: `ConnectivityCubit`, `LocaleCubit`, `NutritionCubit`, `OnboardingCubit`, `PremiumConfigCubit`, `SaleCampaignCubit` (follows a Remote Config campaign and re-emits at its start and end), `SeasonalCollectionsCubit`, `SmartSpotlightCubit`, `TranslationCubit`, and `RecipeSearchCubit` (provided and closed by the search screen so each visit starts fresh; it never logs query text).

## Events / states

All event/state files in this directory use Freezed unions (every `_event.dart` / `_state.dart` has a `.freezed.dart` sibling). `equatable` isn't a project dependency. New BLoCs use Freezed too. See [docs/architecture.md](../../docs/architecture.md#events-and-states-use-freezed) for the enumerated list.

Run build_runner once after changing a Freezed source (command in AGENTS.md). Hand edits to the generated `.freezed.dart` files are blocked by a hook.

## Sync pattern

HydratedBloc handlers emit state first (UI updates immediately), then fire-and-forget a Firestore sync with `try/catch` + `developer.log` on failure. Local copy is authoritative — never throw from the sync helper.

## Registration

Register new BLoCs under `MultiBlocProvider` in [`lib/main.dart`](../main.dart). Provide services through the constructor (no service locator).

## Tests

`test/bloc/` mirrors this directory. Cover happy path, error path, and any edge cases that map to user behavior.
