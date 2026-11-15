"""The club's main room: the bar, the tables, the band stand, the telephone booth on the shared line,
the machine's window, the street door, the door to the house detective's office, and the twelve
regulars. Writes out/club.png.

Named points let a viewer replay a night (find-the-ring/replay.js). Each regular is two groups,
"regular-R1-sit" and "regular-R1-stand", and only one shows at a time. Seats are "seat-bar-0" to
"seat-bar-6" and "seat-t1-0" to "seat-t6-2". Places to stand are "spot-booth", "spot-wait-0" to
"spot-wait-2", "spot-machine-0" to "spot-machine-2", "spot-door", "spot-stand" and "spot-piano".

Run: .venv/bin/python find-the-ring/club.py [--big] [--glb]
--glb also writes out/club.glb for the 3D viewer (kit/viewer.html?scene=club).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bpy  # noqa: E402
from kit.build import aim, box, cone, cylinder, figure, group, haze, light, marker, material, sphere, text  # noqa: E402
from kit.export import export  # noqa: E402
from kit.render import empty_scene, render  # noqa: E402

# The scene keeps its own copy of the names it shows, so it never imports the game.
CLUB = "THE BLUE LANTERN"
OFFICE_DOOR = "HOUSE DETECTIVE"
MACHINE = "WAMAC No. 9"
REGULARS = 12
W, D, H = 14.0, 10.0, 3.6  # the room: x from -7 to 7, y from -5 to 5, height


def materials():
    return {
        "floor": material("floor", (0.08, 0.02, 0.02), rough=0.25),
        "tile": material("tile", (0.6, 0.58, 0.52), rough=0.3),
        "wall": material("wall", (0.12, 0.05, 0.04), rough=0.85),
        "ceiling": material("ceiling", (0.04, 0.035, 0.03), rough=0.9),
        "wood": material("wood", (0.09, 0.04, 0.02), rough=0.3),
        "brass": material("brass", (0.8, 0.6, 0.3), rough=0.3, metal=1),
        "leather": material("leather", (0.25, 0.03, 0.03), rough=0.45),
        "cloth": material("cloth", (0.7, 0.68, 0.62), rough=0.9),
        "mirror": material("mirror", (0.8, 0.8, 0.8), rough=0.05, metal=1),
        "bottle green": material("bottle green", (0.05, 0.2, 0.08), rough=0.1),
        "bottle amber": material("bottle amber", (0.4, 0.15, 0.03), rough=0.1),
        "bottle clear": material("bottle clear", (0.6, 0.6, 0.62), rough=0.1),
        "neon": material("neon", (0.02, 0.1, 1.0), emit=(0.02, 0.15, 1.0), strength=6),
        "lantern": material("lantern", (0.2, 0.4, 1.0), emit=(0.25, 0.5, 1.0), strength=6),
        "shade": material("shade", (0.9, 0.6, 0.3), emit=(1.0, 0.6, 0.3), strength=3),
        "bakelite": material("bakelite", (0.01, 0.01, 0.01), rough=0.2),
        "frosted": material("frosted", (0.7, 0.68, 0.6), rough=0.6, emit=(1.0, 0.8, 0.55), strength=0.6),
        "letters": material("letters", (0.02, 0.02, 0.02), rough=0.6),
        "curtain": material("curtain", (0.3, 0.02, 0.03), rough=0.8),
        "steel": material("steel", (0.5, 0.5, 0.52), rough=0.3, metal=0.9),
    }


def people_mats(i):
    coats = [(0.05, 0.05, 0.06), (0.18, 0.15, 0.12), (0.08, 0.06, 0.1), (0.25, 0.22, 0.2), (0.04, 0.06, 0.05), (0.15, 0.03, 0.03)]
    skins = [(0.6, 0.42, 0.32), (0.35, 0.22, 0.15), (0.75, 0.58, 0.45), (0.2, 0.12, 0.08)]
    return {
        "coat": material(f"coat {i % 6}", coats[i % 6], rough=0.8),
        "skin": material(f"skin {i % 4}", skins[i % 4], rough=0.6),
        "hat": material(f"hat {i % 3}", [(0.05, 0.05, 0.05), (0.2, 0.17, 0.13), (0.1, 0.08, 0.06)][i % 3], rough=0.9),
    }


def room(m):
    box("floor", (W, D, 0.1), (0, 0, -0.05), m["floor"])
    for i in range(7):  # a pale dance floor in front of the stand
        for j in range(5):
            if (i + j) % 2 == 0:
                box(f"tile {i} {j}", (0.6, 0.6, 0.01), (2.8 + i * 0.6, -1.4 + j * 0.6, 0.005), m["tile"])
    box("ceiling", (W, D, 0.1), (0, 0, H + 0.05), m["ceiling"])
    box("wall back", (W, 0.2, H), (0, D / 2, H / 2), m["wall"])
    box("wall left", (0.2, D, H), (-W / 2, 0, H / 2), m["wall"])
    box("wall right", (0.2, D, H), (W / 2, 0, H / 2), m["wall"])
    for x in (-6.4, 2.4):
        box(f"column {x}", (0.35, 0.35, H), (x, 1.2, H / 2), m["wood"])


def bar(m):
    box("bar", (6.0, 0.7, 1.1), (-3.0, 3.4, 0.55), m["wood"])
    box("bar top", (6.2, 0.85, 0.06), (-3.0, 3.35, 1.13), m["wood"])
    box("bar rail", (6.0, 0.05, 0.05), (-3.0, 2.95, 0.25), m["brass"])
    box("back bar", (6.4, 0.4, 0.9), (-3.0, 4.75, 0.45), m["wood"])
    box("mirror", (5.6, 0.02, 1.2), (-3.0, 4.88, 1.6), m["mirror"])
    bottles = [m["bottle green"], m["bottle amber"], m["bottle clear"]]
    for shelf, z in enumerate((0.92, 1.45)):
        box(f"shelf {shelf}", (5.6, 0.25, 0.03), (-3.0, 4.75, z - 0.02), m["wood"])
        for k in range(26):
            hgt = 0.26 + 0.06 * ((k * 7) % 3)
            cylinder(f"bottle {shelf} {k}", 0.035, hgt, (-5.6 + k * 0.205, 4.75, z + hgt / 2), bottles[(k + shelf) % 3], verts=12)
    for k in range(7):
        x = -5.5 + k * 0.8
        cylinder(f"stool {k} post", 0.03, 0.7, (x, 2.75, 0.35), m["steel"])
        cylinder(f"stool {k} seat", 0.18, 0.08, (x, 2.75, 0.74), m["leather"])
        marker(f"seat-bar-{k}", (x, 2.75, 0.78), turn=math.pi)
    # The club's sign over the bar, in blue tubing, and a blue lantern hanging at each end.
    text("sign", CLUB, (-3.0, 4.86, 2.55), 0.42, m["neon"], extrude=0.01)
    light("AREA", (-3.0, 4.2, 2.65), 120, color=(0.25, 0.45, 1.0), size=4, rot=(math.radians(-90), 0, 0))
    for x in (-6.2, 0.2):
        cylinder(f"lantern chain {x}", 0.008, 0.9, (x, 3.6, H - 0.45), m["steel"])
        cylinder(f"lantern {x}", 0.13, 0.32, (x, 3.6, H - 1.05), m["lantern"])
        light("POINT", (x, 3.6, H - 1.05), 40, color=(0.3, 0.5, 1.0), size=0.1, shadow=False)
    # The bartender's own lamp over the till.
    light("SPOT", (-3.0, 3.4, H - 0.2), 400, color=(1.0, 0.75, 0.45), size=0.1, spot=math.radians(80), blend=0.6, rot=(0, 0, 0))


def table(m, n, at, seats=3):
    """A round table with a lamp and chairs that face it. Each chair is a marker "seat-t<n>-<k>"."""
    x, y = at
    name = f"table {n}"
    cylinder(f"{name} top", 0.45, 0.04, (x, y, 0.74), m["cloth"])
    cylinder(f"{name} post", 0.04, 0.72, (x, y, 0.36), m["steel"])
    cylinder(f"{name} lamp", 0.06, 0.18, (x, y, 0.85), m["shade"])
    light("POINT", (x, y, 0.95), 12, color=(1.0, 0.65, 0.35), size=0.05, shadow=False)
    for k in range(seats):
        a = k * 2 * math.pi / seats + 0.4
        cx, cy = x + 0.8 * math.cos(a), y + 0.8 * math.sin(a)
        turn = math.atan2(x - cx, -(y - cy))  # the chair's front (-y) faces the table
        parts = [
            box(f"{name} chair {k} seat", (0.42, 0.42, 0.05), (0, 0, 0.45), m["leather"]),
            box(f"{name} chair {k} back", (0.42, 0.05, 0.5), (0, 0.2, 0.72), m["leather"]),
        ] + [cylinder(f"{name} chair {k} leg {q}", 0.018, 0.45, (0.17 * sx, 0.17 * sy, 0.225), m["steel"], verts=8)
             for q, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)])]
        group(f"{name} chair {k}", parts, (cx, cy, 0), turn)
        marker(f"seat-t{n}-{k}", (cx, cy, 0.48), turn)


def stand(m):
    """The band stand in the right corner: a low stage, a curtain, a microphone and a piano."""
    box("stage", (4.0, 2.6, 0.35), (4.9, 3.6, 0.175), m["wood"])
    box("curtain", (4.0, 0.1, H - 0.35), (4.9, 4.85, 0.35 + (H - 0.35) / 2), m["curtain"])
    cylinder("mic stand", 0.012, 1.4, (4.6, 3.0, 1.05), m["steel"])
    sphere("mic", 0.04, (4.6, 3.0, 1.78), m["steel"])
    box("piano", (1.5, 0.6, 1.2), (6.0, 4.2, 0.95), m["bakelite"])
    marker("spot-stand", (4.6, 3.3, 0.35), turn=math.pi)
    marker("spot-piano", (6.0, 3.6, 0.35), turn=math.pi)
    s = light("SPOT", (4.6, -0.5, H - 0.1), 1500, color=(1.0, 0.85, 0.65), size=0.05, spot=math.radians(18), blend=0.3)
    aim(s, (4.6, 3.0, 1.2))


def booth(m):
    """The telephone booth by the left wall: the shared line every regular can use."""
    x, y = -6.35, -1.5
    box("booth back", (0.08, 1.0, 2.3), (x - 0.4, y, 1.15), m["wood"])
    box("booth left", (0.9, 0.08, 2.3), (x, y - 0.5, 1.15), m["wood"])
    box("booth right", (0.9, 0.08, 2.3), (x, y + 0.5, 1.15), m["wood"])
    box("booth roof", (0.9, 1.08, 0.08), (x, y, 2.34), m["wood"])
    box("booth door glass", (0.02, 0.9, 1.4), (x + 0.45, y, 1.3), m["frosted"])
    box("booth phone box", (0.12, 0.25, 0.35), (x - 0.32, y, 1.5), m["bakelite"])
    text("booth sign", "TELEPHONE", (x + 0.47, y, 2.15), 0.12, m["letters"], rot=(math.pi / 2, 0, math.pi / 2))
    light("POINT", (x, y, 2.1), 15, color=(1.0, 0.85, 0.6), size=0.1, shadow=False).name = "booth-light"
    marker("spot-booth", (x - 0.05, y, 0.0), turn=-math.pi / 2)
    for k in range(3):
        marker(f"spot-wait-{k}", (x + 1.0, y - 1.0 + k * 0.6, 0.0), turn=-math.pi / 2)


def office_door(m):
    """The door to the house detective's office, on the right wall, with a lit glass panel."""
    x, y = 6.88, -2.5
    box("office door", (0.06, 1.0, 2.2), (x, y, 1.1), m["wood"])
    box("office door glass", (0.02, 0.7, 0.8), (x - 0.04, y, 1.55), m["frosted"])
    text("office door name", OFFICE_DOOR, (x - 0.06, y, 1.62), 0.075, m["letters"], rot=(math.pi / 2, 0, -math.pi / 2))


def machine_window(m):
    """The machine's window on the right wall: a brass grille with a slot, where regulars hand in
    their requests to the club's machine, which works in the back."""
    x, y = 6.86, 0.6
    box("machine window frame", (0.1, 1.4, 1.2), (x, y, 1.3), m["brass"])
    box("machine window glass", (0.02, 1.2, 0.7), (x - 0.06, y, 1.45), m["frosted"])
    for k in range(9):
        box(f"machine grille {k}", (0.03, 0.015, 0.7), (x - 0.08, y - 0.56 + k * 0.14, 1.45), m["brass"])
    box("machine slot", (0.04, 0.5, 0.04), (x - 0.07, y, 0.95), m["bakelite"])
    text("machine window name", MACHINE, (x - 0.09, y, 1.95), 0.12, m["letters"], rot=(math.pi / 2, 0, -math.pi / 2))
    light("POINT", (x - 0.6, y, 1.6), 10, color=(1.0, 0.6, 0.25), size=0.1, shadow=False).name = "machine-light"
    for k in range(3):
        marker(f"spot-machine-{k}", (x - 0.7 - 0.6 * k, y - 0.3 + 0.3 * k, 0.0), turn=math.pi / 2)


def street_door(m):
    """The street door on the left wall, near the front. A regular who steps out leaves by it."""
    x, y = -6.88, -4.0
    box("street door", (0.06, 1.1, 2.3), (x, y, 1.15), m["wood"])
    box("street door glass", (0.02, 0.6, 0.5), (x + 0.04, y, 1.8), m["frosted"])
    marker("spot-door", (x + 0.6, y, 0.0), turn=math.pi / 2)


def regular_groups(m):
    """Each regular twice, sitting and standing, under groups a viewer can move. The standing
    group is hidden at first. Homes: R1 sings on the stand, R2 plays the piano, R3 to R6 sit at the
    bar, R7 to R12 at the tables."""
    homes = {"R1": ("spot-stand", False), "R2": ("spot-piano", False)}
    homes.update({f"R{k}": (f"seat-bar-{(k - 3) * 2}", True) for k in range(3, 7)})
    homes.update({f"R{k}": (f"seat-t{k - 6}-0", True) for k in range(7, 13)})
    for k in range(1, REGULARS + 1):
        rid = f"R{k}"
        mats = people_mats(k - 1)
        spot, sitting = homes[rid]
        home = bpy.data.objects[spot]
        sit = group(f"regular-{rid}-sit", figure(f"regular {k} sitting", (0, 0, 0), mats, sitting=True, hat=k % 3 != 2))
        stand = group(f"regular-{rid}-stand", figure(f"regular {k} standing", (0, 0, 0), mats, sitting=False, hat=k % 3 != 2))
        shown, hidden = (sit, stand) if sitting else (stand, sit)
        shown.location, shown.rotation_euler = home.location.copy(), home.rotation_euler.copy()
        hidden.location = (0, -20, 0)  # parked out of sight; a viewer moves it in when needed
        for o in [hidden, *hidden.children]:
            o.hide_render = True


def build():
    scene = empty_scene()
    m = materials()
    room(m)
    bar(m)
    for k, (x, y) in enumerate([(-3.5, 0.3), (-0.5, -1.0), (1.0, 1.0), (-3.2, -2.8), (0.8, -3.2), (4.0, -2.5)]):
        table(m, k + 1, (x, y))
    stand(m)
    booth(m)
    office_door(m)
    machine_window(m)
    street_door(m)
    regular_groups(m)
    for x in (-4.5, 0.0, 4.5):  # dim pendant lights down the room
        cone(f"pendant {x}", 0.25, 0.05, 0.2, (x, -1.5, H - 0.5), m["shade"])
        light("POINT", (x, -1.5, H - 0.7), 60, color=(1.0, 0.7, 0.4), size=0.2)
    haze(scene, density=0.02, color=(0.6, 0.6, 0.7))
    scene.eevee.volumetric_tile_size = "4"
    scene.eevee.volumetric_samples = 96
    bpy.ops.object.camera_add(location=(0.3, -4.75, 2.3))
    cam = aim(bpy.context.object, (-0.3, 3.0, 0.9))
    cam.data.lens = 15
    scene.camera = cam
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - High Contrast"
    return scene


if __name__ == "__main__":
    big = "--big" in sys.argv
    scene = build()
    scene.eevee.taa_render_samples = 64 if big else 16
    print(render(scene, "club", width=1920 if big else 960, height=1080 if big else 540))
    if "--glb" in sys.argv:
        print(export("club"))
