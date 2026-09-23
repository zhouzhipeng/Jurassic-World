"""Add fishing clips to the current survivor rowing Blender source.

Run with Blender in the background and pass an absolute disposable output
directory after --. This script never replaces a production asset directly.
"""

import json
import math
import sys
from pathlib import Path

import bpy


out = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
out.mkdir(parents=True, exist_ok=True)
arm = bpy.data.objects["SurvivorRig"]
skin = bpy.data.objects["SurvivorSkin"]
existing = {action.name for action in bpy.data.actions}
new_names = ("BoatFishCast", "BoatFishWait", "BoatFishBite", "BoatFishReel")
assert {"BoatSit", "BoatRow"} <= existing
assert not (set(new_names) & existing)
bpy.context.scene.render.fps = 30


def pose(frame, count, kind):
    t = (frame - 1) / (count - 1)
    phase = 2 * math.pi * t
    for bone in arm.pose.bones:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (0, 0, 0)
        bone.location = (0, 0, 0)
        bone.scale = (1, 1, 1)
    bones = arm.pose.bones
    bones["Hips"].location.y = -0.42
    bones["ThighL"].rotation_euler.x = -1.12
    bones["ThighR"].rotation_euler.x = -1.12
    bones["ShinL"].rotation_euler.x = 1.28
    bones["ShinR"].rotation_euler.x = 1.28
    bones["FootL"].rotation_euler.x = -0.15
    bones["FootR"].rotation_euler.x = -0.15
    bones["Spine"].rotation_euler.x = 0.13
    bones["Head"].rotation_euler.x = -0.08
    bones["ArmL"].rotation_euler = (-0.56, 0, 0.28)
    bones["ForearmL"].rotation_euler.x = -0.92
    bones["ArmR"].rotation_euler = (-0.78, 0, -0.12)
    bones["ForearmR"].rotation_euler.x = -0.55
    bones["GripR"].rotation_euler.x = 0.25

    if kind == "BoatFishCast":
        # Draw the rod back, then release it forward in one smooth gesture.
        sweep = (1 - math.cos(math.pi * t)) / 2
        bones["Spine"].rotation_euler.x += 0.12 - 0.28 * sweep
        bones["ArmR"].rotation_euler.x = -0.20 - 1.35 * sweep
        bones["ForearmR"].rotation_euler.x = -0.24 - 0.48 * sweep
        bones["GripR"].rotation_euler.x = -0.32 + 0.95 * sweep
        bones["Head"].rotation_euler.x -= 0.10 * sweep
    elif kind == "BoatFishWait":
        breath = math.sin(phase)
        bones["Spine"].rotation_euler.x += 0.025 * breath
        bones["ArmR"].rotation_euler.x += 0.035 * breath
        bones["GripR"].rotation_euler.x += 0.035 * breath
        bones["Head"].rotation_euler.x += 0.018 * breath
    elif kind == "BoatFishBite":
        tug = (1 - math.cos(phase)) / 2
        bones["Spine"].rotation_euler.x -= 0.16 * tug
        bones["ArmR"].rotation_euler.x -= 0.32 * tug
        bones["ForearmR"].rotation_euler.x -= 0.25 * tug
        bones["GripR"].rotation_euler.x += 0.28 * tug
        bones["Head"].rotation_euler.x -= 0.10 * tug
    elif kind == "BoatFishReel":
        pull = math.sin(phase)
        bones["Spine"].rotation_euler.x -= 0.14 + 0.16 * pull
        bones["ArmR"].rotation_euler.x -= 0.34 + 0.32 * pull
        bones["ForearmR"].rotation_euler.x -= 0.18 + 0.20 * pull
        bones["GripR"].rotation_euler.x += 0.20 + 0.25 * pull
        bones["ArmL"].rotation_euler.x -= 0.13 * pull
    bpy.context.view_layer.update()


def add_track(name, count):
    arm.animation_data_create()
    arm.animation_data.action = None
    for frame in range(1, count + 1):
        pose(frame, count, name)
        for bone in arm.pose.bones:
            bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone.name)
            bone.keyframe_insert(data_path="location", frame=frame, group=bone.name)
    action = arm.animation_data.action
    action.name = name
    track = arm.animation_data.nla_tracks.new()
    track.name = name
    track.strips.new(name, 1, action)
    track.mute = True
    arm.animation_data.action = None


for clip, frame_count in (("BoatFishCast", 22), ("BoatFishWait", 31), ("BoatFishBite", 19), ("BoatFishReel", 31)):
    add_track(clip, frame_count)
for track in arm.animation_data.nla_tracks:
    track.mute = False
bpy.context.scene.frame_set(1)
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
skin.select_set(True)
bpy.context.view_layer.objects.active = arm
glb = out / "survivor-animated.glb"
bpy.ops.export_scene.gltf(
    filepath=str(glb), export_format="GLB", use_selection=True,
    export_apply=True, export_animations=True, export_animation_mode="NLA_TRACKS",
    export_cameras=False, export_lights=False,
)
source = out / "survivor-fishing-source.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(source))
assert glb.stat().st_size > 0 and source.stat().st_size > 0
report = {"existingActions": len(existing), "actions": sorted(action.name for action in bpy.data.actions),
          "boneCount": len(arm.data.bones), "glbBytes": glb.stat().st_size}
(out / "fishing-animation-manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("FISHING_ANIMATIONS", json.dumps(report))
