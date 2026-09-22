"""Blender 5.1: --background --python ABS_SCRIPT -- ABS_OUTPUT_DIRECTORY.

Reads the preserved expanded-island source; writes only to the explicit output
directory. Generates editable blend, partitioned GLB and height-based radar SVG.
Uses mountain_profile.py for the same height function as the native game events.
"""
import bpy, bmesh, math, random, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from mountain_profile import height, BOUNDS
from partition_island import partition
OUT = Path(sys.argv[sys.argv.index('--')+1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
random.seed(922)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'sources/models/island-expanded-source.blend'))
old = bpy.context.scene.objects[0]
assert old.type == 'MESH' and len(old.data.vertices) == 9488
mats = list(old.data.materials)
# Remove original broad grass slab and sand island. Preserve authored camp and
# small paths, lifting each small ground detail onto the new height field.
bm = bmesh.new(); bm.from_mesh(old.data)
bm.verts.ensure_lookup_table()
visited = set(); remove = []
for seed in bm.verts:
    if seed in visited: continue
    todo = [seed]; visited.add(seed); component = []
    while todo:
        v = todo.pop(); component.append(v)
        for e in v.link_edges:
            w = e.other_vert(v)
            if w not in visited: visited.add(w); todo.append(w)
    xs = [v.co.x for v in component]; ys = [v.co.y for v in component]
    cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
    faces = {f for v in component for f in v.link_faces}
    names = {mats[f.material_index].name for f in faces}
    if ('grass' in names and max(xs)-min(xs)>40) or ('sand' in names and max(xs)-min(xs)>80):
        remove.extend(component); continue
    # The old distant cliffs are now inside the expanded playable region.
    # Replace that non-walkable backdrop with the continuous mountain surface.
    if cy > 40 and names <= {'rockLight','leafLight','foam'}:
        remove.extend(component); continue
    if names == {'water'}: continue
    ground_detail = names <= {'sand','grassLight'}
    for v in component:
        v.co.z += height(v.co.x*100, -v.co.y*100)/100 if ground_detail else height(cx*100,-cy*100)/100
bmesh.ops.delete(bm, geom=remove, context='VERTS')
bm.to_mesh(old.data); bm.free()

def material(name, color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=.94
    return m
terrain_mats=[material('Valley moss',(.29,.43,.14)),material('Fern slopes',(.38,.49,.19)),
              material('Mountain heath',(.43,.48,.24)),material('Exposed granite',(.46,.49,.44)),
              material('Summit stone',(.62,.62,.53)),material('Coastal sand',(.72,.64,.43))]
# Keep the 1 m surface accurate on steep slopes; camera queries use separate
# height-grid traversal and component bounds from build_camera_bounds.py.
verts=[]; faces=[]; nx=129; ny=130
for j in range(ny):
    y=-62+j
    for i in range(nx):
        x=-64+i
        edge=min(64-abs(x),y+62,67-y)
        z=height(x*100,-y*100)/100 - max(0,3-edge)*.8
        verts.append((x,y,z))
for j in range(ny-1):
    for i in range(nx-1):
        k=j*nx+i; faces.extend([(k,k+1,k+nx+1),(k,k+nx+1,k+nx)])
me=bpy.data.meshes.new('Mountain surface');me.from_pydata(verts,[],faces);me.update()
terrain=bpy.data.objects.new('Mountain surface',me);bpy.context.collection.objects.link(terrain)
for m in terrain_mats:me.materials.append(m)
for p in me.polygons:
    z=sum(me.vertices[i].co.z for i in p.vertices)/3
    c=p.center; edge=min(64-abs(c.x),c.y+62,67-c.y)
    p.material_index=5 if edge<4 else 4 if z>22 else 3 if z>14 else 2 if z>8 else (0 if c.x<0 else 1)
    p.use_smooth=True

def ico(name, loc, scale, mat, sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=loc)
    o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return o
wood=next(m for m in mats if m.name=='wood'); leaf=next(m for m in mats if m.name=='leaf'); rock=terrain_mats[3]
# Clear sightlines through valley floors; groves and rocky outcrops distinguish
# the new exploration regions without placing decorative obstacles on camp.
for n in range(90):
    x=random.uniform(-57,57); y=random.uniform(-53,59)
    if abs(x)<30 and -28<y<35:continue
    z=height(x*100,-y*100)/100
    if z>18:
        ico('Highland outcrop',(x,y,z+.15),(random.uniform(.5,1.2),.8,.65),rock)
        continue
    s=random.uniform(.7,1.3)
    bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=.22*s,radius2=.13*s,depth=3.8*s,location=(x,y,z+1.9*s))
    bpy.context.object.name='Outer woodland trunk';bpy.context.object.data.materials.append(wood)
    ico('Outer woodland crown',(x,y,z+4*s),(1.9*s,1.6*s,1.35*s),leaf,2)

bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=old
bpy.ops.object.convert(target='MESH');bpy.ops.object.join();old.name='island'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
bpy.context.view_layer.update()
triangles=sum(len(p.vertices)-2 for p in old.data.polygons)
dimensions=[float(v)*100 for v in old.dimensions]
assert triangles<100000 and all(abs(v-1)<1e-6 for v in old.scale)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island-mountain-source.blend'))
raw=OUT/'island-unpartitioned.glb'
bpy.ops.export_scene.gltf(filepath=str(raw),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
partition(raw,OUT/'island.glb')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(OUT/'island.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert meshes and sum(len(o.data.polygons) for o in meshes)==triangles
assert not [im for im in bpy.data.images if im.source=='FILE' and not im.packed_file and im.filepath]
report={'triangles':triangles,'meshesAfterRoundTrip':len(meshes),'bytes':(OUT/'island.glb').stat().st_size,
        'gdevelopSize':dimensions,
        'playableBounds':BOUNDS,'areaRatio':(BOUNDS[1]-BOUNDS[0])*(BOUNDS[3]-BOUNDS[2])/(5200*5100),
        'summitHeight':height(2200,-4450),'source':'sources/models/island-expanded-source.blend'}
(OUT/'mountain-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
# Keep radar artwork reproducible without rebuilding the model.
from render_radar import render_radar
render_radar(OUT/'radar-map.svg')
print('MOUNTAIN_RESULT',json.dumps(report))
