// Replays one night of Find the Ring in the club scene, half hour by half hour, from the night's
// public records (out/night-<seed>.json, made by night.mjs). It moves each regular to where their
// records put them: the telephone booth for a call, the machine's window for a request, a shared
// table to sit with someone, the card table for cards, out of the street door for a step out, and
// home for nothing. It shows only what the records show, the same as the desk.
// Open: kit/viewer.html?scene=club&addon=find-the-ring/replay.js&night=test-0

const HALVES = 16;
const MACHINE_KINDS = new Set(['look', 'msg', 'note', 'refused']);
const CARD_TABLE = 6;

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

// Where every regular is in one half hour. Returns { R1: { spot, sitting } or { out: true } }.
// One place each, by the strongest record: out, then a call, then the machine, then sitting with
// someone, then cards, then home.
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

const clock = (half) => {
  const m = 20 * 60 + half * 30, h = Math.floor(m / 60) % 24, mm = String(m % 60).padStart(2, '0');
  return `${((h + 11) % 12) + 1}:${mm} ${h >= 12 && h < 24 ? 'PM' : 'AM'}`;
};

export default async function replay({ THREE, root, camera, renderer, params, onFrame }) {
  // Loaded here, not at the top, so node can test placesAt and say without three.js.
  const { CSS2DRenderer, CSS2DObject } = await import('three/addons/renderers/CSS2DRenderer.js');
  const seed = params.get('night') || 'test-0';
  const night = await (await fetch(`../out/night-${seed}.json`)).json();
  const node = (n) => root.getObjectByName(n);

  // Each regular: both groups, a name label, and the home they start at.
  const people = night.regulars.map((r) => {
    const sit = node(`regular-${r.id}-sit`), stand = node(`regular-${r.id}-stand`);
    // glTF turns Blender's z-up into y-up: a group parked at Blender y = -20 sits at z = +20 here.
    const startsSitting = sit.position.z < 10;
    const home = (startsSitting ? sit : stand).clone(false);
    const div = document.createElement('div');
    div.className = 'tag';
    div.textContent = r.name;
    div.title = r.role;
    const label = new CSS2DObject(div);
    root.add(label);
    return { ...r, sit, stand, home, homeSitting: startsSitting, label, target: null };
  });

  const labels = new CSS2DRenderer();
  labels.setSize(innerWidth, innerHeight);
  Object.assign(labels.domElement.style, { position: 'fixed', top: '0', left: '0', pointerEvents: 'none' });
  document.body.appendChild(labels.domElement);
  addEventListener('resize', () => labels.setSize(innerWidth, innerHeight));

  const style = document.createElement('style');
  style.textContent = `
    .tag { color: #e8dcc0; font: 11px Georgia, serif; text-shadow: 0 0 4px #000, 0 0 2px #000; white-space: nowrap; }
    .tag.busy { color: #ffd27a; }
    #night { position: fixed; top: 16px; left: 16px; width: min(360px, calc(100vw - 32px)); max-height: 60vh; overflow: auto;
      background: rgba(8, 9, 12, .82); color: #d8d0bc; font: 13px/1.45 Georgia, serif; padding: 12px 14px; border: 1px solid #3a3326; }
    #night h2 { margin: 0 0 4px; font-size: 15px; font-weight: normal; letter-spacing: .04em; }
    #night .row { display: flex; gap: 8px; align-items: center; margin: 6px 0 8px; }
    #night input[type=range] { flex: 1; }
    #night button { background: #2a241a; color: #e8dcc0; border: 1px solid #5a4c33; padding: 2px 10px; font: inherit; cursor: pointer; }
    #night ul { margin: 0; padding-left: 18px; }
    #night .flag { color: #ff9b6b; }
    #night .ship { color: #8fb4ff; }`;
  document.head.appendChild(style);
  const panel = document.createElement('div');
  panel.id = 'night';
  panel.innerHTML = `<h2>${night.place}, night ${seed}</h2>
    <div class="row"><button id="play">Play</button><input id="half" type="range" min="0" max="${HALVES - 1}" value="0"><b id="clock"></b></div>
    <div id="ships"></div><ul id="events"></ul>`;
  document.body.appendChild(panel);
  const $ = (id) => panel.querySelector(`#${id}`);

  const boothLight = node('booth-light'), machineLight = node('machine-light');
  const base = { booth: boothLight?.intensity ?? 0, machine: machineLight?.intensity ?? 0 };

  function show(half) {
    $('clock').textContent = clock(half);
    const now = night.records.filter((e) => e.half === half);
    $('events').innerHTML = now.length
      ? now.map((e) => `<li${e.flag ? ' class="flag"' : ''}>${e.id}: ${say(e)}${e.flag ? ` (flag ${e.flag})` : ''}</li>`).join('')
      : '<li>Nothing in the books this half hour.</li>';
    const ships = night.ships.filter((s) => s.half === half || s.half - 1 === half);
    $('ships').innerHTML = ships.map((s) => `<div class="ship">${s.half === half ? `${s.name} sails now` : `${s.name} sails at ${s.sails}`}</div>`).join('');
    const place = placesAt(night.records, half, night.regulars);
    for (const p of people) {
      const where = place[p.id];
      const busy = where !== 'home';
      p.label.element.classList.toggle('busy', busy);
      if (where.out) { p.target = { out: true }; continue; }
      const spot = where === 'home' ? p.home : node(where.spot);
      p.target = { pos: spot.position.clone(), rot: spot.quaternion.clone(), sitting: where === 'home' ? p.homeSitting : where.sitting };
    }
    if (boothLight) boothLight.intensity = base.booth * (now.some((e) => e.kind === 'call') ? 6 : 1);
    if (machineLight) machineLight.intensity = base.machine * (now.some((e) => MACHINE_KINDS.has(e.kind)) ? 6 : 1);
  }

  // Each frame, slide every regular toward their place. The right figure, sitting or standing,
  // shows; the other hides. Someone out of the club fades from view.
  onFrame((dt) => {
    const k = 1 - Math.exp(-dt * 4);
    for (const p of people) {
      const t = p.target;
      if (!t) continue;
      const on = t.out ? null : t.sitting ? p.sit : p.stand;
      for (const g of [p.sit, p.stand]) g.visible = g === on;
      if (on) {
        const off = on === p.sit ? p.stand : p.sit;
        if (!on.userData.placed) { on.position.copy(off.userData.placed ? off.position : t.pos); on.userData.placed = true; }
        on.position.lerp(t.pos, k);
        on.quaternion.slerp(t.rot, k);
        off.position.copy(on.position);
        off.quaternion.copy(on.quaternion);
        p.label.position.copy(on.position).setY(on.position.y + (t.sitting ? 1.15 : 1.95));
        p.label.visible = true;
      } else {
        p.label.visible = false;
      }
    }
    labels.render(root.parent, camera);
  });

  for (const p of people) p.sit.userData.placed = p.stand.userData.placed = false;
  const half = $('half');
  half.oninput = () => show(Number(half.value));
  let timer = null;
  $('play').onclick = () => {
    if (timer) { clearInterval(timer); timer = null; $('play').textContent = 'Play'; return; }
    $('play').textContent = 'Pause';
    timer = setInterval(() => {
      const next = (Number(half.value) + 1) % HALVES;
      half.value = next;
      show(next);
    }, 2500);
  };
  show(0);
}
