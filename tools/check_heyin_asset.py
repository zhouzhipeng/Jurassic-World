"""Blender background QA: -- ABS_ASSET_DIRECTORY ABS_REPORT_DIRECTORY.
Reads generated GLB and blend; writes a round-trip report and pose renders only.
"""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
src,out=map(Path,sys.argv[sys.argv.index('--')+1:]);out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(src/'heyin.glb'))
arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
assert len(arms)==1
actions=sorted(a.name for a in bpy.data.actions)
assert actions==['Idle','Injured','Rest','Talk','Walk'],actions
assert not any(im.filepath and not im.packed_file for im in bpy.data.images if im.name not in ['Render Result','Viewer Node'])
report={'roundTrip':True,'actions':actions,'armatures':len(arms),'samples':[]}
bpy.ops.wm.open_mainfile(filepath=str(src/'heyin-source.blend'))
sc=bpy.context.scene;arm=bpy.data.objects['HeyinRig'];body=bpy.data.objects['HeyinSkin']
sc.render.resolution_x=630;sc.render.resolution_y=800;sc.cycles.samples=24
for tr in arm.animation_data.nla_tracks:tr.mute=True
for clip,frames in [('Idle',[1]),('Injured',[1,21,41]),('Rest',[1,23,46]),('Talk',[1,21,41]),('Walk',[1,4,7,10,13,16,19,22,25])]:
 arm.animation_data.action=bpy.data.actions[clip]
 for frame in frames:
  sc.frame_set(frame);bpy.context.view_layer.update()
  feet={side:list(arm.pose.bones['Foot'+side].matrix.translation) for side in ['R','L']}
  # Rest/standing recovery and the stance foot in the gait remain on the ground.
  if clip in ['Rest','Injured','Walk']:
   assert min(p[2] for p in feet.values())>=.092,feet
   assert min(p[2] for p in feet.values())<=.098,feet
  mesh=body.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
  minz=min(v.co.z for v in mesh.vertices)
  report['samples'].append({'clip':clip,'frame':frame,'ankles':feet,'meshMinZ':minz})
  body.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
  if frame in [1,7,19]:
   sc.render.filepath=str(out/f'{clip.lower()}-{frame}.png');bpy.ops.render.render(write_still=True)
(out/'asset-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'samples':len(report['samples'])}))
