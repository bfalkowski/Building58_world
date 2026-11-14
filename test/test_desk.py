import importlib.util
import unittest
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent


def load():
    spec = importlib.util.spec_from_file_location("desk", ROOT / "find-the-ring" / "desk.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class DeskScene(unittest.TestCase):
    def test_builds_the_office(self):
        desk = load()
        scene = desk.build()
        self.assertIsNotNone(scene.camera)
        names = {o.name for o in scene.objects}
        for part in ("desk top", "lamp shade", "cabinet", "plate name", "slat 0", "phone base"):
            self.assertIn(part, names)
        self.assertEqual(bpy.data.objects["plate name"].data.body, desk.MACHINE)
        self.assertGreater(sum(o.type == "LIGHT" for o in scene.objects), 3)

    def test_builds_the_same_scene_twice(self):
        desk = load()
        first = sorted(o.name for o in desk.build().objects)
        second = sorted(o.name for o in desk.build().objects)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
