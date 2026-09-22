"""Original survival props, authored in Blender metres; GDevelop uses 100 units/m.

Run with Blender --background --python <absolute path>. Only survival-* outputs
are owned by this script. Each source is saved before its GLB export, then the
export is re-imported into the disposable background scene for verification.
"""
import bpy
import json
import math
import random
from pathlib import Path
SOURCE_DIR = Path(__file__).resolve().parents[1] / 'sources/models'
SOURCE_DIR.mkdir(parents=True, exist_ok=True)

OUT = Path(__file__).resolve().parents[1] / 'assets/models'
random.seed(91)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1

def material(name, color, metallic=0, emission=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = .72 if not metallic else .36
    p.inputs['Emission Color'].default_value = (*color, 1)
    p.inputs['Emission Strength'].default_value = emission
    return m

M = {n: material(n, c, metal, glow) for n, c, metal, glow in [
    ('River stone', (.30,.38,.37), 0,0), ('Stone highlight', (.52,.60,.53),0,0),
    ('Fresh turquoise water', (.055,.48,.57),.35,.12),
    ('Copper seam', (.83,.39,.11),.7,0), ('Iron stone', (.17,.22,.27),.1,0),
    ('Charcoal', (.075,.052,.035),0,0), ('Wood', (.38,.20,.085),0,0),
    ('Fire gold', (1,.45,.035),0,1.8), ('Fire heart', (1,.12,.009),0,1.2),
    ('Anvil', (.24,.30,.33),.8,0), ('Linen', (.75,.64,.43),0,0)]}

def finish(obj, name, scale, mat):
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(M[mat])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

def rock(name, pos, scale, mat='River stone'):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=pos)
    return finish(bpy.context.object, name, scale, mat)

def box(name, pos, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    return finish(bpy.context.object, name, scale, mat)

reports = []
for asset in ['spring', 'ore', 'hearth', 'flame', 'forge']:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    if asset == 'spring':
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.45, depth=.055, location=(0,0,.10))
        finish(bpy.context.object, 'Clear spring pool', (1,.84,1), 'Fresh turquoise water')
        for i in range(18):
            a=i*math.tau/18
            rock('Spring bank', (math.cos(a)*1.49, math.sin(a)*1.24,.13),
                 (.22+random.random()*.12,.20+random.random()*.1,.18), 'Stone highlight' if i%3 else 'River stone')
        rock('Spring outflow', (.3,1.15,.40), (.48,.29,.43))
    elif asset == 'ore':
        for i, (x,y,z,s) in enumerate([(-.35,0,.52,.65),(.36,.1,.67,.82),(.03,-.43,.36,.46)]):
            rock('Iron bearing boulder', (x,y,z), (s,s*.80,s), 'Iron stone')
        for i in range(11):
            a=i*2.4
            rock('Copper fleck', (.12+math.cos(a)*.56,math.sin(a)*.46,.57+(i%4)*.19),(.16,.12,.09),'Copper seam')
    elif asset == 'hearth':
        for i in range(12):
            a=i*math.tau/12
            rock('Fire ring', (math.cos(a)*.65,math.sin(a)*.65,.12),(.18,.17,.13))
        for i in range(4):
            o=box('Firewood', (0,(i-1.5)*.19,.13+(i%2)*.12),(1.03,.15,.15),'Charcoal')
            o.rotation_euler.z = .25 if i%2 else -.28
    elif asset == 'flame':
        for i in range(6):
            a=i*math.tau/6
            bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=.18, radius2=.01, depth=.55+(i%3)*.18,
                location=(math.cos(a)*.19,math.sin(a)*.19,.43+(i%3)*.07))
            finish(bpy.context.object, 'Flame tongue', (1,1,1), 'Fire gold' if i%2 else 'Fire heart')
    else:
        for row in range(3):
            for i in range(10):
                a=(i+row*.5)*math.tau/10
                rock('Kiln stone', (-.6+math.cos(a)*.53,math.sin(a)*.53,.18+row*.28),(.23,.22,.19))
        box('Workbench', (.90,0,.67),(1.1,1,.14),'Wood')
        for x in [.48,1.32]:
            for y in [-.36,.36]:box('Bench leg',(x,y,.33),(.12,.12,.66),'Wood')
        box('Anvil foot',(.9,0,.82),(.40,.32,.2),'Anvil')
        box('Anvil face',(.9,0,1.02),(.69,.37,.18),'Anvil')
        box('Tool grip',(.90,.33,.79),(.55,.065,.07),'Wood')
        rock('Hammer head',(1.13,.33,.83),(.12,.11,.10),'Anvil')
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()
    obj=bpy.context.object
    obj.name='Survival_'+asset
    bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.context.view_layer.update()
    dimensions=list(obj.dimensions)
    triangles=sum(len(p.vertices)-2 for p in obj.data.polygons)
    assert all(v > 0 for v in dimensions)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_DIR/f'survival-{asset}-source.blend'))
    destination=OUT/f'survival-{asset}.glb'
    bpy.ops.export_scene.gltf(filepath=str(destination), export_format='GLB',use_selection=True,
        export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
    assert destination.stat().st_size > 100
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(destination))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert meshes and all(o.data.polygons for o in meshes)
    assert not [im for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
    reports.append(dict(asset=asset, dimensions=dimensions, triangles=triangles, bytes=destination.stat().st_size, roundTripMeshes=len(meshes)))
(OUT/'survival-manifest.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print(json.dumps(reports))
