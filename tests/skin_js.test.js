const test = require('node:test');
const assert = require('node:assert');
const k = require('../skin.js');

test('stav: neplatné uložené hodnoty → výchozí (Inkoust, systém, bez akcentu a vzoru)', () => {
  assert.deepStrictEqual(k.stav({ skin: null, rezim: null, akcent: null, pozadi: null }),
    { skin: 'inkoust', volba: 'system', akcent: '', pozadi: '' });
  // smazaný motiv nebo poškozené úložiště nesmí stránku nechat bez barev
  assert.deepStrictEqual(k.stav({ skin: 'zruseny', rezim: 'noc', akcent: 'cerna', pozadi: '"><b>' }),
    { skin: 'inkoust', volba: 'system', akcent: '', pozadi: '' });
  assert.deepStrictEqual(k.stav({ skin: 'priroda', rezim: 'tmavy', akcent: 'tyrkys', pozadi: 'mrizka' }),
    { skin: 'priroda', volba: 'tmavy', akcent: 'tyrkys', pozadi: 'mrizka' });
});

test('stav: hodnoty vyřazené zúžením (2026-10-11) uložené u návštěvníků → výchozí', () => {
  assert.deepStrictEqual(k.stav({ skin: 'kyberpunk', rezim: 'tmavy', akcent: 'zlata', pozadi: 'krajina' }),
    { skin: 'inkoust', volba: 'tmavy', akcent: '', pozadi: '' });
  ['indigo', 'minimal'].forEach((s) => assert.strictEqual(k.stav({ skin: s }).skin, 'inkoust'));
  assert.strictEqual(k.stav({ akcent: 'azur' }).akcent, '');
  ['mech', 'soumrak', 'aurora'].forEach((p) => assert.strictEqual(k.stav({ pozadi: p }).pozadi, ''));
});

test('seznamy: zúžená nabídka (docs/plans/2026-10-11-skiny-zuzeni.md)', () => {
  assert.deepStrictEqual(k.SKINY.map((x) => x.id), ['inkoust', 'teple', 'hluboka', 'priroda']);
  // názvy přejmenoval uživatel 2026-10-11; id zůstala, aby uložená volba návštěvníků platila dál
  assert.deepStrictEqual(k.SKINY.map((x) => x.nazev), ['Inkoust', 'Veselé', 'Voda', 'Příroda']);
  assert.deepStrictEqual(k.POZADI.map((x) => x.id), ['papir', 'mrizka', 'tecky']);
  assert.deepStrictEqual(k.AKCENTY.map((x) => x.id), ['fialova', 'purpur', 'malina', 'oranzova', 'zelena', 'tyrkys', 'modra']);
});

test('rezim: volba přebije systém, „system“ se řídí systémem', () => {
  assert.strictEqual(k.rezim('svetly', true), 'svetly');
  assert.strictEqual(k.rezim('tmavy', false), 'tmavy');
  assert.strictEqual(k.rezim('system', true), 'tmavy');
  assert.strictEqual(k.rezim('system', false), 'svetly');
});

test('panel: všechny volby, zaškrtnutý aktuální stav, náhledy v aktuálním režimu', () => {
  const s = k.stav({ skin: 'priroda', rezim: 'tmavy', akcent: 'tyrkys', pozadi: '' });
  const h = k.panel(s, 'tmavy');
  const pocet = (re) => (h.match(re) || []).length;
  assert.strictEqual(pocet(/name="skin"/g), k.SKINY.length);
  assert.strictEqual(pocet(/name="akcent"/g), k.AKCENTY.length + 1);   // + „podle motivu“
  assert.strictEqual(pocet(/name="pozadi"/g), k.POZADI.length + 1);
  assert.strictEqual(pocet(/name="rezim"/g), 3);
  assert.strictEqual(pocet(/ checked/g), 4);   // jedna volba v každé skupině
  assert.match(h, /value="priroda" checked/);
  assert.match(h, /value="tyrkys" checked/);
  assert.match(h, /name="pozadi" value="" checked/);
  assert.match(h, /value="tmavy" checked/);
  // dlaždice motivů nesou vlastní data-skin a ukazují motiv bez voleb návštěvníka
  k.SKINY.forEach((m) => assert.match(h, new RegExp('vzhled-motiv vzhled-cisty" data-skin="' + m.id + '" data-rezim="tmavy"')));
  assert.doesNotMatch(h, /data-rezim="svetly"/);
  // pořadí sekcí: režim první (pokyn uživatele 2026-10-11), pak Pozadí, Základní barvy, Motivy
  const poradi = ['vzhled-rezim', 'vzhled-pozadi', 'vzhled-barvy', 'vzhled-motivy']
    .map((c) => h.indexOf('<fieldset class="' + c + '"'));
  assert.ok(poradi.every((i, j) => i >= 0 && (j === 0 || i > poradi[j - 1])), String(poradi));
});

test('seznamy: id bez duplicit, jen malá písmena (použijí se v selektorech a atributech)', () => {
  [k.SKINY, k.AKCENTY, k.POZADI, k.REZIMY].forEach((seznam) => {
    const ids = seznam.map((x) => x.id);
    assert.strictEqual(new Set(ids).size, ids.length);
    ids.forEach((id) => assert.match(id, /^[a-z]+$/));
  });
});
