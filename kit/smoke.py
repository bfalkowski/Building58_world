"""The smoke render: one lit cube, to show bpy works here. Writes out/smoke.png."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bpy  # noqa: E402
from kit.render import empty_scene, render  # noqa: E402


def build():
    scene = empty_scene()
    bpy.ops.mesh.primitive_cube_add(size=1)
    bpy.ops.object.light_add(type="AREA", location=(2, -2, 3))
    bpy.context.object.data.energy = 300
    bpy.ops.object.camera_add(location=(3, -3, 2), rotation=(1.1, 0, 0.785))
    scene.camera = bpy.context.object
    return scene


if __name__ == "__main__":
    print(render(build(), "smoke", width=320, height=180))
