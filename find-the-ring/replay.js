// Replays one night of Find the Ring in the club scene from the night's public records
// (out/night-<seed>.json, made by night.mjs). It shows only what the records show, the same as the
// desk.
//
// It tells the night one record at a time. At the start of each half hour, anyone with nothing in
// the books walks back to their own seat. Then each record plays in turn: a caption says what
// happened, the person in it walks to where it puts them, and everyone else waits. The camera can
// follow them. "Watch" picks one regular: their records play slowly and everyone else's jump.
//
// Where a record puts someone: the telephone booth for a call (a second caller waits beside it),
// the machine's window for a request, a shared table to sit with someone, the card table for cards,
// out of the street door for a step out.
// Open: kit/viewer.html?scene=club&addon=find-the-ring/replay.js&night=test-0

const HALVES = 16;
const MACHINE_KINDS = new Set(['look', 'msg', 'note', 'refused']);
const CARD_TABLE = 6;
const WALK = 1.3; // meters a second at normal speed
const PAUSE = 2.2; // seconds to read a caption after everyone arrives

// One record in plain words.
export function say(e) {
  switch (e.kind) {
    case 'call': return `${e.name} calls ${e.line} (${e.mins} min)`;
    case 'sit': return `${e.name} sits with ${e.withName}`;
    case 'out': return `${e.name} steps out`;
    case 'msg': return `${e.name} sends a message to ${e.toName} through the machine`;
    case 'look': return `${e.name} asks the machine about ${e.ship}`;
    case 'note': return `${e.name} leaves a note with the machine`;
    case 'cards': return `${e.name} plays cards (${e.pot} pot)`;
    case 'refused': return `The machine refuses ${e.name}: a question about ${e.aboutName}`;
    default: return `${e.name}: ${e.kind}`;
  }
}

// Where every regular is at the end of one half hour. Returns { R1: { spot, sitting } or
// { out: true } or 'home' }. One place each, by the strongest record: out, then a call, then the
// machine, then sitting with someone, then cards, then home.
export function placesAt(records, half, regulars) {
  const now = records.filter((e) => e.half === half);
  const place = {};
  const take = (id, p) => { if (!place[id]) place[id] = p; };
  for (const e of now) if (e.kind === 'out') take(e.who, { out: true });
  let caller = 0;
  for (const e of now) if (e.kind === 'call' && !place[e.who]) take(e.who, { spot: caller++ ? `spot-wait-${Math.min(caller - 2, 2)}` : 'spot-booth', sitting: false });
  let window = 0;
  for (const e of now) if (MACHINE_KINDS.has(e.kind) && !place[e.who]) take(e.who, { spot: `spot-machine-${Math.min(window++, 2)}`, sitting: false });
  // A pair that sits together gets its own table, from table 1, never the card table.
  let t = 1;
  for (const e of now) if (e.kind === 'sit' && !place[e.who] && !place[e.with] && t < CARD_TABLE) {
    take(e.who, { spot: `seat-t${t}-1`, sitting: true });
    take(e.with, { spot: `seat-t${t}-2`, sitting: true });
    t++;
  }
  let hand = 0;
  for (const e of now) if (e.kind === 'cards' && !place[e.who] && hand < 3) take(e.who, { spot: `seat-t${CARD_TABLE}-${hand++}`, sitting: true });
  for (const r of regulars) take(r.id, 'home');
  return place;
}

// Does this record's kind lead to this place? A person's place comes from their strongest record,
// so a weaker record of theirs moves no one.
function leadsTo(kind, where) {
  if (where.out) return kind === 'out';
  const s = where.spot;
  if (/booth|wait/.test(s)) return kind === 'call';
  if (s.startsWith('spot-machine')) return MACHINE_KINDS.has(kind);
  if (s.startsWith(`seat-t${CARD_TABLE}`)) return kind === 'cards';
  if (s.startsWith('seat-t')) return kind === 'sit';
  return false;
}

// The story of one half hour, as steps. The first step sends everyone with nothing in the books
// home. Then one step per record, in order, moving the people that record places. A person moves
// once a half hour, at the first record that leads to their place.
export function stepsFor(records, half, regulars) {
  const place = placesAt(records, half, regulars);
  const steps = [{ home: true, movers: regulars.map((r) => r.id).filter((id) => place[id] === 'home') }];
  const moved = new Set();
  for (const e of records.filter((x) => x.half === half)) {
    const movers = [];
    for (const id of [e.who, e.kind === 'sit' ? e.with : null]) {
      if (!id || moved.has(id) || place[id] === 'home' || !leadsTo(e.kind, place[id])) continue;
      moved.add(id);
      movers.push(id);
    }
    steps.push({ record: e, movers });
  }
  return { place, steps };
}

// Where a place is, in plain words, for the caption.
export function whereWords(where) {
  if (where === 'home') return 'goes back to their seat';
  if (where.out) return 'leaves by the street door';
  if (where.spot === 'spot-booth') return 'goes into the telephone booth';
  if (where.spot.startsWith('spot-wait')) return 'waits by the telephone booth';
  if (where.spot.startsWith('spot-machine')) return "goes to the machine's window";
  if (where.spot.startsWith(`seat-t${CARD_TABLE}`)) return 'sits down at the card table';
  return `sits down at table ${where.spot.match(/seat-t(\d)/)?.[1] ?? ''}`.trim();
}

export const clockOf = (half) => {
  const m = 20 * 60 + half * 30, h = Math.floor(m / 60) % 24, mm = String(m % 60).padStart(2, '0');
  return `${((h + 11) % 12) + 1}:${mm} ${h >= 12 ? 'PM' : 'AM'}`;
};

export default async function replay({ THREE, root, camera, controls, params, onFrame }) {
  // Loaded here, not at the top, so node can test the functions above without three.js.
  const { CSS2DRenderer, CSS2DObject } = await import('three/addons/renderers/CSS2DRenderer.js');
  const seed = params.get('night') || 'test-0';
  const night = await (await fetch(`../out/night-${seed}.json`)).json();
  const node = (n) => root.getObjectByName(n);
  const door = node('spot-door');
  const byId = {};

  // Each regular: both figures, a name label, and the home they start at.
  const people = night.regulars.map((r) => {
    const sit = node(`regular-${r.id}-sit`), stand = node(`regular-${r.id}-stand`);
    // glTF turns Blender's z-up into y-up: a figure parked at Blender y = -20 sits at z = +20 here.
    const homeSitting = sit.position.z < 10;
    const homeNode = homeSitting ? sit : stand;
    const home = { pos: homeNode.position.clone(), quat: homeNode.quaternion.clone(), sitting: homeSitting };
    const div = document.createElement('div');
    div.className = 'tag';
    div.textContent = r.name;
    div.title = r.role;
    const label = new CSS2DObject(div);
    root.add(label);
    const p = { ...r, sit, stand, home, label, key: 'home', walk: null, out: false };
    byId[r.id] = p;
    return p;
  });

  const spotOf = (p, where) => {
    if (where === 'home') return { ...p.home, key: 'home' };
    if (where.out) return { pos: door.position.clone(), quat: door.quaternion.clone(), out: true, key: 'out' };
    const n = node(where.spot);
    return { pos: n.position.clone(), quat: n.quaternion.clone(), sitting: where.sitting, key: where.spot };
  };
  const floorOf = (s) => (s.sitting ? 0 : s.pos.y);
  const shown = (p) => (p.out ? null : p.sit.visible ? p.sit : p.stand);

  // Put a person somewhere at once, with no walk.
  function put(p, s) {
    p.walk = null;
    p.key = s.key;
    p.out = Boolean(s.out);
    p.sit.visible = !p.out && Boolean(s.sitting);
    p.stand.visible = !p.out && !s.sitting;
    const g = s.sitting ? p.sit : p.stand;
    g.position.copy(s.pos);
    g.quaternion.copy(s.quat);
  }

  // Start a person walking to a place. They stand up, or come in by the street door.
  function walkTo(p, s) {
    if (p.key === s.key && !p.walk) return false;
    const from = p.out ? door.position : shown(p).position;
    p.stand.position.set(from.x, p.sit.visible ? 0 : from.y, from.z);
    if (p.sit.visible) p.stand.quaternion.copy(p.sit.quaternion);
    p.sit.visible = false;
    p.stand.visible = true;
    p.out = false;
    p.walk = s;
    return true;
  }

  for (const p of people) put(p, spotOf(p, 'home'));

  // The night's ships, at their berths outside the harbor window. Each sails at its half hour:
  // it gathers speed, turns west and heads out to sea.
  const ships = night.ships.slice(0, 2).map((s, i) => {
    const g = node(`ship-${i}`);
    if (!g) return null;
    const div = document.createElement('div');
    div.className = 'tag ship-tag';
    div.textContent = `${s.name}, sails ${s.sails}`;
    const label = new CSS2DObject(div);
    root.add(label);
    return { ...s, g, label, berth: g.position.clone(), quat: g.quaternion.clone(), t: -1 };
  }).filter(Boolean);
  const fwd = new THREE.Vector3();
  function dock(ship, gone) {
    ship.g.position.copy(ship.berth);
    ship.g.quaternion.copy(ship.quat);
    ship.g.visible = !gone;
    ship.t = -1;
  }

  // Labels, a ring on the floor under whoever the caption is about, and the page's own styles.
  const labels = new CSS2DRenderer();
  labels.setSize(innerWidth, innerHeight);
  Object.assign(labels.domElement.style, { position: 'fixed', top: '0', left: '0', pointerEvents: 'none' });
  document.body.appendChild(labels.domElement);
  addEventListener('resize', () => labels.setSize(innerWidth, innerHeight));
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.32, 0.4, 40), new THREE.MeshBasicMaterial({ color: 0xffc860, transparent: true, opacity: 0.9, side: THREE.DoubleSide, fog: false }));
  ring.rotation.x = -Math.PI / 2;
  ring.visible = false;
  root.add(ring);

  const style = document.createElement('style');
  style.textContent = `
    .tag { color: #e8dcc0; font: 11px Georgia, serif; text-shadow: 0 0 4px #000, 0 0 2px #000; white-space: nowrap; }
    .tag.active { color: #ffd27a; font-size: 15px; }
    .tag.dim { opacity: .35; }
    .tag.ship-tag { color: #8fb4ff; font-style: italic; }
    #night { position: fixed; top: 16px; left: 16px; width: min(380px, calc(100vw - 32px)); max-height: 62vh; overflow: auto;
      background: rgba(8, 9, 12, .86); color: #d8d0bc; font: 13px/1.45 Georgia, serif; padding: 12px 14px; border: 1px solid #3a3326; }
    #night h2 { margin: 0 0 4px; font-size: 15px; font-weight: normal; letter-spacing: .04em; }
    #night .row { display: flex; gap: 6px; align-items: center; margin: 6px 0; flex-wrap: wrap; }
    #night input[type=range] { flex: 1; min-width: 120px; }
    #night button, #night select { background: #2a241a; color: #e8dcc0; border: 1px solid #5a4c33; padding: 2px 8px; font: inherit; cursor: pointer; }
    #night ul { margin: 6px 0 0; padding-left: 0; list-style: none; }
    #night li { padding: 2px 6px; border-left: 3px solid transparent; cursor: pointer; }
    #night li:hover { background: #1c1913; }
    #night li.now { border-left-color: #ffc860; background: #221d14; color: #fff3d6; }
    #night li.done { opacity: .55; }
    #night li .t { color: #9a8f78; margin-right: 6px; }
    #night .flag { color: #ff9b6b; }
    #night .ship { color: #8fb4ff; }
    #caption { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); max-width: min(760px, calc(100vw - 32px));
      background: rgba(8, 9, 12, .86); color: #fff3d6; font: 18px/1.4 Georgia, serif; padding: 10px 18px; border: 1px solid #5a4c33; text-align: center; }
    #caption small { display: block; color: #b3a78c; font-size: 13px; }
    #caption:empty { display: none; }`;
  document.head.appendChild(style);
  const panel = document.createElement('div');
  panel.id = 'night';
  panel.innerHTML = `<h2>${night.place}, night ${seed}</h2>
    <div class="row"><button id="play">Play</button><button id="next" title="The next record">Next</button>
      <input id="half" type="range" min="0" max="${HALVES - 1}" value="0"><b id="clock"></b></div>
    <div class="row">
      <select id="speed"><option value="0.5">Slow</option><option value="1" selected>Normal</option><option value="2">Fast</option></select>
      <label><input id="follow" type="checkbox" checked> Follow</label>
      <button id="harbor" title="Look out of the harbor window">Harbor</button>
      <select id="watch"><option value="">Watch everyone</option>${night.regulars.map((r) => `<option value="${r.id}">Watch ${r.name}</option>`).join('')}</select>
    </div>
    <div id="ships"></div><ul id="events"></ul>`;
  document.body.appendChild(panel);
  const caption = document.createElement('div');
  caption.id = 'caption';
  document.body.appendChild(caption);
  const $ = (id) => panel.querySelector(`#${id}`);

  const lights = { booth: node('booth-light'), machine: node('machine-light') };
  const base = Object.fromEntries(Object.entries(lights).map(([k, l]) => [k, l?.intensity ?? 0]));
  const glow = (k, on) => { if (lights[k]) lights[k].intensity = base[k] * (on ? 6 : 1); };

  // The story: which half hour, its steps, and which step is playing.
  const S = { half: 0, steps: [], place: {}, i: -1, pause: 0, playing: false, active: null };
  const speed = () => Number($('speed').value);
  const watching = () => $('watch').value;
  const about = (e, id) => [e.who, e.with, e.to, e.about].includes(id);

  function listRecords() {
    const w = watching();
    const recs = w ? night.records.filter((e) => about(e, w)) : night.records.filter((e) => e.half === S.half);
    const cur = S.steps[S.i]?.record;
    const doneIds = new Set(S.steps.slice(0, Math.max(0, S.i)).map((s) => s.record?.id));
    $('events').innerHTML = recs.length
      ? recs.map((e) => {
        const state = cur && e.id === cur.id ? 'now' : e.half < S.half || doneIds.has(e.id) ? 'done' : '';
        return `<li data-id="${e.id}" class="${state}${e.flag ? ' flag' : ''}"><span class="t">${w ? e.time : e.id}</span>${say(e)}${e.flag ? ` (flag ${e.flag})` : ''}</li>`;
      }).join('')
      : '<li>Nothing in the books this half hour.</li>';
    $('events').querySelector('.now')?.scrollIntoView({ block: 'nearest' });
  }

  function setActive(p) {
    const w = watching();
    for (const q of people) {
      q.label.element.classList.toggle('active', q === p);
      q.label.element.classList.toggle('dim', Boolean(w) && q.id !== w && q !== p);
    }
    S.active = p;
  }

  // Go to the start of a half hour. A jump puts everyone where the half hour before left them.
  function startHalf(h, jump) {
    S.half = h;
    $('half').value = h;
    $('clock').textContent = clockOf(h);
    if (jump) {
      const before = h > 0 ? placesAt(night.records, h - 1, night.regulars) : {};
      for (const p of people) put(p, spotOf(p, before[p.id] ?? 'home'));
    }
    for (const ship of ships) {
      if (jump || ship.half === h) dock(ship, ship.half < h);
      if (ship.half === h) ship.t = 0;
    }
    ({ steps: S.steps, place: S.place } = stepsFor(night.records, h, night.regulars));
    S.i = -1;
    const soon = night.ships.filter((s) => s.half === h || s.half - 1 === h);
    $('ships').innerHTML = soon.map((s) => `<div class="ship">${s.half === h ? `${s.name} sails now` : `${s.name} sails at ${s.sails}`}</div>`).join('');
    next();
  }

  // Play the next step. When watching one regular, steps not about them happen at once.
  function next() {
    for (;;) {
      S.i++;
      if (S.i >= S.steps.length) {
        if (S.half < HALVES - 1) return startHalf(S.half + 1, false);
        S.playing = false;
        $('play').textContent = 'Play';
        caption.innerHTML = 'The night is over. 4:00 AM.';
        return;
      }
      const step = S.steps[S.i];
      const e = step.record;
      const w = watching();
      const shown = !w || step.movers.includes(w) || (e && about(e, w));
      let moving = 0;
      for (const id of step.movers) {
        const p = byId[id], s = spotOf(p, S.place[id]);
        if (shown) moving += walkTo(p, s) ? 1 : 0;
        else put(p, s);
      }
      glow('booth', S.steps.slice(0, S.i + 1).some((x) => x.record?.kind === 'call'));
      glow('machine', Boolean(e && MACHINE_KINDS.has(e.kind)));
      if (!shown) continue;
      if (step.home) {
        const n = S.steps.length - 1;
        const sails = ships.find((x) => x.half === S.half);
        caption.innerHTML = `${clockOf(S.half)}${sails ? ` · <span style="color:#8fb4ff">${sails.name} sails</span>` : ''}<small>${moving ? 'Anyone with nothing in the books goes back to their seat' : n ? `${n} record${n > 1 ? 's' : ''} this half hour` : 'Nothing in the books this half hour'}</small>`;
        setActive(null);
        S.pause = moving ? PAUSE / 2 : 1.0;
      } else {
        const p = byId[e.who];
        const where = step.movers.includes(e.who) ? whereWords(S.place[e.who]) : 'stays where they are';
        const joins = e.kind === 'sit' && step.movers.length === 2 ? `, and ${byId[e.with].name} joins them` : '';
        caption.innerHTML = `${e.time} · ${e.id}${e.flag ? ` · <span style="color:#ff9b6b">flag ${e.flag}</span>` : ''}<br>${say(e)}<small>${p.name} ${where}${joins}</small>`;
        setActive(p);
        S.pause = PAUSE;
      }
      listRecords();
      return;
    }
  }

  // Each frame: walk everyone who is walking, then count down the pause when all have arrived.
  const target = new THREE.Vector3();
  onFrame((dt) => {
    const v = WALK * speed() * dt;
    let walking = false;
    for (const p of people) {
      const s = p.walk;
      if (s) {
        walking = true;
        target.set(s.pos.x, floorOf(s), s.pos.z);
        const d = target.clone().sub(p.stand.position);
        if (d.length() <= v) {
          put(p, s);
        } else {
          p.stand.position.addScaledVector(d.normalize(), v);
          p.stand.lookAt(target.x, p.stand.position.y, target.z);
        }
      }
      const g = shown(p);
      p.label.visible = Boolean(g);
      if (g) p.label.position.set(g.position.x, g.position.y + (g === p.sit ? 1.15 : 1.95), g.position.z);
    }
    for (const ship of ships) {
      if (ship.t >= 0) {
        ship.t += dt * speed();
        const turn = Math.min(1, ship.t / 10) * Math.PI / 2;
        ship.g.quaternion.copy(ship.quat).multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), turn));
        ship.g.position.addScaledVector(fwd.set(0, 0, -1).applyQuaternion(ship.g.quaternion), Math.min(5, 0.5 * ship.t) * dt * speed());
        if (ship.t > 45) { ship.g.visible = false; ship.t = -1; }
      }
      ship.label.visible = ship.g.visible;
      ship.label.position.set(ship.g.position.x, 6.5, ship.g.position.z);
    }
    const a = S.active && shown(S.active);
    ring.visible = Boolean(a);
    if (a) ring.position.set(a.position.x, (a === S.active.sit ? 0 : a.position.y) + 0.02, a.position.z);
    if (a && $('follow').checked) controls.target.lerp(target.set(a.position.x, 1.0, a.position.z), 1 - Math.exp(-dt * 2));
    if (S.playing && !walking) {
      S.pause -= dt * speed();
      if (S.pause <= 0) next();
    }
    labels.render(root.parent, camera);
  });

  $('half').oninput = () => startHalf(Number($('half').value), true);
  $('next').onclick = () => next();
  // Stand at the harbor window and look out at the berths.
  $('harbor').onclick = () => {
    $('follow').checked = false;
    camera.position.set(-4.6, 1.9, -0.85);
    controls.target.set(-22, 1.5, 1.5);
  };
  $('watch').onchange = () => { setActive(watching() ? byId[watching()] : null); listRecords(); };
  $('play').onclick = () => {
    S.playing = !S.playing;
    $('play').textContent = S.playing ? 'Pause' : 'Play';
  };
  // Click a record to look at the person in it.
  $('events').onclick = (ev) => {
    const e = night.records.find((x) => x.id === ev.target.closest('li')?.dataset.id);
    if (e) { setActive(byId[e.who]); $('follow').checked = true; }
  };
  startHalf(0, true);
  caption.innerHTML = `${night.place}<small>Press Play, or Next to go one record at a time</small>`;
  // For another add-on built on the replay, such as the detective's desk.
  return {
    night, seed, people, byId, caption,
    focus(id) { setActive(byId[id]); $('follow').checked = true; },
    jumpTo(half) { startHalf(half, true); },
  };
}
