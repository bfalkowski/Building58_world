#!/usr/bin/env node
// Writes out/night-<seed>.json: one night of Find the Ring as the house detective sees it at the
// desk. Only the public records and the summary, never the night's truth: who is in the ring and
// how they work stay inside the game.
// Usage: GAMES_REPO=../Building58_games node find-the-ring/night.mjs [seed ...]
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const games = resolve(process.env.GAMES_REPO || join(root, '..', 'Building58_games'));
const load = (f) => import(pathToFileURL(join(games, 'find-the-ring', f)).href);

export async function publicNight(seed) {
  const { buildNight } = await load('night.js');
  const { openDesk } = await load('desk.js');
  const desk = openDesk(buildNight(seed));
  const s = desk.summary();
  return { seed, place: s.place, machine: s.machine, hours: s.hours, regulars: s.regulars, ships: s.ships, records: desk.records() };
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  const seeds = process.argv.slice(2);
  mkdirSync(join(root, 'out'), { recursive: true });
  for (const seed of seeds.length ? seeds : ['test-0']) {
    const path = join(root, 'out', `night-${seed}.json`);
    writeFileSync(path, JSON.stringify(await publicNight(seed), null, 1));
    console.log(path);
  }
}
