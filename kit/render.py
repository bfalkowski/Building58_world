"""The render setup every scene uses: an empty file, a fast engine, and a PNG out."""
from pathlib import Path

import bpy

OUT = Path(__file__).resolve().parent.parent / "out"


def empty_scene():
    """Start from an empty file, with nothing in it."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def render(scene, name, width=640, height=360, engine="BLENDER_EEVEE"):
    """Render the scene's camera to out/<name>.png and return the path."""
    OUT.mkdir(exist_ok=True)
    scene.render.engine = engine
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.image_settings.file_format = "PNG"
    path = OUT / f"{name}.png"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return path
