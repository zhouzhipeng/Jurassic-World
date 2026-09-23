"""Add seated and rowing clips to the current survivor or rowboat Blender source.

Run Blender with the corresponding source .blend, then --python this script --
character|boat ABSOLUTE_OUTPUT_DIR. Outputs are review copies; install only after
inspecting the GLB and .blend. Re-running replaces files in that output directory.
"""

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


mode, target = sys.argv[sys.argv.index("--") + 1 : sys.argv.index("--") + 3]
out = Path(target).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.context.scene.render.fps = 30


def new_track(obj, name, frame_count, pose):
    obj.animation_data_create()
    obj.animation_data.action = None
    for frame in range(1, frame_count + 1):
        pose(frame, frame_count)
        if obj.type == "ARMATURE":
            for bone in obj.pose.bones:
                bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone.name)
                bone.keyframe_insert(data_path="location", frame=frame, group=bone.name)
        else:
            obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    action = obj.animation_data.action
    action.name = name
    track = obj.animation_data.nla_tracks.new()
    track.name = name
    track.strips.new(name, 1, action)
    track.mute = True
    obj.animation_data.action = None


if mode == "character":
    arm = bpy.data.objects["SurvivorRig"]
    skin = bpy.data.objects["SurvivorSkin"]
    existing = {action.name for action in bpy.data.actions}
    assert {"Idle", "Walk", "JumpLand"} <= existing
    assert not ({"BoatSit", "BoatRow"} & existing)

    def seated(frame, count, rowing):
        phase = 2 * math.pi * (frame - 1) / (count - 1)
        stroke = math.sin(phase) if rowing else 0
        for bone in arm.pose.bones:
            bone.rotation_mode = "XYZ"
            bone.rotation_euler = (0, 0, 0)
            bone.location = (0, 0, 0)
            bone.scale = (1, 1, 1)
        arm.pose.bones["Hips"].location.y = -0.42 + (0.025 * math.cos(phase) if rowing else 0)
        arm.pose.bones["Spine"].rotation_euler.x = 0.13 + (0.19 * stroke if rowing else 0)
        arm.pose.bones["Head"].rotation_euler.x = -0.08 - (0.08 * stroke if rowing else 0)
        for side, sign in (("L", 1), ("R", -1)):
            arm.pose.bones["Thigh" + side].rotation_euler.x = -1.12
            arm.pose.bones["Shin" + side].rotation_euler.x = 1.28
            arm.pose.bones["Foot" + side].rotation_euler.x = -0.15
            arm.pose.bones["Arm" + side].rotation_euler = (-0.82 + (0.45 * stroke if rowing else 0), 0, sign * 0.18)
            arm.pose.bones["Forearm" + side].rotation_euler.x = -0.72 - (0.18 * stroke if rowing else 0)
        bpy.context.view_layer.update()

    new_track(arm, "BoatSit", 31, lambda f, n: seated(f, n, False))
    new_track(arm, "BoatRow", 31, lambda f, n: seated(f, n, True))
    for track in arm.animation_data.nla_tracks:
        track.mute = False
    bpy.context.scene.frame_set(1)
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    skin.select_set(True)
    bpy.context.view_layer.objects.active = arm
    basename = "survivor-animated"
    glb = out / f"{basename}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(glb), export_format="GLB", use_selection=True,
        export_apply=True, export_animations=True, export_animation_mode="NLA_TRACKS",
        export_cameras=False, export_lights=False,
    )
    source = out / "survivor-rowing-source.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(source))
    assert existing <= {action.name for action in bpy.data.actions}
    report = {"mode": mode, "actions": sorted(action.name for action in bpy.data.actions),
              "bones": len(arm.data.bones), "glbBytes": glb.stat().st_size}

elif mode == "boat":
    existing = {obj.name for obj in bpy.data.objects}
    assert {"Cedar hull", "Oar -1", "Oar 1", "Rowing bench -0.95"} <= existing
    for sign in (-1, 1):
        oar = bpy.data.objects[f"Oar {sign}"]
        # Put the rotation origin at the gunwale while retaining the same rest mesh.
        pivot = Vector((sign * 0.94, -0.4, 0.38))
        oar.data.transform(Matrix.Translation(oar.location - pivot))
        oar.location = pivot

        def rest(frame, count, obj=oar):
            phase = 2 * math.pi * (frame - 1) / (count - 1)
            obj.rotation_euler = (0.015 * math.sin(phase), 0, 0)

        def stroke(frame, count, obj=oar, side=sign):
            phase = 2 * math.pi * (frame - 1) / (count - 1)
            obj.rotation_euler = (0.10 * math.cos(phase), side * 0.14 * math.sin(phase),
                                  side * 0.38 * math.sin(phase))

        new_track(oar, "OarsRest", 31, rest)
        new_track(oar, "OarsRow", 31, stroke)
        for track in oar.animation_data.nla_tracks:
            track.mute = False
    bpy.context.scene.frame_set(1)
    bpy.ops.object.select_all(action="SELECT")
    basename = "coastal-rowboat"
    glb = out / f"{basename}.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(glb), export_format="GLB", use_selection=True,
        export_apply=True, export_animations=True, export_animation_mode="NLA_TRACKS",
        export_cameras=False, export_lights=False,
    )
    source = out / "coastal-rowboat-rowing-source.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(source))
    report = {"mode": mode, "objects": sorted(existing),
              "actions": sorted(action.name for action in bpy.data.actions),
              "glbBytes": glb.stat().st_size}
else:
    raise SystemExit(f"Unknown mode: {mode}")

assert glb.stat().st_size > 0 and source.stat().st_size > 0
(out / f"{mode}-manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("ROWBOAT_EXPORT", json.dumps(report))
