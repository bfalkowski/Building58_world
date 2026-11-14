"""The house detective's office at the club: the desk, the lamp, the books, the telephone and the
club's calculating machine, with harbor light through the blinds. Writes out/desk.png.

Run: .venv/bin/python find-the-ring/desk.py [--big]
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bpy  # noqa: E402
from kit.build import aim, box, cone, cylinder, haze, light, material, text  # noqa: E402
from kit.render import empty_scene, render  # noqa: E402

# Names come from the game's theme, but the scene keeps its own copy so it never imports the game.
MACHINE = "WAMAC No. 9"
MAKER = "WHITNEYVILLE CALCULATING WORKS"


def room(m):
    box("floor", (8, 8, 0.1), (0, 0, -0.05), m["floor"])
    box("ceiling", (8, 8, 0.1), (0, 0, 3.25), m["wall"])
    # The back wall, with a window opening 1.4 m wide and 1.5 m high.
    box("wall back left", (2.3, 0.15, 3.2), (-2.85, 2.5, 1.6), m["wall"])
    box("wall back right", (4.3, 0.15, 3.2), (1.85, 2.5, 1.6), m["wall"])
    box("wall under window", (1.4, 0.15, 0.9), (-1.0, 2.5, 0.45), m["wall"])
    box("wall over window", (1.4, 0.15, 0.8), (-1.0, 2.5, 2.8), m["wall"])
    box("wall left", (0.15, 8, 3.2), (-4.0, 0, 1.6), m["wall"])
    box("wainscot", (8, 0.04, 0.9), (0, 2.42, 0.45), m["wood"])
    # Blinds: thin slats across the opening. The street light outside throws their stripes.
    for i in range(22):
        box(f"slat {i}", (1.4, 0.06, 0.012), (-1.0, 2.44, 0.95 + i * 0.066), m["slat"], rot=(math.radians(35), 0, 0))
    box("sill", (1.6, 0.25, 0.05), (-1.0, 2.38, 0.9), m["wood"])


def desk(m):
    box("desk top", (1.9, 0.95, 0.06), (0, 0.6, 0.76), m["wood"])
    box("desk left", (0.5, 0.85, 0.73), (-0.65, 0.6, 0.365), m["wood"])
    box("desk right", (0.5, 0.85, 0.73), (0.65, 0.6, 0.365), m["wood"])
    box("blotter", (0.7, 0.45, 0.005), (0.05, 0.45, 0.792), m["blotter"])
    # Banker's lamp: brass base and stem, green glass shade, a warm bulb under it.
    cylinder("lamp base", 0.08, 0.025, (-0.55, 0.75, 0.80), m["brass"])
    cylinder("lamp stem", 0.012, 0.32, (-0.55, 0.75, 0.96), m["brass"])
    shade = cylinder("lamp shade", 0.09, 0.42, (-0.45, 0.72, 1.12), m["shade"], rot=(0, math.pi / 2, 0))
    shade.scale = (1, 1, 1)
    light("POINT", (-0.45, 0.68, 1.04), 40, color=(1.0, 0.72, 0.4), size=0.03)
    # Ledgers: the house's books, one open.
    colors = [m["book red"], m["book brown"], m["book red"], m["book green"]]
    for i, mat in enumerate(colors):
        box(f"ledger {i}", (0.32, 0.24, 0.045), (0.62, 0.78, 0.815 + i * 0.047), mat, rot=(0, 0, math.radians(4 * (i % 2) - 2)))
    box("open ledger", (0.5, 0.33, 0.012), (0.05, 0.42, 0.80), m["paper"], rot=(0, 0, math.radians(-6)))
    # The telephone: a candlestick set.
    cylinder("phone base", 0.06, 0.02, (0.45, 0.35, 0.80), m["bakelite"])
    cylinder("phone stem", 0.014, 0.26, (0.45, 0.35, 0.94), m["bakelite"])
    cone("phone mouth", 0.035, 0.02, 0.05, (0.45, 0.32, 1.06), m["bakelite"], rot=(math.radians(-70), 0, 0))
    cylinder("phone earpiece", 0.02, 0.08, (0.5, 0.36, 0.98), m["bakelite"], rot=(0, math.radians(15), 0))
    # An ashtray and a hat.
    cylinder("ashtray", 0.07, 0.02, (-0.25, 0.85, 0.80), m["glass"])
    cylinder("hat crown", 0.1, 0.11, (-0.75, 0.35, 0.86), m["felt"])
    cylinder("hat brim", 0.17, 0.012, (-0.75, 0.35, 0.80), m["felt"])
    # The chair, pushed back.
    box("chair seat", (0.5, 0.5, 0.06), (0.1, 1.45, 0.48), m["leather"])
    box("chair back", (0.5, 0.07, 0.6), (0.1, 1.7, 0.82), m["leather"], rot=(math.radians(-8), 0, 0))
    cylinder("chair post", 0.03, 0.42, (0.1, 1.45, 0.24), m["brass"])


def machine(m):
    """The club's calculating machine: a tall steel cabinet with rows of glowing tubes and a plate."""
    x, y = 2.6, 1.9
    box("cabinet", (1.3, 0.6, 2.2), (x, y, 1.1), m["steel"])
    box("cabinet window", (1.0, 0.02, 0.8), (x, y - 0.31, 1.55), m["glass dark"])
    for row in range(4):
        for col in range(9):
            cylinder(f"tube {row} {col}", 0.025, 0.12, (x - 0.4 + col * 0.1, y - 0.34, 1.27 + row * 0.19), m["tube"])
    light("AREA", (x, y - 0.6, 1.2), 25, color=(1.0, 0.55, 0.2), size=0.9, rot=(math.radians(-90), 0, 0))
    for i in range(6):
        cylinder(f"dial {i}", 0.045, 0.02, (x - 0.38 + i * 0.15, y - 0.31, 0.95), m["brass"], rot=(math.pi / 2, 0, 0))
    box("plate", (0.7, 0.01, 0.16), (x, y - 0.31, 0.7), m["brass"])
    text("plate name", MACHINE, (x, y - 0.32, 0.705), 0.06, m["engraved"])
    text("plate maker", MAKER, (x, y - 0.32, 0.655), 0.022, m["engraved"])
    lamp = light("SPOT", (x - 0.6, y - 1.6, 2.9), 300, color=(1.0, 0.8, 0.55), size=0.05, spot=math.radians(30), blend=0.4)
    aim(lamp, (x, y - 0.3, 0.9))
    box("tape slot", (0.5, 0.02, 0.03), (x, y - 0.31, 0.45), m["glass dark"])
    box("tape", (0.06, 0.25, 0.002), (x - 0.1, y - 0.44, 0.44), m["paper"], rot=(math.radians(-25), 0, 0))


def materials():
    return {
        "floor": material("floor", (0.05, 0.03, 0.02), rough=0.35),
        "wall": material("wall", (0.16, 0.15, 0.13), rough=0.9),
        "wood": material("wood", (0.09, 0.04, 0.02), rough=0.3),
        "slat": material("slat", (0.5, 0.48, 0.42), rough=0.7),
        "blotter": material("blotter", (0.03, 0.08, 0.04), rough=0.95),
        "brass": material("brass", (0.8, 0.6, 0.3), rough=0.3, metal=1),
        "shade": material("shade", (0.02, 0.25, 0.08), rough=0.15, emit=(0.1, 0.6, 0.2), strength=0.12),
        "book red": material("book red", (0.25, 0.03, 0.02), rough=0.6),
        "book brown": material("book brown", (0.15, 0.08, 0.03), rough=0.6),
        "book green": material("book green", (0.03, 0.1, 0.05), rough=0.6),
        "paper": material("paper", (0.75, 0.7, 0.58), rough=0.9),
        "bakelite": material("bakelite", (0.01, 0.01, 0.01), rough=0.2),
        "glass": material("glass", (0.3, 0.32, 0.3), rough=0.05, metal=0.3),
        "felt": material("felt", (0.06, 0.055, 0.05), rough=1),
        "leather": material("leather", (0.12, 0.04, 0.02), rough=0.5),
        "steel": material("steel", (0.45, 0.47, 0.48), rough=0.35, metal=0.8),
        "glass dark": material("glass dark", (0.01, 0.01, 0.012), rough=0.05),
        "tube": material("tube", (0.9, 0.5, 0.2), emit=(1.0, 0.45, 0.12), strength=8),
        "engraved": material("engraved", (0.02, 0.015, 0.01), rough=0.6),
    }


def build():
    scene = empty_scene()
    m = materials()
    room(m)
    desk(m)
    machine(m)
    # Harbor light: a cold street lamp outside, shining in through the blinds.
    street = light("SPOT", (-1.3, 6.5, 3.3), 14000, color=(0.6, 0.75, 1.0), size=0.05, spot=math.radians(25))
    aim(street, (-0.3, 0.6, 0.78))
    light("AREA", (0, -2.5, 3.0), 15, color=(0.5, 0.6, 0.8), size=3, rot=(math.radians(40), 0, 0))
    haze(scene, density=0.015)
    scene.eevee.volumetric_tile_size = "4"
    scene.eevee.volumetric_samples = 96
    scene.eevee.volumetric_shadow_samples = 32
    bpy.ops.object.camera_add(location=(-1.5, -2.3, 1.6))
    cam = aim(bpy.context.object, (0.9, 1.3, 1.0))
    cam.data.lens = 24
    scene.camera = cam
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - High Contrast"
    return scene


if __name__ == "__main__":
    big = "--big" in sys.argv
    scene = build()
    scene.eevee.taa_render_samples = 64 if big else 16
    print(render(scene, "desk", width=1920 if big else 960, height=1080 if big else 540))
