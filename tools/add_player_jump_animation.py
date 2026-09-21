"""Extend the existing survivor source in a background Blender process.

Run with --background survivor-animated-source.blend --python THIS -- OUTPUT_DIR.
The original source stays unchanged; outputs are reviewed before installation.
"""
import bpy
import json
import math
import sys
from pathlib import Path

out = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
out.mkdir(parents=True, exist_ok=True)
arm = bpy.data.objects['SurvivorRig']
mesh = bpy.data.objects['SurvivorSkin']
original_actions = {a.name for a in bpy.data.actions}
assert original_actions == {'Idle', 'Walk', 'Run', 'Gather', 'Chop', 'Thrust', 'Hurt', 'Death'}
for track in arm.animation_data.nla_tracks:
    track.mute = True
arm.animation_data.action = None
bpy.context.scene.render.fps = 30

# Each tuple is spine pitch, thigh pitch, knee flex, arm swing, elbow flex.
# The rig's local Y follows the vertical rest bone; local X is sagittal flexion.
neutral = (0, 0, 0, 0, 0)
crouch = (.25, -.58, 1.0, .38, -.25)
launch = (.06, -.10, .16, -.85, -.48)
tuck = (.10, -.52, .92, -.60, -.72)
fall = (.02, -.14, .30, -.28, -.35)
impact = (.32, -.72, 1.15, -.45, -.65)
clips = {
    'JumpStart': (6, [(0, neutral), (.32, crouch), (1, launch)]),
    'JumpRise': (9, [(0, launch), (.65, tuck), (1, tuck)]),
    'JumpFall': (9, [(0, tuck), (.7, fall), (1, fall)]),
    'JumpLand': (9, [(0, fall), (.32, impact), (1, neutral)]),
}

def reset():
    for pb in arm.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)

def pose(values, grounded):
    reset()
    spine, thigh, knee, shoulder, elbow = values
    arm.pose.bones['Spine'].rotation_euler.x = spine
    arm.pose.bones['Head'].rotation_euler.x = -spine * .45
    for side, sign in [('L', 1), ('R', -1)]:
        arm.pose.bones['Thigh'+side].rotation_euler.x = thigh
        arm.pose.bones['Shin'+side].rotation_euler.x = knee
        arm.pose.bones['Foot'+side].rotation_euler.x = -thigh-knee
        arm.pose.bones['Arm'+side].rotation_euler = (shoulder, 0, sign*.12)
        arm.pose.bones['Forearm'+side].rotation_euler.x = elbow
    if grounded:
        # Compress the body while the soles remain on the ground; no root translation.
        bpy.context.view_layer.update()
        evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        minimum = min((evaluated.matrix_world @ v.co).z for v in evaluated.data.vertices)
        arm.pose.bones['Hips'].location.y -= minimum
    bpy.context.view_layer.update()

for name, (length, keys) in clips.items():
    arm.animation_data.action = None
    for frame in range(length+1):
        t = frame/length
        a, b = next((a, b) for a, b in zip(keys, keys[1:]) if a[0] <= t <= b[0])
        u = (t-a[0])/(b[0]-a[0]); u = u*u*(3-2*u)
        values = tuple(x+(y-x)*u for x, y in zip(a[1], b[1]))
        pose(values, name in ('JumpStart', 'JumpLand'))
        for pb in arm.pose.bones:
            for prop in ('rotation_euler', 'location', 'scale'):
                pb.keyframe_insert(data_path=prop, frame=frame+1, group=pb.name)
    action = arm.animation_data.action
    action.name = name
    track = arm.animation_data.nla_tracks.new(); track.name = name
    track.strips.new(name, 1, action); track.mute = True
    arm.animation_data.action = None

reset()
for track in arm.animation_data.nla_tracks:
    track.mute = False
bpy.context.scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True); mesh.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=str(out/'survivor-animated.glb'), export_format='GLB',
    use_selection=True, export_apply=True, export_animations=True,
    export_animation_mode='NLA_TRACKS', export_cameras=False, export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'survivor-jump-source.blend'))
report = {'actions': {a.name: list(a.frame_range) for a in bpy.data.actions},
          'boneCount': len(arm.data.bones), 'meshCount': 1,
          'originalActionsPreserved': original_actions <= {a.name for a in bpy.data.actions},
          'bytes': (out/'survivor-animated.glb').stat().st_size}
(out/'survivor-jump-manifest.json').write_text(json.dumps(report, indent=2))
print('JUMP_EXPORT', json.dumps(report))
