import bpy,json
from pathlib import Path
SOURCE_DIR = Path(__file__).resolve().parents[1] / 'sources/models'
SOURCE_DIR.mkdir(parents=True, exist_ok=True)
from mathutils import Vector
P=Path(__file__).resolve().parents[1]/'assets/models'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for name,a,b,r1,r2,c in [('Shaft',(0,.15,0),(0,-1.65,0),.035,.035,(.35,.19,.075)),('Stone tip',(0,-1.65,0),(0,-2.1,0),.115,.005,(.43,.48,.46))]:
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=r1,radius2=r2,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);o.data.materials.append(m)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.join();o=bpy.context.object;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
bpy.ops.export_scene.gltf(filepath=str(P/'combat-spear.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE_DIR/'combat-spear-source.blend'))
