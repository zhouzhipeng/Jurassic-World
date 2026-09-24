"""Build the west hill mine's editable sources and game GLBs.

Run with Blender 5.1: blender --background --python <this file> -- <absolute output dir>
Only files in the requested output directory are replaced. Inspect there before
installing the four GLBs in assets/models and the .blend files in sources/models.
"""
import math
import os
import sys
import bpy
from mathutils import Vector

OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
os.makedirs(OUT, exist_ok=True)


def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for material in list(bpy.data.materials):
        bpy.data.materials.remove(material)


def mat(name, color, metallic=0, roughness=0.8, emission=None):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if emission:
        shader.inputs["Emission Color"].default_value = (*emission, 1)
        shader.inputs["Emission Strength"].default_value = 1.5
    return material


def cube(name, loc, scale, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    if bevel:
        mod = ob.modifiers.new("Chipped corners", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        ob.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return ob


def ball(name, loc, radius, material, segments=12, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=radius, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(material)
    return ob


def beam(name, p, q, radius, material, vertices=7):
    p, q = Vector(p), Vector(q)
    direction = q - p
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=direction.length,
                                        location=(p + q) / 2)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    ob.data.materials.append(material)
    return ob


def export(stem):
    blend = os.path.join(OUT, stem + "-source.blend")
    glb = os.path.join(OUT, stem + ".glb")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_cameras=False,
                              export_lights=False, export_apply=True, export_animations=False)
    assert os.path.getsize(glb) > 1024, glb
    print(f"EXPORTED {stem}: {len(bpy.context.scene.objects)} objects, {os.path.getsize(glb)} bytes")


# 6.2 metre uphill gallery following the existing west hill surface. The
# foundation stays slightly above the game's sampled terrain floor.
reset()
rock = mat("Basalt exterior", (.18, .20, .22))
inside = mat("Dark slate interior", (.095, .115, .13))
floor = mat("Excavated floor", (.16, .15, .14))
timber = mat("Old timber", (.28, .16, .075))
amber = mat("Amber guide lamps", (.95, .42, .06), emission=(.95, .30, .025))
sections = 13
arc = 9


def slope(i):
    t = i / sections
    return 2.35 * (t * (2 - t))


for side in ("inner", "outer"):
    vertices, faces = [], []
    for i in range(sections + 1):
        t = i / sections
        x = -6.2 * t
        z = slope(i)
        width = 1.75 + .35 * max(0, (t - .65) / .35)
        if side == "outer":
            width += .38
        profile = [(-width, -.08), (-width, 1.3)]
        for j in range(1, arc):
            theta = math.pi * j / arc
            profile.append((-width * math.cos(theta), 1.3 + (2.25 if side == "outer" else 1.9) * math.sin(theta)))
        profile.extend([(width, 1.3), (width, -.08)])
        for y, h in profile:
            jitter = .05 * math.sin(i * 7.2 + y * 3) if side == "outer" else 0
            vertices.append((x, y + jitter, z + h + jitter))
    stride = arc + 3
    for i in range(sections):
        for j in range(stride - 1):
            a = i * stride + j
            face = (a, a + 1, a + stride + 1, a + stride)
            faces.append(face if side == "outer" else tuple(reversed(face)))
    mesh = bpy.data.meshes.new("Gallery " + side)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    ob = bpy.data.objects.new("West hill gallery " + side, mesh)
    bpy.context.collection.objects.link(ob)
    mesh.materials.append(rock if side == "outer" else inside)

for i in range(sections):
    x = -6.2 * (i + .5) / sections
    z = (slope(i) + slope(i + 1)) / 2
    cube(f"Stone floor {i:02}", (x, 0, z - .12), (6.2 / sections + .03, 3.35, .24), floor)

for i in (0, 4, 8, 12):
    x = -6.2 * i / sections
    z = slope(i)
    for side in (-1, 1):
        beam(f"Timber upright {i} {side}", (x, side * 1.53, z), (x, side * 1.53, z + 2.55), .09, timber)
    beam(f"Timber crossbar {i}", (x, -1.57, z + 2.5), (x, 1.57, z + 2.5), .09, timber)
for i in (1, 5, 9, 12):
    x = -6.2 * i / sections
    for side in (-1, 1):
        ball(f"Waylight {i} {side}", (x, side * 1.42, slope(i) + 1.65), .12, amber, 8, 6)

cube("Back wall", (-6.26, 0, slope(13) + 1.15), (.27, 3.8, 2.7), inside, .12)
export("hill-mine-gallery")

# Mineral veins show three differently coloured metal seams on one rock.
reset()
ore = mat("Dark ore stone", (.16, .18, .20))
titanium = mat("Titanium", (.63, .72, .76), metallic=.8, roughness=.34)
cobalt = mat("Cobalt", (.13, .36, .72), metallic=.6, roughness=.32)
gold = mat("Gold", (.85, .57, .13), metallic=.8, roughness=.28)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=.64, location=(0, 0, .36))
bpy.context.object.name = "Metal vein boulder"
bpy.context.object.scale = (1.2, .82, .64)
bpy.context.object.data.materials.append(ore)
for i, m in enumerate((titanium, cobalt, gold, titanium, cobalt, gold)):
    a = i * math.tau / 6
    beam("Exposed metal seam", (.38 * math.cos(a), .38 * math.sin(a), .57),
         (.50 * math.cos(a + .3), .50 * math.sin(a + .3), .92), .065, m, 5)
export("hill-mine-vein")

# Two crystal colours in a cluster; gameplay instance Kind chooses the loot.
reset()
base = mat("Crystal matrix", (.11, .13, .17))
violet = mat("Amethyst", (.52, .18, .82), roughness=.14, emission=(.14, .03, .23))
cyan = mat("Azure crystal", (.11, .69, .78), roughness=.14, emission=(.025, .17, .2))
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=.54, location=(0, 0, .22))
bpy.context.object.name = "Crystal matrix"
bpy.context.object.scale = (1.25, .95, .45)
bpy.context.object.data.materials.append(base)
for i in range(9):
    a = i * math.tau / 9
    x, y = .34 * math.cos(a), .27 * math.sin(a)
    h = .5 + .18 * (i % 3)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=.15, radius2=0, depth=h,
                                    location=(x, y, .36 + h / 2))
    ob = bpy.context.object
    ob.name = "Amethyst shard" if i % 2 else "Azure shard"
    ob.rotation_euler[1] = .2 * math.sin(a)
    ob.data.materials.append(violet if i % 2 else cyan)
export("hill-mine-crystal")

# Large cave spider, about 1.3 m across.
reset()
chitin = mat("Spider chitin", (.18, .085, .08))
dark = mat("Spider limbs", (.085, .07, .065))
eyes = mat("Spider eyes", (.95, .08, .025), emission=(.55, .025, .005))
ball("Spider abdomen", (-.3, 0, .38), .35, chitin)
ball("Spider thorax", (.18, 0, .38), .25, dark)
for side in (-1, 1):
    for i in range(4):
        x = .1 - i * .18
        joint = (x + .13 * (1 - i / 4), side * (.46 + i * .035), .67)
        tip = (x + (.34 - i * .15), side * (1.05 + i * .05), .08)
        beam("Spider upper leg", (x, side * .18, .39), joint, .052, chitin)
        beam("Spider lower leg", joint, tip, .035, dark)
    for i in (-1, 1):
        ball("Spider eye", (.34, side * .13 + i * .055, .47), .042, eyes, 8, 6)
export("hill-mine-spider")

# Coiled oversized cave serpent with a raised head and amber eyes.
reset()
scales = mat("Serpent scales", (.16, .27, .20))
belly = mat("Serpent belly", (.43, .40, .23))
eyes = mat("Serpent eyes", (.96, .47, .06), emission=(.5, .17, .01))
points = []
for i in range(18):
    t = i / 17
    points.append((-.55 + 1.15 * t, .28 * math.sin(t * math.tau * 1.35),
                   .16 + .15 * t + .4 * max(0, (t - .76) / .24)))
for i in range(len(points) - 1):
    beam("Serpent body segment", points[i], points[i + 1], .19 * (1 - .48 * i / 17), scales, 9)
ball("Serpent head", (.66, .24, .79), .24, scales)
cube("Lower jaw", (.82, .24, .62), (.30, .24, .07), belly, .025)
for side in (-1, 1):
    ball("Serpent eye", (.75, .24 + side * .16, .88), .045, eyes, 8, 6)
export("hill-mine-serpent")
