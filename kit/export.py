"""Export a built scene to out/<name>.glb, a 3D file a browser can load (kit/viewer.html)."""
from kit.render import OUT

import bpy


def export(name):
    OUT.mkdir(exist_ok=True)
    path = OUT / f"{name}.glb"
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", export_lights=True, export_cameras=True, export_apply=True)
    return path
