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
