"""Export a small pair of sand impressions. Run with Blender -- OUT_DIRECTORY."""
import bpy
import json
import math
import sys
from pathlib import Path

out = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

mat = bpy.data.materials.new('Pressed damp sand')
mat.diffuse_color = (0.24, 0.19, 0.13, 1)
mat.use_nodes = True
shader = mat.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value = mat.diffuse_color
shader.inputs['Roughness'].default_value = 1

def impression(cx, cy, turn):
    outline = [(-.10, -.18), (.06, -.19), (.105, -.11), (.10, .04),
               (.13, .13), (.09, .20), (-.05, .19), (-.11, .10), (-.12, -.05)]
    ct, st = math.cos(turn), math.sin(turn)
    points = [(cx + x * ct - y * st, cy + x * st + y * ct, .002)
              for x, y in outline]
    mesh = bpy.data.meshes.new('Impression mesh')
    mesh.from_pydata(points, [], [tuple(range(len(points)))])
    mesh.materials.append(mat)
    obj = bpy.data.objects.new('Sand impression', mesh)
    bpy.context.collection.objects.link(obj)

impression(-.16, -.11, -.10)
impression(.16, .11, .10)
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'sand-footprints-source.blend'))
bpy.ops.export_scene.gltf(filepath=str(out / 'sand-footprints.glb'),
                          export_format='GLB', export_animations=False,
                          export_cameras=False, export_lights=False)
print('FOOTPRINT_RESULT', json.dumps({'meshes': 2,
      'glbBytes': (out / 'sand-footprints.glb').stat().st_size}))
