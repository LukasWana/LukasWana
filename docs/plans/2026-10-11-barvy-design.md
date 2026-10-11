# Barvy z původního banneru — návrh

Datum: 2026-10-11 · Stav: **implementováno a živě 11. 10.** (commit `5774f16`, testy 59 Python + 10 JS, snímky desktop a mobil ověřeny, živá data s barvami po ručním `sync.sh` 09:06, viz Stav v `2026-10-10-prezentace.md`)

## Proč

Po přechodu na vzhled „prezentace“ (`2026-10-10-prezentace-design.md`) je stránka čistá, ale uživatel
se obává, že je pro běžné publikum příliš strohá. Původní banner `W-ilustration-banner.png` (smazaný
v `d965581`, v gitu dostupný přes `git show d965581^:W-ilustration-banner.png`) byl ručně dělaný bokeh
z barevných třpytek. Jeho barvy mají stránku lehce dokreslit, ne ji přebarvit: ensō, typografie
a box Domácí server zůstávají černobílé.

## Paleta

Sytá místa banneru (s > 0,55, v > 0,6), průměr po odstínech, 8 barev:

| název | RGB | | název | RGB |
|---|---|---|---|---|
| fialova | 168, 34, 196 | | malina | 205, 52, 91 |
| tyrkys | 60, 193, 154 | | azur | 32, 152, 227 |
| zlata | 224, 184, 58 | | modra | 81, 135, 244 |
| zelena | 54, 196, 102 | | purpur | 172, 50, 148 |

Zlatá je zesvětlená (průměr vyšel zakalený #b79923, třpytky na obrázku jsou světlejší).

## Tři návrhy (náhledy 11. 10.) a volba

- **A — třpytivý opar za ensō:** rozostřené barevné kruhy jen v banneru.
- **B — barevný inkoust:** podtahy štětcem barevným přechodem, azurové sloupce aktivity.
- **C — každá karta svou třpytkou:** měkký bokeh v rohu karty, sloupce aktivity v téže barvě.

**Volba uživatele:** banner z A, karty z C. Barvu dostanou jen hlavní projekty, box Domácí server
zůstává černobílý, starší projekty šedé. Každý projekt má mít unikátní barvu.

## Provedení

**Banner:** `.enso-banner::before` s vrstvami `radial-gradient` v barvách palety, `filter: blur`,
maska elipsou do průhledna. Vodorovně nepřesahuje banner (`inset: -60px 0`), aby na mobilu
nevznikl vodorovný posuvník; náhled A měl `-8 %` do stran.

**Karty:**
- Barva patří projektu, ne pozici: pole `barva` u projektu v `projekty.json`. Když se pořadí karet
  změní podle aktivity, barvy se nepřehodí.
- Přiřazení (uživatel, 11. 10.): EmailRator fialová, Gramps (Rodokmen) tyrkys, WanGP zlatá,
  whisper-sk-transcriber zelená, NakupUX malina, meditation-app (Meditácie) azur. Volné: modrá, purpur.
- Unikátnost hlídají dvě věci. Že se barvy v `projekty.json` neopakují, kontroluje test
  (`test_skutecne_nastaveni`), generátor duplicitu v nastavení neopraví. Hlavní karta bez barvy z nastavení
  (aktivní repo, které v `projekty` není) dostane v `tools/projekty.py` (`obarvi`) první volnou barvu palety,
  kterou nemá žádná jiná hlavní karta.
  Hlavních karet je nejvýš `max_aktivnich` = 8 = počet barev. Skupina (Domácí server) barvu nedostane.
- `projekty.js` přidá kartě s barvou třídy `projekty-barevna barva-<název>` (jen `[a-z]+`).
- `style.css`: `.barva-<název> { --barva: R, G, B }` pro 8 barev; `.projekty-barevna` má bokeh
  jako `background-image` (barvu plochy i `:hover` dál určuje `.projekty-karta`; hover snímkem neověřen) a sloupce aktivity `fill: rgb(var(--barva))`.

**Testy:** barva z nastavení projde na kartu; volné barvy pro karty bez barvy; 8 karet = 8 různých
barev; skupina, archiv a starší barvu nemají; skutečné `projekty.json` má přiřazení výše a barvy
jsou unikátní a z palety; CSS má třídu pro každou barvu palety a banner má opar; JS dá třídu podle dat.
