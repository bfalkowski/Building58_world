#!/usr/bin/env node
// Play the house detective in the 3D club. This server holds the desk, so the night's truth stays
// here and the browser only sees what the desk shows: the public records, and the text of a record
// after a read. The truth comes out only after the detective hands in.
//
// It serves this repo's files on this computer only (GET, nothing outside the repo, no dot files),
// builds out/night-<seed>.json on request, and answers the desk's plays:
//   POST /desk/<seed>/<play>   play is summary, state, read, tail, ban, clear, handin, reveal or new
// state gives back what this desk has already done tonight, so a reloaded page picks up where it was.
// Usage: GAMES_REPO=../Building58_games node find-the-ring/play.mjs [--port 5860]
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { publicNight } from './night.mjs';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const games = resolve(process.env.GAMES_REPO || join(ROOT, '..', 'Building58_games'));
const load = (f) => import(pathToFileURL(join(games, 'find-the-ring', f)).href);
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.css': 'text/css', '.glb': 'model/gltf-binary', '.png': 'image/png',
};
const SEED = /^[\w-]{1,40}$/;

export async function serve(port = 5860) {
  const { buildNight, clock } = await load('night.js');
  const { openDesk, Refused } = await load('desk.js');
  const { scoreAnswer } = await load('score.js');
  const { LOOKALIKES } = await load('rules.js');
  const { detective, houseAlarm, informant } = await load('investigators.js');
  const theme = await load('theme.js');

  // One desk for each night, kept until the server stops or the detective starts over.
  const desks = new Map();
  const deskFor = (seed) => {
    if (!desks.has(seed)) { const night = buildNight(seed); desks.set(seed, { night, desk: openDesk(night) }); }
    return desks.get(seed);
  };
  const nameOf = (id) => theme.regulars[Number(id.slice(1)) - 1].name;

  // What the other detectives would have done on the same night, for the newspaper.
  async function others(seed) {
    const out = {};
    for (const [k, work] of Object.entries({ houseAlarm, detective, informant })) {
      const night = buildNight(seed), d = openDesk(night);
      await work(d, { night, seed });
      const a = d.answer();
      const s = scoreAnswer(night, a, LOOKALIKES);
      out[k] = { bans: Object.keys(a.bans), caught: s.caught, wrongBans: s.wrongBans, points: s.points };
    }
    return out;
  }

  async function play(seed, kind, a) {
    if (kind === 'new') { desks.delete(seed); return { fresh: true }; }
    const { night, desk } = deskFor(seed);
    switch (kind) {
      case 'summary': return desk.summary();
      case 'state': {
        const done = desk.log.filter((x) => x.ok);
        const reads = {}, tails = {}, bans = {};
        for (const x of done) {
          if (x.kind === 'read') { const e = night.records.find((r) => r.id === String(x.args.record)); if (e) reads[e.id] = e.text; }
          if (x.kind === 'tail') {
            const id = String(x.args.regular).trim().toUpperCase();
            tails[id] = night.records.filter((e) => e.who === id && e.kind === 'out').map((e) => ({ record: e.id, time: clock(e.half), went: e.dest }));
          }
        }
        const answer = desk.answer();
        for (const x of done) {
          const id = String(x.args.regular ?? '').trim().toUpperCase();
          if (x.kind === 'ban') bans[id] = x.args.because;
          if (x.kind === 'clear') delete bans[id];
        }
        return { budget: desk.summary().budget, reads, tails, bans, handedIn: Boolean(answer), scores: answer?.scores ?? null };
      }
      case 'read': return desk.read(a.record, a.because);
      case 'tail': return desk.tail(a.regular);
      case 'ban': return desk.ban(a.regular, a.because);
      case 'clear': return desk.clear(a.regular);
      case 'handin': return desk.handIn(a.scores);
      case 'reveal': {
        const answer = desk.answer();
        if (!answer) throw new Refused('hand in first. The truth comes out after that');
        const ringRecords = night.records.filter((e) => e.ring).map((e) => ({
          id: e.id, half: e.half, who: e.who, name: nameOf(e.who), kind: e.kind, ...(e.text ? { text: e.text } : {}), ...(e.dest ? { went: e.dest } : {}),
        }));
        return {
          ring: night.ring, method: night.method, ringName: theme.names.ring, member: theme.names.member, cargo: theme.cargo,
          answer, score: scoreAnswer(night, answer, LOOKALIKES), ringRecords, others: await others(seed),
        };
      }
      default: throw new Refused(`there is no play "${kind}"`);
    }
  }

  const send = (res, code, type, body) => res.writeHead(code, { 'content-type': type, 'cache-control': 'no-store' }).end(body);
  const json = (res, code, x) => send(res, code, 'application/json', JSON.stringify(x));

  const server = createServer(async (req, res) => {
    const url = new URL(req.url, 'http://x');
    const desk = url.pathname.match(/^\/desk\/([^/]+)\/(\w+)$/);
    if (desk) {
      if (req.method !== 'POST' || !SEED.test(desk[1])) return json(res, 404, { error: 'not found' });
      let body = '';
      for await (const c of req) { body += c; if (body.length > 20000) return json(res, 413, { error: 'too long' }); }
      try {
        return json(res, 200, await play(desk[1], desk[2], body ? JSON.parse(body) : {}));
      } catch (err) {
        return json(res, err instanceof Refused || err instanceof SyntaxError ? 400 : 500, { error: err.message });
      }
    }
    if (req.method !== 'GET') return send(res, 405, 'text/plain', 'GET only');
    const night = url.pathname.match(/^\/out\/night-([\w-]{1,40})\.json$/);
    if (night) return json(res, 200, await publicNight(night[1]));
    const path = normalize(decodeURIComponent(url.pathname));
    const file = resolve(join(ROOT, path));
    if (!file.startsWith(ROOT + '/') || file.includes('/.') || !TYPES[extname(file)]) return send(res, 404, 'text/plain', 'Not found');
    try { send(res, 200, TYPES[extname(file)], await readFile(file)); } catch { send(res, 404, 'text/plain', 'Not found'); }
  });
  return new Promise((ok) => server.listen(port, '127.0.0.1', () => ok(server)));
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  const i = process.argv.indexOf('--port');
  const server = await serve(i > 0 ? Number(process.argv[i + 1]) : 5860);
  const seed = process.argv.find((x) => x.startsWith('--night='))?.slice(8) || 'test-10';
  console.log(`The club: http://127.0.0.1:${server.address().port}/kit/viewer.html?scene=club&addon=find-the-ring/detective.js&night=${seed}`);
}
