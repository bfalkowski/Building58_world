import importlib.util
import unittest
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent


def load():
    spec = importlib.util.spec_from_file_location("club", ROOT / "find-the-ring" / "club.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ClubScene(unittest.TestCase):
    def test_builds_the_room(self):
        club = load()
        scene = club.build()
        self.assertIsNotNone(scene.camera)
        names = {o.name for o in scene.objects}
        for part in ("bar", "sign", "stage", "booth back", "office door", "table 1 top"):
            self.assertIn(part, names)
        self.assertEqual(bpy.data.objects["sign"].data.body, club.CLUB)
        self.assertEqual(bpy.data.objects["office door name"].data.body, club.OFFICE_DOOR)

    def test_has_twelve_regulars(self):
        club = load()
        scene = club.build()
        for k in range(1, club.REGULARS + 1):
            self.assertIn(f"regular-R{k}-sit", bpy.data.objects)
            self.assertIn(f"regular-R{k}-stand", bpy.data.objects)

    def test_has_the_places_a_replay_needs(self):
        club = load()
        club.build()
        names = ["spot-booth", "spot-door", "spot-stand", "spot-piano"]
        names += [f"spot-wait-{k}" for k in range(3)] + [f"spot-machine-{k}" for k in range(3)]
        names += [f"seat-bar-{k}" for k in range(7)] + [f"seat-t{t}-{k}" for t in range(1, 7) for k in range(3)]
        names += ["booth-light", "machine-light", "ship-0", "ship-1", "berth-0", "berth-1"]
        for n in names:
            self.assertIn(n, bpy.data.objects)

    def test_each_figure_and_ship_is_one_mesh(self):
        club = load()
        club.build()
        # A browser draws one object in one go. Joined parts keep the room fast.
        for k in range(1, club.REGULARS + 1):
            for pose in ("sit", "stand"):
                self.assertEqual(len(bpy.data.objects[f"regular-R{k}-{pose}"].children), 1)
        for k in range(2):
            meshes = [c for c in bpy.data.objects[f"ship-{k}"].children if c.type == "MESH"]
            self.assertEqual(len(meshes), 1)
            self.assertGreater(len(meshes[0].data.polygons), 1000)

    def test_lights_say_if_they_cast_shadows(self):
        club = load()
        club.build()
        lights = [o for o in bpy.data.objects if o.type == "LIGHT"]
        self.assertTrue(all("shadow" in o for o in lights))
        # A browser runs out of texture slots with too many shadow lights.
        self.assertLessEqual(sum(1 for o in lights if o["shadow"]), 8)


if __name__ == "__main__":
    unittest.main()
