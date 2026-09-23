"""Add prone surface-crawl and underwater-dive clips to the survivor rig.

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
    phase = 2 * math.pi * (frame - 1) / 40
    for bone in arm.pose.bones:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (0, 0, 0)
        bone.location = (0, 0, 0)
        bone.scale = (1, 1, 1)
    b = arm.pose.bones
    # Positive rig-X pitches the face and chest toward the swimming direction.
    # Keep the pelvis in place so the gameplay object still controls buoyancy.
    b["Hips"].rotation_euler.x = 1.06 if clip == "Swim" else 1.30
    b["Hips"].location.z = (0.16 if clip == "Swim" else 0) + 0.04 * math.sin(phase)
    b["Spine"].rotation_euler.x = -0.10 + 0.045 * math.sin(phase)
    b["Head"].rotation_euler.x = -0.55 if clip == "Swim" else -0.10
    if clip == "Swim":
        # Alternating reach, pull and recovery; elbows bend during the pull.
        left = math.sin(phase)
        right = math.sin(phase + math.pi)
        b["ArmL"].rotation_euler = (-1.80 - 0.88 * left, 0.08, 0.20)
        b["ArmR"].rotation_euler = (-1.80 - 0.88 * right, -0.08, -0.20)
        b["ForearmL"].rotation_euler.x = -0.16 - 0.55 * max(0, -left)
        b["ForearmR"].rotation_euler.x = -0.16 - 0.55 * max(0, -right)
        b["ThighL"].rotation_euler.x = -0.20 + 0.24 * left
        b["ThighR"].rotation_euler.x = -0.20 + 0.24 * right
        b["ShinL"].rotation_euler.x = 0.10 + 0.24 * max(0, left)
        b["ShinR"].rotation_euler.x = 0.10 + 0.24 * max(0, right)
    else:
        # A calmer underwater pull with both hands together and a dolphin kick.
        pull = (1 - math.cos(phase)) / 2
        b["ArmL"].rotation_euler = (-2.48 + 0.55 * pull, 0, 0.12 + 0.18 * pull)
        b["ArmR"].rotation_euler = (-2.48 + 0.55 * pull, 0, -0.12 - 0.18 * pull)
        b["ForearmL"].rotation_euler.x = -0.14 - 0.42 * pull
        b["ForearmR"].rotation_euler.x = -0.14 - 0.42 * pull
        b["ThighL"].rotation_euler.x = -0.10 + 0.20 * math.sin(phase)
        b["ThighR"].rotation_euler.x = -0.10 + 0.20 * math.sin(phase)
        b["ShinL"].rotation_euler.x = 0.18 + 0.22 * math.sin(phase + 0.9)
        b["ShinR"].rotation_euler.x = 0.18 + 0.22 * math.sin(phase + 0.9)

for clip in ("Swim", "Dive"):
    arm.animation_data_create()
    arm.animation_data.action = None
    for frame in range(1, 42):
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
