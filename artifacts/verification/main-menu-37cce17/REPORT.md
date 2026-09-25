# Main menu verification

Source revision: `37cce17` (`Add main menu with continue and new journey`).

## Checks

- `validate_project_files`: structurally valid, event code generation valid, semantic lint passed, no diagnostics.
- Reloaded project from committed disk sources; regenerated catalogs successfully.
- Default preview launched in `Menu` (the project's `firstLayout`). Screenshot: `artifacts/verification/main-menu-37cce17/main-menu.png`.
- Existing local save detected. Pressing Return on the menu entered `Game`; runtime `Mode=0`, `IntroStep=5`, confirming the intro was skipped for Continue.
- Pressing N on a fresh menu entered `Game`; runtime `Mode=11`, `IntroStep=0`, showing the opening story screen. Screenshot: `artifacts/verification/main-menu-37cce17/new-journey-intro.png`.
- In `Game`, the pause menu's Title button returned to `Menu`.

The new-journey check stopped at the intro prompt, before changing the watched-intro flag or replacing the local save.
