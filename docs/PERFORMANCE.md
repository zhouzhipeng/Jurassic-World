# FPS display and camera performance

## FPS extension

Imported the official reviewed **FPS 1.2.1** extension by Ahnaf30e, with no
dependencies, through GDevelop's native extension importer. Upstream source:
https://github.com/GDevelopApp/GDevelop-extensions/blob/3f71acc8f3d68cea9839654ea8ff606162a4cb39/extensions/reviewed/FPS.json

The upstream repository uses the MIT license; original author, origin, and
version metadata remain in `extensions/FPS/extension.settings`.

`FPSDisplay.events` uses `FPS::FPS()` and refreshes the label four times per
second. `FPSCounter` sits at y=8 on the independent topmost `Performance`
layer. Its x coordinate follows `(SceneWindowWidth() - FPSCounter.Width()) / 2`,
so menus and touch-mode layer changes cannot hide it. Local extension changes
guard frame callbacks and avoid division by zero during startup. The imported
array-pruning loop remains the upstream loop, bounded by its existing entries
and removing one entry on every iteration.

## Camera changes

`CameraVisibility.events` still performs its body-corridor tests and movement
prediction. Near-wall headroom probes now run only when a close body hit needs
classification. The center-or-both-sides test short-circuits without changing
its boolean result.

The static, unanimated `Island3D` model caches scalar ray-hit distances for
identical rays. Changing the camera pivot, yaw, requested zoom, or island
identity/visibility/XY position/angle/width/height invalidates the cache.
Individual keys include full ray origin, direction, and distance; at most 256
ray entries are retained. Scene reload recreates the cache. All other solids,
including moving dinosaurs and newly built objects, are queried live; foliage
fading is also queried live. No runtime renderer objects are stored.

This cache relies on the current project's invariant that `Island3D` is static:
its Z position, X/Y rotations, geometry, and animation do not change at runtime.
If future gameplay animates or edits the island, invalidate `CameraFollow`'s
`TerrainRayCache` for that change, or remove the static-cache path.

The final project retains its original MSAA, high-quality sunlight shadows,
1600x900 logical resolution, and 60 FPS cap. A trial of reduced render quality
did not produce a convincing improvement, so those settings were restored.

## Measurements on 2026-09-21

Same machine, fresh Game preview, initial stationary camera, 3196x1800 captured
canvas, original render quality:

| Measurement | Before | After camera cache |
| --- | ---: | ---: |
| Live FPS label, sampled screenshot | 42 | 59 |
| Tool wall time for 120 paused frames, gameplay paused with Mode=2 | 2674 ms | 984 ms |

These are local observations, not a guarantee of 60 FPS everywhere. Tool wall
time includes debugger overhead and is not a CPU profiler measurement. The
cache helps a stationary camera most; movement changes its key and still does
fresh terrain queries. Lighting, animation phase, system load, and background
window throttling can affect live samples.

## Editor importer fix

The first import returned valid persisted sources but omitted compatibility
preflight receipts. The host hook had dropped the MCP preflight callback.
Engine commit `e6f47b4c96` in `D:/code/GDevelop` forwards it through native
installation, checks the full downloaded batch before project mutation, and
returns the receipts. Five focused importer/preflight tests and the commit's
ESLint checks passed. The broader MCP test suite had one catalog-generation
assertion failure outside this fix (88 tests passed). The initial FPS import
has no retroactive pre-mutation receipt; its complete upstream event source
was audited, and installed project sources passed generated-code validation.

Existing unrelated working-tree changes and staged documentation moves were
preserved; task commits contain only FPS and performance changes.

## Verification

Final source validation passed structural, event generation, extension generated
code, strict JavaScript authoring, and semantic checks. The paused preview gate
returned `runtimeVerified: true` and `completionReady: true`; it found exactly
one FPSCounter, zero runtime errors, 220 visible World3D meshes, and no failed
World3D textures. Ten changed/relevant TOML sources also parsed independently.

All five existing camera gameplay tests passed on the final camera code:

- CameraVisibility: obstacles, new construction, hiding, zoom recovery, riding,
  and multiple island orbit angles.
- CameraSmoothFollow: bushes, opacity restoration, harvest visibility, moving
  follow, reversals, and large orbit input.
- CameraTableFollow: table approaches and reversals.
- CameraWallApproach: approaching and pressing against a wall.
- CameraFenceFollow: fence/eaves crossings and restoration of the requested view.

The FPS source commit is `b31aad7` (Add community FPS counter at the top center).
The final camera implementation is `41274e8` (Cache static island raycasts while
preserving render quality), including the earlier headroom optimization.
