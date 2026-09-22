"""Original timber kit: 3 m sockets, 3 m stories, model origins at socket base."""
import bpy, json
from pathlib import Path
SOURCE_DIR = Path(__file__).resolve().parents[1] / 'sources/models'
SOURCE_DIR.mkdir(parents=True, exist_ok=True)
P=Path(__file__).resolve().parents[1]/'assets/models'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,a=1):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,a); m.use_nodes=True
 s=m.node_tree.nodes.get('Principled BSDF'); s.inputs['Base Color'].default_value=(*c,a); s.inputs['Alpha'].default_value=a; s.inputs['Roughness'].default_value=.85
 if a<1:m.surface_render_method='DITHERED'
 return m
m={n:mat(n,c) for n,c in {'frame':(.30,.18,.085),'wood':(.64,.43,.23),'light':(.73,.55,.32),'iron':(.22,.27,.26),'rope':(.76,.68,.46)}.items()}
def box(n,p,s,material='wood'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=n; o.scale=s; o.data.materials.append(m[material]); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
reports=[]
for name in ['foundation','pillar','wall','doorframe','ceiling','door','stairs']:
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 if name in ['foundation','ceiling']:
  # Foundation top at +20 units; ceiling top at its socket height.
  top=.2 if name=='foundation' else 0
  for i in range(10):box('Deck plank',((i-4.5)*.3,0,top-.05),(.29,3,.1),'light' if i%3==0 else 'wood')
  for x in [-1.37,1.37]:box('Joist',(x,0,top-.16),(.20,3,.22),'frame')
  for y in [-1.38,1.38]:box('End beam',(0,y,top-.16),(3,.22,.22),'frame')
  if name=='foundation':
   for x in [-1.33,1.33]:
    for y in [-1.33,1.33]:box('Foot',(x,y,-.12),(.3,.3,.5),'frame')
 elif name=='pillar':
  box('Timber post',(0,0,1.5),(.28,.28,3),'frame')
  for z in [.1,2.9]:box('Collar',(0,0,z),(.4,.4,.2),'wood')
  for z in [.45,2.55]:box('Binding',(0,0,z),(.3,.3,.10),'rope')
 elif name in ['wall','doorframe']:
  for x in [-1.4,1.4]:box('Post',(x,0,1.5),(.2,.24,3),'frame')
  box('Lintel',(0,0,2.88),(3,.24,.24),'frame')
  if name=='wall':
   for i in range(10):box('Wall plank',((i-4.5)*.3,0,1.46),(.29,.15,2.82),'light' if i%3==0 else 'wood')
   for z in [.3,2.45]:box('Brace',(0,-.10,z),(2.85,.1,.16),'frame')
  else:
   # Clear opening: 160 wide / 245 high, enough for the survivor.
   for x in [-1.18,1.18]:box('Side panel',(x,0,1.42),(.64,.15,2.84))
   for x in [-.88,.88]:box('Door jamb',(x,0,1.28),(.16,.25,2.56),'frame')
   box('Door header',(0,0,2.70),(1.8,.24,.60),'wood')
 elif name=='door':
  for i in range(6):box('Door board',((i-2.5)*.26,0,1.2),(.255,.12,2.4),'wood')
  for z in [.3,2.10]:box('Strap',(0,-.09,z),(1.5,.075,.10),'iron')
  box('Latch',(.5,-.13,1.12),(.24,.10,.09),'iron')
 elif name=='stairs':
  # Ascends toward -Y in game (toward +Y in Blender).
  for i in range(12):box('Tread',(0,-1.5+(i+.5)*.25,(i+1)*.25-.06),(2.4,.25,.12),'light')
  for x in [-1.13,1.13]:
   o=box('Stringer',(x,0,1.4),(.14,4.1,.18),'frame'); o.rotation_euler.x=.785398
 bpy.ops.object.select_all(action='SELECT'); bpy.context.view_layer.objects.active=bpy.context.selected_objects[0]; bpy.ops.object.join(); o=bpy.context.object; o.name='Modular_'+name
 bpy.context.scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR'); bpy.ops.object.transform_apply(location=False,rotation=True,scale=True); bpy.context.view_layer.update()
 dims=list(o.dimensions); triangles=sum(len(p.vertices)-2 for p in o.data.polygons)
 bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_DIR/f'modular-{name}-source.blend'))
 for suffix,color in [('',None),('-valid',(.12,.85,.52)),('-invalid',(.95,.16,.10))]:
  if color:
   o.data.materials.clear(); o.data.materials.append(mat(name+suffix,color,.38))
   for p in o.data.polygons:p.material_index=0
  out=P/f'modular-{name}{suffix}.glb'
  bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
  assert out.stat().st_size>100
 reports.append(dict(name=name,dimensions=dims,triangles=triangles))
(P/'modular-manifest.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print(json.dumps(reports))
