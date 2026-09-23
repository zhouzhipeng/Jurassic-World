# Coastal scenery ground contact

- Issue: `issues/issue-20260923-073517-245.md`
- Source revision: `b2e08b6` — Seat coastal scenery on walkable ground
- Scene: `Game`
- Date: 2026-09-23

The walkable coast replaced the mountain ground in `assets/models/island.glb`,
but static trees and scenery joined into that GLB retained their earlier
mountain elevations. `tools/build_walkable_coast.py` now moves those connected
scenery components from the mountain profile to the coastal floor before
exporting. Ground details use per-vertex corrections; props use one correction
at their footprint centre. The regenerated editable source is
`sources/environment/island-coast-source.blend`.

Blender 5.1 reported 38 scenery components reseated, with a maximum correction
of 13.60 m. GLB partitioning preserved triangle attributes, and a Blender GLB
round trip found one island mesh, 70,806 triangles, and 24 materials.

GDevelop `validate_project_files` passed structural, event generation,
extension code, JavaScript authoring, and semantic checks. After commit, a
fresh paused `Game` preview passed six assertions: one island, zero runtime
errors, a 3D group with 236 visible meshes, zero failed textures, and zero
rejected 3D objects. The player was moved to the reported eastern shoreline
area for [visual inspection](shoreline-angle.png). This view confirms the
coast renders with the updated GLB; its camera angle differs from the report's
annotated frame.
