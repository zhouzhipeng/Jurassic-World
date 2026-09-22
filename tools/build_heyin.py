"""Original He Yin companion. Blender 5.1 background; outputs only task-owned files.
Run: blender --background --python ABS/tools/build_heyin.py -- ABS/tmp/heyin
The output directory contains editable blend, runtime GLB, portraits and manifest.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
OUT = Path(sys.argv[sys.argv.index('--')+1]); OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene; sc.unit_settings.system='METRIC'; sc.render.fps=30
palette={'skin':(.66,.39,.255),'lip':(.36,.105,.09),'hair':(.055,.025,.018),'hairlight':(.105,.052,.025),'cloth':(.69,.59,.39),'teal':(.055,.25,.23),'trim':(.29,.48,.38),'leather':(.16,.075,.037),'ivory':(.88,.77,.52),'eye':(.13,.235,.16),'dark':(.025,.018,.014),'white':(.86,.80,.65)}
m={}
for name,c in palette.items():
 mat=bpy.data.materials.new('Heyin_'+name); mat.diffuse_color=(*c,1); mat.use_nodes=True
 bs=mat.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*c,1); bs.inputs['Roughness'].default_value=.67 if name=='skin' else .85; m[name]=mat
parts=[]
def finish(o,n,c,b):
 o.name=n; o.data.materials.append(m[c]); bpy.context.view_layer.objects.active=o
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 for f in o.data.polygons:f.use_smooth=True
 o.vertex_groups.new(name=b).add(list(range(len(o.data.vertices))),1,'REPLACE');parts.append(o);return o
def ell(n,p,s,c,b='Head',seg=20,rings=12):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,radius=1,location=p);o=bpy.context.object;o.scale=s;return finish(o,n,c,b)
def tube(n,points,radii,c,b,sides=10):
 # Smooth curves and transported frames avoid twisted cross sections.
 if len(points)>2:
  pp=[];rr=[]
  for i in range(len(points)-1):
   a,bp,cp,d=[Vector(points[max(0,min(len(points)-1,j))]) for j in [i-1,i,i+1,i+2]]
   for k in range(4):
    t=k/4;pp.append(.5*((2*bp)+(-a+cp)*t+(2*a-5*bp+4*cp-d)*t*t+(-a+3*bp-3*cp+d)*t*t*t));rr.append(radii[i]*(1-t)+radii[i+1]*t)
  pp.append(Vector(points[-1]));rr.append(radii[-1]);points,radii=pp,rr
 vv=[];ff=[]
 normal=None
 for i,p in enumerate(points):
  tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
  tangent.normalize()
  if normal is None:normal=Vector((1,0,0)) if abs(tangent.x)<.9 else Vector((0,1,0))
  normal=(normal-tangent*normal.dot(tangent)).normalized();other=tangent.cross(normal).normalized()
  for j in range(sides):
   a=j*math.tau/sides; r=radii[i];vv.append(Vector(p)+r*(normal*math.cos(a)+other*math.sin(a)))
 for i in range(len(points)-1):
  for j in range(sides):a=i*sides+j;nn=i*sides+(j+1)%sides;ff.append((a,nn,nn+sides,a+sides))
 ff.extend([tuple(reversed(range(sides))),tuple(range((len(points)-1)*sides,len(points)*sides))])
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(vv,[],ff);mesh.update();o=bpy.data.objects.new(n,mesh);bpy.context.collection.objects.link(o);return finish(o,n,c,b)
def rings(n,levels,c,b,sides=32):
 vv=[];ff=[]
 for z,rx,ry,cy in levels:
  for j in range(sides):a=j*math.tau/sides;vv.append((rx*math.cos(a),cy+ry*math.sin(a),z))
 for i in range(len(levels)-1):
  for j in range(sides):a=i*sides+j;nn=i*sides+(j+1)%sides;ff.append((a,nn,nn+sides,a+sides))
 ff.extend([tuple(reversed(range(sides))),tuple(range((len(levels)-1)*sides,len(levels)*sides))])
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(vv,[],ff);mesh.update();o=bpy.data.objects.new(n,mesh);bpy.context.collection.objects.link(o);return finish(o,n,c,b)
bones=[('Root',(0,0,0),None),('Hips',(0,0,.86),'Root'),('Spine',(0,0,1.03),'Hips'),('Head',(0,0,1.39),'Spine')]
# Tailored silhouette: layered wrap tunic, narrow belt and split walking skirt.
rings('WovenTunic',[(.86,.225,.125,0),(.95,.175,.105,0),(1.07,.165,.11,0),(1.19,.21,.135,-.005),(1.30,.235,.115,0),(1.35,.18,.09,0),(1.38,.08,.065,0)],'cloth','Spine')
rings('WrapSkirt',[(.60,.285,.165,0),(.70,.27,.155,0),(.86,.232,.14,0),(.94,.185,.115,0)],'teal','Hips')
rings('Hem',[(.60,.289,.168,0),(.625,.285,.168,0)],'trim','Hips')
rings('Belt',[(.91,.193,.122,0),(.96,.183,.12,0)],'leather','Hips')
ell('Buckle',(0,-.13,.935),(.036,.015,.03),'ivory','Hips')
for s,side in [(-1,'R'),(1,'L')]:
 hip=(s*.115,0,.84); knee=(s*.12,-.005,.48); ankle=(s*.12,0,.095)
 shoulder=(s*.22,0,1.29); elbow=(s*.29,-.005,1.075); wrist=(s*.31,-.065,.875)
 bones += [('Thigh'+side,hip,'Hips'),('Shin'+side,knee,'Thigh'+side),('Foot'+side,ankle,'Shin'+side),('Arm'+side,shoulder,'Spine'),('Forearm'+side,elbow,'Arm'+side),('Hand'+side,wrist,'Forearm'+side)]
 tube('LegUpper'+side,[hip,(s*.12,0,.64),knee],[.085,.084,.059],'cloth','Thigh'+side)
 tube('LegLower'+side,[knee,(s*.12,.005,.31),ankle],[.062,.055,.035],'skin','Shin'+side)
 ell('Boot'+side,(s*.12,-.045,.058),(.065,.128,.057),'leather','Foot'+side)
 tube('BootCuff'+side,[(s*.12,0,.07),(s*.12,0,.21)],[.049,.053],'leather','Shin'+side)
 for z in [.10,.145,.19]:tube('Laces'+side,[(s*.12-.042,-.032,z),(s*.12,-.058,z+.008),(s*.12+.042,-.032,z)],[.006]*3,'cloth','Shin'+side,6)
 ell('Shoulder'+side,shoulder,(.083,.084,.09),'teal','Arm'+side)
 tube('Sleeve'+side,[shoulder,(s*.26,0,1.185),elbow],[.079,.071,.053],'cloth','Arm'+side)
 ell('Elbow'+side,elbow,(.05,.05,.053),'skin','Forearm'+side)
 tube('Forearm'+side,[elbow,(s*.30,-.025,.98),wrist],[.052,.046,.032],'skin','Forearm'+side)
 ell('Palm'+side,(s*.315,-.073,.835),(.039,.025,.05),'skin','Hand'+side)
 for i in range(4):
  x=s*(.29+i*.016);tube('Finger'+side+str(i),[(x,-.079,.824),(x,-.084,.79),(x,-.078,.776+abs(i-1.5)*.005)],[.008,.008,.006],'skin','Hand'+side,6)
 tube('Thumb'+side,[(s*.286,-.071,.844),(s*.271,-.081,.82),(s*.274,-.088,.804)],[.012,.01,.008],'skin','Hand'+side,7)
 # Embroidered short mantle on shoulders, leaving hands free.
 tube('MantleEdge'+side,[(s*.08,-.061,1.375),(s*.20,-.088,1.32),(s*.266,-.067,1.25)],[.027,.05,.033],'teal','Spine')
 # Eye whites remain inset inside almond eyelid outlines.
 ell('Ear'+side,(s*.128,.002,1.514),(.027,.023,.046),'skin')
 ell('EyeWhite'+side,(s*.052,-.097,1.552),(.028,.013,.012),'white')
 ell('Iris'+side,(s*.052,-.109,1.551),(.011,.004,.011),'eye')
 ell('Pupil'+side,(s*.052,-.113,1.552),(.005,.002,.007),'dark')
 ell('EyeGlint'+side,(s*.049,-.115,1.556),(.0025,.001,.0025),'white',seg=8,rings=6)
 tube('UpperLid'+side,[(s*.025,-.101,1.551),(s*.05,-.109,1.563),(s*.080,-.090,1.554)],[.002,.0025,.0015],'hair','Head',6)
 tube('Brow'+side,[(s*.027,-.12,1.589),(s*.05,-.122,1.594),(s*.08,-.105,1.588)],[.003,.005,.002],'hair','Head',6)
 ell('Earring'+side,(s*.14,-.006,1.475),(.009,.009,.023),'ivory')
# Anatomical head with a tapered jaw and rounded cranial dome.
rings('Face',[(1.388,.025,.03,-.025),(1.41,.065,.065,-.022),(1.455,.101,.087,-.012),(1.50,.125,.104,0),(1.555,.126,.111,.008),(1.605,.121,.111,.015),(1.648,.094,.091,.021),(1.675,.035,.037,.022)],'skin','Head',40)
tube('Neck',[(0,0,1.33),(0,0,1.43)],[.061,.058],'skin','Head',20)
ell('NoseBridge',(0,-.105,1.529),(.018,.026,.036),'skin')
ell('NoseTip',(0,-.131,1.508),(.022,.022,.015),'skin')
tube('UpperLip',[(-.028,-.096,1.464),(-.01,-.107,1.468),(0,-.108,1.465),(.01,-.107,1.468),(.028,-.096,1.464)],[.003,.005,.004,.005,.003],'lip','Head',7)
ell('LowerLip',(0,-.102,1.457),(.024,.008,.006),'lip')
# Hair cap deliberately open at the face, with sculpted locks and one side braid.
vv=[];ff=[];N=40;K=12
for i in range(K+1):
 for j in range(N):
  a=math.tau*j/N; front=max(0,-math.sin(a)); end=2.15-.95*front
  t=.025+(end-.025)*i/K
  vv.append((.137*math.sin(t)*math.cos(a),.024+.126*math.sin(t)*math.sin(a),1.568+.131*math.cos(t)))
for i in range(K):
 for j in range(N):a=i*N+j;nn=i*N+(j+1)%N;ff.append((a,nn,nn+N,a+N))
mesh=bpy.data.meshes.new('HairCap');mesh.from_pydata(vv,[],ff);mesh.update();o=bpy.data.objects.new('HairCap',mesh);bpy.context.collection.objects.link(o);finish(o,'HairCap','hair','Head')
for i in range(11):
 x=(i-5)*.023
 tube('BackLock'+str(i),[(x,.075,1.65),(x*1.15,.132,1.52),(x*1.08,.13,1.36),(x*.9,.11,1.22)],[.026,.030,.025,.006],'hairlight' if i%3==0 else 'hair','Head')
for s in [-1,1]:
 tube('FaceLock',[(s*.025,-.029,1.69),(s*.105,-.081,1.637),(s*.135,-.066,1.535),(s*.128,-.047,1.42)],[.027,.031,.022,.004],'hair','Head')
for i in range(9):
 z=1.48-i*.032;x=.148+.013*math.sin(i*2.2); y=-.022-i*.006
 o=ell('Braid'+str(i),(x,y,z),(.027-i*.0012,.024-i*.0012,.027),'hairlight' if i%2 else 'hair');o.rotation_euler.y=(-1)**i*.35
tube('BraidTie',[(.13,-.073,1.204),(.159,-.073,1.204)],[.009,.009],'teal','Head')
# Bone pendant is the visual story clue; cords and medicine satchel have real geometry.
tube('PendantCord',[(-.052,-.06,1.36),(-.072,-.116,1.29),(0,-.144,1.235),(.072,-.116,1.29),(.052,-.06,1.36)],[.006]*5,'leather','Spine',6)
tube('MoonPendant',[(.014,-.15,1.246),(-.009,-.155,1.237),(-.018,-.155,1.214),(-.007,-.155,1.195),(.016,-.15,1.192)],[.004,.008,.009,.008,.002],'ivory','Spine',9)
tube('SatchelStrap',[(-.18,-.079,1.32),(-.10,-.15,1.17),(.035,-.141,1.04),(.23,-.03,.88)],[.014]*4,'leather','Spine',8)
ell('HerbalSatchel',(.235,.015,.865),(.095,.062,.11),'leather','Hips')
ell('SatchelFlap',(.236,-.037,.895),(.088,.016,.061),'cloth','Hips')
ell('SatchelClasp',(.237,-.055,.872),(.014,.006,.014),'ivory','Hips')
for i in range(4):tube('Herbs',[(.20+i*.018,.025,.93),(.20+i*.024,.022,1.035)],[.004,.002],'trim','Hips',5)
# Bind a single mesh to one rig, with stable named clips.
bpy.ops.object.select_all(action='DESELECT')
for p in parts:p.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();body=bpy.context.object;body.name='HeyinSkin'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
ad=bpy.data.armatures.new('HeyinRig');arm=bpy.data.objects.new('HeyinRig',ad);bpy.context.collection.objects.link(arm)
body.select_set(False);arm.select_set(True);bpy.context.view_layer.objects.active=arm;bpy.ops.object.mode_set(mode='EDIT')
for n,p,parent in bones:
 b=ad.edit_bones.new(n);b.head=p;b.tail=Vector(p)+Vector((0,0,.10))
 if parent:b.parent=ad.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');body.parent=arm;mod=body.modifiers.new('Skin','ARMATURE');mod.object=arm
def reset():
 for pb in arm.pose.bones:pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.location=(0,0,0);pb.scale=(1,1,1)
def rot(n,x=0,y=0,z=0):arm.pose.bones[n].rotation_euler=(x,y,z)
clips={'Idle':72,'Walk':36,'Rest':90,'Talk':80,'Injured':80}
for clip,length in clips.items():
 arm.animation_data_create();arm.animation_data.action=None
 for f in range(0,length+1,2):
  reset();p=f/length*math.tau;rot('Spine',.012*math.sin(p),0,.008*math.sin(p));rot('Head',0,.018*math.sin(p))
  if clip=='Walk':
   for side,phase in [('R',p),('L',p+math.pi)]:
    swing=math.sin(phase);rot('Thigh'+side,-.33*swing);rot('Shin'+side,max(0,swing)*.45);rot('Arm'+side,.24*swing);rot('Forearm'+side,-.14-.05*swing)
  if clip in ['Rest','Injured']:
   arm.pose.bones['Hips'].location.y=-.49;rot('ThighR',-1.15);rot('ThighL',-1.1);rot('ShinR',1.5);rot('ShinL',1.5)
   rot('Spine',.16+.018*math.sin(p));rot('Head',.12);rot('ArmR',-.38);rot('ArmL',-.38);rot('ForearmR',-.6);rot('ForearmL',-.6)
  if clip=='Talk':rot('Head',.025*math.sin(p),0,.05*math.sin(p));rot('ArmL',-.3-.12*math.sin(p));rot('ForearmL',-.55-.12*math.sin(p))
  for pb in arm.pose.bones:
   pb.keyframe_insert(data_path='rotation_euler',frame=f+1,group=pb.name);pb.keyframe_insert(data_path='location',frame=f+1,group=pb.name)
 action=arm.animation_data.action;action.name=clip;tr=arm.animation_data.nla_tracks.new();tr.name=clip;tr.strips.new(clip,1,action);arm.animation_data.action=None
for tr in arm.animation_data.nla_tracks:tr.mute=True
reset();bpy.context.view_layer.update();dims=list(body.dimensions)
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);arm.select_set(True)
for tr in arm.animation_data.nla_tracks:tr.mute=False
bpy.ops.export_scene.gltf(filepath=str(OUT/'heyin.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_cameras=False,export_lights=False)
for tr in arm.animation_data.nla_tracks:tr.mute=True
reset();bpy.context.view_layer.update()
# Presentation collection is excluded from selected GLB export.
world=bpy.data.worlds.new('Studio');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.16,.16,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for n,p,power,size in [('Key',(-3,-4,5),450,4),('Fill',(3,-2,2),240,3),('Rim',(1,3,4),550,3)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,1))
bpy.ops.object.camera_add(location=(2.1,-4.8,2.2));cam=bpy.context.object;aim(cam,(0,0,.89));cam.data.type='ORTHO';cam.data.ortho_scale=2.05;sc.camera=cam
sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=900;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'heyin-source.blend'))
sc.render.filepath=str(OUT/'heyin-full.png');bpy.ops.render.render(write_still=True)
cam.location=(.9,-3,1.72);aim(cam,(0,0,1.48));cam.data.ortho_scale=.62;sc.render.resolution_x=900;sc.render.resolution_y=900;sc.render.filepath=str(OUT/'heyin-portrait.png');bpy.ops.render.render(write_still=True)
report={'dimensions':dims,'triangles':sum(len(p.vertices)-2 for p in body.data.polygons),'bones':[b[0] for b in bones],'clips':clips,'glbBytes':(OUT/'heyin.glb').stat().st_size,'originalAsset':True}
(OUT/'heyin-manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
