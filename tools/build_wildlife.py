"""Run with Blender --background --factory-startup --python. Original low-poly fauna."""
import bpy, math, json
from pathlib import Path
SOURCE_DIR = Path(__file__).resolve().parents[1] / 'sources/models'
SOURCE_DIR.mkdir(parents=True, exist_ok=True)
from mathutils import Vector
P=Path(__file__).resolve().parents[1]/'assets/models'
def material(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=.86
 return m
def part(o,name,mat,bone):
 o.name=name;o.data.materials.append(mat)
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
 return o
def ell(name,p,s,mat,bone='Body'):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=p);o=bpy.context.object;o.scale=s
 for f in o.data.polygons:f.use_smooth=True
 return part(o,name,mat,bone)
def beam(name,a,b,r,mat,bone='Body',r2=.02):
 a,b=Vector(a),Vector(b);d=b-a
 bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=r,radius2=r2,depth=d.length,location=(a+b)/2)
 o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return part(o,name,mat,bone)
def build(species,scale,color):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 skin=material(species+' skin',color);dark=material(species+' markings',tuple(v*.48 for v in color));ivory=material('Ivory',(.8,.72,.50));eye=material('Eyes',(.035,.024,.018));mouth=material('Mouth',(.16,.055,.04))
 carn=species in ['raptor','tyrannosaur'];rex=species=='tyrannosaur'
 ell('Torso',(0,0,1.45),(.60,1.1,.63),skin)
 ell('Belly',(0,-.22,1.26),(.51,.80,.42),ivory)
 if carn:
  beam('Neck',(0,-.7,1.6),(0,-1.08,2.2),.37,skin,'Neck',.29)
  ell('Head',(0,-1.38,2.22),(.36 if rex else .25,.62,.32 if rex else .23),skin,'Neck')
  ell('Jaw',(0,-1.45,2.0),(.30 if rex else .22,.55,.105),mouth,'Jaw')
  ell('Lower jaw',(0,-1.44,1.93),(.31 if rex else .23,.54,.12),skin,'Jaw')
  for side in [-1,1]:
   for i in range(5):beam('Tooth',(side*(.25 if rex else .17),-1.15-i*.14,2.08),(side*(.25 if rex else .17),-1.15-i*.14,1.98),.035,ivory,'Neck',.005)
   ell('Eye',(side*(.31 if rex else .22),-1.35,2.36),(.04,.075,.06),eye,'Neck')
   ell('Thigh',(side*.48,.35,.98),(.32,.45,.53),skin,'HindL' if side<0 else 'HindR')
   leg='HindL' if side<0 else 'HindR'
   beam('Shin',(side*.50,.30,.85),(side*.53,.66,.30),.16,skin,leg,.09)
   beam('Ankle',(side*.53,.66,.30),(side*.54,.38,.12),.09,skin,leg,.075)
   ell('Foot',(side*.54,.16,.10),(.16,.40,.10),dark,leg)
   for toe in [-1,0,1]:beam('Claw',(side*.54+toe*.10,-.03,.10),(side*.54+toe*.10,-.28,.055),.045,ivory,leg,.005)
   arm='ForeL' if side<0 else 'ForeR'
   beam('Arm',(side*.43,-.60,1.55),(side*.50,-.91,1.30),.10,skin,arm,.06)
   beam('Hand',(side*.50,-.91,1.30),(side*.53,-1.05,1.43),.06,ivory,arm,.025)
  for i in range(5):ell('Back markings',(0,.65-i*.3,2.0),(.24,.12,.12),dark)
 else:
  ell('Shoulder',(0,-.63,1.45),(.60,.65,.60),skin)
  ell('Head',(0,-1.35,1.35),(.42,.56,.38),skin,'Neck')
  ell('Beak',(0,-1.78,1.16),(.24,.27,.18),dark,'Neck')
  for side in [-1,1]:
   ell('Eye',(side*.36,-1.54,1.48),(.035,.075,.06),eye,'Neck')
   for y,bname in [(.62,'Hind'),(-.67,'Fore')]:
    leg=bname+('L' if side<0 else 'R')
    ell('Leg',(side*.48,y,.58),(.22,.26,.56),skin,leg)
    ell('Foot',(side*.49,y-.07,.10),(.25,.32,.12),ivory,leg)
  if species=='triceratops':
   ell('Frill',(0,-.90,1.93),(.91,.17,.75),dark,'Neck')
   ell('Frill interior',(0,-1.055,1.95),(.72,.07,.58),skin,'Neck')
   for side in [-1,1]:beam('Brow horn',(side*.27,-1.40,1.61),(side*.35,-2.07,2.04),.12,ivory,'Neck',.008)
   beam('Nose horn',(0,-1.76,1.42),(0,-2.05,1.78),.095,ivory,'Neck',.008)
  else:
   for i in range(8):
    y=-.90+i*.32;h=.55+.45*math.sin((i+1)/9*math.pi)
    ell('Dorsal plate',((-.10 if i%2 else .10),y,1.96+h*.36),(.075,.23,h*.58),dark)
   for side in [-1,1]:
    for y in [2.20,2.65]:beam('Tail spike',(0,y,.86),(side*.6,y+.15,1.25),.085,ivory,'Tail',.004)
 beam('Tail',(0,.78,1.45),(0,2.03,1.0),.40,skin,'Tail',.18)
 beam('Tail tip',(0,2.03,1.0),(0,3.0,.80),.18,skin,'Tail',.015)
 parts=list(bpy.context.scene.objects)
 bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name=species+'Skin'
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');mesh.scale=(scale,)*3;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 ad=bpy.data.armatures.new(species+'Rig');arm=bpy.data.objects.new(species+'Rig',ad);bpy.context.collection.objects.link(arm)
 mesh.select_set(False);arm.select_set(True);bpy.context.view_layer.objects.active=arm;bpy.ops.object.mode_set(mode='EDIT')
 bones=[('Root',(0,0,0),(0,0,1),None),('Body',(0,0,1.3),(0,0,2),'Root'),('Neck',(0,-.7,1.5),(0,-1.4,1.8),'Body'),('Jaw',(0,-1.05,2.03),(0,-1.7,1.97),'Neck'),('Tail',(0,.8,1.4),(0,2,1),'Body')]
 for side in [-1,1]:
  for pos,name in [(.5,'Hind'),(-.67,'Fore')]:bones.append((name+('L' if side<0 else 'R'),(side*.48,pos,1.2),(side*.48,pos,.1),'Root'))
 for name,h,t,parent in bones:
  b=ad.edit_bones.new(name);b.head=Vector(h)*scale;b.tail=Vector(t)*scale
  if parent:b.parent=ad.edit_bones[parent]
 bpy.ops.object.mode_set(mode='OBJECT');mesh.parent=arm;mod=mesh.modifiers.new('Skin','ARMATURE');mod.object=arm
 bpy.context.scene.render.fps=30
 clips=['Idle','Walk']+(['Attack'] if carn else [])
 for clip in clips:
  arm.animation_data_create();arm.animation_data.action=None
  frames=60 if clip=='Idle' else 30
  for frame in range(1,frames+2):
   phase=(frame-1)/frames*math.tau
   for pb in arm.pose.bones:
    pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
    if clip=='Idle':
     if pb.name=='Body':pb.scale.x=1+.014*math.sin(phase)
     if pb.name=='Neck':pb.rotation_euler.x=.035*math.sin(phase)
    if clip=='Walk' and pb.name in ['HindL','ForeR','HindR','ForeL']:pb.rotation_euler.x=math.sin(phase+(0 if pb.name in ['HindL','ForeR'] else math.pi))*(.40 if carn else .20)
    if clip=='Attack':
     if pb.name=='Neck':pb.rotation_euler.x=math.sin(phase)*.22
     if pb.name=='Jaw':pb.rotation_euler.x=-max(0,math.sin(phase))*.55
    if pb.name=='Tail':pb.rotation_euler.z=math.sin(phase)*.07
    pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=pb.name);pb.keyframe_insert(data_path='scale',frame=frame,group=pb.name)
  action=arm.animation_data.action;action.name=clip;tr=arm.animation_data.nla_tracks.new();tr.name=clip;tr.strips.new(clip,1,action);arm.animation_data.action=None
 for tr in arm.animation_data.nla_tracks:tr.mute=True
 for pb in arm.pose.bones:pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
 bpy.context.view_layer.update();dims=list(mesh.dimensions)
 for tr in arm.animation_data.nla_tracks:tr.mute=False
 bpy.context.scene.frame_set(1);bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);mesh.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(P/(species+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_cameras=False,export_lights=False)
 bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_DIR/(species+'-source.blend')))
 return {'species':species,'dimensions':dims,'clips':clips,'triangles':sum(len(f.vertices)-2 for f in mesh.data.polygons)}
results=[build('triceratops',.95,(.46,.40,.22)),build('stegosaur',1,(.37,.42,.25)),build('raptor',.75,(.52,.20,.105)),build('tyrannosaur',1.35,(.25,.33,.17))]
(P/'wildlife-manifest.json').write_text(json.dumps(results,indent=2));print('WILDLIFE',json.dumps(results))
