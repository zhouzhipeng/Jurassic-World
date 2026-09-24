# Hill mine spawn verification

- Source revision: `aca5138` (`Face player toward hill mine at spawn`), including `9c0e79c` (`Spawn new games beside hill mine entrance`).
- Changed sources: `scenes/Game/scene.settings` and `scenes/Game/functions/sceneLoad.events`.
- Validation: `validate_project_files` passed structural, event generation, extension generation, JavaScript authoring, and semantic checks after the final source edit.
- Runtime: `verify_project_change` reloaded the project and launched a fresh paused `Game` preview (`preview-ws-26`). All assertions passed, including zero runtime errors and one player at finite coordinates.
- Observed starting state after 12 frames: `Player3D` at X=-1250, Y=600, Z=19.5786, angle=90 degrees. `mine-spawn.png` shows the player on the ground facing the cave entrance.
- Scope: verifies a fresh new-game preview. Existing saved positions and death respawn were not exercised.
