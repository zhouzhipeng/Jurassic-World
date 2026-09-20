"""Original low-poly building kit, including translucent placement silhouettes."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]/'assets/models'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(n,c,alpha=1):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,alpha);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,alpha);bs.inputs['Alpha'].default_value=alpha;bs.inputs['Roughness'].default_value=.88
 if alpha<1:m.surface_render_method='DITHERED'
 return m
m={n:mat(n,c) for n,c in {'timber':(.38,.22,.10),'plank':(.62,.41,.21),'thatch':(.69,.52,.22),'rope':(.67,.58,.37),'stone':(.42,.47,.44),'fire':(1,.38,.025)}.items()}
def box(n,p,s,c):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.scale=s;o.data.materials.append(m[c]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def beam(n,a,b,r,c,r2=None):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=r,radius2=r2 if r2 is not None else r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m[c]);return o
reports=[]
for name in ['shelter','palisade','campfire']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 if name=='shelter':
  # Open front (-Y in Blender / +Y in GDevelop); three enclosing walls.
  for x in [-1.9,1.9]:
   for y in [-1.7,1.7]:beam('Upright',(x,y,0),(x,y,2.7),.12,'timber')
  for z in [.25,.65,1.05,1.45,1.85,2.25]:
   box('Back boards',(0,1.7,z),(3.8,.16,.37),'plank')
   for x in [-1.9,1.9]:box('Side boards',(x,0,z),(.16,3.4,.37),'plank')
  for side in [-1,1]:
   roof=box('Thatch roof',(side*1.1,0,2.94),(2.5,4.05,.18),'thatch');roof.rotation_euler.y=side*.30
   beam('Roof brace',(side*1.9,-1.7,2.55),(0,-1.7,3.3),.09,'timber')
  beam('Ridge',(0,-2.04,3.31),(0,2.04,3.31),.095,'timber')
  box('Bedroll',(.8,.7,.12),(1,1.6,.18),'rope')
 elif name=='palisade':
  for i in range(11):
   x=(i-5)*.36;beam('Palisade post',(x,0,0),(x,0,2.2),.17,'timber');beam('Point',(x,0,2.2),(x,0,2.65),.17,'plank',0)
  for z in [.7,1.6]:box('Crossbar',(0,-.2,z),(4,.12,.16),'plank')
 else:
  for i in range(9):
   a=i*math.tau/9;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(math.cos(a)*.62,math.sin(a)*.62,.15));o=bpy.context.object;o.scale=(.20,.20,.17);o.data.materials.append(m['stone'])
  for a in [0,math.pi/3,-math.pi/3]:beam('Log',(-.5*math.cos(a),-.5*math.sin(a),.18),(.5*math.cos(a),.5*math.sin(a),.18),.095,'timber')
  for x,y,h in [(0,0,.95),(.2,.12,.65),(-.17,-.15,.72)]:beam('Flame',(x,y,.24),(x+.08,y,h),.20,'fire',.01)
 bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name='Build_'+name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);bpy.context.view_layer.update()
 dims=list(o.dimensions);bpy.ops.wm.save_as_mainfile(filepath=str(P/('build-'+name+'-source.blend')))
 def export(suffix):bpy.ops.export_scene.gltf(filepath=str(P/('build-'+name+suffix+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
 export('');original=list(o.data.materials)
 for suffix,c in [('-valid',(.16,.85,.52)),('-invalid',(.95,.19,.12))]:
  o.data.materials.clear();o.data.materials.append(mat(name+suffix,c,.36))
  for poly in o.data.polygons:poly.material_index=0
  export(suffix)
 reports.append({'name':name,'dimensions':dims,'triangles':sum(len(f.vertices)-2 for f in o.data.polygons)})
(P/'construction-manifest.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports))
