"""Run through Blender: --background --python THIS -- ABSOLUTE_PROJECT.

Original GLBs are never overwritten. Static lower-detail meshes keep the
original bounds, origin, material slots and normal/UV data where possible.
"""
import bpy
import json
import pathlib
import sys
from mathutils import Vector

root = pathlib.Path(sys.argv[sys.argv.index('--') + 1]).resolve()
reports = []
for source, ratios in [('fiber-fern', (0.25, 0.08)), ('berry-bush', (0.4, 0.16))]:
    for level, ratio in enumerate(ratios, 1):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(root / 'assets/models' / (source + '.glb')))
        meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        before = sum(len(obj.data.polygons) for obj in meshes)
        for obj in meshes:
            assert not obj.animation_data and not obj.vertex_groups
            vertices = [v.co.copy() for v in obj.data.vertices]
            lo = Vector(tuple(min(v[a] for v in vertices) for a in range(3)))
            hi = Vector(tuple(max(v[a] for v in vertices) for a in range(3)))
            bpy.context.view_layer.objects.active = obj
            modifier = obj.modifiers.new('DistanceLOD', 'DECIMATE')
            modifier.ratio = ratio
            modifier.use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            reduced = [v.co.copy() for v in obj.data.vertices]
            new_lo = Vector(tuple(min(v[a] for v in reduced) for a in range(3)))
            new_hi = Vector(tuple(max(v[a] for v in reduced) for a in range(3)))
            for vertex in obj.data.vertices:
                for axis in range(3):
                    span = new_hi[axis] - new_lo[axis]
                    if span > 0:
                        vertex.co[axis] = lo[axis] + (vertex.co[axis] - new_lo[axis]) * (hi[axis] - lo[axis]) / span
            obj.data.update()
        target = root / 'assets/models' / f'{source}-lod{level}.glb'
        bpy.ops.export_scene.gltf(filepath=str(target), export_format='GLB',
            export_animations=False, export_cameras=False, export_lights=False,
            export_apply=True, export_normals=True, export_texcoords=True)
        after = sum(len(obj.data.polygons) for obj in meshes)
        assert target.stat().st_size > 0 and 0 < after < before
        reports.append(dict(file=str(target), trianglesBefore=before, trianglesAfter=after,
                            materials=len(bpy.data.materials), bytes=target.stat().st_size))
print(json.dumps(reports))
