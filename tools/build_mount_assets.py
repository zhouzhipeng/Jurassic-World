import bpy, math, random, json
from pathlib import Path
SOURCE_DIR = Path(__file__).resolve().parents[1] / 'sources/models'
SOURCE_DIR.mkdir(parents=True, exist_ok=True)
from mathutils import Vector
random.seed(18)
P=Path(__file__).resolve().parents[1]/'assets/models';P.mkdir(parents=True,exist_ok=True)
# This script runs in a fresh background Blender process, never the user's open file.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.85
    return m
m={k:mat(k,v) for k,v in {'grass':(.36,.53,.15),'grassLight':(.53,.65,.22),'sand':(.75,.64,.40),'rock':(.43,.48,.46),'rockLight':(.61,.64,.57),'water':(.08,.53,.67),'foam':(.63,.85,.82),'wood':(.36,.21,.10),'plank':(.58,.37,.18),'roof':(.74,.55,.24),'leaf':(.16,.38,.20),'leafLight':(.29,.49,.20),'teal':(.13,.39,.37),'belly':(.71,.70,.43),'stripe':(.08,.25,.27),'eye':(.035,.045,.035),'skin':(.65,.39,.22),'shirt':(.78,.46,.10),'pants':(.22,.23,.20),'hair':(.16,.09,.04),'canvas':(.60,.48,.29),'flame':(1,.39,.025)}.items()}
def finish(o,name,material):o.name=name;o.data.materials.append(m[material]);return o
def box(name,pos,scale,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=finish(bpy.context.object,name,material);o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:mod=o.modifiers.new('Soft corners','BEVEL');mod.width=bevel;mod.segments=1
    return o
def ell(name,pos,scale,material,sub=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=pos);o=finish(bpy.context.object,name,material);o.scale=scale
    for face in o.data.polygons: face.use_smooth=True
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def beam(name,a,b,r,material,r2=None,verts=8):
    a,b=Vector(a),Vector(b);d=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=(a+b)/2)
    o=finish(bpy.context.object,name,material);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def mesh(name,verts,faces,material):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return finish(o,name,material)
def join_export(name,subset):
    bpy.ops.object.select_all(action='DESELECT')
    for o in subset:o.select_set(True)
    bpy.context.view_layer.objects.active=subset[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=name
    bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bpy.context.view_layer.update();dims=list(o.dimensions)
    bpy.ops.export_scene.gltf(filepath=str(P/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
    return o,{'file':name+'.glb','dimensions':dims,'triangles':sum(len(f.vertices)-2 for f in o.data.polygons)}

# Upright dinosaur with a continuous visual silhouette, separate asset.
start=set(bpy.context.scene.objects)
ell('Dino body',(0,0,2.05),(.9,1.6,.98),'teal',3)
ell('Cream chest',(0,-.65,1.97),(.72,.94,.78),'belly',2)
ell('Shoulders',(0,-.85,2.45),(.65,.8,.8),'teal',2)
beam('Neck',(0,-.9,2.35),(0,-1.55,3.65),.52,'teal',.35,12)
ell('Head',(0,-1.85,3.75),(.39,.62,.36),'teal',3)
ell('Muzzle',(0,-2.25,3.58),(.35,.40,.23),'belly',2)
beam('Crest',(0,-1.55,3.97),(0,-.70,4.2),.18,'stripe',.14,10)
beam('Crest tip',(0,-.70,4.2),(0,-.25,4.06),.14,'stripe',.07,10)
for side in [-1,1]:
    ell('Eye',(side*.35,-1.98,3.87),(.045,.09,.09),'eye',2)
    ell('Hind thigh',(side*.7,.72,1.35),(.35,.5,.7),'teal',2)
    beam('Hind shin',(side*.7,.6,1.1),(side*.7,.9,.25),.23,'teal',.15)
    ell('Hind foot',(side*.7,.60,.15),(.24,.43,.16),'belly',2)
    beam('Foreleg',(side*.52,-.9,1.9),(side*.5,-1.04,.27),.17,'teal',.10)
    ell('Front foot',(side*.5,-1.15,.15),(.17,.29,.13),'belly',2)
beam('Tail base',(0,1.2,2),(0,2.7,1.3),.57,'teal',.29,12)
beam('Tail tip',(0,2.7,1.3),(0,4,1.0),.29,'teal',.03,10)
box('Saddle',(0,.15,2.99),(1.3,1.1,.16),'wood',.1)
for side in [-1,1]:box('Saddlebag',(side*.95,.15,2.35),(.25,.65,.7),'canvas',.08)

# Preserve rigid part weights before joining; one armature owns both clips.
parts=list(bpy.context.scene.objects)
for o in parts:
 name=o.name;x=o.location.x
 bone='Body'
 if any(k in name for k in ['Hind thigh','Hind shin','Hind foot']):bone='HindL' if x<0 else 'HindR'
 elif any(k in name for k in ['Foreleg','Front foot']):bone='ForeL' if x<0 else 'ForeR'
 elif any(k in name for k in ['Neck','Head','Muzzle','Crest','Eye']):bone='Neck'
 elif 'Tail' in name:bone='Tail'
 group=o.vertex_groups.new(name=bone);group.add(list(range(len(o.data.vertices))),1,'REPLACE')
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();meshobj=bpy.context.object;meshobj.name='ParasaurSkin'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
armdata=bpy.data.armatures.new('ParasaurRig');arm=bpy.data.objects.new('ParasaurRig',armdata);bpy.context.collection.objects.link(arm)
bpy.context.view_layer.objects.active=arm;meshobj.select_set(False);arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
bones=[('Root',(0,0,0),(0,0,1),None),('Body',(0,0,2),(0,0,3),'Root'),('Neck',(0,-.9,2.35),(0,-1.55,3.65),'Body'),('Tail',(0,1.2,2),(0,2.7,1.3),'Body'),('HindL',(-.7,.72,1.85),(-.7,.9,.25),'Root'),('HindR',(.7,.72,1.85),(.7,.9,.25),'Root'),('ForeL',(-.52,-.9,1.9),(-.5,-1.04,.27),'Root'),('ForeR',(.52,-.9,1.9),(.5,-1.04,.27),'Root')]
for name,head,tail,parent in bones:
 b=armdata.edit_bones.new(name);b.head=head;b.tail=tail
 if parent:b.parent=armdata.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');meshobj.parent=arm;mod=meshobj.modifiers.new('Skin','ARMATURE');mod.object=arm
bpy.context.scene.render.fps=30
for clip,frames in [('Idle',60),('Walk',30)]:
 arm.animation_data_create();arm.animation_data.action=None
 for pb in arm.pose.bones:pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.scale=(1,1,1);pb.location=(0,0,0)
 for frame in range(1,frames+2):
  phase=(frame-1)/frames*math.tau
  for pb in arm.pose.bones:
   pb.rotation_euler=(0,0,0);pb.scale=(1,1,1);pb.location=(0,0,0)
   if clip=='Idle':
    if pb.name=='Body':pb.scale.x=1+math.sin(phase)*.012
    if pb.name=='Neck':pb.rotation_euler.x=math.sin(phase)*.025
    if pb.name=='Tail':pb.rotation_euler.z=math.sin(phase)*.035
   else:
    if pb.name in ['HindL','ForeR','HindR','ForeL']:
     offset=0 if pb.name in ['HindL','ForeR'] else math.pi
     pb.rotation_euler.x=math.sin(phase+offset)*.25
    if pb.name=='Neck':pb.rotation_euler.x=math.sin(phase*2)*.02
    if pb.name=='Tail':pb.rotation_euler.z=math.sin(phase)*.065
   pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=pb.name)
   pb.keyframe_insert(data_path='scale',frame=frame,group=pb.name)
 action=arm.animation_data.action;action.name=clip
 track=arm.animation_data.nla_tracks.new();track.name=clip;strip=track.strips.new(clip,1,action);strip.action_frame_start=1;strip.action_frame_end=frames+1
 arm.animation_data.action=None
# Export only this rig; reset pose to neutral to measure the same world scale.
for pb in arm.pose.bones:pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
for tr in arm.animation_data.nla_tracks:tr.mute=True
bpy.context.view_layer.update();dims=list(meshobj.dimensions)
for tr in arm.animation_data.nla_tracks:tr.mute=False
bpy.context.scene.frame_set(1);bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);meshobj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'parasaur-animated.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_cameras=False,export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_DIR/'parasaur-animated-source.blend'))
# Seated rider is a separate mesh with leg clearance around saddle bags.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for side in [-1,1]:
 beam('Upper leg',(side*.22,0,.05),(side*1.1,-.22,-.2),.14,'pants',.12,10)
 beam('Shin',(side*1.1,-.22,-.2),(side*1.24,-.20,-.82),.12,'pants',.10,10)
 ell('Boot',(side*1.24,-.30,-.9),(.15,.24,.15),'wood',2)
 beam('Sleeve',(side*.32,-.02,.62),(side*.36,-.30,.36),.14,'shirt',.11,10)
 beam('Arm',(side*.36,-.30,.36),(side*.25,-.60,.25),.095,'skin',.08,10)
 ell('Hand',(side*.25,-.61,.25),(.09,.10,.1),'skin',2)
ell('Torso',(0,0,.43),(.34,.22,.44),'shirt',2)
box('Belt',(0,0,.1),(.56,.44,.09),'wood',.02)
beam('Neck',(0,0,.75),(0,0,.90),.11,'skin')
ell('Head',(0,-.025,1.03),(.21,.19,.26),'skin',3)
ell('Hair',(0,.015,1.18),(.23,.21,.15),'hair',2)
for side in [-1,1]:ell('Eye',(side*.075,-.2,1.06),(.025,.02,.025),'eye',1)
box('Backpack',(0,.29,.51),(.46,.22,.54),'canvas',.07)
rider,info=join_export('seated-rider',list(bpy.context.scene.objects))
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_DIR/'seated-rider-source.blend'))
(P/'mount-manifest.json').write_text(json.dumps({'dinosaurDimensions':dims,'rider':info,'clips':['Idle','Walk']},indent=2))
print('MOUNT_ASSETS',json.dumps({'dinosaurDimensions':dims,'rider':info}))
