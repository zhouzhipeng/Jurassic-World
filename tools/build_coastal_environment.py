"""Build the sky sphere and subdivided sea in a disposable Blender process.

Run with Blender --background --python ABSOLUTE_SCRIPT_PATH.
One Blender unit = 100 game units, matching the existing island.
"""
import bpy
import json
import math
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/environment'
bpy.ops.wm.read_factory_settings(use_empty=True)

# Tone-map the CC0 panorama once; the runtime uses a compact embedded PNG.
hdr = bpy.data.images.load(str(OUT / 'kloppenheim_05_puresky_2k.hdr'))
w, h = hdr.size
pixels = np.empty(w * h * 4, dtype=np.float32)
hdr.pixels.foreach_get(pixels)
pixels = pixels.reshape(h, w, 4)
rgb = pixels[:, :, :3] * 0.65
pixels[:, :, :3] = np.clip((rgb * (2.51 * rgb + 0.03)) / (rgb * (2.43 * rgb + 0.59) + 0.14), 0, 1)
pixels[:, :, 3] = 1
sky_image = bpy.data.images.new('Coastal daylight panorama', width=w, height=h)
sky_image.colorspace_settings.name = 'Linear Rec.709'
sky_image.pixels.foreach_set(pixels.ravel())
sky_image.filepath_raw = str(OUT / 'coastal-sky.png')
sky_image.file_format = 'PNG'
sky_image.save()
# Reload the saved sRGB file so the exporter preserves the correct color space.
sky_image = bpy.data.images.load(str(OUT / 'coastal-sky.png'))

def export(obj, filename):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.export_scene.gltf(filepath=str(OUT / filename), export_format='GLB',
        use_selection=True, export_apply=True, export_animations=False,
        export_cameras=False, export_lights=False)
    return {'file': filename, 'triangles': sum(len(p.vertices)-2 for p in obj.data.polygons),
            'dimensions': list(obj.dimensions), 'bytes': (OUT / filename).stat().st_size}

bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=260)
sky = bpy.context.object
sky.name = 'CoastalSky'
for p in sky.data.polygons:
    p.use_smooth = True
mat = bpy.data.materials.new('CoastalSkyPanorama')
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get('Principled BSDF')
tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
tex.image = sky_image
mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
mat.diffuse_color = (0.35, 0.6, 0.8, 1)
sky.data.materials.append(mat)
manifest = [export(sky, 'coastal-sky.glb')]

# Radial grid: dense around the playable coast, progressively coarser offshore.
segments = 192
radii = [0.0] + [i * 1.0 for i in range(1, 101)] + [100 + i * 8 for i in range(1, 31)]
verts = [(0, 0, 0)]
for r in radii[1:]:
    verts.extend((r*math.cos(j*math.tau/segments), r*math.sin(j*math.tau/segments), 0)
                 for j in range(segments))
faces = [(0, 1+j, 1+(j+1)%segments) for j in range(segments)]
for ring in range(len(radii)-2):
    a = 1 + ring*segments
    b = a + segments
    faces.extend((a+j, b+j, b+(j+1)%segments, a+(j+1)%segments) for j in range(segments))
mesh = bpy.data.meshes.new('CoastalSeaGrid')
mesh.from_pydata(verts, [], faces)
mesh.update()
ocean = bpy.data.objects.new('CoastalOcean', mesh)
bpy.context.collection.objects.link(ocean)
for p in mesh.polygons:
    p.use_smooth = True
water = bpy.data.materials.new('CoastalOceanWater')
water.use_nodes = True
water.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (0.015, 0.19, 0.24, 1)
water.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = 0.18
ocean.data.materials.append(water)
manifest.append(export(ocean, 'coastal-ocean.glb'))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'coastal-environment.blend'))
for entry in manifest:
    assert entry['bytes'] > 1000
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(OUT / entry['file']))
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    assert len(meshes) == 1
    assert all(i.packed_file or i.filepath for i in bpy.data.images)
    entry['roundtrip_meshes'] = len(meshes)
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps(manifest))
