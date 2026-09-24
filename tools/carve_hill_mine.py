"""Cut the west-hill adit into the maintained coast island mesh.

Run through Blender 5.1 with -- <absolute output directory>. Reads the
unchanged island-coast source, writes a new editable island-mine source and
partitioned island.glb only in the requested directory. Install after review.
"""
from pathlib import Path
import json
import sys

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mountain_profile import floor_height
from partition_island import partition

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT / "sources/environment/island-coast-source.blend"))
island = bpy.data.objects["island"]
before_bounds = tuple(round(x, 4) for x in island.dimensions)

# Two overlapping ground layers exist in this source: the original grass mesh
# and the later continuous coast mesh. Cut both to leave a real open trench.
ground_names = {"grass", "grassLight", "Valley moss", "Fern slopes", "Mountain heath"}
bm = bmesh.new()
bm.from_mesh(island.data)
materials = list(island.data.materials)
for axis, coordinate in ((0, -17.8), (0, -14.5), (1, -7.8), (1, -4.2)):
    normal = [0.0, 0.0, 0.0]
    normal[axis] = 1.0
    nearby = [face for face in bm.faces if
              any(abs(vertex.co[axis] - coordinate) < 2.0 for vertex in face.verts)]
    geometry = set(nearby)
    for face in nearby:
        geometry.update(face.edges)
        geometry.update(face.verts)
    bmesh.ops.bisect_plane(bm, geom=list(geometry), dist=0.00001,
                           plane_co=tuple(coordinate if i == axis else 0 for i in range(3)),
                           plane_no=tuple(normal), clear_inner=False, clear_outer=False)
bm.faces.ensure_lookup_table()
cut = [face for face in bm.faces
       if -17.8 < face.calc_center_median().x < -14.5
       and -7.8 < face.calc_center_median().y < -4.2
       and abs(face.normal.z) > .35
       and materials[face.material_index].name in ground_names]
assert 30 < len(cut) < 300, len(cut)
bmesh.ops.delete(bm, geom=cut, context="FACES")
bm.to_mesh(island.data)
bm.free()
island.data.update()

# The cut has natural rock side faces down to the new tunnel floor. The
# separate gallery GLB supplies the traversable floor and the inner lining.
vertices, faces = [], []
for side_y in (-7.78, -4.22):
    base = len(vertices)
    for i in range(18):
        x = -14.5 - 3.3 * i / 17
        game_x = x * 100
        bottom = (144 + .1 * (-game_x - 1450)) / 100 - .08
        top = max(bottom + .03, floor_height(game_x, -side_y * 100) / 100 + .08)
        vertices.extend([(x, side_y, bottom), (x, side_y, top)])
    for i in range(17):
        a = base + 2 * i
        quad = (a, a + 1, a + 3, a + 2)
        faces.append(quad if side_y < -6 else tuple(reversed(quad)))
mesh = bpy.data.meshes.new("Mine excavation walls")
mesh.from_pydata(vertices, [], faces)
mesh.update()
walls = bpy.data.objects.new("Mine excavation walls", mesh)
bpy.context.collection.objects.link(walls)
rock_index = next(i for i, material in enumerate(island.data.materials) if material.name == "rock")
mesh.materials.append(island.data.materials[rock_index])

bpy.ops.object.select_all(action="DESELECT")
island.select_set(True)
walls.select_set(True)
bpy.context.view_layer.objects.active = island
bpy.ops.object.join()
island.name = "island"
assert tuple(round(x, 4) for x in island.dimensions) == before_bounds

source = OUT / "island-mine-source.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(source))
raw = OUT / "island-mine-unpartitioned.glb"
bpy.ops.export_scene.gltf(filepath=str(raw), export_format="GLB", use_selection=True,
                          export_apply=True, export_animations=False,
                          export_cameras=False, export_lights=False)
runtime = OUT / "island.glb"
partition(raw, runtime, 4096)
report = {"cutFaces": len(cut), "wallFaces": len(faces),
          "modelSizeGameUnits": [round(v * 100, 4) for v in island.dimensions],
          "triangleCount": sum(len(p.vertices) - 2 for p in island.data.polygons),
          "glbBytes": runtime.stat().st_size,
          "editableSource": str(source), "runtimeAsset": str(runtime)}
(OUT / "mine-carve-manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("MINE_CARVE_RESULT", json.dumps(report))
