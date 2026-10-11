# Skiny — návrh

Datum: 2026-10-11 · Stav: **implementováno, čeká na push** (větev `skiny`). Push schválil uživatel větou „takhle to pushni“.

## Zadání a rozhodnutí uživatele (11. 10.)

- Zadání: „připrav projekt na skinování: nahoře na stránce dej tlačítko s vysouvací nabídkou skinů, všechny
  skiny budou mít dark/light verzi“.
- Rozsah: nejdřív „základ + 1 skin“. Režim při první návštěvě: **podle systému** a volba se uloží.
- Uživatel nechce textový návrh po částech, chce rovnou vidět náhled (paměť `navrh-nahled-ne-text`).
- Nad prvním náhledem (Inkoust světlý i tmavý, malá nabídka) řekl „jako výchozí verze dobrý“ a poslal
  koncept z Gemini (`Downloads/Gemini_Generated_Image_37vkh537vkh537vk.jpeg`, mimo repo): panel
  „Vzhled & Motivy“ se sekcemi Pozadí, Základní barvy, Světlý/Tmavý režim, Základní motivy.
  Ze čtyř nabídnutých věcí vybral **všechny**: panel jako na obrázku, víc motivů, barevné akcenty, pozadí
  s texturou.
- Nad druhým náhledem: „ty outline dej všude pryč“. Karty nemají barevný okraj ani linku, panel a vzorníky
  nemají linku. Zůstal jen prstenec u vybrané volby (jinak není poznat, co je zvolené) a obrys fokusu
  z klávesnice (přístupnost). Minimal tím přišel o linku karet, proto má karty na světle šedé ploše.

**Vědomě jinak než koncept z Gemini:** ensō zůstává tah štětcem (v motivech v barevném přechodu), ne zářící
prstenec. Ikony zůstávají ručně kreslené, jen v barvách značek, bez pastelových koleček. Texty a data karet
zůstávají skutečné, koncept je měl vymyšlené.

## Jak to funguje

- **Role místo barev.** Každá viditelná barva je proměnná: `--pozadi`, `--inkoust`, `--text`, `--text-tlumeny`,
  `--text-popisek`, `--plocha`, `--plocha-hover`, `--inv-*` (inverzní karty starších projektů),
  `--motiv-akcent{,-2,-3}`, `--opar-sila`, `--bokeh-sila`, `--znacky`.
- **Motiv = dva bloky** `[data-skin="id"][data-rezim="svetly|tmavy"]`. Selektory nejsou vázané na `:root`, takže
  stejné bloky obarví i dlaždici motivu v panelu. Barvy motivu tak nejsou opsané nikde v JS.
- **Volby nad motivem:** `data-akcent` (Základní barvy, nastaví `--volba-akcent*`) a `data-pozadi` (vzor,
  nastaví `--volba-vzor`). Výsledné role skládá obecné pravidlo `:root, [data-skin]`:
  `--akcent: var(--volba-akcent, var(--motiv-akcent))`. Pozadí je průsvitný vzor přes barvu motivu, takže
  čitelnost drží motiv a režim. Čáry a tečky berou barvu z `--inkoust`, zrno papíru a krajina jsou SVG
  a mají světlou i tmavou verzi.
- **Soubory:** `style.css` obsahuje obecné pravidlo a výchozí Inkoust ve světlém režimu, takže se stránka
  vykreslí i bez druhého souboru. Na snímcích se nenačtený `skiny.css` projevil neviditelným nadpisem. `skiny.css`
  obsahuje ostatní motivy, tmavé verze, Základní barvy a Pozadí. `skin.js` drží seznamy id a staví panel.
- **Bez probliknutí:** skript v `<head>`, který běží před `style.css`, přečte `localStorage` (`skin`, `rezim`, `akcent`,
  `pozadi`) a nastaví atributy na `<html>`. Neplatné hodnoty opraví `skin.js` (`stav()`). Bez JS zůstane
  tlačítko skryté a stránka je ve výchozím Inkoustu.
- **Tahy štětcem a ikony jako maska.** Ensō a podtahy jsou `mask: url(img/…svg)` s pozadím `--enso` nebo `--tah`
  (kuželový nebo lineární přechod z akcentů; u Inkoustu jsou všechny tři akcenty inkoust, takže je to plná barva).
  Ikony v patičce mají masku ze dvou vrstev téhož SVG: tvar (alpha) minus bílý symbol (luminance). Symbol
  je průhledný, takže jím prosvítá pozadí skinu. Kořenový `fill` ikon je proto `#000`: jas `#1a1a1a` by maska
  odečetla a inkoust by vyšel `rgb(49,49,49)` místo `(26,26,26)` (změřeno na snímku). `tools/enso.py` se nemění.

## Motivy

| id | název | charakter |
|---|---|---|
| `inkoust` | Inkoust (výchozí) | černobílý, beze změny proti dosavadnímu webu; tmavý = teplá `#151413` |
| `teple` | Teplé světlo | krémová, námořnická modř, akcent modrá → fialová → oranžová |
| `hluboka` | Hluboká práce | břidlicová, tyrkys a modrá |
| `indigo` | Kreativní indigo | fialová a růžová |
| `priroda` | Příroda | písková a olivová, zelená a jantar |
| `kyberpunk` | Kyberpunk | neonová purpurová a azurová, jemná mřížka jako výchozí vzor |
| `minimal` | Minimal | jen šedé, bez oparu a bokehu |

Barevné motivy (všechny kromě Inkoustu a Minimalu) mají nadpis a podtitul v přechodu a ikony v barvách značek.
Základní barvy: 9 barev z palety původního banneru (+ oranžová), každá se dvěma sousedními barvami pro přechod.
Pozadí: papír, mřížka, tečky, mech, soumrak, polární záře, krajina.

**Nový motiv:** id a název do `SKINY` ve `skin.js`, dva bloky do `skiny.css` se všemi rolemi (test
`TestSkiny` je vyjmenuje). Barevný motiv navíc do seznamu selektorů „Barevné motivy“ na začátku `skiny.css`.

## Ověření

- Testy: `TestSkiny` v `tests/test_stranka.py` hlídá, že každý motiv má světlý i tmavý blok se všemi rolemi,
  že kontrast textu je ≥ 4,5 : 1 (WCAG AA) na pozadí i na ploše karet, a to v obou režimech, že ke každé Základní
  barvě a každému Pozadí existuje pravidlo, že skript v hlavičce běží před styly a že nikde nejsou obrysy. Dále
  `tests/skin_js.test.js` (oprava neplatných uložených hodnot, režim podle systému, stavba panelu).
  Kontrast poprvé našel 5 slabých párů (popisky Teplého světla, Hluboké práce a Přírody, `--inv-text-3`
  tmavé Přírody, 3,83–4,45) a ty byly ztmaveny. Mutace 4 chyb (chybějící role, slabý kontrast, obrys panelu,
  bez validace skinu) testy chytily.
- Snímky headless Chromem: 7 motivů × 2 režimy, otevřený panel (desktop i iframe 400 px), 8 kombinací pozadí,
  patička. **Past snímků:** při 4 souběžných Chromech se občas nenačetla data, maska nebo `skiny.css`.
  Opakování po jednom vždy vyšlo správně, takže prázdné místo na snímku nejdřív zopakuj samostatně.
- Neověřeno: Firefox a Safari (`mask-composite: subtract`, `color-mix`, `background-clip: text` mají
  podporu v aktuálních verzích; starší Safari potřebuje `-webkit-` prefixy, které jsou uvedené).
