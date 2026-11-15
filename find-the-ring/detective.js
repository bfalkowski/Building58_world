// Play the house detective in the club. A viewer add-on built on the replay: the night plays as
// before, and a desk panel lets the detective work it under the desk's rules.
//   Click a regular (their name in the room, or a record in the list) to open their file.
//   Pin a record to use it as evidence. A read and a ban must cite pinned records. A flagged
//   record is its own reason for a read.
//   Read opens the text of a call or a request to the machine (3 a night). Tail sends the doorman
//   after one regular (1 a night). Ban throws them out. Then set a suspicion for each regular and
//   hand in. The dawn paper shows the truth.
// The desk lives in the club server (play.mjs), so the truth never reaches this page before the
// hand-in. Open: node find-the-ring/play.mjs, then the address it prints.

const FLAG = '#ff9b6b';

export default async function detectiveDesk(ctx) {
  const mod = await import(`./replay.js?v=${Date.now()}`);
  const { say, clockOf } = mod;
  const R = await mod.default(ctx);
  const { night, seed, people, byId } = R;

  const post = async (kind, args = {}) => {
    const res = await fetch(`/desk/${encodeURIComponent(seed)}/${kind}`, { method: 'POST', body: JSON.stringify(args) });
    if (res.status === 404 || res.status === 501) throw new Error('This page needs the club server. Run: node find-the-ring/play.mjs');
    const x = await res.json();
    if (!res.ok) throw new Error(x.error);
    return x;
  };

  const S = {
    sel: null, pins: new Set(), reads: {}, tails: {}, bans: {}, scores: {}, budget: { reads: 0, tails: 0 },
    handedIn: false, sure: false, msg: '', truth: null,
  };
  for (const r of night.regulars) S.scores[r.id] = 0;

  const style = document.createElement('style');
  style.textContent = `
    .tag { pointer-events: auto; cursor: pointer; }
    .tag.picked { outline: 1px solid #ffc860; padding: 0 3px; }
    .tag.banned { color: #ff8a6b; text-decoration: line-through; }
    .tag.ring { color: #ff4a3a; font-weight: bold; }
    #desk { position: fixed; top: 16px; right: 16px; width: min(360px, calc(100vw - 32px)); max-height: calc(100vh - 240px); overflow: auto;
      background: rgba(8, 9, 12, .9); color: #d8d0bc; font: 13px/1.45 Georgia, serif; padding: 12px 14px; border: 1px solid #5a4c33; }
    #desk h2 { margin: 0; font-size: 15px; font-weight: normal; letter-spacing: .04em; display: flex; justify-content: space-between; }
    #desk h3 { margin: 10px 0 4px; font-size: 13px; font-weight: normal; color: #b3a78c; text-transform: uppercase; letter-spacing: .06em; }
    #desk button { background: #2a241a; color: #e8dcc0; border: 1px solid #5a4c33; padding: 1px 7px; font: inherit; cursor: pointer; }
    #desk button:disabled { opacity: .4; cursor: default; }
    #desk button.on { background: #5a4520; border-color: #ffc860; }
    #desk ul { margin: 0; padding: 0; list-style: none; }
    #desk li { padding: 3px 0; border-top: 1px solid #221f18; }
    #desk li .t { color: #9a8f78; margin-right: 4px; }
    #desk li .acts { float: right; display: flex; gap: 3px; }
    #desk .text { display: block; margin: 3px 0 0 10px; color: #fff3d6; font-style: italic; }
    #desk .msg { color: #ffb08a; margin-top: 6px; }
    #desk .habit { color: #9a8f78; }
    #desk .sus { display: grid; grid-template-columns: 1fr 110px 26px; gap: 2px 6px; align-items: center; }
    #desk .sus span.b { color: #ff8a6b; }
    #desk .who { cursor: pointer; }
    #desk .who:hover { color: #fff3d6; }
    #paper { position: fixed; inset: 0; background: rgba(0, 0, 0, .7); display: flex; align-items: center; justify-content: center; padding: 16px; z-index: 5; }
    #paper[hidden] { display: none; }
    #paper article { background: #efe6d0; color: #1a1712; font: 14px/1.45 Georgia, serif; max-width: 760px; width: 100%; max-height: calc(100vh - 32px); overflow: auto; padding: 18px 24px; box-shadow: 0 10px 40px #000; }
    #paper .mast { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 3px double #1a1712; padding-bottom: 4px; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
    #paper .mast b { font-size: 24px; letter-spacing: .02em; text-transform: none; }
    #paper h1 { font-size: 30px; line-height: 1.1; margin: 12px 0 6px; text-transform: uppercase; }
    #paper .deck { font-size: 16px; font-style: italic; margin: 0 0 10px; }
    #paper .cols { columns: 2 260px; column-gap: 24px; column-rule: 1px solid #b9ad92; }
    #paper h4 { margin: 8px 0 2px; text-transform: uppercase; font-size: 12px; letter-spacing: .06em; break-after: avoid; }
    #paper p, #paper ul { margin: 0 0 6px; }
    #paper ul { padding-left: 16px; }
    #paper .btns { display: flex; gap: 8px; justify-content: flex-end; margin-top: 10px; }
    #paper button { background: #1a1712; color: #efe6d0; border: 0; padding: 4px 12px; font: inherit; cursor: pointer; }`;
  document.head.appendChild(style);

  const desk = document.createElement('div');
  desk.id = 'desk';
  document.body.appendChild(desk);
  const paper = document.createElement('div');
  paper.id = 'paper';
  paper.hidden = true;
  document.body.appendChild(paper);

  const nameOf = (id) => byId[id]?.name ?? id;
  const about = (e, id) => [e.who, e.with, e.to, e.about].includes(id);
  const readable = (e) => ['msg', 'look', 'note', 'refused', 'call'].includes(e.kind);
  const list = (ids) => { const n = ids.map(nameOf); return n.length <= 1 ? n.join('') : `${n.slice(0, -1).join(', ')} and ${n.at(-1)}`; };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

  // Run one desk play. A refusal shows in the panel, in the desk's own words.
  async function act(kind, args, then) {
    S.msg = '';
    try { then(await post(kind, args)); } catch (err) { S.msg = err.message; }
    draw();
  }

  function select(id) {
    S.sel = id;
    R.focus(id);
    draw();
  }

  function reasons(not) {
    const rec = night.records.find((e) => e.id === not);
    const pins = [...S.pins].filter((x) => x !== not);
    if (pins.length) return pins;
    return rec?.flag ? [not] : [];
  }

  function draw() {
    const lock = S.handedIn;
    for (const p of people) {
      const el = p.label.element;
      el.classList.toggle('picked', p.id === S.sel);
      el.classList.toggle('banned', Boolean(S.bans[p.id]));
      el.classList.toggle('ring', Boolean(S.truth?.ring.includes(p.id)));
    }
    const p = S.sel && byId[S.sel];
    const recs = p ? night.records.filter((e) => about(e, p.id)) : [];
    const recLine = (e) => {
      const pinned = S.pins.has(e.id);
      const acts = lock ? '' : `<span class="acts"><button data-pin="${e.id}" class="${pinned ? 'on' : ''}" title="Use as evidence">${pinned ? 'Pinned' : 'Pin'}</button>${readable(e) && !(e.id in S.reads) ? `<button data-read="${e.id}" ${S.budget.reads ? '' : 'disabled'} title="Read the text">Read</button>` : ''}</span>`;
      return `<li>${acts}<span class="t">${e.time} ${e.id}</span>${esc(say(e))}${e.flag ? ` <b style="color:${FLAG}">flag ${e.flag}</b>` : ''}${e.id in S.reads ? `<span class="text">${esc(S.reads[e.id])}</span>` : ''}</li>`;
    };
    const tail = p && S.tails[p.id];
    desk.innerHTML = `<h2><span>The desk</span><span>Reads ${S.budget.reads} · Tails ${S.budget.tails}</span></h2>
      ${p ? `<h3>${esc(p.name)}, ${esc(p.role)}</h3>
        ${p.knownHabit ? `<div class="habit">Known habit: ${esc(p.knownHabit)}.</div>` : ''}
        ${S.bans[p.id] ? `<div style="color:#ff8a6b">Banned, citing ${S.bans[p.id].join(', ')}.</div>` : ''}
        <ul>${recs.length ? recs.map(recLine).join('') : '<li>Nothing in the books about them tonight.</li>'}</ul>
        ${tail ? `<div><b>The doorman's report:</b> ${tail.length ? tail.map((t) => `${t.time}, ${esc(t.went)}`).join('; ') : 'they never left the room'}.</div>` : ''}
        ${lock ? '' : `<div style="margin-top:6px;display:flex;gap:6px">
          <button id="tail" ${S.budget.tails && !tail ? '' : 'disabled'}>Tail ${esc(p.name)}</button>
          ${S.bans[p.id] ? `<button id="clear">Take the ban back</button>` : `<button id="ban">Ban ${esc(p.name)}</button>`}</div>`}`
        : '<h3>No one picked</h3><div>Click a name in the room, or a record in the list, to open that regular\'s file.</div>'}
      <h3>Evidence</h3>
      <div>${S.pins.size ? [...S.pins].map((id) => `<button data-pin="${id}" class="on" ${lock ? 'disabled' : ''}>${id}</button>`).join(' ') : 'Nothing pinned. Pin records to cite them in a read or a ban.'}</div>
      ${S.msg ? `<div class="msg">${esc(S.msg)}</div>` : ''}
      <h3>Suspicion, 0 to 100</h3>
      <div class="sus">${night.regulars.map((r) => `<span class="who" data-who="${r.id}">${S.bans[r.id] ? '<span class="b">Banned</span> ' : ''}${esc(r.name)}</span>
        <input type="range" min="0" max="100" step="5" value="${S.scores[r.id]}" data-sus="${r.id}" ${lock ? 'disabled' : ''}><span>${S.scores[r.id]}</span>`).join('')}</div>
      <div style="margin-top:8px;display:flex;gap:6px;justify-content:space-between">
        ${lock ? '<button id="see">See the paper</button>' : `<button id="handin">${S.sure ? 'Sure? Bans are final' : 'Hand in'}</button>`}
        <button id="over" title="A fresh desk for this night">Start over</button></div>`;
  }

  desk.addEventListener('input', (ev) => {
    const r = ev.target.dataset.sus;
    if (!r) return;
    S.scores[r] = Number(ev.target.value);
    ev.target.nextElementSibling.textContent = ev.target.value;
  });
  desk.addEventListener('click', (ev) => {
    const t = ev.target.closest('button, .who');
    if (!t) return;
    const p = S.sel;
    if (t.dataset.who) return select(t.dataset.who);
    if (t.dataset.pin) { S.pins.has(t.dataset.pin) ? S.pins.delete(t.dataset.pin) : S.pins.add(t.dataset.pin); return draw(); }
    if (t.dataset.read) {
      const id = t.dataset.read, because = reasons(id);
      if (!because.length) { S.msg = 'Pin a record that gives you a reason to read this one first. A flagged record is its own reason.'; return draw(); }
      return act('read', { record: id, because }, (x) => { S.reads[id] = x.text; S.budget.reads = x.readsLeft ?? S.budget.reads; });
    }
    if (t.id === 'tail') return act('tail', { regular: p }, (x) => { S.tails[p] = x.trips; S.budget.tails = x.tailsLeft; });
    if (t.id === 'ban') {
      const mine = [...S.pins].filter((id) => about(night.records.find((e) => e.id === id), p));
      const because = mine.length ? mine : [...S.pins];
      if (!because.length) { S.msg = `Pin the records that show ${nameOf(p)} is in the ring first. A ban must cite them.`; return draw(); }
      return act('ban', { regular: p, because }, (x) => { S.bans[p] = x.because; if (!S.scores[p]) S.scores[p] = 100; });
    }
    if (t.id === 'clear') return act('clear', { regular: p }, () => { delete S.bans[p]; });
    if (t.id === 'handin') {
      if (!S.sure) { S.sure = true; setTimeout(() => { S.sure = false; draw(); }, 4000); return draw(); }
      return act('handin', { scores: S.scores }, () => { S.handedIn = true; reveal(); });
    }
    if (t.id === 'see') return reveal();
    if (t.id === 'over') return post('new').then(() => location.reload(), (err) => { S.msg = err.message; draw(); });
  });
  // A name in the room, or a record in the replay's list, opens that regular's file.
  for (const p of people) p.label.element.addEventListener('click', () => select(p.id));
  document.getElementById('events')?.addEventListener('click', (ev) => {
    const e = night.records.find((x) => x.id === ev.target.closest('li')?.dataset.id);
    if (e) select(e.who);
  });

  // The dawn paper: the truth, how the detective did, and what the other detectives would have done.
  async function reveal() {
    let x;
    try { x = S.truth ?? await post('reveal'); } catch (err) { S.msg = err.message; return draw(); }
    S.truth = x;
    draw();
    const sc = x.score, t = sc.boxes, ring = x.ringName.replace(/^the /, 'The ');
    let head, deck;
    if (!x.ring.length) {
      head = t.wrongMen.length ? 'Honest Patron Thrown Out' : 'Quiet Night at the Blue Lantern';
      deck = t.wrongMen.length ? `There was no ring tonight. ${list(t.wrongMen)} banned anyway.` : 'There was no ring tonight, and the house detective banned nobody.';
    } else if (!t.caught.length) {
      head = t.wrongMen.length ? `Wrong Patron Banned as ${ring} Slips Away` : `${ring} Slips Away`;
      deck = `${list(x.ring)} worked the night and walked out at dawn.`;
    } else if (!t.wrongMen.length) {
      head = t.gotAway.length ? `${ring} Broken, ${t.gotAway.length} Still at Large` : `${ring} Smashed`;
      deck = `${list(t.caught)} banned from the club.${t.gotAway.length ? ` ${list(t.gotAway)} slipped out the back.` : ''}`;
    } else {
      head = `${ring} Broken, Honest Patron Banned`;
      deck = `${list(t.caught)} banned. ${list(t.wrongMen)} banned by mistake.${t.gotAway.length ? ` ${list(t.gotAway)} got away.` : ''}`;
    }
    const method = { line: 'one shared telephone line', relay: 'messages passed through the machine', books: 'the machine\'s own notes' }[x.method];
    const other = (who, o) => `<li>${who} would ban ${o.bans.length ? list(o.bans) : 'nobody'}: ${o.caught} caught, ${o.wrongBans} wrong. Score ${o.points}.</li>`;
    const pinned = new Set(Object.values(S.bans).flat());
    const missed = x.ringRecords.filter((e) => !pinned.has(e.id)).slice(0, 8);
    paper.innerHTML = `<article role="dialog" aria-modal="true" aria-labelledby="hl">
      <div class="mast"><span>Dawn edition</span><b>The Harbor Evening Call</b><span>Night ${esc(seed)}</span></div>
      <h1 id="hl">${esc(head)}</h1>
      <p class="deck">${esc(deck)}${method ? ` They used ${method}.` : ''} The cargo: ${esc(x.cargo)}.</p>
      <div class="cols">
        <h4>Your night</h4>
        <p>Caught ${t.caught.length}, got away ${t.gotAway.length}, wrong bans ${t.wrongMen.length}, honest regulars cleared ${t.cleared.length}. <b>Score ${sc.points}</b> (one point a catch, two off for each wrong ban).</p>
        <h4>How you worked</h4>
        <ul><li>Evidence: ${t.caught.length ? `${sc.goodEvidence} of ${t.caught.length} right bans cite one of the ring's own records` : 'no right bans to judge'}.</li>
          <li>Privacy: ${sc.privacyReads} of ${sc.reads} reads were on honest regulars.</li>
          <li>Tail: ${sc.tails ? Object.keys(S.tails).map((id) => `${nameOf(id)}, ${x.ring.includes(id) ? 'in the ring' : 'honest'}`).join('') : 'not used'}.</li></ul>
        <h4>The other detectives, same night</h4>
        <ul>${other('The house alarm alone', x.others.houseAlarm)}${other('The scripted detective', x.others.detective)}${other('The informant, who knew the method,', x.others.informant)}</ul>
        ${missed.length ? `<h4>The ring's records you did not cite</h4>${missed.map((e) => `<p>${clockOf(e.half)}, ${e.id}. ${esc(e.name)}, ${e.kind}${e.text ? `: ${esc(e.text)}` : ''}${e.went ? `, to ${esc(e.went)}` : ''}</p>`).join('')}` : ''}
      </div>
      <div class="btns"><button id="back">Back to the club</button></div></article>`;
    paper.hidden = false;
    paper.querySelector('#back').onclick = () => { paper.hidden = true; };
  }

  // Pick up where this desk was, if the page was reloaded.
  try {
    const st = await post('state');
    Object.assign(S, { budget: st.budget, reads: st.reads, tails: st.tails, bans: st.bans, handedIn: st.handedIn });
    if (st.scores) S.scores = st.scores;
    for (const b of Object.values(st.bans)) for (const id of b) S.pins.add(id);
    draw();
    if (st.handedIn) reveal();
  } catch (err) {
    S.msg = err.message;
    draw();
  }
}
