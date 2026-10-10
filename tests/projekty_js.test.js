const test = require('node:test');
const assert = require('node:assert');
const p = require('../projekty.js');
const DNES = new Date(2026, 9, 10);

test('pred: dny, týdny, měsíce, roky', () => {
  assert.strictEqual(p.pred('2026-10-10', DNES), 'dnes');
  assert.strictEqual(p.pred('2026-10-09', DNES), 'včera');
  assert.strictEqual(p.pred('2026-10-07', DNES), 'před 3 dny');
  assert.strictEqual(p.pred('2026-10-03', DNES), 'před týdnem');
  assert.strictEqual(p.pred('2026-09-19', DNES), 'před 3 týdny');
  assert.strictEqual(p.pred('2026-09-01', DNES), 'před měsícem');
  assert.strictEqual(p.pred('2026-05-01', DNES), 'před 5 měsíci');
  assert.strictEqual(p.pred('2023-06-01', DNES), 'před 3 lety');
});

test('dniPrace: skloňování', () => {
  assert.strictEqual(p.dniPrace(1), '1 den práce');
  assert.strictEqual(p.dniPrace(3), '3 dny práce');
  assert.strictEqual(p.dniPrace(5), '5 dní práce');
});

test('graf: 12 sloupků a popis pro čtečky', () => {
  const svg = p.graf([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 4]);
  assert.strictEqual((svg.match(/<rect/g) || []).length, 12);
  assert.match(svg, /aria-label="[^"]*0, 1, 0, 4"/);
});

test('esc: HTML znaky z popisů', () => {
  assert.strictEqual(p.esc('<a href="x">&'), '&lt;a href=&quot;x&quot;&gt;&amp;');
});

test('datumCesky', () => {
  assert.strictEqual(p.datumCesky('2026-10-09'), '9. 10. 2026');
});

test('boxSamostatny: aplikace, graf jen při aktivitě', () => {
  const b = { nazev: 'Domácí server', popis: 'služby', posledni: '2026-10-09', dni_prace: 3,
    tydny: [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 4],
    aplikace: [{ nazev: 'Knihy', popis: 'e-knihy' }, { nazev: 'A<b>', popis: 'x' }] };
  const html = p.boxSamostatny(b, DNES);
  assert.strictEqual((html.match(/<li/g) || []).length, 2);
  assert.match(html, /A&lt;b&gt;/);
  assert.match(html, /<svg/);
  assert.match(html, /naposledy včera/);
  const bezAktivity = p.boxSamostatny({ nazev: 'S', posledni: '2025-03-01', aplikace: [] }, DNES);
  assert.doesNotMatch(bezAktivity, /<svg|<ul/);
});
