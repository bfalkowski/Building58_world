# Find the Ring scenes

Scenes for Find the Ring in Building58_games. Each script builds its scene from an empty file.

- `desk.py`: the house detective's office at the club. The desk with a green banker's lamp, the
  house's ledgers and a candlestick telephone. Harbor light comes through the blinds, and the club's
  calculating machine, WAMAC No. 9, stands by the wall with its tubes lit.
- `club.py`: the club's main room. The bar under the club's blue sign, round tables with lamps, the
  band stand with a curtain and a microphone, the telephone booth on the shared line by the left
  wall, the door to the house detective's office on the right wall, and the twelve regulars as
  plain figures with no faces. A window in the left wall looks out on the quay and the harbor:
  cranes, lamp posts, ships at anchor far out, and the night's two ships at their berths.
- `night.mjs`: writes `out/night-<seed>.json`, one night's public records and summary from the
  games repo (`GAMES_REPO`), the same ones the detective sees at the desk. Never the truth.
- `replay.js`: a viewer add-on that replays that night in the club, one record at a time. At
  each half hour, anyone with nothing in the books walks back to their seat. Then each record
  plays in turn: a caption says what happened and where the person goes, they walk there, and a
  gold ring marks them while the camera follows. Everyone else waits. The booth and the machine's
  window light up when used. Play, Next, a speed choice and a time slider run it. Watch picks one
  regular: only their records play slowly, and the panel lists their whole night. Each of the
  night's ships sails at its half hour: it turns west and heads out to sea. Harbor puts the camera
  at the window.
- `play.mjs` and `detective.js`: play the house detective in the club. `play.mjs` is a small
  server on this computer that holds the desk from the games repo, so the night's truth never
  reaches the browser before the hand-in. `detective.js` is a viewer add-on built on the replay.
  The night plays as before, and a desk panel lets you click a regular to open their file, pin
  records as evidence, read the text of a call or a request (3 a night, each citing a pinned
  record or a flag), tail one regular (1 a night), ban, set a suspicion for each regular and hand
  in. Then the dawn paper shows who was in the ring, your score, and what the other detectives
  would have done on the same night. A reloaded page keeps the desk. Start over gives a fresh one.

  Run it: `GAMES_REPO=../Building58_games node find-the-ring/play.mjs`, then open the address it
  prints. Add `--night=<seed>` to pick the night.

Each scene keeps its own copy of the names it shows, so it never imports the game.
