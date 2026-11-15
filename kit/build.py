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
    obj["shadow"] = shadow  # the viewer reads this: a browser can afford only a few shadow lights
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


def rod(name, a, b, radius, mat=None, verts=10):
    """A round bar from point a to point b: a limb, a rail, a rope."""
    from mathutils import Vector
    a, b = Vector(a), Vector(b)
    d = b - a
    obj = cylinder(name, radius, d.length, (a + b) / 2, mat, verts=verts)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = d.to_track_quat("Z", "Y")
    return obj


def join(name, parts):
    """Merge parts into one object, so a browser draws it in one go. Materials are kept."""
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    return obj


def mesh(name, verts, faces, mats, face_mats=None, smooth=False):
    """An object from a list of points and faces. face_mats gives each face's material number."""
    import bmesh
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    for m in mats:
        me.materials.append(m)
    if face_mats:
        for f, k in zip(me.polygons, face_mats):
            f.material_index = k
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = smooth
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    return obj


def hull_width(t):
    """A ship's half width at deck, from stern (t = -1) to bow (t = 1), as a share of the beam."""
    if t > 0.35:
        return max(0.02, math.cos((t - 0.35) / 0.65 * math.pi / 2))
    if t < -0.75:
        return 1 - 0.6 * ((-t - 0.75) / 0.25) ** 2
    return 1.0


def hull(name, length, beam, deck, keel, waterline, mats):
    """A ship's hull: a pointed bow, a rounded stern, and a deck that rises toward the bow.
    mats is (topsides, bottom paint, deck). Paint below `waterline` is the bottom paint."""
    stations = [-1.0, -0.97, -0.9, -0.8, -0.6, -0.2, 0.2, 0.4, 0.55, 0.7, 0.82, 0.92, 1.0]
    verts, faces, fm = [], [], []
    for t in stations:
        w = beam / 2 * hull_width(t)
        y = t * length / 2
        top = deck + 0.5 * max(0.0, t - 0.3) ** 2 + 0.15 * max(0.0, -t - 0.8)
        # The bow rakes: the keel stops short of the stem.
        yk = min(y, 0.42 * length)
        verts += [(-w, y, top), (w, y, top), (w * 0.92, y, waterline), (-w * 0.92, y, waterline),
                  (-w * 0.55, yk, keel), (w * 0.55, yk, keel)]
    n = len(stations)
    for i in range(n - 1):
        a, b = 6 * i, 6 * (i + 1)
        faces += [(a + 1, b + 1, b + 2, a + 2), (a + 0, a + 3, b + 3, b + 0),  # sides, above water
                  (a + 2, b + 2, b + 5, a + 5), (a + 3, a + 4, b + 4, b + 3),  # sides, below
                  (a + 5, b + 5, b + 4, a + 4),  # keel
                  (a + 0, b + 0, b + 1, a + 1)]  # deck
        fm += [0, 0, 1, 1, 1, 2]
    e = 6 * (n - 1)
    faces += [(0, 1, 2, 5, 4, 3), (e, e + 1, e + 2, e + 5, e + 4, e + 3)]  # the stern, and the stem
    fm += [0, 0]
    return mesh(name, verts, faces, list(mats), fm)


def figure(name, at, mats, sitting=False, hat=True, dress=False):
    """A plain person, standing on `at` or sitting on a seat at `at`, facing -y. No face and no
    likeness. Shoes, legs, a coat over a shirt and tie (or a dress), arms in two parts with hands,
    a neck, a head, and a hat or hair. mats needs "coat", "skin", "hat", "shirt", "tie", "hair" and
    "shoe". Returns the parts, joined into one object."""
    x, y, z = at
    parts = []
    cloth = mats["dress"] if dress else mats["coat"]
    legs = mats["skin"] if dress else mats["coat"]
    waist = z + 0.02 if sitting else z + 0.92
    for side in (-1, 1):
        hx = x + side * 0.095
        if sitting:  # thighs forward along the seat, shins down to the floor
            knee, ankle = (hx, y - 0.42, z + 0.06), (hx, y - 0.45, z - 0.38)
            parts.append(rod(f"{name} thigh {side}", (hx, y, z + 0.06), knee, 0.075, cloth if dress else legs))
            parts.append(rod(f"{name} shin {side}", knee, ankle, 0.06, legs))
            parts.append(box(f"{name} shoe {side}", (0.1, 0.24, 0.08), (hx, ankle[1] - 0.06, ankle[2] - 0.04), mats["shoe"]))
        else:
            knee, ankle = (hx, y, z + 0.5), (hx, y, z + 0.09)
            parts.append(rod(f"{name} thigh {side}", (hx, y, waist), knee, 0.078, legs))
            parts.append(rod(f"{name} shin {side}", knee, ankle, 0.062, legs))
            parts.append(box(f"{name} shoe {side}", (0.1, 0.26, 0.09), (hx, y - 0.05, z + 0.045), mats["shoe"]))
    if dress:  # a skirt from the waist to below the knee
        if sitting:
            parts.append(box(f"{name} skirt", (0.36, 0.48, 0.14), (x, y - 0.2, z + 0.08), mats["dress"]))
        else:
            parts.append(cone(f"{name} skirt", 0.27, 0.17, 0.55, (x, y, waist - 0.23), mats["dress"]))
    top = waist + 0.58
    body = cone(f"{name} body", 0.165, 0.215, 0.6, (x, y, waist + 0.29), cloth)
    body.scale = (1, 0.62, 1)
    parts.append(body)
    parts.append(sphere(f"{name} shoulders", 0.215, (x, y, top), cloth, scale=(1, 0.62, 0.3)))
    if not dress:  # the shirt front and tie show between the lapels
        parts.append(box(f"{name} shirt", (0.1, 0.01, 0.2), (x, y - 0.135, top - 0.1), mats["shirt"]))
        parts.append(box(f"{name} tie", (0.035, 0.012, 0.18), (x, y - 0.14, top - 0.11), mats["tie"]))
    for side in (-1, 1):
        sh = (x + side * 0.235, y, top - 0.02)
        if sitting:  # forearms forward, hands resting in front
            elbow, hand = (x + side * 0.26, y + 0.02, top - 0.3), (x + side * 0.17, y - 0.3, top - 0.36)
        else:
            elbow, hand = (x + side * 0.27, y + 0.01, top - 0.31), (x + side * 0.27, y - 0.06, top - 0.58)
        parts.append(rod(f"{name} upper arm {side}", sh, elbow, 0.058, cloth))
        parts.append(rod(f"{name} forearm {side}", elbow, hand, 0.05, cloth))
        parts.append(sphere(f"{name} hand {side}", 0.045, hand, mats["skin"]))
    parts.append(cylinder(f"{name} neck", 0.045, 0.1, (x, y, top + 0.07), mats["skin"], verts=12))
    head = top + 0.2
    parts.append(sphere(f"{name} head", 0.1, (x, y, head), mats["skin"], scale=(0.95, 1, 1.15)))
    if hat:
        parts.append(cylinder(f"{name} hat brim", 0.155, 0.015, (x, y, head + 0.08), mats["hat"], verts=24))
        parts.append(cone(f"{name} hat crown", 0.1, 0.085, 0.11, (x, y, head + 0.14), mats["hat"]))
        parts.append(cylinder(f"{name} hat band", 0.101, 0.025, (x, y, head + 0.1), mats["tie"], verts=24))
    else:
        parts.append(sphere(f"{name} hair", 0.108, (x, y + 0.012, head + 0.025), mats["hair"], scale=(1, 1, 1.05 if dress else 0.95)))
        if dress:  # hair down to the collar at the back
            parts.append(sphere(f"{name} hair back", 0.1, (x, y + 0.04, head - 0.08), mats["hair"], scale=(1.05, 0.8, 1.0)))
    return [join(name, parts)]


def group(name, parts, at=(0, 0, 0), turn=0.0):
    """Put parts built around the origin under one empty, then move and turn the empty to `at`.
    A viewer can then move the whole thing by its name."""
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    g = bpy.context.object
    g.name = name
    g.empty_display_size = 0.1
    for p in parts:
        p.parent = g
    g.location = at
    g.rotation_euler = (0, 0, turn)
    return g


def marker(name, at, turn=0.0):
    """A named point with nothing to draw: a seat or a place to stand, for a viewer to find."""
    return group(name, [], at, turn)
