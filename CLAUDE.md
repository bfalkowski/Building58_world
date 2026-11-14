# Building58 world

3D scenes for the games in Building58_games. Scripts build every scene with Blender's Python module
(bpy). The words are in [docs/GLOSSARY.md](docs/GLOSSARY.md).

## Rules

- **Code, not files.** A script builds each scene from an empty file. No saved .blend files in git,
  and no renders: they go to `out/`.
- **Made-up only.** Made-up people, places, signs and brands. No real brands, people or politics, and
  nothing copied from a film, book or game. The look is the free noir genre and nothing more.
- **Own assets only.** Every model, texture and font is made by a script here or has a free license
  that allows it. Write the license next to the asset.
- **The scene reads, never writes, the game.** A scene may read a night's public records from the
  games repo. It never holds a game's sealed truth.
- **The kit holds only what two scenes use.**
- **Keys stay out.** The secret check runs on commit (`git config core.hooksPath .githooks`).
- Pinned versions in `requirements.txt`. Python 3.13, `unittest`, no other test tools.
- No theme word in repo or folder names.
- Write plain words: short sentences, no em dashes.
