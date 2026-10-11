const test = require('node:test');
const assert = require('node:assert');
const k = require('../skin.js');

test('stav: neplatné uložené hodnoty → výchozí (Inkoust, systém, bez akcentu a vzoru)', () => {
  assert.deepStrictEqual(k.stav({ skin: null, rezim: null, akcent: null, pozadi: null }),
    { skin: 'inkoust', volba: 'system', akcent: '', pozadi: '' });
  // smazaný motiv nebo poškozené úložiště nesmí stránku nechat bez barev
  assert.deepStrictEqual(k.stav({ skin: 'zruseny', rezim: 'noc', akcent: 'cerna', pozadi: '"><b>' }),
    { skin: 'inkoust', volba: 'system', akcent: '', pozadi: '' });
  assert.deepStrictEqual(k.stav({ skin: 'kyberpunk', rezim: 'tmavy', akcent: 'zlata', pozadi: 'krajina' }),
    { skin: 'kyberpunk', volba: 'tmavy', akcent: 'zlata', pozadi: 'krajina' });
});

test('rezim: volba přebije systém, „system“ se řídí systémem', () => {
  assert.strictEqual(k.rezim('svetly', true), 'svetly');
  assert.strictEqual(k.rezim('tmavy', false), 'tmavy');
  assert.strictEqual(k.rezim('system', true), 'tmavy');
  assert.strictEqual(k.rezim('system', false), 'svetly');
});

test('panel: všechny volby, zaškrtnutý aktuální stav, náhledy v aktuálním režimu', () => {
  const s = k.stav({ skin: 'priroda', rezim: 'tmavy', akcent: 'azur', pozadi: '' });
  const h = k.panel(s, 'tmavy');
  const pocet = (re) => (h.match(re) || []).length;
  assert.strictEqual(pocet(/name="skin"/g), k.SKINY.length);
  assert.strictEqual(pocet(/name="akcent"/g), k.AKCENTY.length + 1);   // + „podle motivu“
  assert.strictEqual(pocet(/name="pozadi"/g), k.POZADI.length + 1);
  assert.strictEqual(pocet(/name="rezim"/g), 3);
  assert.strictEqual(pocet(/ checked/g), 4);   // jedna volba v každé skupině
  assert.match(h, /value="priroda" checked/);
  assert.match(h, /value="azur" checked/);
  assert.match(h, /name="pozadi" value="" checked/);
  assert.match(h, /value="tmavy" checked/);
  // dlaždice motivů nesou vlastní data-skin a ukazují motiv bez voleb návštěvníka
  k.SKINY.forEach((m) => assert.match(h, new RegExp('vzhled-motiv vzhled-cisty" data-skin="' + m.id + '" data-rezim="tmavy"')));
  assert.doesNotMatch(h, /data-rezim="svetly"/);
});

test('seznamy: id bez duplicit, jen malá písmena (použijí se v selektorech a atributech)', () => {
  [k.SKINY, k.AKCENTY, k.POZADI, k.REZIMY].forEach((seznam) => {
    const ids = seznam.map((x) => x.id);
    assert.strictEqual(new Set(ids).size, ids.length);
    ids.forEach((id) => assert.match(id, /^[a-z]+$/));
  });
});
