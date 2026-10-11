# Skiny — návrh

Datum: 2026-10-11 · Stav: **živě 7 motivů; zúžení schválené v náhledu 11. 10., implementace podle `2026-10-11-skiny-zuzeni.md` (ještě neprovedena).** Původně: Commit `7efd5e3` (push `9328901..7efd5e3` po „takhle to pushni“),
Action run 38125366926 `success`. Živý web ověřen: `skin.js`, `skiny.css` a `style.css` mají přes `curl` stejnou
velikost jako v repu (8 142 / 13 860 / 26 827 B; po opravě miniatury motivu v `f8caa16`, run 38125535416
`success`, má živý `style.css` 26 799 B = repo) a snímek živé stránky v čistém headless Chromu ukazuje tlačítko
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

## Revize proti zásadám projektu (11. 10., na otázku uživatele)

Otázka: „jsou všechny skiny nejlepší možné a ctí nejvyšší estetické, typografické a grafické standardy ze
začátku projektu?“ Zásady jsou zadání z 10. 10. („profesionální prezentace, drž se jednoduchosti, odstraň zbytečné
linky, … jednoduše a profesionálně“, laťka „nejlepší top designéři“) a `2026-10-10-prezentace-design.md`
(ručně kreslený je jen inkoust, jinak čistá typografie, jedno písmo ve 2–3 velikostech, méně verzálek, mezery
místo čar). Podklad: 14 snímků (7 motivů × 2 režimy) + panel + pozadí Krajina z headless Chromu.

**Verdikt: ne všechny.** Inkoust (světlý i tmavý) zásady drží. Systém rolí, kontrast AA a panel jsou v pořádku.
Nálezy (nic zatím neopraveno, čeká na rozhodnutí uživatele):
1. **Počet voleb:** 7 motivů × 9 barev × 7 pozadí × 2 režimy = 882 kombinací. Odporuje to zásadě „drž se
   jednoduchosti“: dobrý design nabídku vybírá, ne sčítá. Většina kombinací se nikdy neviděla.
   Uživatel ale 11. 10. vybral všechny čtyři rozšíření sám, takže jde o konflikt zásad, ne o chybu provedení.
2. **Opar v banneru má v každém motivu stejnou duhovou paletu** a nebere barvy motivu. V Přírodě a Kyberpunku
   se proto růžové, modré a zelené skvrny tlučou s paletou.
3. **Ikony v barvách značek:** v barevných motivech stojí vedle sebe 8 sytých barev, které s paletou motivu
   nesouvisí (nejvíc to bije do očí v Přírodě a v Teplém světle). Navíc tím ikony přestávají působit jako inkoust.
4. **Prázdné dny v grafech aktivity jsou v tmavých režimech vidět jako čárkovaná linka** („_ _ _“), takže se tam
   vrací čára, kterou zadání rušilo. Ve světlých režimech je skoro neviditelná, takže režimy nejsou konzistentní.
5. **Typografie:** jméno je ve verzálkách s prostrkáním −0,03em (`style.css` `.main-title`). Verzálky potřebují
   kladné prostrkání a návrh chtěl verzálek méně. Na stránce je vidět ~7–8 velikostí písma, návrh chtěl 2–3
   (`style.css` jich deklaruje 13, část patří skrytému starému obsahu). Jméno a podtitul mají v barevných motivech
   text vyplněný přechodem; podtitul je tím slabší na čtení a kontrast přechodu test nehlídá.
6. **Pozadí Krajina** (kopce přes střed stránky za kartami), **Soumrak** a **Polární záře** působí jako ilustrace
   z fotobanky. Odporují zásadě „ručně kreslený je jen inkoust“.
7. **Kyberpunk** (neonová mřížka) jde proti celé myšlence ensō a klidu.
8. **Minimal** se od Inkoustu skoro neliší a grafy aktivity v něm zůstávají barevné, i když motiv má být „jen šedý“.
9. **Základní barvy:** dvojice skoro stejných vzorníků (dvě oranžové a azur/tyrkys vedle sebe).
10. Mimo skiny: `<title>` je pořád starý anglický „Lukáš - AI Micro-Tools & Digital Creator“ a s obsahem nesedí.

Návrh (neschválený): méně, ale vybraně. Inkoust jako výchozí a 2–3 barevné motivy, u kterých opar i ikony
převezmou barvy motivu. Kyberpunk a Minimal vyřadit. Z pozadí ponechat Papír, případně Tečky. Prostrkání
verzálek změnit na kladné nebo jméno sázet bez verzálek. V grafech zrušit čárky prázdných dnů. Sloučit zdvojené
barvy. Uživatel chce vidět náhled, ne text (paměť `navrh-nahled-ne-text`).

**Náhled (11. 10., na „ano“ uživatele):** kopie webu ve scratchpadu session (ne v repu) s body 1–4, 6–9 a s jedinou
změnou z bodu 5 (prostrkání jména +0,02em). Obsahuje motivy Inkoust, Teplé světlo, Hlubokou práci a Přírodu (Indigo
vyřazeno, protože se fialovou kryje s Teplým světlem), pozadí Papír, Mřížka a Tečky (Mřížku vrátil uživatel:
„dej tam i ty čtverečky“). V panelu je Světlý / tmavý režim první volbou (pokyn „světlý / tmavý dej jako první
volbu“), za ním Pozadí, Základní barvy a Motivy. **Barvy hlavních projektů ladí s volbou** (pokyn „přepínátkem chci
ladit i barvy top projektů“). V barevném motivu nebo po výběru Základní barvy má každý projekt jiný odstín odvozený
z akcentu: `oklch(from rgb(var(--akcent)) l c calc(h + posun))`, takže všechny mají stejný jas a sytost a odstíny
jsou po 36° v rozpětí 180° (EmailRator −90°, Rodokmen −54°, WanGP −18°, whisper +18°, NakupUX +54°, Meditácie +90°).
Každý projekt má tak dál unikátní barvu. Inkoust bez zvolené barvy si nechal barvy původního banneru. Ověřeno snímky
Teplé světlo, Příroda tmavá, Hluboká práce a Inkoust + Malinová. Relativní barvy (`oklch(from …)`) umí Chrome 119+,
Safari 16.4+ a Firefox 128+, ale ověřeno je to jen v Chromu. **Opar nahoře** přebarví motiv i Základní barva,
tedy stejně jako karty (volba uživatele z nabídky „ať je přebarví i Základní barva“; zamítnuté možnosti byly
„opar neměnit“ a „opar zrušit“). Ověřeno snímky Inkoust + Zelená a Příroda tmavá + Malinová. **Výchozí Inkoust
bez zvolené barvy je čistě černobílý** (pokyn „defaultní motiv bude černobílý“, mění volbu z 11. 10. ráno, kdy měl
Inkoust opar a karty v barvách banneru): `--opar-sila: 0`, `--bokeh-sila: 0`, grafy v inkoustu. Barvu dostane až po
výběru Základní barvy. Ověřeno snímky Inkoust světlý i tmavý. **Ikony sociálních sítí**
přecházejí zleva doprava akcenty motivu jako ensō (pokyn „motiv mění i ikony sociálních sítí“), ověřeno
snímky Teplé světlo, Příroda tmavá a Inkoust + Modrá. Dál 7 Základních barev (bez Zlaté a Azurové).
Jméno a podtitul jsou plnou barvou, ikony v inkoustu motivu, opar barevných motivů je z akcentů motivu (Inkoust si
nechal barvy původního banneru) a v grafech chybějí čárky prázdných týdnů. Barvy projektů na kartách zůstaly
(pokyn „každý projekt unikátní barvu“). Neřešeno: počet velikostí písma a `<title>`. Čeká se na verdikt uživatele.

## Další práce

Předávka se přesunula do implementačního plánu `docs/plans/2026-10-11-skiny-zuzeni.md`
(sekce `## Předávka` tam). Tady je jen návrh a historie rozhodnutí.
