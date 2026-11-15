// The club server: the browser sees only public records until the hand-in, and the desk's rules hold.
// Needs GAMES_REPO, a games checkout with find-the-ring.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { serve } from '../find-the-ring/play.mjs';

const server = await serve(0);
const base = `http://127.0.0.1:${server.address().port}`;
const play = async (kind, args = {}) => {
  const res = await fetch(`${base}/desk/test-10/${kind}`, { method: 'POST', body: JSON.stringify(args) });
  return { code: res.status, body: await res.json() };
};
test.after(() => server.close());

test('the night the page loads has no truth in it', async () => {
  const night = await (await fetch(`${base}/out/night-test-10.json`)).json();
  const text = JSON.stringify(night);
  assert.ok(night.records.length > 0);
  for (const k of ['"ring"', '"method"', '"text"', '"dest"']) assert.ok(!text.includes(k), `${k} must not be in the public night`);
});

test('the truth comes out only after the hand-in', async () => {
  await play('new');
  assert.equal((await play('reveal')).code, 400);
  const ban = await play('ban', { regular: 'R10', because: [] });
  assert.equal(ban.code, 400, 'a ban must cite a record');
  const scores = Object.fromEntries(Array.from({ length: 12 }, (_, i) => [`R${i + 1}`, 0]));
  assert.equal((await play('handin', { scores })).code, 200);
  const r = await play('reveal');
  assert.equal(r.code, 200);
  assert.ok(Array.isArray(r.body.ring));
  assert.equal(typeof r.body.score.points, 'number');
  assert.equal((await play('ban', { regular: 'R1', because: ['E1'] })).code, 400, 'bans are final after the hand-in');
});

test('a reloaded page gets back what the desk did', async () => {
  await play('new');
  const night = await (await fetch(`${base}/out/night-test-10.json`)).json();
  const e = night.records.find((x) => ['call', 'msg', 'look', 'note'].includes(x.kind));
  const other = night.records.find((x) => x.id !== e.id);
  assert.equal((await play('read', { record: e.id, because: [other.id] })).code, 200);
  assert.equal((await play('tail', { regular: 'R2' })).code, 200);
  const st = (await play('state')).body;
  assert.equal(typeof st.reads[e.id], 'string');
  assert.ok(Array.isArray(st.tails.R2));
  assert.deepEqual(st.budget, { reads: 2, tails: 0 });
});

test('only files inside the repo are served', async () => {
  assert.equal((await fetch(`${base}/../../etc/passwd`)).status, 404);
  assert.equal((await fetch(`${base}/.git/config`)).status, 404);
  assert.equal((await fetch(`${base}/desk/..%2F/summary`, { method: 'POST' })).status, 404);
});
