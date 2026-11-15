import { test } from 'node:test';
import assert from 'node:assert/strict';
import { placesAt, say } from '../find-the-ring/replay.js';

const regulars = ['R1', 'R2', 'R3', 'R4', 'R5'].map((id) => ({ id }));
const rec = (id, kind, who, more = {}) => ({ id, half: 0, kind, who, name: who, ...more });

test('each regular gets one place, by the strongest record', () => {
  const p = placesAt([
    rec('E1', 'call', 'R1', { line: 'X' }),
    rec('E2', 'out', 'R1'),
    rec('E3', 'call', 'R2', { line: 'Y' }),
    rec('E4', 'look', 'R3', { ship: 'S' }),
    rec('E5', 'sit', 'R4', { with: 'R3' }),
  ], 0, regulars);
  assert.deepEqual(p.R1, { out: true });
  assert.deepEqual(p.R2, { spot: 'spot-booth', sitting: false });
  assert.deepEqual(p.R3, { spot: 'spot-machine-0', sitting: false });
  assert.equal(p.R4, 'home', 'R3 is busy at the machine, so R4 has no one to sit with');
  assert.equal(p.R5, 'home');
});

test('a second caller waits by the booth, and a pair gets a table', () => {
  const p = placesAt([
    rec('E1', 'call', 'R1', { line: 'X' }),
    rec('E2', 'call', 'R2', { line: 'X' }),
    rec('E3', 'sit', 'R3', { with: 'R4' }),
  ], 0, regulars);
  assert.equal(p.R2.spot, 'spot-wait-0');
  assert.deepEqual([p.R3.spot, p.R4.spot], ['seat-t1-1', 'seat-t1-2']);
});

test('only the given half counts', () => {
  const p = placesAt([{ ...rec('E1', 'out', 'R1'), half: 3 }], 0, regulars);
  assert.equal(p.R1, 'home');
});

test('records read as plain words', () => {
  assert.equal(say(rec('E1', 'call', 'Dutch', { name: 'Dutch', line: 'Exchange 8-777', mins: 3 })), 'Dutch calls Exchange 8-777 (3 min)');
  assert.equal(say({ kind: 'refused', name: 'Nell', aboutName: 'Kass' }), 'The machine refuses Nell: a question about Kass');
});
