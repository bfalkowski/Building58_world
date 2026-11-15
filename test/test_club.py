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
        names += ["booth-light", "machine-light"]
        for n in names:
            self.assertIn(n, bpy.data.objects)


if __name__ == "__main__":
    unittest.main()
