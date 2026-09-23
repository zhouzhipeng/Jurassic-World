"""Add looping surface-swim and underwater-dive clips to the survivor rig.

Run Blender with sources/models/survivor-fishing-source.blend and this script;
pass an absolute disposable output directory after --. Production files stay intact.
"""
import bpy
import json
import math
import sys
from pathlib import Path

out = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
out.mkdir(parents=True, exist_ok=True)
arm = bpy.data.objects["SurvivorRig"]
skin = bpy.data.objects["SurvivorSkin"]
assert not {"Swim", "Dive"} & {action.name for action in bpy.data.actions}
bpy.context.scene.render.fps = 30

def pose(frame, clip):
    t = (frame - 1) / 30
    phase = 2 * math.pi * t
    for bone in arm.pose.bones:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (0, 0, 0)
        bone.location = (0, 0, 0)
        bone.scale = (1, 1, 1)
    b = arm.pose.bones
    # The rig's X pitch brings the chest forward while preserving the world root.
    b["Hips"].rotation_euler.x = -0.85 if clip == "Swim" else -1.08
    b["Hips"].location.z = 0.22 if clip == "Swim" else 0.12
    b["Spine"].rotation_euler.x = -0.20 + 0.04 * math.sin(phase)
    b["Head"].rotation_euler.x = 0.25 if clip == "Swim" else 0.03
    b["ArmL"].rotation_euler = (-0.92 + 0.55 * math.sin(phase), 0, 0.35)
    b["ArmR"].rotation_euler = (-0.92 - 0.55 * math.sin(phase), 0, -0.35)
    b["ForearmL"].rotation_euler.x = -0.35 - 0.45 * max(0, math.sin(phase))
    b["ForearmR"].rotation_euler.x = -0.35 + 0.45 * min(0, math.sin(phase))
    b["ThighL"].rotation_euler.x = 0.24 * math.sin(phase + math.pi)
    b["ThighR"].rotation_euler.x = 0.24 * math.sin(phase)
    b["ShinL"].rotation_euler.x = 0.28 + 0.18 * math.sin(phase)
    b["ShinR"].rotation_euler.x = 0.28 - 0.18 * math.sin(phase)
    if clip == "Dive":
        b["ArmL"].rotation_euler.x -= 0.35
        b["ArmR"].rotation_euler.x -= 0.35
        b["Spine"].rotation_euler.x -= 0.10

for clip in ("Swim", "Dive"):
    arm.animation_data_create()
    arm.animation_data.action = None
    for frame in range(1, 32):
        pose(frame, clip)
        for bone in arm.pose.bones:
            bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone.name)
            bone.keyframe_insert(data_path="location", frame=frame, group=bone.name)
    action = arm.animation_data.action
    action.name = clip
    track = arm.animation_data.nla_tracks.new()
    track.name = clip
    track.strips.new(clip, 1, action)
    track.mute = True
    arm.animation_data.action = None

for track in arm.animation_data.nla_tracks:
    track.mute = False
bpy.context.scene.frame_set(1)
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
skin.select_set(True)
bpy.context.view_layer.objects.active = arm
glb = out / "survivor-animated.glb"
bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=True,
    export_apply=True, export_animations=True, export_animation_mode="NLA_TRACKS",
    export_cameras=False, export_lights=False)
source = out / "survivor-swim-source.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(source))
report = {"actions": sorted(a.name for a in bpy.data.actions), "boneCount": len(arm.data.bones),
          "glbBytes": glb.stat().st_size}
assert glb.stat().st_size > 0 and source.stat().st_size > 0
(out / "swim-animation-manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("SWIM_ANIMATIONS", json.dumps(report))
