import bpy, math, random, json
from pathlib import Path
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
    bpy.ops.export_scene.gltf(filepath=str(P/(name+'-pending.glb')),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
    return o,{'file':name+'.glb','dimensions':dims,'triangles':sum(len(f.vertices)-2 for f in o.data.polygons)}

# Broad readable island shapes, a flat walkable camp, sea and distant skyline.
box('Sea',(0,25,-1.1),(180,180,.3),'water')
ell('Sand island',(0,3,-3.5),(46,46,3.3),'sand',3)
box('Camp grass',(0,3,-.5),(58,58,1),'grass',.25)
for i in range(135):
    x=random.uniform(-28,28);y=random.uniform(-25,31)
    if abs(x)<4 and y<15:continue
    ell('Ground patch',(x,y,-.15),(random.uniform(2,4),random.uniform(2,4),.2),'grassLight',1)
# Winding path deliberately open from arrival to hut and dinosaur.
for i in range(15):ell('Path',(math.sin(i*.3)*2,-15+i*2,.01),(2.3,2,.05),'sand',1)
# House to the left: post-and-beam timber with visible plank modules.
cx,cy=-9,7
for i in range(12):box('Floor plank',(cx-3+i*.55,cy,.18),(.51,6,.25),'plank',.03)
for dx in [-3,3]:
    for dy in [-2.6,2.6]:beam('House post',(cx+dx,cy+dy,0),(cx+dx,cy+dy,3.3),.16,'wood')
for row in range(7):
    z=.4+row*.38
    box('Rear wall',(cx,cy+2.6,z),(6,.18,.33),'plank')
    for dx in [-3,3]:box('Side wall',(cx+dx,cy,z),(.18,5.2,.33),'plank')
    box('Front left',(cx-2.15,cy-2.6,z),(1.7,.18,.33),'plank')
    box('Front right',(cx+2.15,cy-2.6,z),(1.7,.18,.33),'plank')
for side in [-1,1]:
    verts=[(cx,cy-3.2,4.6),(cx,cy+3.2,4.6),(cx+side*3.7,cy+3.2,2.9),(cx+side*3.7,cy-3.2,2.9)]
    roof=mesh('Thatch roof',verts,[(0,1,2,3)],'roof')
    for i in range(17):
        y=cy-3.2+i*.4;beam('Thatch ridge',(cx,y,4.62),(cx+side*3.75,y,2.85),.09,'roof',verts=5)
box('Step',(cx,cy-3.15,.04),(2,1,.12),'plank')
# Table, crates, split wood, fences, a campfire.
box('Workbench top',(-12,1,1.15),(2.8,1.1,.18),'plank')
for x in [-13,-11]:
    for y in [.65,1.35]:beam('Table leg',(x,y,0),(x,y,1.1),.10,'wood')
for x,y in [(-5,6),(-5,7.4),(-6,8)]:
    box('Crate',(x,y,.5),(1.1,1,.95),'plank',.05)
    for z in [.15,.8]:box('Crate brace',(x,y-.51,z),(1.2,.10,.12),'wood')
for i in range(7):beam('Gathered logs',(-13,10+i*.28,.3),(-10,10+i*.28,.3),.19,'wood')
for i in range(7):
    x=-15+i*2;beam('Fence post',(x,12,0),(x,12,1.7),.13,'wood')
for z in [.6,1.3]:beam('Fence rail',(-15,12,z),(-3,12,z),.09,'plank')
for i in range(9):
    t=i*math.tau/9;ell('Fire stone',(-5+math.cos(t)*.8,-1+math.sin(t)*.8,.15),(.24,.24,.18),'rock',1)
for t in [0,1.5]:beam('Firewood',(-5-math.cos(t)*.65,-1-math.sin(t)*.65,.16),(-5+math.cos(t)*.65,-1+math.sin(t)*.65,.16),.12,'wood')
for i in range(4):beam('Flame',(-5+random.uniform(-.2,.2),-1+random.uniform(-.2,.2),.2),(-5,-1,.9+random.random()*.35),.22,'flame',0,5)
# Tree silhouettes, layered broad crowns.
def tree(x,y,s):
    beam('Trunk',(x,y,0),(x+.2*s,y,4.3*s),.28*s,'wood',.12*s)
    for dx,dy in [(-1,0),(1,.5),(.1,-1)]:
        beam('Branch',(x,y,2.5*s),(x+dx*s,y+dy*s,4.1*s),.13*s,'wood',.045*s)
        ell('Canopy',(x+dx*s,y+dy*s,4.7*s),(2*s,1.7*s,.95*s),'leafLight' if dx>0 else 'leaf',2)
for x,y,s in [(-29,-12,1.3),(-29,17,1.5),(-20,32,1.25),(29,18,1.4),(30,1,1.2),(13,33,1.8),(-28,30,1.6),(-22,-27,1.1),(29,30,1.5),(12,-28,1.3),(-8,-28,1.5),(29,-20,1.4)]:tree(x,y,s)
for i in range(65):
    x=random.choice([-1,1])*random.uniform(30,36);y=random.uniform(-26,38)
    ell('Coastal boulder',(x,y,random.uniform(-.4,.1)),(random.uniform(.6,1.6),random.uniform(.8,1.8),random.uniform(.6,1.3)),'rockLight',1)
for i in range(420):
    x=random.uniform(-28,28);y=random.uniform(-25,31)
    if abs(x)<3 or (-13<x<-5 and 3<y<11):continue
    h=random.uniform(.25,.65)
    mesh('Grass tuft',[(x-.14,y,0),(x+.14,y,0),(x+.18,y,h),(x,y-.13,0),(x,y+.13,0),(x-.12,y,h*.8)],[(0,1,2),(3,4,5)],'grassLight')
for i in range(14):
    x=-40+i*6;y=48+random.uniform(0,15);h=random.uniform(6,15)
    ell('Distant cliff',(x,y,h/2-1),(5,7,h),'rockLight',1)
    ell('Cliff canopy',(x,y,h*1.25),(5,6,1.3),'leafLight',1)
box('Waterfall',(-14,44,6),(1.8,.12,12),'foam')
# Branch paths connect old camp to the expanded resource clearings.
for side in [-1,1]:
    for i in range(12):
        ell('Explorer path',(side*(3+i*2),-3+math.sin(i*.4)*2,.01),(1.3,1.2,.035),'sand',1)
for i in range(12):
    ell('North trail',(4+math.sin(i*.4)*2,10+i*1.8,.01),(1.3,1.5,.035),'sand',1)

env,envinfo=join_export('island',list(bpy.context.scene.objects))


# Inspect before replacing the registered asset. The original source blend is retained.
assert len(bpy.context.scene.objects)==1
assert all(abs(v-1)<1e-6 for v in env.scale)
assert abs(env.dimensions.x-180)<.01 and abs(env.dimensions.y-180)<.01
assert envinfo['triangles'] < 60000
pending=P/'island-pending.glb'
assert pending.read_bytes()[:4]==b'glTF' and pending.stat().st_size>10000
bpy.ops.wm.save_as_mainfile(filepath=str(P/'island-expanded-source.blend'))
pending.replace(P/'island.glb')
(P/'island-expanded-manifest.json').write_text(json.dumps(envinfo,indent=2),encoding='utf-8')
print('EXPANDED_ISLAND',json.dumps(envinfo))
