# Initial spawn ground verification

- Source revision: `c622fabca841740f04a77f4f069f737da0292455` (`Place initial spawn on clear level beach`).
- Issue: `issues/issue-20260924-010858-952.md` reported that the survivor appeared to float at birth.
- Changed sources: `scenes/Game/scene.settings` and `scenes/Game/functions/sceneLoad.events` place the initial survivor at `(5200, 2800)`.
- Terrain check: `tools/mountain_profile.py` gives floor height `0` at that point and at offsets of 25 units in each horizontal direction. The original `(5000, 2500)` point has a steep slope and a computed floor height of about `123.17`.
- Validation: `validate_project_files` passed structural, event code generation, extension generated code, JavaScript authoring, and semantic checks.
- Runtime: `verify_project_change` reloaded the committed sources, launched `Game` paused, and stepped 120 frames. The survivor remained at `(5200, 2800, 0)`. All seven typed assertions passed: one finite player instance, zero runtime errors, a Three group with 221 visible meshes, zero failed textures, and zero rejected objects. The receipt reported `runtimeVerified: true` and `completionReady: true`.
- Visual review: [spawn.png](spawn.png) shows the survivor standing on the dry beach with a clear camera view.
- Scope: initial spawn position and its settled preview; other gameplay and save restoration paths were not retested for this issue.
