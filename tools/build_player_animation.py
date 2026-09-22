"""Original survivor rig. Run with Blender in a fresh background process."""
import bpy, math, json
from pathlib import Path
SOURCE_DIR = Path(__file__).resolve().parents[1] / 'sources/models'
SOURCE_DIR.mkdir(parents=True, exist_ok=True)
from mathutils import Vector
P = Path(__file__).resolve().parents[1] / 'assets/models'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system = 'METRIC'
colors = dict(wood=(.36,.21,.10), skin=(.65,.39,.22), shirt=(.78,.46,.10), pants=(.22,.23,.20), hair=(.16,.09,.04), canvas=(.60,.48,.29), eye=(.035,.045,.035))
m = {}
for n,c in colors.items():
 mat = bpy.data.materials.new(n); mat.diffuse_color=(*c,1); mat.use_nodes=True
 bs=mat.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*c,1); bs.inputs['Roughness'].default_value=.85; m[n]=mat
def finish(o,n,c,b):
 o.name=n; o.data.materials.append(m[c]); bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 g=o.vertex_groups.new(name=b);g.add(list(range(len(o.data.vertices))),1,'REPLACE');return o
def ell(n,p,s,c,b,sub=2):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=p);o=bpy.context.object;o.scale=s
 for f in o.data.polygons:f.use_smooth=True
 return finish(o,n,c,b)
def beam(n,a,b,r,c,bone,r2=None):
 a,b=Vector(a),Vector(b);d=b-a
 bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=r,radius2=r2 or r,depth=d.length,location=(a+b)/2)
 o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,n,c,bone)
def box(n,p,s,c,b):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.scale=s
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=.025;mod.segments=2
 bpy.ops.object.modifier_apply(modifier=mod.name);return finish(o,n,c,b)
bones=[('Root',(0,0,0),None),('Hips',(0,0,.91),'Root'),('Spine',(0,0,1.05),'Hips'),('Head',(0,0,1.51),'Spine')]
for s,side in [(-1,'R'),(1,'L')]:
 hip=(s*.16,0,.9);knee=(s*.18,0,.55);ankle=(s*.18,0,.16)
 shoulder=(s*.32,0,1.4);elbow=(s*.43,0,1.05);hand=(s*.43,-.10,.78)
 bones += [('Thigh'+side,hip,'Hips'),('Shin'+side,knee,'Thigh'+side),('Foot'+side,ankle,'Shin'+side),('Arm'+side,shoulder,'Spine'),('Forearm'+side,elbow,'Arm'+side),('Grip'+side,hand,'Forearm'+side)]
 beam('Upper trousers',hip,knee,.145,'pants','Thigh'+side,.12)
 ell('Knee',knee,(.12,.12,.13),'pants','Shin'+side)
 beam('Lower trousers',knee,ankle,.12,'pants','Shin'+side,.105)
 ell('Boot',(s*.18,-.08,.13),(.14,.24,.13),'wood','Foot'+side)
 beam('Sleeve',shoulder,elbow,.15,'shirt','Arm'+side,.12)
 ell('Elbow',elbow,(.105,.11,.11),'skin','Forearm'+side)
 beam('Forearm',elbow,hand,.095,'skin','Forearm'+side,.075)
 ell('Hand',hand,(.09,.10,.105),'skin','Grip'+side)
 beam('Strap',(s*.22,-.18,1.45),(s*.23,-.20,.97),.028,'canvas','Spine')
ell('Torso',(0,0,1.14),(.34,.22,.40),'shirt','Spine')
box('Belt',(0,0,.89),(.57,.43,.08),'wood','Hips')
beam('Neck',(0,0,1.45),(0,0,1.59),.11,'skin','Head')
ell('Head',(0,-.025,1.72),(.21,.19,.26),'skin','Head',3)
ell('Hair',(0,.015,1.87),(.23,.21,.15),'hair','Head')
for s in [-1,1]:ell('Eye',(s*.075,-.2,1.75),(.025,.02,.025),'eye','Head')
box('Backpack',(0,.29,1.2),(.46,.22,.54),'canvas','Spine')
parts=list(bpy.context.scene.objects);bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SurvivorSkin'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
ad=bpy.data.armatures.new('SurvivorRig');arm=bpy.data.objects.new('SurvivorRig',ad);bpy.context.collection.objects.link(arm)
mesh.select_set(False);arm.select_set(True);bpy.context.view_layer.objects.active=arm;bpy.ops.object.mode_set(mode='EDIT')
for n,p,parent in bones:
 b=ad.edit_bones.new(n);b.head=p;b.tail=Vector(p)+Vector((0,0,.15))
 if parent:b.parent=ad.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');mesh.parent=arm;mod=mesh.modifiers.new('Skin','ARMATURE');mod.object=arm
bpy.context.scene.render.fps=30
clips={'Idle':60,'Walk':24,'Run':18,'Gather':24,'Chop':11,'Thrust':9,'Hurt':11,'Death':30}
def rot(n,x=0,y=0,z=0):arm.pose.bones[n].rotation_euler=(x,y,z)
for clip,length in clips.items():
 arm.animation_data_create();arm.animation_data.action=None
 for f in range(length+1):
  t=f/length;p=t*math.tau
  for pb in arm.pose.bones:pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.location=(0,0,0);pb.scale=(1,1,1)
  if clip=='Idle':
   rot('Spine',.018*math.sin(p),.015*math.sin(p));rot('Head',-.012*math.sin(p),.025*math.sin(p));arm.pose.bones['Spine'].scale=(1+.012*math.sin(p),1+.008*math.sin(p),1)
  if clip in ['Walk','Run']:
   run=clip=='Run';amp=.70 if run else .43
   rot('Spine',.15 if run else .025,0,.045*math.sin(p))
   arm.pose.bones['Hips'].location.y=(.035 if run else .018)*(1-math.cos(p*2))
   for side,phase in [('R',p),('L',p+math.pi)]:
    swing=math.sin(phase);rot('Thigh'+side,-amp*swing);rot('Shin'+side,max(0,swing)*(.95 if run else .58));rot('Foot'+side,-max(0,swing)*.30)
    rot('Arm'+side,amp*.8*swing);rot('Forearm'+side,-(.85 if run else .16)-.15*swing)
  if clip=='Gather':
   rot('Spine',.30+.12*math.sin(p));rot('Head',-.12);rot('ArmR',-.55-.20*math.sin(p));rot('ForearmR',-.45-.4*math.sin(p));rot('ThighL',-.12);rot('ShinL',.18)
  if clip=='Chop':
   # Anticipate above the shoulder, strike forward, then recover.
   k = math.sin(math.pi*min(1,t/.8))
   rot('Spine',.18*k,0,-.22*math.sin(p));rot('ArmR',-1.95*max(0,1-t/.65)-.30*k);rot('ForearmR',-.55-.45*k);rot('ArmL',-.25*k)
  if clip=='Thrust':
   k=math.sin(math.pi*t);rot('Spine',.18*k,0,-.16*k);rot('ArmR',-1.28*k);rot('ForearmR',-.55*(1-k));rot('ArmL',-.30*k)
   rot('GripR',1.10*k+.55*(1-k))
  if clip=='Hurt':
   k=math.sin(math.pi*t);rot('Spine',-.30*k,0,.14*k);rot('Head',-.18*k);rot('ArmR',-.40*k);rot('ArmL',-.25*k)
  if clip=='Death':
   k=min(1,t/.75);k=k*k*(3-2*k)
   rot('Hips',-math.pi/2*k,0,.12*k);arm.pose.bones['Hips'].location.y=-.65*k
   rot('ShinR',.25*k);rot('ShinL',.40*k);rot('ArmR',-.3*k,0,-.35*k);rot('ArmL',-.5*k,0,.35*k)
  for pb in arm.pose.bones:
   for prop in ['rotation_euler','location','scale']:pb.keyframe_insert(data_path=prop,frame=f+1,group=pb.name)
 action=arm.animation_data.action;action.name=clip;tr=arm.animation_data.nla_tracks.new();tr.name=clip;tr.strips.new(clip,1,action);arm.animation_data.action=None
for tr in arm.animation_data.nla_tracks:tr.mute=True
for pb in arm.pose.bones:pb.rotation_euler=(0,0,0);pb.location=(0,0,0);pb.scale=(1,1,1)
bpy.context.view_layer.update();dims=list(mesh.dimensions)
for tr in arm.animation_data.nla_tracks:tr.mute=False
bpy.context.scene.frame_set(1);mesh.select_set(True);arm.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'survivor-animated.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_cameras=False,export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_DIR/'survivor-animated-source.blend'))
report={'dimensions':dims,'clips':clips,'bones':[x[0] for x in bones],'triangles':sum(len(p.vertices)-2 for p in mesh.data.polygons),'bytes':(P/'survivor-animated.glb').stat().st_size}
(P/'survivor-animation-manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
