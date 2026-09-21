# FPS display and camera performance

## Issue 20260921-071339-601: moving-frame optimization

The earlier identical-ray cache improved stationary views but missed on every
moving frame. The report showed 25 FPS while moving around camp. The island's
13 material batches each spanned large parts of the world, making their
raycast bounds ineffective for local camera probes.

`tools/partition_island.py`, executed through Blender 5.1, partitions each
static material batch by triangle-centroid position into leaves of at most
256 triangles. The replacement `assets/models/island.glb` contains 85 spatial
batches and the same 13 materials and 13,318 triangles. An exact multiset check
preserves each triangle's winding, position/normal/UV bytes and material;
node transforms and materials are unchanged. A Blender import verified the
triangle/material counts, and GDevelop inspection verified 85 runtime meshes.
The asset grows from 668,020 to 773,788 bytes. More spatial batches trade some
draw submissions for much cheaper ray rejection. Camera behavior, graphical
quality settings and the top-center third-party FPS display are unchanged.

Same-host, identical `CameraFenceFollow` test (1,083 frames):

| Measurement | Before | After |
| --- | ---: | ---: |
| Average harness frame processing | 51.81 ms | 20.34 ms |
| Test duration including harness overhead | 65,625 ms | 31,790 ms |

The average processing cost fell 60.7%. This is a moving-camera comparison,
not an inference from stationary FPS. Both versions passed the same camera
assertions, including the same minimum distance and maximum zoom step.

New `CameraPerformance` runs two warmed 240-frame WASD paths. It checks real
movement, finite camera positions, the FPS display position and a 33 ms average
budget calibrated for this development host. Profiles measured 16.64 ms in
the reported camp view and 31.72 ms at the fence/eaves. A fresh normal-paced
preview screenshot while W was held displayed 61 FPS near camp. These are
local samples, not a guarantee of 60 FPS everywhere. The fence profile still
contained an isolated 434.2 ms frame, mostly rendering (370.5 ms); eliminating
all first-use rendering spikes is not established by this change.

Verification: all pre-runtime validation phases passed; the fresh preview
gate returned runtimeVerified/completionReady, with one FPSCounter, no runtime
errors, 292 visible World3D meshes and no failed textures or rejected objects.
CameraVisibility, CameraSmoothFollow, CameraTableFollow, CameraWallApproach,
CameraFenceFollow and CameraPerformance all passed. Source commits:
`68eb504` (Partition island geometry to accelerate moving camera raycasts) and
`917192f` (Add moving-camera performance regression coverage).

Rebuild after replacing the source island with an unpartitioned export:

```powershell
& 'D:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python 'ABSOLUTE_PROJECT/tools/partition_island.py' -- 'ABSOLUTE_SOURCE/island.glb' 'ABSOLUTE_TEMP/island.glb'
```

Inspect the temporary result before replacing the registered asset, then follow
the project validation, commit, reload and gameplay-test gates. The utility is
deliberately restricted to this static, untextured, unskinned indexed model.

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
