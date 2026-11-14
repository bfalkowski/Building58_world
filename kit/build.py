"""Small builders every scene uses: boxes, cylinders, materials and lights, each in one call."""
import math

import bpy


def material(name, color, rough=0.6, metal=0.0, emit=None, strength=0.0):
    """A plain material. color is (r, g, b) from 0 to 1. emit makes it glow."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = strength
    return m


def _finish(obj, name, mat):
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj


def box(name, size, at, mat=None, rot=(0, 0, 0)):
    """A box of size (x, y, z) in meters, centered at `at`."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=at, rotation=rot)
    obj = bpy.context.object
    obj.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(obj, name, mat)


def cylinder(name, radius, depth, at, mat=None, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=at, rotation=rot, vertices=verts)
    return _finish(bpy.context.object, name, mat)


def cone(name, r1, r2, depth, at, mat=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, location=at, rotation=rot, vertices=32)
    return _finish(bpy.context.object, name, mat)


def text(name, body, at, size, mat=None, rot=(math.pi / 2, 0, 0), extrude=0.002):
    """Raised letters, standing up and facing -y by default."""
    bpy.ops.object.text_add(location=at, rotation=rot)
    obj = bpy.context.object
    obj.data.body = body
    obj.data.size = size
    obj.data.extrude = extrude
    obj.data.align_x = "CENTER"
    return _finish(obj, name, mat)


def light(kind, at, energy, color=(1, 1, 1), rot=(0, 0, 0), size=None, spot=None, blend=0.15, shadow=True):
    bpy.ops.object.light_add(type=kind, location=at, rotation=rot)
    obj = bpy.context.object
    obj.data.energy = energy
    obj.data.color = color
    obj.data.use_shadow = shadow
    if size is not None:
        if kind == "AREA":
            obj.data.size = size
        else:
            obj.data.shadow_soft_size = size
    if spot is not None:
        obj.data.spot_size = spot
        obj.data.spot_blend = blend
    return obj


def aim(obj, target):
    """Turn a camera or light to look at a point."""
    from mathutils import Vector
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return obj


def haze(scene, density=0.02, color=(0.55, 0.6, 0.7)):
    """A thin fog in the air, so light beams show."""
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    bg.inputs["Color"].default_value = (0.003, 0.004, 0.006, 1)
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = density
    vol.inputs["Color"].default_value = (*color, 1)
    nt.links.new(vol.outputs["Volume"], nt.nodes["World Output"].inputs["Volume"])


def sphere(name, radius, at, mat=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=at, segments=24, ring_count=12)
    obj = bpy.context.object
    obj.scale = scale
    bpy.ops.object.shade_smooth()
    return _finish(obj, name, mat)


def figure(name, at, mats, sitting=False, hat=True):
    """A plain person, standing on `at` or sitting on a seat at `at`: legs, body, head and a hat.
    No face and no likeness. mats needs "coat", "skin" and "hat"."""
    x, y, z = at
    waist = z if sitting else z + 0.85
    if not sitting:
        for side in (-1, 1):
            cylinder(f"{name} leg {side}", 0.075, 0.85, (x + side * 0.09, y, z + 0.425), mats["coat"], verts=12)
    body = cylinder(f"{name} body", 0.2, 0.6, (x, y, waist + 0.3), mats["coat"], verts=16)
    body.scale = (1, 0.7, 1)
    top = waist + 0.6
    sphere(f"{name} shoulders", 0.21, (x, y, top), mats["coat"], scale=(1, 0.7, 0.4))
    sphere(f"{name} head", 0.11, (x, y, top + 0.19), mats["skin"])
    if hat:
        cylinder(f"{name} hat brim", 0.16, 0.015, (x, y, top + 0.27), mats["hat"])
        cylinder(f"{name} hat crown", 0.095, 0.1, (x, y, top + 0.32), mats["hat"])
