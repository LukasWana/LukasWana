# Skiny — návrh

Datum: 2026-10-11 · Stav: **hotovo a živě.** Commit `7efd5e3` (push `9328901..7efd5e3` po „takhle to pushni“),
Action run 38125366926 `success`. Živý web ověřen: `skin.js`, `skiny.css` a `style.css` mají přes `curl` stejnou
velikost jako v repu (8 142 / 13 860 / 26 827 B) a snímek živé stránky v čistém headless Chromu ukazuje tlačítko
Vzhled. Stránka se vykreslila v tmavém Inkoustu, protože se řídí systémem a Windows je v tmavém režimu.
Testy: 71 Python + 15 JS (11 `projekty_js` + 4 `skin_js`).

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

## Předávka

Tuto sekci každá session na konci PŘEPÍŠE (ne připíše) — pravidlo `~/.claude/rules/konec-session.md`. Historie je v gitu.

```
Skills: žádný konkrétní — práce je dokončená. Na novou úpravu vzhledu superpowers:brainstorming, ale uživatel nechce textový návrh po částech: po krátké otázce na rozsah rovnou postav náhled (paměť navrh-nahled-ne-text). Na rozbitou věc superpowers:systematic-debugging.

Pracovní adresář: c:\work\graphic\LukasWana (repo LukasWana/LukasWana, větev main). Push = živý web. Při konci session bylo vše pushnuté. Na začátku zkontroluj git status -sb.
Plán / návrh: docs/plans/2026-10-11-skiny-design.md (tento soubor, HOTOVO a živě, Stav nahoře).
Předchozí: docs/plans/2026-10-10-prezentace.md (hotový, ve Stavu je historie vzhledu), docs/plans/2026-10-11-barvy-design.md, docs/plans/2026-10-10-projekty.md (otevřený bod 5).
Paměť projektu: web-nasazeni.md (server, cron, souběh, ikony jako maska s fill #000, ensō), ps-roura-ssh-bom.md, navrh-nahled-ne-text.md.

Stav k 11. 10. 2026:
- Živě od 7efd5e3: tlačítko „◐ Vzhled“ vpravo nahoře, panel „Vzhled a motivy“: Pozadí (7 vzorů), Základní barvy (9), režim Světlý / Tmavý / Systém (výchozí Systém), Motivy (7, každý světlý i tmavý). Výchozí motiv Inkoust = dosavadní vzhled. Volby v localStorage (skin, rezim, akcent, pozadi).
- Kde co je: style.css = obecné skládání rolí + výchozí Inkoust světlý + komponenty a panel; skiny.css = ostatní motivy, tmavé verze, Základní barvy, Pozadí; skin.js = seznamy id (SKINY, AKCENTY, POZADI, REZIMY) a stavba panelu; skript v <head> index.html nastaví atributy před vykreslením. Nový motiv: postup v sekci Motivy výše.
- Ensō, podtahy a ikony patičky jsou CSS maska. img/enso.svg a img/tah.svg dál generuje tools/enso.py (ručně neupravovat). Ikony img/social mají kořenový fill #000 (důvod v sekci Jak to funguje).
- Obrysy karet a panelu jsou pryč (pokyn „ty outline dej všude pryč“). Zůstal jen prstenec vybrané volby a fokus.
- Testy: 71 Python + 15 JS zelených. TestSkiny hlídá role, kontrast WCAG AA ve všech motivech a režimech, pravidla voleb, skript v hlavičce a obrysy. tests/skin_js.test.js hlídá stav, režim a panel.
- Další práce není zadaná. Nic nedělat bez pokynu uživatele.

Otevřené (čeká na rozhodnutí uživatele):
- Neověřeno ve Firefoxu a Safari (mask-composite, color-mix, background-clip: text). Ověřeno jen v Chromu.
- (5) Token na GitHub API (~/.config/lukaswana-web/token na asus-server) platí do 2027-01-08. Po vypršení cron padá a na webu stojí datum „Aktualizováno“. Varianty jsou v docs/plans/2026-10-10-projekty.md, bod (5). Uživatel: „zatím neřeším“.
- Text banneru pod kruhem i na desktopu: náhled ukázán 10. 10., uživatel nevybral.

Užitečné příkazy:
- Testy: python -m pytest -q tests/ (BEZ -I, s ním spadne import pygments) a node --test tests/projekty_js.test.js tests/skin_js.test.js
- Náhled: data z webu do data/projekty.generated.json (gitignored): curl -s "https://lukaswana.github.io/web/data/projekty.generated.json?v=$RANDOM" -o data/projekty.generated.json, pak python -m http.server 8790 --bind 127.0.0.1 (ne 8765, tam je API EmailRatoru).
- Snímky motivů: kopie index.html do data/ s <base href="/"> a skriptem, který před <head> nastaví localStorage (skin, rezim, akcent, pozadi). Headless Chrome s vlastním --user-data-dir, nejvýš 2 souběžně a --virtual-time-budget=6000. Při 4 souběžných se občas nenačetla data, maska nebo skiny.css; prázdné místo na snímku nejdřív zopakuj samostatně. Otevřený panel: skript, který po 400 ms klikne na .vzhled-tlacitko. Mobil přes <iframe width="400"> v okně 600 px. Headless Chrome přebírá tmavý režim Windows, takže režim „Systém“ vyjde tmavý.
- Log cronu: ssh asus-server 'tail -n 12 ~/.local/state/lukaswana-web/sync.log | cut -c1-200'

Důležité:
- Push do main = hned živý web. Pushovat jen po výslovném schválení uživatele.
- Po pushi změny tools/projekty.py nebo projekty.json: počkej na deploy, pusť ručně sync.sh (příkaz v paměti web-nasazeni), ověř živá data curl s ?v=$RANDOM.
- Repo LukasWana/web je výstup nasazení. NEMAZAT, ručně neupravovat. Token nikdy do chatu a nikdy do souboru rourou z PowerShellu.
- Kód a texty se zpětným lomítkem piš jen přes Write/Edit (python heredoc v této session srazil lomítka v testu, assert to chytil před zápisem). Zprávy commitů piš přes Write do souboru a commituj s git commit -F.
- Pravidlo každé session (~/.claude/rules/konec-session.md): dokumentaci aktualizuj průběžně, na konci přepiš tuto sekci a commitni, před „hotovo“ udělej kontrolu do nuly.
```
