"""Create the editable boat and nearby islet assets for the coastal voyage."""

from pathlib import Path
import math
import random
import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources" / "environment"
OUTPUT = ROOT / "assets" / "environment"
SOURCE.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"


def material(name, rgb, roughness=0.82):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def mesh(name, vertices, faces, mat):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.materials.append(mat)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return obj


def cube(name, location, scale, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft edges", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj


def cone(name, location, radius1, radius2, depth, vertices, mat):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def export(stem):
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE / f"{stem}-source.blend"))
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT / f"{stem}.glb"),
        export_format="GLB",
        use_selection=False,
        export_cameras=False,
        export_lights=False,
        export_apply=True,
        export_animations=False,
    )
    print(f"ASSET {stem}: {len(bpy.context.scene.objects)} objects; {(OUTPUT / f'{stem}.glb').stat().st_size} bytes")


reset()
wood = material("Oiled cedar", (0.47, 0.28, 0.13))
gunwale = material("Warm gunwale", (0.65, 0.42, 0.20))
inside = material("Boat inner deck", (0.27, 0.18, 0.10))
rope = material("Linen rope", (0.76, 0.68, 0.46))

# Bow points toward local +Y. The boat's origin sits at the waterline.
stations = [(-2.7, 0.0), (-2.2, 0.67), (-1.15, 1.04), (0.65, 1.10), (1.95, 0.78), (2.7, 0.0)]
outer = []
inner_ring = []
for y, half_width in stations:
    for sign in (-1, 1):
        outer.append((sign * half_width, y, 0.22 if half_width else 0.42))
        inner_ring.append((sign * half_width * 0.77, y, 0.38))
bottom = [(0, y, -0.48 if abs(y) < 2.2 else -0.13) for y, _ in stations]
vertices = outer + inner_ring + bottom
faces = []
for i in range(len(stations) - 1):
    a = i * 2
    b = (i + 1) * 2
    faces.extend([(a, b, b + 1, a + 1), (a, a + 1, 2 * len(stations) + i + 1, 2 * len(stations) + i)])
    faces.extend([(a, b, len(outer) + b, len(outer) + a), (a + 1, len(outer) + a + 1, len(outer) + b + 1, b + 1)])
mesh("Cedar hull", vertices, faces, wood)
cube("Inner floor", (0, 0, -0.14), (1.45, 3.45, 0.12), inside, 0.06)
for y in (-0.95, 0.65):
    cube(f"Rowing bench {y}", (0, y, 0.36), (1.9, 0.24, 0.14), gunwale, 0.04)
for sign in (-1, 1):
    cube(f"Rim {sign}", (sign * 0.94, -0.12, 0.40), (0.13, 3.9, 0.12), gunwale, 0.04)
    cube(f"Oar {sign}", (sign * 1.68, -0.40, 0.38), (1.7, 0.12, 0.10), wood, 0.03)
cube("Bow rope", (0, 2.25, 0.48), (0.52, 0.10, 0.08), rope, 0.03)
export("coastal-rowboat")

reset()
sand = material("Pale shell sand", (0.78, 0.69, 0.43))
shore = material("Wet shoreline", (0.59, 0.57, 0.40))
grass = material("Island grass", (0.38, 0.55, 0.25))
leaf = material("Palm leaves", (0.16, 0.43, 0.26))
trunk = material("Palm trunks", (0.42, 0.29, 0.17))
stone = material("Weathered stone", (0.42, 0.46, 0.40))

def disc(name, radius, z, depth, mat, segments=16):
    verts = []
    for height in (z - depth, z):
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            distortion = 1 + 0.045 * math.sin(i * 3.7)
            verts.append((radius * distortion * math.cos(angle), radius * distortion * math.sin(angle), height))
    faces = []
    faces.append(tuple(range(segments, 2 * segments)))
    faces.append(tuple(reversed(range(segments))))
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i, j, segments + j, segments + i))
    return mesh(name, verts, faces, mat)


# Seven metre radius. The top of the walkable core is 0.25 m above origin.
disc("Submerged rocky skirt", 7.2, -0.10, 0.90, shore)
disc("Sand beach", 6.65, 0.13, 0.35, sand)
disc("Walkable grassy core", 5.15, 0.25, 0.28, grass)

random.seed(23)
for i, (x, y) in enumerate(((-2.9, 2.4), (2.6, 2.3), (-0.4, -2.6))):
    cone(f"Palm trunk {i}", (x, y, 1.45), 0.18, 0.11, 2.6, 7, trunk)
    for j in range(5):
        angle = 2 * math.pi * j / 5 + i * 0.35
        tip = Vector((x + 1.65 * math.cos(angle), y + 1.65 * math.sin(angle), 2.20))
        left = Vector((x + 0.35 * math.cos(angle + 0.55), y + 0.35 * math.sin(angle + 0.55), 2.90))
        right = Vector((x + 0.35 * math.cos(angle - 0.55), y + 0.35 * math.sin(angle - 0.55), 2.90))
        mesh(f"Palm frond {i}-{j}", [(x, y, 2.82), tuple(left), tuple(tip), tuple(right)], [(0, 1, 2), (0, 2, 3)], leaf)
for i in range(7):
    angle = i * 2.4
    radius = 3.6 + (i % 3) * 0.65
    cone(f"Coastal rock {i}", (radius * math.cos(angle), radius * math.sin(angle), 0.31), 0.34, 0.16, 0.42, 6, stone)
export("nearshore-islet")
