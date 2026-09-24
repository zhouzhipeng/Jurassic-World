# Beach slope and footprints verification

- Source revision: `21c15424e64cf6c559b47035b20623b8f1086e6b`
- Issue: `issues/issue-20260924-012102-056.md`
- Scope: shore terrain mesh, ground height, island model dimensions, and temporary sand marks.

## Changes

- `assets/models/island.glb` and `sources/environment/island-coast-source.blend` rebuild the beach with 0.5 m shore sampling and a smooth sand to hill transition. The inland grid stays 1 m.
- `scenes/Game/objects/Island3D.settings` now matches the exported model's 18000 × 19400 × 3276.766 game unit bounds. The earlier 18000 unit height scaled the whole visible island below gameplay ground.
- `tools/mountain_profile.py` and the `Mountain*.events` fragments use the same ground formula for the player, actors, and foliage.
- `assets/models/sand-footprints.glb`, `sources/environment/sand-footprints-source.blend`, and `scenes/Game/functions/sceneUpdate.events` create marks on grounded beach steps and remove them after five seconds.

## Evidence

- Blender 5.1 export completed: 128442 triangles and 4008288 GLB bytes. The source manifest reported 18000 × 19400 × 3276.766 game unit model bounds.
- 12482 sampled beach points compared the continuous game floor to the rendered triangle interpolation: maximum gap 6.75 game units (6.75 cm), 99th percentile 2.33 units (2.33 cm). The previous sampled maximum was 23.06 units.
- `validate_project_files`: valid, structural, event code generation, extension code generation, JavaScript authoring, and semantic checks all passed.
- `verify_project_change`: runtime verified and completion ready; seven assertions passed, including a finite player position, 402 visible World3D meshes, zero failed textures, zero rejected objects, and zero runtime errors.
- `tests/CoastalSwimming.js`: passed all 14 assertions over 333 frames. Its event log recorded a `SandFootprints` spawn at frame 17 and removal at frame 317 (five simulated seconds).
- `tests/MountainRadar.js`: all five mesh contact samples passed after the island size correction. Four contact errors were below 0.001 game units; the fifth was 10.92 units. The test later failed at its radar/touch button overlap assertion at 1600×900; that UI condition remains outside this issue's verified scope.
- `final-shore.png` shows the corrected player position at the reported shore coordinates; `corrected-shore.png` shows the same area with collision display enabled. `final-footprints-aligned.png` shows a pair of marks on the dry sand.

## Limits

The sampled mesh gap measures static geometry. It does not measure every animation pose or every shore position. The failed radar/touch UI assertion is not accepted as a passing full MountainRadar test.
