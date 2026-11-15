# Find the Ring scenes

Scenes for Find the Ring in Building58_games. Each script builds its scene from an empty file.

- `desk.py`: the house detective's office at the club. The desk with a green banker's lamp, the
  house's ledgers and a candlestick telephone. Harbor light comes through the blinds, and the club's
  calculating machine, WAMAC No. 9, stands by the wall with its tubes lit.
- `club.py`: the club's main room. The bar under the club's blue sign, round tables with lamps, the
  band stand with a curtain and a microphone, the telephone booth on the shared line by the left
  wall, the door to the house detective's office on the right wall, and the twelve regulars as
  plain figures with no faces.
- `night.mjs`: writes `out/night-<seed>.json`, one night's public records and summary from the
  games repo (`GAMES_REPO`), the same ones the detective sees at the desk. Never the truth.
- `replay.js`: a viewer add-on that replays that night in the club, one record at a time. At
  each half hour, anyone with nothing in the books walks back to their seat. Then each record
  plays in turn: a caption says what happened and where the person goes, they walk there, and a
  gold ring marks them while the camera follows. Everyone else waits. The booth and the machine's
  window light up when used. Play, Next, a speed choice and a time slider run it. Watch picks one
  regular: only their records play slowly, and the panel lists their whole night.

Each scene keeps its own copy of the names it shows, so it never imports the game.
