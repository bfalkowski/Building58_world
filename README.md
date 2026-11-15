# Building58 world

3D scenes for the games in Building58_games, built with Blender's Python module. A script builds
each scene from nothing, so the repo holds code, not saved .blend files. Renders go to `out/`, which
git ignores.

## Set up

bpy needs Python 3.13 on Apple Silicon (arm64) or another platform with a bpy wheel.

    uv venv --python cpython-3.13 .venv
    uv pip install --python .venv/bin/python -r requirements.txt
    git config core.hooksPath .githooks

## Run

    .venv/bin/python kit/smoke.py                 # renders out/smoke.png
    .venv/bin/python find-the-ring/desk.py --big  # renders out/desk.png at 1920 x 1080
    .venv/bin/python find-the-ring/desk.py --glb  # also writes out/desk.glb
    .venv/bin/python -m http.server 5859 --bind 127.0.0.1
    # then open http://127.0.0.1:5859/kit/viewer.html?scene=desk to walk around it
    # replay a night in the club: export its public records, then open the replay
    GAMES_REPO=../Building58_games node find-the-ring/night.mjs test-0
    .venv/bin/python find-the-ring/club.py --glb
    # http://127.0.0.1:5859/kit/viewer.html?scene=club&addon=find-the-ring/replay.js&night=test-0
    GAMES_REPO=../Building58_games .venv/bin/python -m unittest discover -s test

## Layout

- `kit/`: what two scenes use: lights, materials, camera rigs, the render setup, the glTF export
  and `viewer.html`, a browser page (three.js from a CDN) that loads a scene's .glb to orbit it.
- `find-the-ring/`: the scenes for Find the Ring. `desk.py` is the house detective's office,
  `club.py` the main room.
- `test/`: a smoke render and the secret check.
