"""Build walkable beach/seabed from the maintained island source.

Run: blender --background --python ABS_SCRIPT -- ABS_OUTPUT_DIR
Writes only to the output directory; install reviewed blend and GLB.
"""
import bmesh
import bpy
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mountain_profile import coast_edge as coast_edge_game, floor_height, height
from partition_island import partition

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT / "sources/environment/island-mountain-source.blend"))
island = bpy.data.objects["island"]
bm = bmesh.new()
bm.from_mesh(island.data)
seen = set()
remove = []
shifted = 0
max_drop = 0.0
materials = list(island.data.materials)
for seed in bm.verts:
    if seed in seen:
        continue
    stack = [seed]
    seen.add(seed)
    component = []
    while stack:
        vertex = stack.pop()
        component.append(vertex)
        for edge in vertex.link_edges:
            other = edge.other_vert(vertex)
            if other not in seen:
                seen.add(other)
                stack.append(other)
    if len(component) == 16770:
        remove = component
        continue
    faces = {face for vertex in component for face in vertex.link_faces}
    names = {materials[face.material_index].name for face in faces}
    if names == {"water"}:
        continue
    ground_detail = names <= {"sand", "grassLight"}
    if ground_detail:
        drops = [
            (height(vertex.co.x * 100, -vertex.co.y * 100)
             - floor_height(vertex.co.x * 100, -vertex.co.y * 100)) / 100
            for vertex in component
        ]
    else:
        xs = [vertex.co.x for vertex in component]
        ys = [vertex.co.y for vertex in component]
        x = (min(xs) + max(xs)) / 2
        y = (min(ys) + max(ys)) / 2
        drop = (height(x * 100, -y * 100) - floor_height(x * 100, -y * 100)) / 100
        drops = [drop] * len(component)
    if any(abs(drop) > 1e-6 for drop in drops):
        shifted += 1
        max_drop = max(max_drop, *map(abs, drops))
        for vertex, drop in zip(component, drops):
            vertex.co.z -= drop
assert len(remove) == 16770, "Mountain grid changed; review before rebuilding"
bmesh.ops.delete(bm, geom=remove, context="VERTS")
bm.to_mesh(island.data)
bm.free()

def material(name, color, roughness):
    result = bpy.data.materials.new(name)
    result.diffuse_color = (*color, 1)
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    return result

mats = [
    material("Coast dry shell sand", (0.74, 0.65, 0.45), 0.96),
    material("Coast pale sand", (0.83, 0.75, 0.56), 0.98),
    material("Coast wet sand", (0.64, 0.57, 0.43), 0.66),
    material("Coast shallow sand", (0.72, 0.68, 0.53), 0.9),
    material("Coast seafloor", (0.49, 0.55, 0.46), 1.0),
    material("Coast foam edge", (0.88, 0.88, 0.76), 0.82),
    *[bpy.data.materials[name] for name in ("Valley moss", "Fern slopes", "Mountain heath", "Exposed granite", "Summit stone")],
]

def coast_edge(x, y):
    return coast_edge_game(x * 100, -y * 100) / 100

def floor_metres(x, y):
    return floor_height(x * 100, -y * 100) / 100

def coast_axis(low, high):
    """Keep the mountain interior light, but resolve the walkable shore at 0.5 m."""
    return [n / 2 for n in range(low * 2, high * 2 + 1)
            if abs(n) >= 90 or n % 2 == 0]

xs = coast_axis(-81, 81)
ys = coast_axis(-79, 84)
verts = [(x, y, floor_metres(x, y)) for y in ys for x in xs]
width = len(xs)
faces = []
for j in range(len(ys) - 1):
    for i in range(width - 1):
        k = j * width + i
        faces.extend(((k, k + 1, k + width + 1), (k, k + width + 1, k + width)))
mesh = bpy.data.meshes.new("Continuous coast and seafloor")
mesh.from_pydata(verts, [], faces)
mesh.update()
coast = bpy.data.objects.new("Continuous coast and seafloor", mesh)
bpy.context.collection.objects.link(coast)
for mat in mats:
    mesh.materials.append(mat)
for poly in mesh.polygons:
    cell = poly.index // 2
    i = cell % (width - 1)
    j = cell // (width - 1)
    x = (xs[i] + xs[i + 1]) / 2
    y = (ys[j] + ys[j + 1]) / 2
    edge = coast_edge(x, y)
    if edge < -2:
        index = 4
    elif edge < 2.5:
        index = 3
    elif edge < 3.1:
        index = 5
    elif edge < 5.5:
        index = 2
    elif edge < 12:
        index = 0 if math.sin(x * 1.7 + y * 0.6) + math.sin(y * 2.3 - x * 0.4) > 0.3 else 1
    else:
        z = poly.center.z
        index = 10 if z > 22 else 9 if z > 14 else 8 if z > 8 else 6 if x < 0 else 7
    poly.material_index = index
    poly.use_smooth = True

bpy.ops.object.select_all(action="DESELECT")
island.select_set(True)
coast.select_set(True)
bpy.context.view_layer.objects.active = island
bpy.ops.object.join()
island.name = "island"
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "island-coast-source.blend"))
raw = OUT / "island-coast-unpartitioned.glb"
bpy.ops.export_scene.gltf(filepath=str(raw), export_format="GLB", use_selection=True,
                          export_apply=True, export_animations=False,
                          export_cameras=False, export_lights=False)
partition(raw, OUT / "island.glb", 4096)
report = {
    "coastTriangles": len(faces),
    "totalTriangles": sum(len(p.vertices) - 2 for p in island.data.polygons),
    "glbBytes": (OUT / "island.glb").stat().st_size,
    "modelSizeGameUnits": [round(v * 100, 5) for v in island.dimensions],
    "beachWidthMetres": 12,
    "shoreGridMetres": 0.5,
    "seafloorExtentMetres": [-81, 81, -79, 84],
    "sampleFloorsMetres": {str(e): floor_metres(64 - e, 0) for e in (12, 6, 4, 2, 0, -5, -10, -16)},
    "sceneryComponentsReseated": shifted,
    "maxSceneryHeightCorrectionMetres": max_drop,
}
(OUT / "coast-manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("COAST_RESULT", json.dumps(report))
