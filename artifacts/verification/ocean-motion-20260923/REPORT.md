# Coastal ocean motion verification

- Source revision: `b6bdfcce9bcd6e886734606dc18160a4fbe10699`
- Changed source: `materials/CoastalOcean.tsl.ts`; clearance note: `docs/COASTAL_ENVIRONMENT.md`
- Color: coastal and offshore base colors were changed to natural ocean blues (`#247eaf` and `#0b619c`).
- Material validation: model-level WebGL2 node backend validation passed for `assets/environment/coastal-ocean.glb`; activation ready, no diagnostics.
- Project validation: structural, event generation, extension code, JavaScript authoring and semantic checks passed.
- Fresh Game preview: six runtime assertions passed. `CoastalOcean` count 1; World3D has a Three group and 308 visible meshes; failed textures, rejected objects and runtime errors all 0.
- Motion check: paused preview, fixed camera and player test position at `(0, -9000)`. The scene advanced 120 frames (2 seconds) between `final-a.png` and `final-b.png`. The water region's mean absolute RGB pixel change was 9.291/255; a sky region changed 0.146/255. The traveling wave pattern changes while the view remains fixed.

The test position was injected into the preview only; it is not part of the saved scene. Screenshots: `final-a.png`, `final-b.png`.
