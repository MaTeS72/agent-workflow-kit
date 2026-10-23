# test/

Full guide: [docs/testing.md](../docs/testing.md).

## Sub-tree rules

- **Mirror `lib/`.** When you add `lib/<area>/<file>.dart`, the test goes under `test/<area>/<file>_test.dart`.
- **Priority: ingredient pipeline.** `lib/utils/` + `lib/services/helper_services/ingredient_resolver_service.dart` carry the highest test-to-LOC value. Touch them → run the test command from AGENTS.md (it skips the timer tests that hang a full run) → verify no regressions.
- **No placeholder tests.** Empty `test()` bodies create false coverage signal — delete or fill them in.
- **Seed initial BLoC state explicitly.** Don't rely on a chain of events from `Initial` when the behavior you're asserting starts elsewhere.

## Asset gotcha

If you see `No file or variants found for asset: assets/env`, create an empty `assets/env` — gitignored but declared in `pubspec.yaml`'s asset list.
