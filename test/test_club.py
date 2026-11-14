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
        heads = [o for o in scene.objects if o.name.startswith("regular ") and o.name.endswith(" head")]
        self.assertEqual(len(heads), club.REGULARS)


if __name__ == "__main__":
    unittest.main()
