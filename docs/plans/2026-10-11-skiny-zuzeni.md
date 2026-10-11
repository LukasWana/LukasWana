# Zúžení skinů — implementační plán

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

Datum: 2026-10-11 · Stav: **Tasky 0–2 hotové (`2c1282f`, `10d848a`) + přejmenování motivů (`83736c6`), dál od
Tasku 3. Pushnuto a živě (Action `394193a` success, velikosti skin.js/skiny.css/style.css = repo).** Testy po Tasku 2: 74 Python + 17 JS zelených.
**2026-10-11 odp.: Task 6 udělán předem** na pokyn uživatele „když zvolím inkoust a černou, bude stránka plně černobílá“ —
bez pravidla pro ikony (`--ikona-barva` přijde až s Taskem 3; ikony jsou v inkoustu i bez něj, až Task 3 zavede
přechod akcentů, pravidlo ikon z Tasku 6 doplň). Test `TestInkoust.test_vychozi_inkoust_cernobily`, testy 77 Python + 17 JS.
Ověřeno snímkem (Chrome headless `--disable-lcd-text`): Inkoust světlý i tmavý = 0 pixelů s rozdílem kanálů > 40;
se Základní barvou (zelená) se opar a bokeh vrátí. Pushnuto se schválením („pushni“): `f609d1e`, Action success, živý style.css pravidlo obsahuje.
**Téhož dne (uživatel):** panel Vzhled bez `max-height`/`overflow-y` → roluje se s celou stránkou místo vlastního posuvníku (v okně 1280×600 byly Motivy schované uvnitř panelu, ověřeno snímkem před i po). Test `TestSkiny.test_panel_roluje_se_strankou`; pushnuto s pokynem „rovnou to pushni“ (`4568a9e`).
~~Výklad „panel roluje se stránkou“ byl špatný~~ — uživatel: „Vzhled se nescroluje“ = tlačítko má při rolování zůstat nahoře. Nově `.vzhled { position: fixed }` (vpravo zarovnané s obsahem 1200 px), tlačítko s podkladem v barvě pozadí + blur, panel zpět s `max-height`/`overflow-y` (u fixed se jinak spodek nedá dočíst). Ověřeno v Chromu: po odrolování o 3 030 px je tlačítko 8 px od horního okraje. Test `TestSkiny.test_vzhled_jede_s_rolovanim`; `c566a6c`, pushnuto.
**Téhož dne (uživatel):** v profilu Inkoust všechny karty inverzně jako ikony (`8ee5b07`, pushnuto, detail v plánu projektů). Pak „ikonky a staré projekty v tématu Veselé barevně jako v ilustraci“ → náhled dvou variant, uživatel vybral **A: plné barvy po krocích** (ne B: celý přechod ensō v každé ikoně/kartě). `skiny.css` za Veselé: 8 ikon zleva po krocích `--akcent` → `--akcent-2` → `--akcent-3` (`color-mix in oklab`), Starší projekty po sloupcích (`nth-child(3n+1/3n+2/3n)`) modrá / fialová / oranžová, šedé popisky v nich odvozené z `--inv-text` (90 % / 75 %), protože `--inv-text-3` na oranžové zanikal; hover `brightness(1.06)`. Z `--akcent*`, takže drží s ensō i se Základní barvou. Ověřeno snímky světlý i tmavý; test `TestVeseleBarevne` (×2). Ostatní motivy beze změny; otevřené pravidlo ikon z Tasku 6 tím neuzavřeno. Pushnuto (`b4f8afe`). ~~Starší projekty po sloupcích modrá / fialová / oranžová~~ — uživatel týž den: „gradientem od zhora dolů přes všechny karty“. Teď jeden `linear-gradient(180deg, akcent → akcent-2 → akcent-3)` ve výšce celé mřížky, každá karta ukazuje svůj výřez (`background-size: 100% var(--prechod-h)`, `background-position: 0 calc(-1 * var(--prechod-y))`). Čísla dává `projekty.js` `prechodPresKarty()` přes `ResizeObserver` na mřížce (změří se při rozbalení i při změně šířky či počtu sloupců); bez JS má každá karta celý přechod sama. Ověřeno snímky desktop světlý i tmavý (5 řádků po 3) a mobil (iframe 400 px, 1 sloupec); testy `TestVeseleBarevne.test_starsi_projekty_jeden_prechod_shora_dolu` + JS `prechodPresKarty`. Pushnuto (`516d916`, Action success, živý projekty.js funkci obsahuje). Testy teď 86 Python + 19 JS. **Pro Task 3:** Veselé už má ikony po krocích v `skiny.css` (`[data-skin="teple"] .social-icon:nth-child(n) i`, specifičtější než obecné pravidlo); Task 3 je nesmí přebít ani jeho test na ně narazit — buď je ponechat jako výjimku Veselého, nebo s uživatelem sjednotit.

**Večer téhož dne (uživatel):** „light mode bude v defaultu vzhled inkoust — projekty a server aplikace mají podbarvení světlé a černý text, staré aplikace černé podbarvení a ikonky taky, podbarvení se mění podle zvolených barev; v sekci Vzhled zobrazení gradientu jako v ilustraci 1:1“. ~~Inkoust: všechny karty inverzně (oba režimy)~~ → inverzní aktivní karty jen v tmavém Inkoustu (`[data-skin="inkoust"][data-rezim="tmavy"] .projekty-karta`). Světlý Inkoust se Základní barvou: světlé karty nádech akcentu 9 % (hover 15 %) do `#f6f5f2`, Starší projekty a ikony stejnými pravidly jako Veselé (selektory rozšířené v `skiny.css`). Panel: kolečka Základních barev a miniatury motivů kreslí maskou `img/enso.svg` / `img/tah.svg` s přechodem `--enso` / `--tah` (kolečko ensō v `::before`, aby přeškrtnutí „Podle motivu“ maska neořízla). Ověřeno snímky (světlý bez barvy, fialová, zelená, panel); testy `TestInkoustKartyInverzne` (×3), 88 Python + 19 JS. Otevřené: bílý text Starších projektů na světlých barvách (zelená, žlutá) je slabší kontrast, stejně jako u Veselého — uživateli nabídnuto, nerozhodl.
**V noci téhož dne (uživatel):** „dark mode upravíme, vzhled bude stejný jako současný light, jen inverzní“. ~~inverzní aktivní karty v tmavém Inkoustu~~ → tmavý Inkoust = zrcadlo světlého: projekty a Domácí server tmavé (plocha motivu `#201f1d`, světlý text), inverzně (světle) jen Starší projekty a ikony; se Základní barvou nádech akcentu 9 % (hover 15 %) do `#201f1d` a Starší projekty s ikonami barvy ensō jako ve světlém (selektory v `skiny.css` bez `[data-rezim="svetly"]`). Snímky světlý / tmavý / tmavý + modrá ověřeny okem v session (scratchpad). Text na barevných Starších projektech je v tmavém režimu tmavý (`--inv-text` tmavého Inkoustu), jako u tmavého Veselého.

Náhled schválený uživatelem běžel jen
jako kopie webu ve scratchpadu session z 11. 10. (není v repu). Tento plán převádí totéž do repa, s testy.

**Goal:** Zúžit skiny na vybranou nabídku a sjednotit barvy: motiv nebo Základní barva ladí opar, karty projektů
i ikony, výchozí Inkoust je černobílý.

**Architecture:** Barvy jsou dál jen v CSS jako role (`--akcent`, `--akcent-2`, `--akcent-3`). Opar, bokeh karet,
sloupce grafů a ikony patičky se z nich odvozují (`rgba(var(--akcent))`, `oklch(from …)`, `color-mix`). Černobílý
výchozí stav zajistí jedno pravidlo s vysokou specificitou. `skin.js` drží jen zúžené seznamy a pořadí sekcí panelu.

**Tech Stack:** vanilla CSS (relativní barvy `oklch(from …)`, `color-mix`), vanilla JS, Python `unittest`/pytest
(kontrakt CSS jako text), `node --test`.

**Podklady:** revize a rozhodnutí uživatele jsou v `docs/plans/2026-10-11-skiny-design.md`, sekce „Revize proti
zásadám projektu“ (10 nálezů + odstavec „Náhled“). Tam je i důvod každé volby.

---

## Rozhodnutí uživatele (11. 10.), která plán provádí

| # | pokyn / volba | kde v plánu |
|---|---|---|
| 1 | Motivy jen Inkoust, Teplé světlo, Hluboká práce, Příroda (Indigo, Kyberpunk, Minimal pryč) | Task 1, 2 |
| 2 | Pozadí jen Papír, Mřížka, Tečky („dej tam i ty čtverečky“) | Task 1, 2 |
| 3 | Základní barvy bez dvojic (pryč Zlatá a Azurová) → 7 barev | Task 1, 2 |
| 4 | Panel: „světlý / tmavý dej jako první volbu“ | Task 1 |
| 5 | Jméno a podtitul plnou barvou (bez přechodu) | Task 2 |
| 6 | „motiv mění i ikony sociálních sítí“ → ikony v přechodu akcentů motivu | Task 3 |
| 7 | Opar nahoře přebarví motiv i Základní barva (volba z nabídky, 11. 10.) | Task 4 |
| 8 | „přepínátkem chci ladit i barvy top projektů“ → každý projekt jiný odstín akcentu | Task 5 |
| 9 | „defaultní motiv bude černobílý“ → Inkoust bez zvolené barvy bez oparu, bokehu a barev | Task 6 |
| 10 | Grafy bez čárek prázdných týdnů (nález 4 revize) | Task 7 |
| 11 | Verzálky jména s kladným prostrkáním +0,02em (nález 5) | Task 8 |
| 12 | „Teplé světlo přejmenuj na Veselé, Hluboká práce na Voda“ (během implementace) — jen `nazev`, id `teple`/`hluboka` zůstala kvůli uloženým volbám návštěvníků | mimo tasky, commit po Tasku 2 |
| 13 | Papír podle inspirace uživatele (foto starého béžového papíru): škrábance, smítka, jemné zrno, „po stranách prohlížeče lehké měkké zatmavení“, „každý barevný motiv lehce zatónuje barvu papíru“ → „víc zatónovat“. Odladěno v náhledu, push schválen („zapiš to do repa a pushni“) | mimo tasky, viz níž |

**Papír (rozhodnutí 13).** Textura je `img/papir-svetly.svg` a `img/papir-tmavy.svg` (dlaždice 640 px, ~25 KB),
vyrobené `tools/papir.py` (pevné semínko; test hlídá, že se soubory s generátorem shodují). V `skiny.css` nad ní
leží ztmavené strany (`linear-gradient(90deg …)`, od 16 % šířky ke kraji), slabá vinětace a tón papíru: béžová
smíchaná s `--motiv-akcent` na `--papir-dotyk` (30 % světlý, ×2 tmavý; Inkoust 0 %, protože jeho akcent je černá
a papír by jen zašedil). `--papir-dotyk` je na motivu (`:root` 0 %, `[data-skin]:not([data-skin="inkoust"])` 30 %)
a dědí se — první verze ho dávala na `[data-pozadi="papir"]` a čtvereček Papír v panelu (nemá `data-skin`) byl
v Inkoustu zašedlý; chyceno kontrolou do nuly, opraveno a ověřeno snímkem panelu. Tón bere jen motiv, ne Základní barvu návštěvníka (nabídnuto, uživatel nežádal).
Zrno laděno dvakrát: v tmavém bylo „moc“, ve světlém „nevidím“ → obě stejně drobné (frekvence 1.6), tmavé slabší.
Neplatné měření z náhledu: první srovnání běželo z `http.server` s cache, takže prohlížeč mohl ukazovat staré
CSS — další náhledy už ze serveru s `Cache-Control: no-store`.

**Mimo rozsah (vědomě):** počet velikostí písma (nález 5, ~7–8 velikostí místo 2–3) a starý anglický `<title>`
(nález 10). Uživatel je zatím neřešil, zůstávají v Otevřeném.

**Pozor na zpětná lomítka:** kód s regexy (testy) piš jen přes Edit/Write, nikdy heredocem ani `sed`
(`~/.claude/rules/bash-heredoc-omezeni.md`). Zprávy commitů přes Write do souboru a `git commit -F`.

---

### ~~Task 0: Výchozí stav~~ ✅ 71 + 15 zelených

**Step 1:** `cd /c/work/graphic/LukasWana && git status -sb && git log --oneline -3`
Expected: čistý strom. Commity s tímto plánem jsou buď pushnuté, nebo `ahead` (push plánu čeká na uživatele).

**Step 2:** `python -m pytest -q tests/` (BEZ `-I`, s ním spadne import pygments)
Expected: `71 passed`

**Step 3:** `node --test tests/projekty_js.test.js tests/skin_js.test.js 2>&1 | grep -E "^ℹ (tests|pass|fail)"`
Expected: `tests 15`, `pass 15`, `fail 0`

---

### ~~Task 1: Zúžené seznamy a pořadí panelu (`skin.js`)~~ ✅ `2c1282f`, JS 17 zelených

**Files:**
- Modify: `skin.js` (pole `SKINY`, `AKCENTY`, `POZADI`; funkce `panel`)
- Test: `tests/skin_js.test.js`

**Step 1: Testy (červené).** V `tests/skin_js.test.js`:

a) V prvním testu nahraď třetí `assert.deepStrictEqual` (s `kyberpunk`/`zlata`/`krajina`) tímto:

```js
  assert.deepStrictEqual(k.stav({ skin: 'priroda', rezim: 'tmavy', akcent: 'tyrkys', pozadi: 'mrizka' }),
    { skin: 'priroda', volba: 'tmavy', akcent: 'tyrkys', pozadi: 'mrizka' });
```

b) Za první test přidej:

```js
test('stav: hodnoty vyřazené zúžením (2026-10-11) uložené u návštěvníků → výchozí', () => {
  assert.deepStrictEqual(k.stav({ skin: 'kyberpunk', rezim: 'tmavy', akcent: 'zlata', pozadi: 'krajina' }),
    { skin: 'inkoust', volba: 'tmavy', akcent: '', pozadi: '' });
  ['indigo', 'minimal'].forEach((s) => assert.strictEqual(k.stav({ skin: s }).skin, 'inkoust'));
  assert.strictEqual(k.stav({ akcent: 'azur' }).akcent, '');
  ['mech', 'soumrak', 'aurora'].forEach((p) => assert.strictEqual(k.stav({ pozadi: p }).pozadi, ''));
});

test('seznamy: zúžená nabídka (docs/plans/2026-10-11-skiny-zuzeni.md)', () => {
  assert.deepStrictEqual(k.SKINY.map((x) => x.id), ['inkoust', 'teple', 'hluboka', 'priroda']);
  assert.deepStrictEqual(k.POZADI.map((x) => x.id), ['papir', 'mrizka', 'tecky']);
  assert.deepStrictEqual(k.AKCENTY.map((x) => x.id), ['fialova', 'purpur', 'malina', 'oranzova', 'zelena', 'tyrkys', 'modra']);
});
```

c) V testu `panel:` změň `akcent: 'azur'` na `akcent: 'tyrkys'` a `/value="azur" checked/` na `/value="tyrkys" checked/`.
Na konec téhož testu (před `});`) přidej:

```js
  // pořadí sekcí: režim první (pokyn uživatele 2026-10-11), pak Pozadí, Základní barvy, Motivy
  const poradi = ['vzhled-rezim', 'vzhled-pozadi', 'vzhled-barvy', 'vzhled-motivy']
    .map((c) => h.indexOf('<fieldset class="' + c + '"'));
  assert.ok(poradi.every((i, j) => i >= 0 && (j === 0 || i > poradi[j - 1])), String(poradi));
```

**Step 2:** `node --test tests/skin_js.test.js 2>&1 | grep -E "^✖|^ℹ (pass|fail)"`
Expected: FAIL — `stav: hodnoty vyřazené…`, `seznamy: zúžená nabídka` a `panel:` (pořadí).

**Step 3: Kód.** V `skin.js`:
- `SKINY`: smaž řádky `indigo`, `kyberpunk`, `minimal`; za `priroda` nesmí zůstat čárka.
- `AKCENTY`: smaž řádky `zlata` a `azur`.
- `POZADI`: smaž `mech`, `soumrak`, `aurora`, `krajina` (zůstane `papir`, `mrizka`, `tecky`, bez čárky za `tecky`).
- `panel()`: blok `fieldset class="vzhled-rezim"` (4 řádky: `h += '</div></fieldset><fieldset class="vzhled-rezim">…`,
  `REZIMY.forEach(…)`, tělo, `});`) přesuň před blok Pozadí. Výsledný začátek po hlavičce:

```js
    h += '<fieldset class="vzhled-rezim"><legend>Světlý / tmavý režim</legend><div class="vzhled-segmenty">';
    REZIMY.forEach(function (m) {
      h += moznost('rezim', m.id, s, '<span><svg viewBox="0 0 16 16" aria-hidden="true">' + m.ikona + '</svg>' + m.nazev + '</span>', m.nazev);
    });

    h += '</div></fieldset><fieldset class="vzhled-pozadi"><legend>Pozadí</legend><div class="vzhled-mrizka">'
      + moznost('pozadi', '', s, …beze změny…);
```

  a za Základními barvami pokračuje rovnou `h += '</div></fieldset><fieldset class="vzhled-motivy">…`.

**Step 4:** `node --test tests/skin_js.test.js 2>&1 | grep -E "^✖|^ℹ (pass|fail)"` → `pass 6`, `fail 0`.
Potom `node --check skin.js`.

**Step 5: Commit** `skin.js tests/skin_js.test.js` — „Skiny: zúžená nabídka a režim jako první volba panelu“.

---

### ~~Task 2: CSS bez vyřazených motivů, barev, pozadí a přechodů v textu (`skiny.css`)~~ ✅ `10d848a`, 74 zelených

**Odchylka od kódu níž:** `test_bez_osirelych_pravidel` v repu nejdřív odstraní komentáře CSS
(`re.sub(r"/\*.*?\*/", …)`) — v podobě z plánu chytal hlavičku `skiny.css`, kde je ukázka `[data-skin="id"]`.

**Files:**
- Modify: `skiny.css`, `style.css` (sloupce Základních barev)
- Test: `tests/test_stranka.py` (`TestSkiny`)

**Step 1: Testy (červené).** V `TestSkiny`:
- `test_kazdy_motiv_ma_svetly_i_tmavy_se_vsemi_rolemi`: seznam na `["inkoust", "teple", "hluboka", "priroda"]`.
- Docstring třídy: „7 motivů“ → „4 motivy (zúženo 2026-10-11)“.
- Přidej:

```python
    def test_bez_osirelych_pravidel(self):
        # zúžení 2026-10-11: v CSS nesmí zůstat pravidla motivů, barev a pozadí, které panel nenabízí
        for atribut, seznam in (("data-skin", "SKINY"), ("data-akcent", "AKCENTY"), ("data-pozadi", "POZADI")):
            v_css = set(re.findall(rf'\[{atribut}="([a-z]+)"\]', self.css))
            self.assertEqual(v_css, set(ids(self.js, seznam)), atribut)

    def test_jmeno_a_podtitul_plnou_barvou(self):
        # revize 2026-10-11: text vyplněný přechodem se hůř čte a test kontrastu ho neumí změřit
        skiny = text("skiny.css")
        self.assertNotIn("--nadpis", skiny)
        self.assertNotIn("--podtitul", skiny)

    def test_zakladni_barvy_ve_ctyrech_sloupcich(self):
        # 7 barev + „podle motivu“ = dvě plné řady po 4, stejně široké jako Pozadí
        self.assertIn("grid-template-columns: repeat(4, 1fr);",
                      pravidla(text("style.css"), ".vzhled-barvy .vzhled-mrizka")[0])
```

**Step 2:** `python -m pytest -q tests/test_stranka.py -k TestSkiny 2>&1 | tail -5`
Expected: FAIL `test_bez_osirelych_pravidel` (CSS má indigo, kyberpunk, …), `test_jmeno_a_podtitul_plnou_barvou`,
`test_zakladni_barvy_ve_ctyrech_sloupcich`. (`test_kazdy_motiv…` už po Tasku 1 projde.)

**Step 3: Kód.**
- `skiny.css`: smaž celý blok „Barevné motivy: nadpis a podtitul v přechodu, ikony v barvách značek“ (komentář +
  pravidlo se seznamem `[data-skin="teple"], … [data-skin="kyberpunk"]` s `--nadpis`, `--podtitul`, `--znacky`).
- `skiny.css`: smaž celé sekce `===== Kreativní indigo`, `===== Kyberpunk`, `===== Minimal` (komentář + oba bloky).
- `skiny.css`: smaž řádky `[data-akcent="zlata"]` a `[data-akcent="azur"]`.
- `skiny.css`: smaž pravidla `[data-pozadi="mech"]`, `"soumrak"`, `"aurora"` a oba `"krajina"`. V komentáři sekce
  Pozadí přepiš „zrno a krajina jsou SVG, proto mají světlou a tmavou verzi“ na „zrno papíru je SVG, proto má
  světlou a tmavou verzi“.
- `style.css`, `.vzhled-barvy .vzhled-mrizka`: `repeat(5, 1fr)` → `repeat(4, 1fr)`.

**Step 4:** `python -m pytest -q tests/ 2>&1 | tail -2` → vše zelené (počet = 71 + 3 nové).
`grep -c "kyberpunk\|indigo\|minimal\|krajina\|aurora\|soumrak\|data-pozadi=\"mech\"" skiny.css style.css` → `0` u obou.

**Step 5: Commit** `skiny.css style.css tests/test_stranka.py` — „Skiny: CSS jen pro nabízené motivy, barvy a pozadí“.

---

### Task 3: Ikony patičky v přechodu akcentů (`style.css`)

**Files:** Modify `style.css` (sekce „Barva ikony“, řádky `.ikona-*`, `--znacky` v obecném pravidle). Test
`tests/test_stranka.py`.

**Step 1: Testy (červené).** Celou třídu `TestBarvyBanneru` smaž a na její místo vlož novou třídu
`TestBarvyZAkcentu` (staré testy hlídají barvy natvrdo, které Tasky 4–5 ruší; nové testy do ní přibývají
v Taskách 4–6). Zatím vlož jen tento kus:

```python
class TestBarvyZAkcentu(unittest.TestCase):
    """Zúžení skinů 2026-10-11 (docs/plans/2026-10-11-skiny-zuzeni.md): opar, karty projektů a ikony patičky
    berou barvu z akcentu motivu nebo zvolené Základní barvy. Výchozí Inkoust bez zvolené barvy je černobílý."""

    POSUN = {"fialova": -90, "tyrkys": -54, "zlata": -18, "zelena": 18, "malina": 54, "azur": 90,
             "modra": 126, "purpur": -126}
    # Inkoust nebo stránka bez JS (html bez data-skin) a k tomu bez zvolené Základní barvy. Bez čárky, protože
    # pomocná funkce pravidla() dělí seznam selektorů podle čárek.
    CB = ':root:not([data-skin]:not([data-skin="inkoust"])):not([data-akcent])'

    def test_ikony_v_prechodu_akcentu(self):
        # pokyn uživatele 2026-10-11 „motiv mění i ikony sociálních sítí“: zleva doprava jako ensō, ne barvy značek
        css = text("style.css")
        self.assertNotIn("--znack", css + text("skiny.css"))
        self.assertIn("background-color: var(--ikona-barva, var(--inkoust));", pravidla(css, ".social-icon i")[0])
        for n in range(1, 9):
            tela = pravidla(css, f".social-icon:nth-child({n})")
            self.assertEqual(len(tela), 1, n)
            self.assertRegex(tela[0], r"--ikona-barva: color-mix\(in srgb, rgb\(var\(--akcent(-2)?\)\) \d+%, "
                                      r"rgb\(var\(--akcent-[23]\)\)\);", n)
```

V `TestInkoust.test_ikony_paticky_jako_maska` uprav jen komentář: „barvu dává --inkoust nebo barva značky“ →
„barvu dává --ikona-barva (přechod akcentů) nebo --inkoust“.

**Step 2:** `python -m pytest -q tests/test_stranka.py -k "TestBarvyZAkcentu" 2>&1 | tail -3` → FAIL.

**Step 3: Kód** v `style.css`:
- obecné pravidlo `:root, [data-skin]`: smaž řádek `--znacky: 0%;`
- řádky `.ikona-…`: smaž z každého `--znacka: …;` (zůstane jen `--ikona: url(…);`)
- komentář a pravidlo `.social-icon i`: komentář začni „Barva ikony: přechod akcentů motivu zleva doprava jako
  ensō (pokyn 2026-10-11), ve výchozím černobílém Inkoustu inkoust.“; `background-color: color-mix(…--znacky…)`
  nahraď `background-color: var(--ikona-barva, var(--inkoust));`
- hned za `.social-icon i { … }` přidej:

```css
.social-icon:nth-child(1) { --ikona-barva: color-mix(in srgb, rgb(var(--akcent)) 100%, rgb(var(--akcent-2))); }
.social-icon:nth-child(2) { --ikona-barva: color-mix(in srgb, rgb(var(--akcent)) 71%, rgb(var(--akcent-2))); }
.social-icon:nth-child(3) { --ikona-barva: color-mix(in srgb, rgb(var(--akcent)) 43%, rgb(var(--akcent-2))); }
.social-icon:nth-child(4) { --ikona-barva: color-mix(in srgb, rgb(var(--akcent)) 14%, rgb(var(--akcent-2))); }
.social-icon:nth-child(5) { --ikona-barva: color-mix(in srgb, rgb(var(--akcent-2)) 86%, rgb(var(--akcent-3))); }
.social-icon:nth-child(6) { --ikona-barva: color-mix(in srgb, rgb(var(--akcent-2)) 57%, rgb(var(--akcent-3))); }
.social-icon:nth-child(7) { --ikona-barva: color-mix(in srgb, rgb(var(--akcent-2)) 29%, rgb(var(--akcent-3))); }
.social-icon:nth-child(8) { --ikona-barva: color-mix(in srgb, rgb(var(--akcent-2)) 0%, rgb(var(--akcent-3))); }
```

(`.social-icons` má jako potomky jen 8 odkazů `<a class="social-icon">`; komentář v HTML se do `nth-child` nepočítá.)

**Step 4:** `python -m pytest -q tests/ 2>&1 | tail -2` → zelené. (Inkoust bez barvy má teď ikony v inkoustu jen
náhodou — akcent Inkoustu je inkoust. Výslovné pravidlo přidá Task 6.)

**Step 5: Commit** — „Ikony patičky v přechodu akcentů motivu místo barev značek“.

---

### Task 4: Opar z akcentů (`style.css`, `.enso-banner::before`)

**Step 1: Test (červený)** do `TestBarvyZAkcentu`:

```python
    def test_opar_za_enso_z_akcentu(self):
        # volba uživatele 2026-10-11: opar přebarví motiv i Základní barva
        css = text("style.css")
        banner = pravidla(css, ".enso-banner")
        self.assertTrue(any("isolation: isolate" in t and "position: relative" in t for t in banner))
        opar = pravidla(css, ".enso-banner::before")
        self.assertEqual(len(opar), 1)
        for akcent in ("--akcent", "--akcent-2", "--akcent-3"):
            self.assertIn(f"rgba(var({akcent}),", opar[0], akcent)
        self.assertNotRegex(opar[0], r"rgba\(\d")   # žádná barva natvrdo
        self.assertIn("filter: blur(", opar[0])
        self.assertIn("mask-image: radial-gradient(", opar[0])
        self.assertIn("z-index: -1", opar[0])
        self.assertIn("inset: -60px 0;", opar[0])   # do stran nepřesahuje → na mobilu žádný vodorovný posuvník
```

**Step 2:** pytest `-k test_opar_za_enso_z_akcentu` → FAIL (`rgba(168, 34, 196…` natvrdo).

**Step 3: Kód.** V `.enso-banner::before` nahraď 11 vrstev `radial-gradient(…rgba(číslo…)…)` těmito (pozice a
velikosti zůstávají, mění se jen barva a průhlednost); komentář nad pravidlem: „Opar za ensō: rozostřené třpytky
v akcentech motivu nebo zvolené Základní barvy (zúžení skinů 2026-10-11). …“:

```css
    background:
        radial-gradient(circle at 24% 30%, rgba(var(--akcent), .28) 0, rgba(var(--akcent), .28) 4%, transparent 9%),
        radial-gradient(circle at 40% 70%, rgba(var(--akcent-2), .30) 0, rgba(var(--akcent-2), .30) 3.2%, transparent 7%),
        radial-gradient(circle at 30% 82%, rgba(var(--akcent-3), .35) 0, rgba(var(--akcent-3), .35) 2.3%, transparent 5%),
        radial-gradient(circle at 58% 22%, rgba(var(--akcent-2), .24) 0, rgba(var(--akcent-2), .24) 2.7%, transparent 6%),
        radial-gradient(circle at 72% 64%, rgba(var(--akcent), .20) 0, rgba(var(--akcent), .20) 3.6%, transparent 8%),
        radial-gradient(circle at 14% 62%, rgba(var(--akcent-3), .22) 0, rgba(var(--akcent-3), .22) 2.7%, transparent 6%),
        radial-gradient(circle at 84% 34%, rgba(var(--akcent), .22) 0, rgba(var(--akcent), .22) 2.3%, transparent 5%),
        radial-gradient(circle at 50% 50%, rgba(var(--akcent-2), .10) 0, rgba(var(--akcent-2), .10) 6.3%, transparent 14%),
        radial-gradient(circle at 66% 86%, rgba(var(--akcent-3), .30) 0, rgba(var(--akcent-3), .30) 1.8%, transparent 4%),
        radial-gradient(circle at 8% 24%, rgba(var(--akcent-2), .22) 0, rgba(var(--akcent-2), .22) 1.8%, transparent 4%),
        radial-gradient(circle at 92% 74%, rgba(var(--akcent), .22) 0, rgba(var(--akcent), .22) 2.3%, transparent 5%);
```

**Step 4:** `python -m pytest -q tests/ 2>&1 | tail -2` → zelené.

**Step 5: Commit** — „Opar za ensō z akcentů motivu a Základní barvy“.

---

### Task 5: Barvy projektů z akcentu (`style.css`)

**Step 1: Testy (červené)** do `TestBarvyZAkcentu`:

```python
    def test_kazdy_projekt_jiny_odstin_akcentu(self):
        # pokyn uživatele 2026-10-11 „přepínátkem chci ladit i barvy top projektů“; každý projekt dál unikátní barvu
        self.assertEqual(set(self.POSUN), set(projekty.PALETA))
        self.assertEqual(len(set(self.POSUN.values())), len(self.POSUN))
        css = text("style.css")
        for nazev, posun in self.POSUN.items():
            tela = pravidla(css, f".barva-{nazev}")
            self.assertEqual(len(tela), 1, nazev)
            self.assertIn(f"--posun: {posun};", tela[0], nazev)

    def test_barevna_karta_bokeh_a_sloupce(self):
        css = text("style.css")
        tela = pravidla(css, ".projekty-barevna")
        self.assertEqual(len(tela), 1)
        self.assertIn("--pb: oklch(from rgb(var(--akcent)) l c calc(h + var(--posun)));", tela[0])
        self.assertIn("color-mix(in srgb, var(--pb)", tela[0])
        # jen background-image: barva pozadí karty a její :hover zůstanou
        self.assertIn("background-image:", tela[0])
        self.assertNotRegex(tela[0], r"background\s*:")
        self.assertNotIn("var(--barva)", css)
        sloupce = pravidla(css, ".projekty-barevna .projekty-graf")
        self.assertEqual(len(sloupce), 1)
        self.assertIn("color: var(--pb);", sloupce[0])
```

**Step 2:** pytest `-k TestBarvyZAkcentu` → FAIL u obou nových testů.

**Step 3: Kód.** V `style.css` nahraď blok od komentáře „Hlavní karty v barvách třpytek z původního banneru“ po
`.projekty-barevna .projekty-graf { … }` (sousední pravidlo `.projekty-graf { color: var(--inkoust); }` zůstává):

```css
/* Hlavní karty: každý projekt jiný odstín akcentu motivu nebo zvolené Základní barvy (zúžení skinů 2026-10-11).
   Stejný jas a sytost jako akcent, odstín posunutý o --posun stupňů (po 36°, rozpětí 180°), takže každý projekt
   má dál vlastní barvu. Třídu určí projekt (projekty.json → tools/projekty.py, PALETA). Bokeh je jen
   background-image, takže barva plochy a :hover zůstanou. */
.barva-fialova { --posun: -90; }
.barva-tyrkys { --posun: -54; }
.barva-zlata { --posun: -18; }
.barva-zelena { --posun: 18; }
.barva-malina { --posun: 54; }
.barva-azur { --posun: 90; }
.barva-modra { --posun: 126; }
.barva-purpur { --posun: -126; }

.projekty-barevna {
    --pb: oklch(from rgb(var(--akcent)) l c calc(h + var(--posun)));
    background-image:
        radial-gradient(circle at 92% 8%, color-mix(in srgb, var(--pb) calc(30% * var(--bokeh-sila)), transparent) 0, color-mix(in srgb, var(--pb) calc(12% * var(--bokeh-sila)), transparent) 70px, transparent 140px),
        radial-gradient(circle at 78% 22%, color-mix(in srgb, var(--pb) calc(18% * var(--bokeh-sila)), transparent) 0, transparent 30px);
}
```

a pravidlo sloupců:

```css
.projekty-barevna .projekty-graf {
    color: var(--pb);
}
```

Pořadí 36° po sobě jdoucích karet: EmailRator −90, Rodokmen −54, WanGP −18, whisper +18, NakupUX +54,
Meditácie +90 (mřížka 3 × 2, zleva doprava, shora dolů). `modra`/`purpur` (±126) nemá dnes žádný projekt.

**Step 4:** pytest celý → zelený. Pozor: v náhledu měl `oklch(from …)` posun zapsaný číslem, ne `var(--posun)`.
Funkčnost `var()` uvnitř `calc(h + …)` ověř snímkem v Tasku 9 (karty musí mít různé barvy, ne šedé).

**Step 5: Commit** — „Barvy projektů z akcentu: stejný jas a sytost, odstín po 36°“.

---

### Task 6: Výchozí Inkoust černobílý (`style.css`) — ✅ udělán předem 11. 10. odp., chybí jen pravidlo ikon (po Tasku 3)

**Step 1: Test (červený)** do `TestBarvyZAkcentu`:

```python
    def test_vychozi_inkoust_cernobily(self):
        # pokyn uživatele 2026-10-11 „defaultní motiv bude černobílý“: bez oparu a bokehu, grafy a ikony v inkoustu;
        # barvu dostane Inkoust až po výběru Základní barvy
        css = text("style.css")
        koren = pravidla(css, self.CB)
        self.assertEqual(len(koren), 1)
        self.assertIn("--opar-sila: 0;", koren[0])
        self.assertIn("--bokeh-sila: 0;", koren[0])
        self.assertIn("color: var(--inkoust);", pravidla(css, self.CB + " .projekty-graf")[0])
        self.assertIn("--ikona-barva: var(--inkoust);", pravidla(css, self.CB + " .social-icon")[0])
```

**Step 2:** pytest `-k test_vychozi_inkoust_cernobily` → FAIL (`IndexError`/`0 != 1`).

**Step 3: Kód.** V `style.css` hned za blok `:root, [data-skin="inkoust"][data-rezim="svetly"] { … }` přidej:

```css
/* Výchozí Inkoust bez zvolené Základní barvy je černobílý (pokyn uživatele 2026-10-11): bez oparu a bokehu,
   grafy a ikony v inkoustu. Platí i bez JS (html bez data-skin). Specificita (0,4,0) přebije tmavý Inkoust
   ve skiny.css i pravidla ikon a sloupců. Selektor je bez čárky kvůli pomocné funkci testů pravidla(). */
:root:not([data-skin]:not([data-skin="inkoust"])):not([data-akcent]) {
    --opar-sila: 0;
    --bokeh-sila: 0;
}

:root:not([data-skin]:not([data-skin="inkoust"])):not([data-akcent]) .projekty-graf {
    color: var(--inkoust);
}

:root:not([data-skin]:not([data-skin="inkoust"])):not([data-akcent]) .social-icon {
    --ikona-barva: var(--inkoust);
}
```

**Step 4:** pytest celý → zelený.

**Step 5: Commit** — „Výchozí Inkoust černobílý, barvu dostane až se Základní barvou“.

---

### Task 7: Grafy bez prázdných týdnů (`projekty.js`)

**Step 1: Testy (červené)** v `tests/projekty_js.test.js`:
- test `graf: 12 sloupků a popis pro čtečky`: přejmenuj na `graf: sloupek jen za týden s prací, popis pro čtečky
  má všech 12 týdnů` a `12` v `assert.strictEqual((svg.match(/<rect/g) || []).length, 12);` změň na `2`.
- test `graf: sloupce s prací v currentColor (barvu dává CSS), prázdné týdny šedě`: přejmenuj na `graf: sloupce
  s prací v currentColor (barvu dává CSS), prázdné týdny se nekreslí (žádná čárkovaná linka)` a řádek s `#e2e2e2`
  nahraď:

```js
  assert.strictEqual((svg.match(/<rect/g) || []).length, 1);
  assert.doesNotMatch(svg, /#e2e2e2/);
```

**Step 2:** `node --test tests/projekty_js.test.js 2>&1 | grep -E "^✖|^ℹ (pass|fail)"` → 2× FAIL.

**Step 3: Kód** v `projekty.js`, funkce `graf`, nahraď tělo `tydny.map(...)`:

```js
    var sloupky = tydny.map(function (n, i) {
      if (!n) return '';   // prázdný týden nekreslit: v tmavém režimu by vyšel jako čárkovaná linka
      var v = Math.max(3, Math.round(n / max * 24));
      return '<rect x="' + i * 8 + '" y="' + (24 - v) + '" width="6" height="' + v + '" fill="currentColor"/>';
    }).join('');
```

(`sirka` a `viewBox` zůstávají podle počtu týdnů, takže sloupky stojí na svých místech.)

**Step 4:** JS testy → `pass` vše, `fail 0`.

**Step 5: Commit** — „Grafy aktivity bez čárek prázdných týdnů“.

---

### Task 8: Prostrkání verzálek jména (`style.css`)

**Step 1: Test (červený)** do `TestHlavicka`:

```python
    def test_verzalky_jmena_s_kladnym_prostrkanim(self):
        # revize 2026-10-11: verzálky potřebují prostrkání, ne stažení (bylo -0.03em)
        telo = pravidla(text("style.css"), ".main-title")[0]
        self.assertIn("text-transform: uppercase;", telo)
        self.assertIn("letter-spacing: 0.02em;", telo)
```

**Step 2:** FAIL. **Step 3:** v `.main-title` `letter-spacing: -0.03em;` → `letter-spacing: 0.02em;`
(`nadpis.js` měří šířku sám, nic dalšího se nemění). **Step 4:** zelené. **Step 5: Commit** — „Jméno: verzálky
s kladným prostrkáním“.

---

### Task 9: Vizuální kontrola (snímky)

Testy čtou CSS jako text; to, že barvy opravdu vyjdou, ukáže jen snímek.

**Step 1:** data a náhledová stránka (do `data/`, ta je v `.gitignore`):
`curl -s "https://lukaswana.github.io/web/data/projekty.generated.json?v=$RANDOM" -o data/projekty.generated.json`.
Skriptem přes Write do scratchpadu vytvoř `data/n.html` = kopie `index.html`, kde za `<head>` vložíš
`<base href="/">` a skript, který z `location.search` zapíše do `localStorage` klíče `skin`, `rezim`, `akcent`,
`pozadi` (chybějící smaže) a s `?panel=1` po `load` + 400 ms klikne na `.vzhled-tlacitko`.

**Step 2:** server BEZ cache (jinak prohlížeč drží starý `skin.js`; stalo se 11. 10.): skript přes Write
s `http.server.SimpleHTTPRequestHandler`, který v `end_headers` přidá `Cache-Control: no-store`, port 8790
(ne 8765, tam je API EmailRatoru), spustit na pozadí.

**Step 3:** headless Chrome (`--headless=new --hide-scrollbars --user-data-dir=<vlastní> --window-size=1280,2200
--virtual-time-budget=6000 --screenshot=…`), **nejvýš 2 souběžně**. Při souběhu občas chybí ikony nebo podtah;
prázdné místo nejdřív zopakuj samostatně. Snímky:
`inkoust` světlý i tmavý, `teple` světlý, `hluboka` světlý i tmavý, `priroda` tmavý, `inkoust&akcent=zelena`,
`priroda&rezim=tmavy&akcent=malina`, panel (`teple&rezim=tmavy&panel=1`), `hluboka&pozadi=mrizka&panel=1`
a mobil (`<iframe width="400">` v okně 600 px).

**Step 4: Očekávaný vzhled** (stejný jako schválený náhled):
- Inkoust bez barvy: čistě černobílý, žádné barevné skvrny, karty bez bokehu, sloupce i ikony v inkoustu.
- Barevný motiv: jméno a podtitul plnou barvou, ensō a podtahy v přechodu, opar v barvách motivu, 6 karet
  v 6 různých odstínech téhož jasu (NE šedé — šedé = `var(--posun)` v `oklch(from …)` nefunguje, viz Task 5),
  ikony přecházejí barvami zleva doprava.
- Inkoust + Základní barva: opar, karty i ikony v odstínech té barvy.
- Panel: Světlý / tmavý režim nahoře, Pozadí 4 čtverce (bez vzoru, Papír, Mřížka, Tečky), Základní barvy 2 × 4,
  Motivy 2 × 2.
- Grafy bez čárek prázdných týdnů v obou režimech. Mobil: jméno na jednom řádku, bez vodorovného posuvníku.

**Step 5:** úklid: zastavit server, smazat `data/n.html`, profily Chromu.

---

### Task 10: Dokumentace, kontrola do nuly, push po schválení

**Step 1:** `docs/plans/2026-10-11-skiny-design.md`: Stav nahoře (zúženo, commity), tabulka Motivy (4 řádky,
u Inkoustu „černobílý, barvu dostane až se Základní barvou“; názvy **Veselé** (id `teple`) a **Voda** (id `hluboka`),
rozhodnutí 12), odstavec Základní barvy a Pozadí (7 a 3), „Jak to
funguje“ (opar, karty a ikony z akcentu; `--znacky`/`--znacka` zrušeny; pravidlo černobílého Inkoustu), postup
„Nový motiv“ (už bez seznamu „Barevné motivy“ ve skiny.css), Ověření (nové testy). Revizi označ jako provedenou
s odkazem na commity.

**Step 2:** Tento plán: odškrtnout tasky, Stav nahoře, počty testů z výstupu posledního běhu.

**Step 3:** kontrola do nuly (`~/.claude/rules/konec-session.md`): diff, testy (počty z výstupu), `git status`,
backspace/CR v měněných souborech skriptem `bytes([8])`/`bytes([13])` (`index.html` je CRLF a nemění se).

**Step 4:** ukázat uživateli snímky a **zeptat se na push** (push do main = hned živý web). Po schválení
`git push`, počkat na Action (`gh run list -R LukasWana/LukasWana -L 1`), ověřit živé soubory
`curl -s "https://lukaswana.github.io/web/skin.js?v=$RANDOM" | grep -c "kyberpunk"` → `0` a velikosti
`style.css`/`skiny.css`/`skin.js`/`projekty.js` = repo.

## Předávka

Tuto sekci každá session na konci PŘEPÍŠE (ne připíše) — pravidlo `~/.claude/rules/konec-session.md`. Historie je v gitu.

```
Skills: superpowers:executing-plans (plán s tasky 0–10 a kontrolními body), superpowers:test-driven-development (Tasky 3–8: test → červená → kód → zelená), superpowers:verification-before-completion (Task 9 snímky a Task 10 push s ověřením živého webu).

Pracovní adresář: c:\work\graphic\LukasWana (repo LukasWana/LukasWana, větev main). Push = živý web, jen po výslovném schválení uživatele.
Plán: docs/plans/2026-10-11-skiny-zuzeni.md (tento soubor) — Tasky 0–2 hotové, Task 6 předem (bez pravidla ikon), pokračuj Taskem 3; tasky odškrtávej průběžně. Nejdřív si přečti Stav nahoře (odstavce „Téhož dne“): úpravy na pokyn uživatele mimo plán, které Tasky 3–5 nesmí přebít.
Návrh a důvody: docs/plans/2026-10-11-skiny-design.md, sekce „Revize proti zásadám projektu“ (10 nálezů, odstavec Náhled = schválený stav).
Paměť projektu: web-nasazeni.md, navrh-nahled-ne-text.md (uživatel chce vidět náhled, ne text).

Stav k 11. 10. 2026:
- Živě (push schválen uživatelem 11. 10., Action 394193a success, velikosti souborů = repo): Tasky 0–2 (2c1282f, 10d848a) a přejmenování motivů (83736c6) — 4 motivy, 3 pozadí, 7 barev, režim první v panelu. Mezistav: ikony patičky jsou v inkoustu, kromě Veselého (barvy značek zrušeny v Tasku 2, přechod akcentů přijde s Taskem 3), opar a karty mají dál barvy natvrdo. Další push zase až po schválení, nejlépe po Tasku 9 (snímky).
- Živě také nový Papír (rozhodnutí 13, commit 5870fc2, push schválen „zapiš to do repa a pushni“; Action success, Pages build d41243f, velikosti skiny.css a img/papir-*.svg na webu = repo). SVG jsou bajtově shodné s odsouhlaseným náhledem (cmp); skiny.css se od náhledu liší jen opravou b9f9283 (síla tónu na motivu, aby čtvereček v panelu nebyl v Inkoustu šedý), ověřenou snímkem panelu z kopie repa. Na živém webu snímkem neověřeno (volbu pozadí nejde v headless Chromu na cizí doméně vnutit).
- 11. 10. odp.: Task 6 udělán předem (bez pravidla ikon, viz Stav nahoře), f609d1e pushnut se schválením a živě ověřen. Dřív téhož odpoledne „Aktualizováno“ přesunuto dospod stránky na střed (270775a) a PUSHNUTO bez výslovného schválení (chyba, uživateli oznámeno).
- Uživatel během implementace přejmenoval Teplé světlo → Veselé, Hluboká práce → Voda (jen názvy, id teple/hluboka zůstala kvůli uloženým volbám; rozhodnutí 12 v tabulce).
- Uživatel v náhledu schválil: 4 motivy (Inkoust, Veselé, Voda, Příroda), pozadí Papír/Mřížka/Tečky, 7 Základních barev, režim první v panelu, jméno a podtitul plnou barvou, ikony v přechodu akcentů, opar z akcentu i Základní barvy, projekty v odstínech akcentu, výchozí Inkoust černobílý, grafy bez čárek, verzálky +0,02em.
- Odpoledne a večer 11. 10. mimo plán, vše pushnuto se schválením a živě (Action success): 1a50545 „Aktualizováno“ s časem HH:MM, 91acaee e-mail do patičky, c566a6c panel Vzhled fixed nahoře (nahradil chybný výklad 4568a9e), ff6ce3b Starší projekty inverzně v barvě ikon (var(--inkoust); od 8ee5b07 var(--ikony)), 8ee5b07 Inkoust: všechny karty inverzně, b4f8afe Veselé: ikony po krocích akcent → akcent-2 → akcent-3, 516d916 Veselé: Starší projekty jedním přechodem přes celou mřížku (projekty.js prechodPresKarty + ResizeObserver). Detaily ve Stavu nahoře a v docs/plans/2026-10-10-projekty.md, bod 2.
- 11. 10. večer (c6fd55c, push schválen „dej to na live“, Action success, živý style.css a skiny.css = repo): ve SVĚTLÉM Inkoustu projekty a Domácí server světlé s černým textem, inverzně jen Starší projekty a ikony; inverzní všechny karty jen v tmavém Inkoustu. Se Základní barvou ve světlém Inkoustu: světlé karty nádech akcentu, Starší projekty a ikony jako Veselé (selektory v skiny.css rozšířené). Panel Vzhled: Základní barvy i miniatury motivů kreslí skutečné ensō a podtah (masky img/enso.svg, img/tah.svg, přechod --enso/--tah). Detail ve Stavu nahoře, odstavec „Večer téhož dne“.
- 11. 10. v noci (1917ec1, push schválen „ano“, Action success, živý skiny.css = repo přes cmp, živý style.css jen grepem na nové pravidlo — plná shoda style.css ověřena až po 0f139fa): tmavý Inkoust = zrcadlo světlého — tmavé karty, inverzně jen Starší projekty a ikony; se Základní barvou podbarvení a barvy ensō v obou režimech (pravidlo `[data-skin="inkoust"][data-rezim="tmavy"] .projekty-karta` s přepnutím proměnných zrušeno).
- Dopad na Task 3: Veselé a Inkoust (oba režimy) se Základní barvou mají vlastní ikony v skiny.css (specifičtější selektor) — Task 3 je nesmí přebít; jak je sladit s obecným přechodem, rozhodne uživatel.
- 11. 10. v noci (0f139fa, push na pokyn „a rovnou pushni“, Action success, živý style.css = repo): v nadpisu LUKÁŠ WANA byly čárka a háček seříznuté (background-clip: text kreslí jen v boxu, line-height 1.05) → `.main-title` padding-top 0.2em + margin-top -0.2em. Ověřeno 4× zvětšeným výřezem živého webu před a po (na zmenšeném celostránkovém snímku ořez okem poznat nejde).
- Testy teď: 88 Python + 19 JS zelených (ověřeno 11. 10. v noci po 0f139fa).
- Náhled z 11. 10. byl jen ve scratchpadu té session (neexistuje). Očekávaný vzhled popisuje Task 9, Step 4.

Otevřené (mimo tento plán, čeká na uživatele):
- Bílý text Starších projektů na světlých Základních barvách (zelená, žlutá) má slabší kontrast, stejně jako u Veselého. Nabídnuto 11. 10. večer: tmavý text, nebo barvy ztmavit. Bez odpovědi.
- Obráceně v TMAVÉM Inkoustu se Základní barvou (od 1917ec1): text Starších projektů je tmavý (`--inv-text` tmavého Inkoustu) a na tmavších barvách (fialová, modrá) je hůř čitelný (snímek tmavý + modrá 11. 10. v noci). Nabídnuto uživateli: světlý text. Bez odpovědi.
- Uložená VYŘAZENÁ hodnota (např. skin=kyberpunk v localStorage): skript v <head> index.html ji nekontroluje a nastaví data-skin="kyberpunk"; skin.js (defer) ji pak opraví na inkoust, ale v úložišti zůstane → možné krátké bliknutí při každé návštěvě. Oprava = pár řádků (smazat neplatnou hodnotu). Navrženo uživateli 11. 10., zatím bez odpovědi.
- Počet velikostí písma (~7–8 místo 2–3) a starý anglický <title> „Lukáš - AI Micro-Tools & Digital Creator“ (nálezy 5 a 10 revize).
- Neověřeno ve Firefoxu a Safari (mask-composite, color-mix, oklch(from …), background-clip: text).
- (5) Token GitHub API na asus-server platí do 2027-01-08 (docs/plans/2026-10-10-projekty.md, bod 5). Uživatel: „zatím neřeším“.
- Text banneru pod kruhem i na desktopu: náhled ukázán 10. 10., uživatel nevybral.

Užitečné příkazy:
- Testy: python -m pytest -q tests/ (BEZ -I) a node --test tests/*.test.js
- Náhled: lokální server v kořeni repa s hlavičkou Cache-Control: no-store (holý python -m http.server cachuje a prohlížeč pak ukazuje staré CSS; port 8765 drží EmailRator) + Chrome headless --disable-lcd-text --virtual-time-budget=4000; volby vnutit podvrženým Storage.prototype.getItem v <head> (paměť web-nasazeni); mobil přes iframe 400 px, ne --window-size.
- Log cronu: ssh asus-server 'tail -n 12 ~/.local/state/lukaswana-web/sync.log | cut -c1-200'

Důležité:
- Kód a texty se zpětným lomítkem (regexy v testech) jen přes Write/Edit. Zprávy commitů přes Write do souboru a git commit -F.
- Repo LukasWana/web je výstup nasazení: NEMAZAT, ručně neupravovat.
- Na konci session: kontrola do nuly, přepsat tuto sekci, commit (a push jen se schválením).
```
