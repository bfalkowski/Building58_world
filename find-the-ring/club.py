"""The club's main room: the bar, the tables, the band stand, the telephone booth on the shared line,
the machine's window, the street door, the door to the house detective's office, and the twelve
regulars. Through a window in the left wall: the quay and the harbor, with the night's two ships at
their berths. Writes out/club.png.

Named points let a viewer replay a night (find-the-ring/replay.js). Each regular is two groups,
"regular-R1-sit" and "regular-R1-stand", and only one shows at a time. Seats are "seat-bar-0" to
"seat-bar-6" and "seat-t1-0" to "seat-t6-2". Places to stand are "spot-booth", "spot-wait-0" to
"spot-wait-2", "spot-machine-0" to "spot-machine-2", "spot-door", "spot-stand" and "spot-piano".
The ships are groups "ship-0" and "ship-1", at the markers "berth-0" and "berth-1".

Run: .venv/bin/python find-the-ring/club.py [--big] [--glb]
--glb also writes out/club.glb for the 3D viewer (kit/viewer.html?scene=club).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bpy  # noqa: E402
from kit.build import aim, box, cone, cylinder, figure, group, haze, hull, hull_width, join, light, marker, material, rod, sphere, text  # noqa: E402
from kit.export import export  # noqa: E402
from kit.render import empty_scene, render  # noqa: E402

# The scene keeps its own copy of the names it shows, so it never imports the game.
CLUB = "THE BLUE LANTERN"
OFFICE_DOOR = "HOUSE DETECTIVE"
MACHINE = "WAMAC No. 9"
REGULARS = 12
DRESSES = {1, 6, 7, 11}  # the regulars, by number, who wear a dress
W, D, H = 14.0, 10.0, 3.6  # the room: x from -7 to 7, y from -5 to 5, height
WINDOW = (-0.7, 2.4, 0.9, 2.9)  # the harbor window in the left wall: y from, y to, z from, z to
QUAY = -16.0  # the quay's edge, west of the club. The water starts here.


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
        "stone": material("stone", (0.1, 0.1, 0.11), rough=0.7),
        "brick": material("brick", (0.12, 0.06, 0.05), rough=0.9),
        "water": material("water", (0.01, 0.02, 0.035), rough=0.08, metal=0.3),
        "hull": material("hull", (0.04, 0.04, 0.05), rough=0.5),
        "ship white": material("ship white", (0.55, 0.53, 0.48), rough=0.7),
        "funnel": material("funnel", (0.05, 0.05, 0.05), rough=0.6),
        "funnel band": material("funnel band", (0.6, 0.4, 0.1), rough=0.5),
        "porthole": material("porthole", (1.0, 0.8, 0.5), emit=(1.0, 0.75, 0.4), strength=4),
        "mast light": material("mast light", (1.0, 0.95, 0.85), emit=(1.0, 0.95, 0.85), strength=8),
        "red light": material("red light", (1.0, 0.1, 0.05), emit=(1.0, 0.1, 0.05), strength=8),
        "hull bottom": material("hull bottom", (0.35, 0.05, 0.04), rough=0.6),
        "deck": material("deck", (0.3, 0.22, 0.14), rough=0.8),
        "tarp": material("tarp", (0.15, 0.17, 0.1), rough=0.95),
        "mast": material("mast", (0.4, 0.33, 0.25), rough=0.7),
        "rope": material("rope", (0.2, 0.18, 0.15), rough=0.9),
        "green light": material("green light", (0.1, 1.0, 0.2), emit=(0.1, 1.0, 0.2), strength=8),
        "crane": material("crane", (0.25, 0.18, 0.06), rough=0.7, metal=0.4),
    }


def people_mats(i):
    coats = [(0.05, 0.05, 0.06), (0.18, 0.15, 0.12), (0.08, 0.06, 0.1), (0.25, 0.22, 0.2), (0.04, 0.06, 0.05), (0.15, 0.03, 0.03)]
    skins = [(0.6, 0.42, 0.32), (0.35, 0.22, 0.15), (0.75, 0.58, 0.45), (0.2, 0.12, 0.08)]
    dresses = [(0.35, 0.02, 0.05), (0.03, 0.08, 0.2), (0.05, 0.05, 0.05), (0.3, 0.25, 0.12)]
    hairs = [(0.02, 0.015, 0.01), (0.25, 0.12, 0.05), (0.5, 0.38, 0.2), (0.35, 0.33, 0.3)]
    ties = [(0.4, 0.05, 0.04), (0.1, 0.12, 0.3), (0.3, 0.25, 0.08)]
    return {
        "coat": material(f"coat {i % 6}", coats[i % 6], rough=0.8),
        "skin": material(f"skin {i % 4}", skins[i % 4], rough=0.6),
        "hat": material(f"hat {i % 3}", [(0.05, 0.05, 0.05), (0.2, 0.17, 0.13), (0.1, 0.08, 0.06)][i % 3], rough=0.9),
        "dress": material(f"dress {i % 4}", dresses[i % 4], rough=0.5),
        "hair": material(f"hair {i % 4}", hairs[i % 4], rough=0.7),
        "tie": material(f"tie {i % 3}", ties[i % 3], rough=0.5),
        "shirt": material("shirt", (0.75, 0.73, 0.68), rough=0.7),
        "shoe": material("shoe", (0.02, 0.015, 0.01), rough=0.3),
    }


def room(m):
    box("floor", (W, D, 0.1), (0, 0, -0.05), m["floor"])
    for i in range(7):  # a pale dance floor in front of the stand
        for j in range(5):
            if (i + j) % 2 == 0:
                box(f"tile {i} {j}", (0.6, 0.6, 0.01), (2.8 + i * 0.6, -1.4 + j * 0.6, 0.005), m["tile"])
    box("ceiling", (W, D, 0.1), (0, 0, H + 0.05), m["ceiling"])
    box("wall back", (W, 0.2, H), (0, D / 2, H / 2), m["wall"])
    # The left wall has a window onto the harbor, between the booth and the bar.
    y0, y1, z0, z1 = WINDOW
    box("wall left front", (0.2, y0 + D / 2, H), (-W / 2, (y0 - D / 2) / 2, H / 2), m["wall"])
    box("wall left back", (0.2, D / 2 - y1, H), (-W / 2, (y1 + D / 2) / 2, H / 2), m["wall"])
    box("wall left under window", (0.2, y1 - y0, z0), (-W / 2, (y0 + y1) / 2, z0 / 2), m["wall"])
    box("wall left over window", (0.2, y1 - y0, H - z1), (-W / 2, (y0 + y1) / 2, (z1 + H) / 2), m["wall"])
    box("harbor window sill", (0.35, y1 - y0, 0.05), (-W / 2 + 0.05, (y0 + y1) / 2, z0), m["wood"])
    for k in range(4):  # the frame: four uprights and a cross bar
        box(f"harbor window bar {k}", (0.08, 0.06, z1 - z0), (-W / 2, y0 + k * (y1 - y0) / 3, (z0 + z1) / 2), m["wood"])
    box("harbor window cross", (0.08, y1 - y0, 0.06), (-W / 2, (y0 + y1) / 2, (z0 + z1) / 2 + 0.3), m["wood"])
    box("wall right", (0.2, D, H), (W / 2, 0, H / 2), m["wall"])
    for x, y in ((-6.4, 2.65), (2.4, 1.2)):  # the left column stands beside the harbor window
        box(f"column {x}", (0.35, 0.35, H), (x, y, H / 2), m["wood"])


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


SHIP = (16.0, 3.2)  # a ship's length and beam, in meters
DECK = 0.9  # deck height over the quay top; the water is at -1.25


def deck_at(t):
    """The height of the deck at t, from stern (-1) to bow (1). It rises toward the bow."""
    return DECK + 0.5 * max(0.0, t - 0.3) ** 2 + 0.15 * max(0.0, -t - 0.8)


def ship(m, k, at):
    """One cargo steamer at its berth, bow to the north, as a group "ship-<k>" a viewer can sail
    away. A shaped hull with red bottom paint, a wooden deck with rails, two cargo hatches, two masts
    with cargo booms and rigging, a deck house and bridge at the stern with lit windows, lifeboats,
    a raked funnel, lit portholes, a red and a green running light, and lights at the mastheads."""
    L, B = SHIP
    p = []
    p.append(hull(f"ship {k} hull", L, B, DECK, -2.2, -1.0, (m["hull"], m["hull bottom"], m["deck"])))
    # Rails along both sides: posts, and a top rail from post to post.
    for side in (-1, 1):
        prev = None
        for i in range(17):
            t = -0.94 + i * 0.115
            x, y, z = side * (B / 2 * hull_width(t) - 0.05), t * L / 2, deck_at(t)
            p.append(rod(f"ship {k} rail post {side} {i}", (x, y, z), (x, y, z + 0.55), 0.018, m["ship white"], verts=6))
            if prev:
                p.append(rod(f"ship {k} rail {side} {i}", prev, (x, y, z + 0.55), 0.02, m["ship white"], verts=6))
            prev = (x, y, z + 0.55)
        # Round portholes along the hull, lit from inside.
        for i in range(9):
            y = -5.5 + i * 1.1
            p.append(cylinder(f"ship {k} porthole {side} {i}", 0.08, 0.04, (side * (B / 2 - 0.02), y, 0.35), m["porthole"], rot=(0, math.pi / 2, 0), verts=12))
    for n, y in enumerate((3.8, 0.2)):  # cargo hatches with canvas covers
        p.append(box(f"ship {k} hatch {n}", (1.9, 2.2, 0.45), (0, y, DECK + 0.22), m["hull"]))
        p.append(box(f"ship {k} hatch cover {n}", (1.95, 2.25, 0.08), (0, y, DECK + 0.48), m["tarp"]))
    # The deck house and the bridge over it, at the stern.
    p.append(box(f"ship {k} house", (2.6, 3.4, 1.7), (0, -4.6, DECK + 0.85), m["ship white"]))
    p.append(box(f"ship {k} bridge", (2.8, 1.5, 0.95), (0, -3.6, DECK + 2.17), m["ship white"]))
    p.append(box(f"ship {k} bridge wings", (3.8, 0.7, 0.08), (0, -3.2, DECK + 1.75), m["ship white"]))
    p.append(box(f"ship {k} bridge roof", (3.0, 1.7, 0.08), (0, -3.6, DECK + 2.68), m["hull"]))
    p.append(box(f"ship {k} bridge windows", (2.4, 0.02, 0.3), (0, -2.84, DECK + 2.3), m["porthole"]))
    for side in (-1, 1):
        for i in range(4):
            p.append(box(f"ship {k} house window {side} {i}", (0.02, 0.22, 0.22), (side * 1.31, -5.9 + i * 0.8, DECK + 1.0), m["porthole"]))
        # Lifeboats on the house roof, each under a pair of davits.
        for n, y in enumerate((-4.4, -5.7)):
            bx = side * 1.15
            p.append(sphere(f"ship {k} lifeboat {side} {n}", 0.3, (bx, y, DECK + 2.0), m["ship white"], scale=(1, 2.1, 0.75)))
            for dy in (-0.45, 0.45):
                p.append(rod(f"ship {k} davit {side} {n} {dy}", (side * 0.75, y + dy, DECK + 1.7), (bx, y + dy, DECK + 2.45), 0.03, m["steel"], verts=6))
    p.append(sphere(f"ship {k} port light", 0.07, (-1.85, -3.2, DECK + 1.85), m["red light"]))
    p.append(sphere(f"ship {k} starboard light", 0.07, (1.85, -3.2, DECK + 1.85), m["green light"]))
    # A raked funnel with a colored band and a black top.
    funnel = [cylinder(f"ship {k} funnel", 0.45, 2.1, (0, -5.3, DECK + 2.7), m["funnel"], verts=20),
              cylinder(f"ship {k} funnel band", 0.46, 0.4, (0, -5.3, DECK + 3.1), m["funnel band"], verts=20),
              cylinder(f"ship {k} funnel top", 0.465, 0.25, (0, -5.3, DECK + 3.65), m["hull"], verts=20)]
    for f in funnel:
        f.rotation_euler = (-0.12, 0, 0)
    p += funnel
    # Two masts, each with a cross tree, a masthead light and a cargo boom over its hatch.
    tops = []
    for n, (y, hgt) in enumerate(((5.6, 6.5), (1.9, 7.0))):
        base, top = (0, y, DECK), (0, y, DECK + hgt)
        tops.append(top)
        p.append(rod(f"ship {k} mast {n}", base, top, 0.08, m["mast"], verts=10))
        p.append(rod(f"ship {k} cross tree {n}", (-0.9, y, DECK + hgt - 1.2), (0.9, y, DECK + hgt - 1.2), 0.035, m["mast"], verts=6))
        p.append(sphere(f"ship {k} masthead light {n}", 0.1, (0, y, DECK + hgt + 0.08), m["mast light"]))
        hatch = 3.8 if n == 0 else 0.2
        p.append(rod(f"ship {k} boom {n}", (0, y, DECK + 0.9), (0, hatch + (y - hatch) * 0.2, DECK + 3.4), 0.05, m["mast"], verts=6))
    # Rigging: stays from the mastheads to the stem, between the masts, and down to the stern.
    rope = m["rope"]
    p.append(rod(f"ship {k} forestay", tops[0], (0, L / 2 - 0.1, deck_at(0.99) + 0.3), 0.015, rope, verts=4))
    p.append(rod(f"ship {k} triatic stay", tops[0], tops[1], 0.015, rope, verts=4))
    p.append(rod(f"ship {k} backstay", tops[1], (0, -3.6, DECK + 2.7), 0.015, rope, verts=4))
    for side in (-1, 1):
        for n, top in enumerate(tops):
            y = top[1]
            p.append(rod(f"ship {k} shroud {side} {n}", (side * 0.9, y, top[2] - 1.2), (side * (B / 2 - 0.1), y - 0.6, DECK + 0.1), 0.012, rope, verts=4))
    p.append(box(f"ship {k} anchor", (0.05, 0.4, 0.55), (B / 2 * hull_width(0.85) + 0.03, 0.85 * L / 2, 0.3), m["hull"]))
    g = group(f"ship-{k}", [join(f"ship {k} body", p)], at)
    lamp = light("POINT", (0, -3.0, DECK + 3.2), 80, color=(1.0, 0.85, 0.6), size=0.2, shadow=False)
    lamp.name = f"ship-{k}-light"
    lamp.parent = g
    return g


def harbor(m):
    """Outside the left wall: the street, the quay and the harbor at night. Two berths hold the
    night's two ships ("ship-0" and "ship-1"). Cranes, bollards, a shed and lamp posts line the quay.
    Far out, the lights of ships at anchor."""
    box("street", (-W / 2 - QUAY + 0.2, 60.0, 0.1), ((QUAY - W / 2) / 2, 0, -0.05), m["stone"])
    box("quay wall", (0.6, 60.0, 2.0), (QUAY + 0.3, 0, -1.0), m["stone"])
    box("water", (160.0, 160.0, 0.1), (QUAY - 80.0, 0, -1.25), m["water"])
    box("club roof", (W + 0.8, D + 0.8, 0.3), (0, 0, H + 0.25), m["brick"])
    box("shed", (5.0, 12.0, 4.0), (QUAY + 5.0, -18.0, 2.0), m["brick"])
    for y in range(-24, 25, 4):
        cylinder(f"bollard {y}", 0.18, 0.5, (QUAY + 0.6, y, 0.25), m["bakelite"], verts=12)
    for n, y in enumerate((-8.0, 13.0)):  # two cranes on the quay, their arms out over the water
        for dx in (-1.0, 1.0):
            for dy in (-1.0, 1.0):
                box(f"crane {n} leg {dx} {dy}", (0.25, 0.25, 9.0), (QUAY + 2.5 + dx, y + dy, 4.5), m["crane"])
        box(f"crane {n} cab", (2.6, 2.6, 1.6), (QUAY + 2.5, y, 9.8), m["crane"])
        box(f"crane {n} arm", (14.0, 0.5, 0.5), (QUAY - 3.5, y, 10.8), m["crane"])
        sphere(f"crane {n} light", 0.12, (QUAY - 10.4, y, 11.2), m["red light"])
    for n, y in enumerate((-12.0, -4.0, 4.0, 12.0)):
        cylinder(f"quay lamp {n} post", 0.06, 4.0, (QUAY + 1.5, y, 2.0), m["steel"], verts=8)
        sphere(f"quay lamp {n}", 0.18, (QUAY + 1.5, y, 4.1), m["shade"])
        light("POINT", (QUAY + 1.5, y, 4.0), 250, color=(1.0, 0.75, 0.45), size=0.2, shadow=False)
    for n, (x, y) in enumerate([(-70, -20), (-85, 15), (-60, 30), (-95, -5)]):
        sphere(f"anchored ship light {n}", 0.25, (x, y, 2.0), m["mast light"])
    # Berth 0 is along the quay. Berth 1 is out in the harbor, at a mooring buoy.
    berths = [(QUAY - SHIP[1] / 2 - 0.3, 4.0, 0.0), (QUAY - 16.0, -8.0, 0.0)]
    cylinder("mooring buoy", 0.5, 0.8, (QUAY - 16.0, 1.5, -1.1), m["hull bottom"], verts=16)
    for k, at in enumerate(berths):
        marker(f"berth-{k}", at)
        ship(m, k, at)


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
        dress = k in DRESSES
        hat = not dress and k % 3 != 2
        sit = group(f"regular-{rid}-sit", figure(f"regular {k} sitting", (0, 0, 0), mats, sitting=True, hat=hat, dress=dress))
        stand = group(f"regular-{rid}-stand", figure(f"regular {k} standing", (0, 0, 0), mats, sitting=False, hat=hat, dress=dress))
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
    harbor(m)
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
