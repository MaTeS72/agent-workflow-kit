# lib/design_system/

See [docs/design-system.md](../../docs/design-system.md) for the full token + component overview, and [`README.md`](README.md) for the component catalogue.

## Hard rules

- **Never hardcode colors, spacing, radii, or text styles.** Use:
  - `LightModeColors` / `DarkModeColors` / `AppColors.accent(context)` — from `app_colors.dart`.
  - `AppSpacing.xs..xxxl` / `radiusXs..Full` / `iconXs..Xxl` / `avatarXs..Xxl` / `buttonHeight*` / `inputHeight*` — from `app_spacing.dart`.
  - `AppTypography.displayLarge / headlineLarge / titleLarge / bodyLarge / labelLarge / ...` and the `serif*` variants — from `app_typography.dart`.
- **Always import via the barrel:** `import 'package:meal_planner/design_system/design_system.dart';`. Never reach for individual files.
- **Remote images** use `MeallyNetworkImage`, never raw `Image.network` or `CachedNetworkImage` calls.

## Components live in `components/`

`AppButton`, `AppCard`, `AppTextField` / `AppSearchField` / `AppDropdownField` (in `app_input.dart`), `AppFormField`, `AppListTile`, `AppFilterChip`, `AppChoiceChip`, `MeallyNetworkImage`, `EmptyState`, `RoundCheck`. Add new shared widgets here and export them through `design_system.dart`.

Wide layouts (iPad, web) read in one content column: `AppContentWidth` (box) and `SliverAppContentWidth` (sliver) cap and centre content at `AppContentWidth.defaultMaxWidth`; phones are untouched. `AppSnackBarWidth`, mounted once in `main.dart`, keeps every snackbar in the same column: on wide layouts it makes them floating with centred side insets (insets, not a width — every Material button animates its theme, and a lerped width asserts). A snackbar that sets its own `margin` takes the sides from `AppSnackBarWidth.sideMargin` (see `snackbar_helper.dart`); one that forces `SnackBarBehavior.fixed` would span the screen again.

## Theme

`AppTheme.lightTheme` and `AppTheme.darkTheme` in `app_theme.dart` wire tokens to Material 3. System theme switching is automatic via `MaterialApp.themeMode: ThemeMode.system`.

## Aesthetic direction

Warm, editorial minimalism: a muted terracotta primary, sage secondary and dark
olive grounding, a serif for editorial headlines, soft shadows and generous
spacing. The values live in `app_colors.dart`, `app_spacing.dart` and
`app_typography.dart`; read them there rather than copying them here.
