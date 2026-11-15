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

import { stepsFor, whereWords, clockOf } from '../find-the-ring/replay.js';

test('a half hour plays as a home step, then one step per record', () => {
  const recs = [
    rec('E1', 'sit', 'R1', { with: 'R2' }),
    rec('E2', 'call', 'R3', { line: 'X' }),
    rec('E3', 'note', 'R3'),
  ];
  const { steps } = stepsFor(recs, 0, regulars);
  assert.equal(steps.length, 4);
  assert.ok(steps[0].home);
  assert.deepEqual(steps[0].movers, ['R4', 'R5']);
  assert.deepEqual(steps[1].movers, ['R1', 'R2'], 'the pair walks to their table together');
  assert.deepEqual(steps[2].movers, ['R3'], 'the call takes R3 to the booth');
  assert.deepEqual(steps[3].movers, [], 'the note does not move R3 again');
});

test('a weaker record moves no one: a call before a step out', () => {
  const { steps, place } = stepsFor([rec('E1', 'call', 'R1', { line: 'X' }), rec('E2', 'out', 'R1')], 0, regulars);
  assert.deepEqual(place.R1, { out: true });
  assert.deepEqual(steps[1].movers, []);
  assert.deepEqual(steps[2].movers, ['R1']);
});

test('captions name the place and the time', () => {
  assert.equal(whereWords({ spot: 'spot-booth', sitting: false }), 'goes into the telephone booth');
  assert.equal(whereWords({ spot: 'seat-t2-1', sitting: true }), 'sits down at table 2');
  assert.equal(whereWords({ out: true }), 'leaves by the street door');
  assert.equal(clockOf(0), '8:00 PM');
  assert.equal(clockOf(9), '12:30 AM');
  assert.equal(clockOf(15), '3:30 AM');
});
