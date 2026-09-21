# FPS display and camera performance

## Issue 20260921-080220-709: dinosaur occlusion slowdown

Reproduced the report at player (650, 200), parasaur (650, -350), requested
yaw 187.642276, pitch 14.601626, and distance 1250. The old camera performs
15 corridor probes for each candidate pitch against animated dinosaur meshes.
The obstructed view repeats this search every frame, even after its resolved
camera has found a clear view. The baseline regression failed at 143.57 ms per
frame: events consumed 136.04 ms, versus 6.41 ms for rendering.

`scenes/Game/external-events/CameraVisibility.events` now uses oriented,
camera-only boxes for Dinosaur3D, Triceratops, Stegosaur, Raptor and Tyrannosaur.
Their five object settings declare CameraBoundsZ and CameraBoundsDepth, updated
with native 3D expressions before the solver. Position, angle and dimensions
are sampled every frame; the boxes follow the prefabs' centered XY and bottom-Z
bounds, with a 15-unit margin. Hidden actors and the player's own mount remain
excluded. Island, building and foliage queries retain their previous paths.
Models, animation, physical collisions and rendering quality are unchanged.

These conservative camera boxes intentionally avoid the spaces between legs
and detailed silhouette gaps. They can raise/retract the camera earlier than
triangle-exact queries. They support the game's upright, yaw-rotated actors;
future actors leaning on X/Y would need correspondingly rotated camera bounds.

Same host, deterministic gameplay harness, original rendering settings:

| Measurement | Before | After |
| --- | ---: | ---: |
| Reported view mean frame | 143.57 ms | 11.46 ms |
| Reported view worst frame | 228.20 ms | 30.00 ms |
| Dinosaur first orbit mean / p95 | Not measured | 16.66 / 28.20 ms |
| Dinosaur warmed orbit mean / worst | Not measured | 14.65 / 36.40 ms |
| Existing warmed orbit mean / worst | Not measured in this task | 10.91 / 19.50 ms |

Reported-view mean frame cost fell 92%. The first dinosaur orbit still contains
a 276.9 ms frame, with rendering responsible for the peak; first-use rendering
stalls described in the earlier LOD investigation are not eliminated here.
These are host measurements, not a universal FPS guarantee. FPS labels captured
after unpaced stepping are not real-time framerate measurements.

`tests/CameraDinosaurPerformance.js`, registered in `tests.settings`, first failed
on the original implementation and now passes. It covers the exact report,
cold/warm orbits, real-mesh head visibility for all five species, turns and
elevation, moving away, hidden actors and mounted exclusion. Existing
CameraVisibility, CameraSmoothFollow, CameraPerformance and
CameraOrbitPerformance also completed with all assertions passing. Moving
camp/fence profiles averaged 17.87/14.29 ms.

Final source validation passed structural, event generation, extension code,
strict JavaScript and semantic checks. The final fresh-preview verification
returned runtimeVerified=true and completionReady=true, with zero runtime
errors, visible World3D meshes, and zero failed textures or rejected World3D
objects. The reported setup was then stepped for 240 frames and visually checked.
Local screenshot: `issues/images/issue-20260921-080220-709-fixed.png`.

Implementation commit: `806268f` (Use oriented dinosaur bounds for camera
obstruction probes). Regression commits: `d5f45c8` and `42f769c`.

## Issue 20260921-072824-223: orbit stutter and automatic foliage LOD

`BerryBush` and `FiberFern` now select three geometry levels from camera
distance, checked every 0.1 seconds. Outward thresholds are 1800/3400 world
units; inward thresholds are 1400/2900, preventing boundary flicker. Plants
within 600 units of the player, or currently fading for camera visibility,
immediately use the original model. The originals continue to own harvesting,
regrowth and exact camera raycasts; only the rendered representation changes.
Proxies follow their source transform, hide during harvest cooldown, and are
deleted with their owner. This implementation is for the current static,
ground-level plants; it does not cover animated actors or elevated vegetation.

| Model | Original triangles | Middle LOD | Far LOD |
| --- | ---: | ---: | ---: |
| Fiber fern | 7,532 | 1,883 | 602 |
| Berry bush | 2,436 | 974 | 389 |

`tools/generate_foliage_lods.py` creates separate GLBs through Blender 5.1,
retaining material slots and fitting each reduced mesh to its original bounds.
Original assets remain available for close views. The official extension
repository was searched first: A3F uses a different rendering framework,
and the foliage/particle extensions do not preserve this project's individual
harvest objects and camera raycasts. A small project-specific selector using
the public API is used here; the existing third-party FPS extension is retained.

Camera fade bindings now remain installed and update only changed opacity
values, avoiding shader destruction/recompilation whenever foliage enters or
leaves the camera corridor. Depth writing retains opaque occlusion at opacity
1. Foliage already found by one corridor ray is excluded from remaining rays.

Keeping many TSL materials alive exposed an engine bug: Three's compatibility
renderer exhausted global uniform-buffer binding points. Engine commit
`35f754a975` in `D:/code/GDevelop` reuses binding points by program block index,
while retaining independent material buffers. A 100-group unit test with only
two binding slots, a WebGL pixel test exceeding the device limit, the pinned
Three bundle build and GDJS build passed. The rebuilt editor runtime is active;
a fresh game preview reports zero runtime errors. Other engine installations
need this engine fix when opening the project.

Two 180-frame rotations at the report's player position and 12.473-degree
requested pitch, using the same host and original render quality:

| Measurement | Before | After LOD and persistent fade |
| --- | ---: | ---: |
| First orbit mean / worst frame | 17.90 / 397.90 ms | 20.18 / 281.90 ms |
| Warmed orbit mean / worst frame | 18.73 / 370.70 ms | 14.97 / 35.10 ms |
| Triangles at final orbit view | 284,550 | 157,042 |
| Draw calls at final orbit view | 469 | 506 |

The sampled geometry load falls 44.8%, and recurring long frames are much
smaller. Warmed mean frame time falls 20.1% after also avoiding redundant
proxy transform/size updates; the first orbit is slower on average because
more material/LOD variants compile on first use. Keeping
transparent fade materials increases draw calls. This is not a guarantee of
60 FPS or elimination of initial shader-compilation stalls.

`FoliageLOD` verifies all three levels, hysteresis, immediate close-range
restoration, cooldown hiding, regrowth, owner deletion and restart cleanup.
`CameraOrbitPerformance` records cold/warm profiles and checks a host-calibrated
warm mean below 33.3 ms, maximum below 100 ms, and final-view geometry below
200,000 triangles.

Final lifecycle checks passed all 38 assertions. CameraSmoothFollow and
CameraVisibility passed, including near-foliage fading and harvested visibility.
CameraPerformance also passed both moving paths: camp mean/worst 19.66/35.30 ms,
fence mean/worst 30.40/70.60 ms, with FPS still visible at the top center.
Scene initialization still includes roughly 6.2-second material setup frames
in these deterministic harness runs; this is outside the warmed profile windows
and is not claimed as improved startup performance.

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
