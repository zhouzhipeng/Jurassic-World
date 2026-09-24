"""Build the task-owned pterosaur and saddle in Blender 5.1.

Run: blender --background --python tools/build_pterosaur_assets.py -- ABSOLUTE_OUTPUT_DIR
Writes only pterosaur.glb, pterosaur-saddle.glb, and two editable .blend files
inside the supplied directory. Existing outputs there are replaced.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

out = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system = "METRIC"

def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .8
    return mat

skin = material("Copper teal skin", (.11, .38, .42))
membrane = material("Amber wing membrane", (.49, .29, .19))
belly = material("Warm belly", (.72, .63, .43))
dark = material("Dark markings", (.035, .09, .11))
leather = material("Saddle leather", (.26, .12, .07))
trim = material("Saddle trim", (.69, .45, .19))

def ellipsoid(name, position, scale, mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj

def beam(name, start, end, r1, r2, mat):
    start, end = Vector(start), Vector(end)
    axis = end - start
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=r1, radius2=r2,
                                    depth=axis.length, location=(start + end) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = axis.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    return obj

def polygon(name, vertices, faces, mat):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj

parts = []
parts.append((ellipsoid("Pterosaur torso", (0, 0, 1.55), (.42, .98, .42), skin), "Body"))
parts.append((ellipsoid("Breast", (0, -.48, 1.48), (.35, .48, .32), belly), "Body"))
parts.append((beam("Neck", (0, -.6, 1.72), (0, -1.16, 2.13), .20, .13, skin), "Body"))
parts.append((ellipsoid("Head", (0, -1.19, 2.17), (.20, .35, .21), skin), "Body"))
parts.append((beam("Long beak", (0, -1.37, 2.10), (0, -2.04, 1.97), .14, .015, belly), "Body"))
parts.append((beam("Rear crest", (0, -.99, 2.30), (0, -.34, 2.73), .12, .008, dark), "Body"))
parts.append((beam("Tail", (0, .8, 1.47), (0, 1.55, 1.23), .13, .018, skin), "Body"))
for side, bone in ((-1, "WingL"), (1, "WingR")):
    parts.append((ellipsoid("Eye", (side * .18, -1.28, 2.25), (.035, .06, .05), dark), "Body"))
    parts.append((beam("Leg", (side * .23, .36, 1.38), (side * .36, .50, .18), .11, .055, skin), "Body"))
    parts.append((ellipsoid("Foot", (side * .37, .28, .11), (.13, .28, .10), dark), "Body"))
    verts = [(side*.32,-.36,1.82), (side*1.45,-.12,1.78),
             (side*3.55,.64,1.80), (side*2.55,1.22,1.55),
             (side*1.52,1.44,1.46), (side*.38,.88,1.54)]
    faces = [(0,1,5), (1,4,5), (1,2,3,4)] if side < 0 else [(5,1,0), (5,4,1), (4,3,2,1)]
    parts.append((polygon("Wing membrane", verts, faces, membrane), bone))
    parts.append((beam("Leading finger", verts[0], verts[2], .08, .012, skin), bone))
    parts.append((beam("Wing spar", verts[1], verts[4], .045, .008, skin), bone))

for obj, group_name in parts:
    group = obj.vertex_groups.new(name=group_name)
    group.add(list(range(len(obj.data.vertices))), 1, "REPLACE")
bpy.ops.object.select_all(action="DESELECT")
for obj, _ in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0][0]
bpy.ops.object.convert(target="MESH")
bpy.ops.object.join()
body = bpy.context.object
body.name = "PterosaurBody"
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

armdata = bpy.data.armatures.new("PterosaurRig")
arm = bpy.data.objects.new("PterosaurRig", armdata)
bpy.context.collection.objects.link(arm)
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
for name, head, tail, parent in (
    ("Root", (0,0,0), (0,0,1), None),
    ("Body", (0,0,1.3), (0,0,2), "Root"),
    ("WingL", (-.32,-.15,1.78), (-1.3,-.10,1.78), "Body"),
    ("WingR", (.32,-.15,1.78), (1.3,-.10,1.78), "Body"),
):
    bone = armdata.edit_bones.new(name)
    bone.head, bone.tail = head, tail
    if parent:
        bone.parent = armdata.edit_bones[parent]
bpy.ops.object.mode_set(mode="OBJECT")
body.parent = arm
modifier = body.modifiers.new("Skin", "ARMATURE")
modifier.object = arm
bpy.context.scene.render.fps = 30
for clip, length, amplitude in (("Idle", 60, .05), ("Flap", 30, .35), ("Glide", 60, .015)):
    arm.animation_data_create()
    arm.animation_data.action = None
    for frame in range(1, length + 2):
        phase = (frame - 1) / length * math.tau
        for side, bone_name in ((-1, "WingL"), (1, "WingR")):
            pose = arm.pose.bones[bone_name]
            pose.rotation_mode = "XYZ"
            pose.rotation_euler = (0, side * amplitude * math.sin(phase), 0)
            pose.keyframe_insert(data_path="rotation_euler", frame=frame)
    action = arm.animation_data.action
    action.name = clip
    track = arm.animation_data.nla_tracks.new()
    track.name = clip
    strip = track.strips.new(clip, 1, action)
    strip.action_frame_start = 1
    strip.action_frame_end = length + 1
    arm.animation_data.action = None
for bone in arm.pose.bones:
    bone.rotation_mode = "XYZ"
    bone.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
body.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out / "pterosaur.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_animations=True,
                          export_animation_mode="NLA_TRACKS", export_cameras=False,
                          export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out / "pterosaur-source.blend"))

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
saddle_parts = [
    ellipsoid("Leather seat", (0, .10, 2.00), (.39, .47, .11), leather),
    beam("Front pommel", (-.27,-.27,2.00), (.27,-.27,2.00), .07, .07, trim),
    beam("Rear pommel", (-.27,.43,2.00), (.27,.43,2.00), .07, .07, trim),
]
for side in (-1, 1):
    saddle_parts.append(beam("Harness strap", (side*.34,-.12,1.98), (side*.38,.33,1.35), .055, .055, leather))
    saddle_parts.append(ellipsoid("Stirrup", (side*.52,.08,1.02), (.08,.12,.13), trim))
bpy.ops.object.select_all(action="DESELECT")
for obj in saddle_parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = saddle_parts[0]
bpy.ops.object.convert(target="MESH")
bpy.ops.object.join()
bpy.context.object.name = "PterosaurSaddle"
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
bpy.ops.export_scene.gltf(filepath=str(out / "pterosaur-saddle.glb"), export_format="GLB",
                          use_selection=True, export_apply=True, export_animations=False,
                          export_cameras=False, export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out / "pterosaur-saddle-source.blend"))
print("PTEROSAUR_ASSETS", json.dumps({"output": str(out), "clips": ["Idle", "Flap", "Glide"]}))
