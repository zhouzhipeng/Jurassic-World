"""Build a simple hand-held fishing rod in an absolute disposable output directory.

Run through Blender with -- <output directory>; production files are untouched.
"""

import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


out = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


def material(name, color, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = 0.52
    return mat


wood = material("Dark bamboo", (0.16, 0.11, 0.065))
wrap = material("Sea green grip", (0.08, 0.33, 0.29))
metal = material("Brass reel", (0.68, 0.48, 0.19), 0.65)
line = material("Fishing line", (0.76, 0.9, 0.86))


def segment(name, start, end, radius_start, radius_end, mat):
    a, b = Vector(start), Vector(end)
    delta = b - a
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=radius_start,
                                    radius2=radius_end, depth=delta.length,
                                    location=(a + b) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    return obj


# Match the GripR origin and forward -Y direction of combat-spear.glb.
segment("Rod grip", (0, 0.18, 0), (0, -0.30, 0), 0.036, 0.032, wrap)
segment("Bamboo rod", (0, -0.25, 0), (0, -1.85, 0.10), 0.029, 0.007, wood)
segment("Fishing line", (0, -1.85, 0.10), (0, -2.13, -0.38), 0.004, 0.004, line)
bpy.ops.mesh.primitive_torus_add(major_radius=0.10, minor_radius=0.018,
                                 location=(0, -0.38, -0.055))
reel = bpy.context.object
reel.name = "Reel"
reel.data.materials.append(metal)
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = reel
bpy.ops.object.join()
rod = bpy.context.object
rod.name = "Fishing rod"
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
glb = out / "fishing-rod.glb"
bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=True,
                          export_apply=True, export_animations=False,
                          export_cameras=False, export_lights=False)
source = out / "fishing-rod-source.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(source))
assert glb.stat().st_size > 0 and source.stat().st_size > 0
print("FISHING_ROD", json.dumps({"vertices": len(rod.data.vertices), "glbBytes": glb.stat().st_size}))
