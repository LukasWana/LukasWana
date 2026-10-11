# Web jako prezentace — plán implementace

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Z https://lukaswana.github.io/web/ udělat jednoduchou profesionální prezentaci: jméno, jeden tah štětcem (ensō), práce. Ručně kreslený je jen inkoust, všechno ostatní je čistá typografie.

**Architecture:** Návrh je v `docs/plans/2026-10-10-prezentace-design.md`. Ensō a krátký podtah generuje deterministický skript `tools/enso.py` jako SVG s vyplněným obrysem (Catmull-Rom → Bézier, žádný filtr). Výstupem jsou `img/enso.svg` a `img/tah.svg`, které stránka vkládá přes `<img>`. Zbytek práce jsou úpravy v `index.html` a `style.css`. Dodržení návrhu hlídá test `tests/test_stranka.py`, který čte HTML, CSS i SVG jako text.

**Tech Stack:** HTML/CSS, písmo Inter Tight z Google Fonts, Python 3.14 (generátor a `unittest`), headless Chrome na snímky.

**Rozhodnutí uživatele 2026-10-10:** návrh **potvrzen** („Ano, podle návrhu“). Kontaktní e-mail v hlavičce bude **qwanap@gmail.com**.

**Odchylky od návrhu, rozhodnuté při psaní plánu:**
1. *Ensō přes `<img>`, ne inline SVG.* Stejně jsou vloženy ikony v patičce. `index.html` zůstane čitelný (cesta má ~18 KB) a soubor se cachuje. Barva je pevně `#000`, takže z inline vložení nic nezískáme.
2. *Text banneru vedle kruhu, ne uvnitř.* Do vnitřku kruhu o průměru 300 px (~200 px volného místa) se „Deep work creator“ ve čitelné velikosti nevejde. Na mobilu jde text pod kruh. Znovu se to zváží nad náhledem v Tasku 6.
3. *Podtitul 22 px místo 18 px.* `nadpis.js` roztáhne jméno přesně na šířku inkoustu podtitulu. Zkrácený podtitul (~46 znaků místo ~80) by jméno zmenšil zhruba na polovinu, větší písmo podtitulu to částečně vyrovná. Konečnou velikost určí náhled.
4. *Podtah pod nadpisem sekce jako `::after` s `background-image`.* HTML se tím nemění a podtah dostanou i nadpisy ve skrytém `div.stary-obsah` (je `hidden`, nevadí to).

**Stav:** 2026-10-10 22:26 — **HOTOVO, Tasky 1–7, web živě.** Commity: `eaadd86` (generátor, `enso.svg` 18 453 B, `tah.svg` 9 755 B), `fae30db` (hlavička), `2d5c12e` (banner), `54f4a30` (čáry, podtah), `698cb80` (motto), `286902f` (karty jako plochy). Push po výslovném „pushni to“, Action run 38083567970 `success`, živý web ověřen `curl` (`enso-banner` 1×, `img/enso.svg` i `img/tah.svg` 200, v CSS `#f6f5f2`). Testy 43 Python + 9 JS zelených.
- Odchylka od Tasku 4: prázdné pravidlo `.projekty-aplikace li` (po odebrání `border-top` a `padding-top` nezbylo nic) smazáno celé.
- **Task 6, rozhodnutí uživatele nad náhledem:** tenké šedé rámečky karet „hrozně ostré“. Ze tří náhledů (A jen mezera, B světlá plocha, C tah pod názvem; doporučoval jsem C) vybral **B s oblými rohy**: `#f6f5f2`, `border-radius: 16px`, hover `#efede8` místo stínu, archiv `#fafaf8`, `.projekty-web` dědí zaoblení kvůli fokusu z klávesnice (`286902f`, test `test_karta_je_plocha_ne_ramecek`). Ostatní (text banneru vedle kruhu, podtitul 22 px, suchý konec ensō) schválil tak, jak jsou. Moje nabídky „výraznější suchý konec“ a „text pod kruh i na desktopu“ nechtěl — neuděláno. *(Později téhož večera si varianty vyžádal a suchý konec změnil na C, viz níže.)*
- Písmo Inter Tight posouzeno jen okem ze snímku, ne měřením.
- **10. 10. večer, další kolo na pokyn uživatele („3 ukaž varianty“):** náhledy suchého konce A (živý) / A2 (bez hrotu) / B (výraznější) / C (hodně suchý) a textu vedle / pod kruhem. Uživatel vybral **C**, doporučoval jsem B. K umístění textu se nevyjádřil, takže text zůstává vedle kruhu (doporučení). C v `enso()`: suchý konec od 0,6, 7 vláken, dojezd 0,45; vlákna se navíc ořezávají na šířku těla. `img/enso.svg` 31 967 B je bajtově shodný se schváleným náhledem. Testy 45 Python + 9 JS. Mobil (kruh 220 px) snímkován až při kontrole ve 23:14 (čas souboru snímku), na živém webu přes iframe 400 px: kruh nad textem, v pořádku. Commity `d965581` (smazán banner) a `d158405` (C + oprava hrotu) pushnuty po výslovném „pushni“, Action run 38085643598 `success`. Živý web ověřen `curl`: `img/enso.svg` 31 967 B, `img/tah.svg` 9 772 B, `W-ilustration-banner.png` 404.

**Otevřené:**
- ~~**Zub v ensō (nalezeno 10. 10. ve 22:45 nad náhledem ve 2× rozlišení, je i na živém webu):**~~ **Opraveno** v `_bezier` (nulová tečna v rozích, `_roh`), test `test_roh_obrysu_neprestreli` (před opravou přestřel na y = 36,7 při okraji 40). Stejný hrot měl i podtah `img/tah.svg`, oprava ho odstranila (ověřeno snímkem před/po). Původní popis: v místě, kde tělo tahu přechází do suchých vláken, vyčnívá ven malý hrot. Příčina: `obrys()` uzavírá obrys Catmull-Rom křivkou (`_bezier`) a v ostrém rohu (rovně useknutý konec těla, začátky vláken) křivka přestřelí ven. Ořez pásu vláken na 0–1 to NEřeší (vyzkoušeno). Řeší to nulová tečna v rozích se zatočením > 50° (ověřeno snímkem, kód v náhledovém skriptu ve scratchpadu, v repu zatím ne). Čeká na rozhodnutí uživatele spolu s variantami suchého konce.
- ~~Server asus-server je „asi bez internetu“ (uživatel 10. 10. před 19:26)~~ — **ověřeno logem cronu ve 20:59:** běh v 19:17 skončil chybou `fatal: unable to access 'https://github.com/LukasWana/LukasWana.git/': Could not resolve host: github.com`. Běh ve 20:17 už prošel („6 aktivních, 10 v archivu / pushnuto da767a0“). Výpadek DNS nebo sítě tedy trval nejvýš do 20:17 a cron se srovnal sám, bez zásahu. Před Taskem 6 stačí znovu pohled do logu (příkaz je v Předávce níže). **22:26: log ukázal běh 22:17 „pushnuto 7c28233“, cron jede.**
- ~~`W-ilustration-banner.png` (736 KB) zůstává v repu a dál se nasazuje, i když ho stránka nepoužívá.~~ — **10. 10. 22:39: smazán na pokyn uživatele** („2 smazat“). Z webu zmizel s nasazením run 38085643598 (`peaceiris/actions-gh-pages` bez `keep_files` cílové repo přepíše), ověřeno `curl` → 404.
- **10. 10. 23:42, pokyn uživatele „6 hlavních projektů rozděl na 3x3“:** `.projekty-grid` má nejvýš 3 sloupce (tentýž vzorec, který dosud měl jen archiv: `minmax(min(100%, max(340px, calc((100% - 60px) / 3))), 1fr)`). Předtím `minmax(260px, 1fr)` dávalo na desktopu 4 + 2. Archiv vzorec dědí. Test `test_hlavni_projekty_po_trech`, celkem 46 Python + 9 JS. Snímek 1400 px nad živými daty: 2 řady po 3. Výklad „3x3“ = 2 řady po 3 kartách (karet je 6). Commit `004090c` pushnut po „pushni“, Action run 38089255740 `success`, živé `style.css` ověřeno `curl` (`minmax(260px` 0×). Mobil po změně nesnímkován (vzorec je tentýž jako u archivu, `min(100%, …)` dává 1 sloupec).
- **11. 10. 00:07, pokyn uživatele „místo videa dej projekt jednotné přihlášení“:** v boxu Domácí server (`projekty.json`, `skupiny.asus-server-.aplikace`) nahrazena položka „Videa“ položkou „Jednotné přihlášení“ — „Jedno přihlášení otiskem prstu pro všechny moje aplikace, funguje i bez internetu“. Popis podle repa `asus-server-prihlaseni` (`plan-prihlaseni.md`: Pocket ID + oauth2-proxy, jen passkey, funguje bez internetu; HANDOFF 10. 10.: nasazeno). Repo `asus-server-videoyou` dál patří do skupiny (počítá se do dní práce), jen se nevypisuje. Commit `4e96b24` pushnut po „pushni a pusť synchronizaci hned“: generátor nanečisto OK, Action run 38091874136 `success`, pak (až po deployi, kvůli souběhu) ruční `sync.sh` na asus-serveru v 00:33:47 → `pushnuto f51ba23`. Živé `data/projekty.generated.json` ověřeno `curl`: „Jednotné přihlášení“ 1×, „Videa“ 0×.
- **11. 10. 07:16, pokyn uživatele „jeden responzivní režim na velké monitory, zvětší všechny prvky, od šířky 1920“:** na konci `style.css` `@media (min-width: 1920px) { html { zoom: 1.25; } }` — zvětší písmo, obrázky, mezery i mřížku najednou (kontejner 1200 → vizuálně 1500 px). Zvoleno místo přepočtu stovek px hodnot. `nadpis.js` beze změny: změřeno headless Chromem (stránka s měřicím skriptem, Range rects) — se zoomem nadpis 557 px na podtitul 553 px, bez zoomu 445 / 443, tedy stejný poměr, nadpis dál sedí. Vnitřní šířka 1888 → zoom 1, 1920 a 2560 → 1,25. Pozor při ověřování: headless `--window-size=1920` má uvnitř jen 1904 px (dotaz nesepne), na 1920 je třeba okno 1936. Test `test_zoom_od_1920`, 47 Python + 9 JS. Snímek 1920 px: 2 řady po 3, nic nepřetéká. Ověřeno jen v Chromu; Firefox má `zoom` podle mé znalosti od verze 126 — nedohledáno ani nezkoušeno. **Téhož rána na pokyn „sniž hranici na 1800px“:** `min-width: 1800px` (zapne se i v okně o něco užším než monitor 1920 — boční lišta, okraje). Změřeno: vnitřní šířka 1798 → zoom 1, 1800 a 1920 → 1,25, nadpis 557 / 553. Při 1800 má stránka po zoomu šířku 1440 CSS px (1800 / 1,25), kontejner 1200 se vejde (vizuálně 1500 px); snímek 1800 px (okno 1816) bez přetékání. Test přejmenován na `test_zoom_od_1800`.
- **11. 10. 08:15, pokyn uživatele „pro 4K udělej další zoom … mez už na 2800px“:** za pravidlem 1800 přidáno `@media (min-width: 2800px) { html { zoom: 2; } }`. Navrhl jsem 3600 / 2,5 (dvojnásobek kroku 1800 / 1,25), uživatel posunul hranici na 2800. Zoom jsem proto snížil na 2: se zoomem 2,5 by obsah (3 000 px) v okně 2800–3000 vyplnil celou šířku. Se zoomem 2 má obsah 2 400 px, tedy 86 % okna 2800 a 62 % okna 3840. Test `test_zoom_4k_od_2800` hlídá i pořadí pravidel (2800 za 1800). Celkem 48 Python + 9 JS. Snímky headless Chromem s `--hide-scrollbars` (pak má okno uvnitř plnou šířku, žádný odečet 16 px): 2799 → zoom 1,25, 2800 → zoom 2, 3840 → zoom 2. Nic nepřetéká, nadpis na snímku sedí, Range rects ale neměřeny. Při měřítku Windows 150 % hlásí 4K prohlížeči šířku 2560, takže se tam uplatní jen stupeň 1800. *(Commit `a6628bd`, nahrazeno stupni níže, pushnuto spolu s nimi.)*
- **11. 10. 08:22, pokyn uživatele „zoomovat až do 8K, aby obsah držel 75–85 % okna“:** dva stupně (1800 / 1,25 a 2800 / 2) nahradilo 15 stupňů od 1540 do 7200 px (`style.css` na konci). Hranice 1800 a 2800 od uživatele zůstaly, zoom se na nich změnil na 1,31 a 2,04. Na začátku stupně je podíl ≤ 85 % a těsně před dalším ≥ 75 %, takže je každý stupeň nejvýš o 13 % širší než předchozí. První model počítal s obsahem 1 200 px. **Měření snímků ukázalo 72,9 % na konci stupňů:** kontejner má padding 2 × 20, viditelný obsah (karty) má tedy 1 160 px. Přepočteno na 1 160. Testy: `TestVelkyMonitor` (3 testy místo `test_zoom_od_1800` a `test_zoom_4k_od_2800`) kontroluje podíl na obou koncích každého stupně, vzestupné pořadí, pokrytí 8K a hranice 1800/2800, celkem 49 Python + 9 JS. Mutační kontrola testu (zoom mimo pásmo nahoru i dolů, přehozené pořadí, chybějící stupeň, chybějící 8K, první hranice 1600, chybějící 1800): 7/7 mutací test chytil. **Ověřeno snímky headless Chromu** (krajní sloupce barvy karty #f6f5f2 / šířka okna): 1539 → 75,3 %, 1540 → 83,6 %, 1799 → 77,4 %, 1800 → 84,4 %, 1920 → 79,2 %, 2560 → 82,5 %, 2799 → 75,4 %, 2800 → 84,5 %, 3840 → 78,2 %, 5120 → 83,6 %, 7199 → 75,2 %, 7680 → 79,5 %. Snímek 8K zmenšený na 1/8: nic nepřetéká, nadpis sedí (Range rects neměřeny). Pod 1540 platí zoom 1 a podíl tam ze stupňů nevychází: od 1546 px dolů je nad 75 %, pod šířkou 1200 vyplní obsah celé okno. Firefox neověřen.
- **11. 10. 09:02, pokyn uživatele „stránka je moc strohá, použij barvy z původního banneru, nejdřív tři návrhy“:** návrh, náhledy A/B/C a volbu uživatele popisuje `docs/plans/2026-10-11-barvy-design.md`. Uživatel vybral banner z A (opar z rozostřených třpytek za ensō) a karty z C (každý hlavní projekt má svou barvu: bokeh v rohu a sloupce aktivity). Domácí server zůstává černobílý, starší projekty šedé. Při přiřazení barev uživatel prohodil Meditácie a whisper. Barva patří projektu (`projekty.json` → pole `barva`). `tools/projekty.py` (`PALETA`, `obarvi`) dá kartě bez barvy první volnou (8 barev = `max_aktivnich`), že se barvy v `projekty.json` neopakují, hlídá test. `projekty.js` přidá třídy `projekty-barevna barva-<název>`. Testy: 59 Python + 10 JS. Snímky v Chromu nad lokálními daty doplněnými funkcí `obarvi`: desktop 1440 a mobil 400 px podle návrhu, na mobilu žádný vodorovný přesah (scrollWidth 345 = clientWidth 345 v iframe 360).
- **11. 10. 09:45, pokyn uživatele „starší projekty udělej inverzně, ale všude použij místo čisté černé nějakou trošku staženou“:** inkoust `#1a1a1a` (běžná off-black, vybral jsem já). V CSS je to proměnná `--inkoust` v `:root`, nahradila 17 výskytů `#000`/`#000000`. V `tools/enso.py` je `INKOUST`, z něj se přegenerovaly `img/enso.svg` a `img/tah.svg`. Sloupce aktivity mají `fill="currentColor"` (`projekty.js`) a barvu dostávají z CSS (`.projekty-graf`, u barevných karet `rgb(var(--barva))`). 8 ručně kreslených ikon v `img/social/` dostalo `fill="#1a1a1a"` na kořenový `<svg>`: jejich tmavé tahy fill neměly, takže se kreslily výchozí černou. Kresba se nezměnila, jen přibyl atribut. Výjimky: maska oparu (`#000` tam znamená neprůhlednost) a stíny `rgba(0, 0, 0, …)`. Starší projekty: plocha v inkoustu, text `#f6f5f2`, popis `#d9d6cf`, jazyk a patička `#a19e97`, hover `#2b2b2b`, odkazy a fokus světlé. Testy `TestInkoust` (CSS a generátor mají stejnou hodnotu, nikde čistá černá, ikony v inkoustu) a `TestStarsiInverzne`, celkem 65 Python + 11 JS. Snímek 1440 × 3600 s rozbalenými staršími projekty: 0 pixelů `#000`, nic tmavšího než inkoust, ikony vypadají jako dřív.

**Pravidla prostředí:** kód, testy a texty se zpětným lomítkem zapisuj jen přes Write/Edit, nikdy heredocem ani `sed` (`~/.claude/rules/bash-heredoc-omezeni.md`). `index.html` má CRLF, `style.css` LF; Edit konce řádků zachová. Zprávy commitů piš přes Write do souboru ve scratchpadu a commituj s `git commit -F`. **Push do `main` = okamžitě živý web.** Proto se pushuje až v Tasku 6 po schválení snímků. Do té doby jen lokální commity.

Testy (bez `-I`, s ním spadne import pygments):
```
python -m pytest -q tests/
node --test tests/projekty_js.test.js
```
Výchozí stav: 28 Python + 9 JS zelených. Po dokončení: 43 Python + 9 JS.

## Předávka

Tuto sekci každá session na konci PŘEPÍŠE (ne připíše) — pravidlo `~/.claude/rules/konec-session.md`. Historie je v gitu.

```
Skills: žádný konkrétní — plán je dokončený. Na novou úpravu vzhledu superpowers:brainstorming (náhledy variant na skutečné stránce), na rozbitou věc superpowers:systematic-debugging.

Pracovní adresář: c:\work\graphic\LukasWana (repo LukasWana/LukasWana, větev main). Vše pushnuté, push = živý web.
Plán: docs/plans/2026-10-10-prezentace.md — HOTOVÝ (Stav nahoře), Tasky 1–7 pod touto sekcí jsou historie.
Návrh: docs/plans/2026-10-10-prezentace-design.md (implementováno, karty viz sekce Karty). Barvy z původního banneru: docs/plans/2026-10-11-barvy-design.md.
Předchozí plán (přehled projektů, hotový): docs/plans/2026-10-10-projekty.md. Jeho otevřený bod (5) je níže.
Paměť projektu: web-nasazeni.md (server, cron, souběh, nové pole v datech, ikony, ensō) a ps-roura-ssh-bom.md.

Stav k 11. 10. 2026, 09:08:
- Web https://lukaswana.github.io/web/ je živě ve vzhledu „prezentace“: hlavička Inter Tight + qwanap@gmail.com, banner s ensō, podtah štětcem pod nadpisem sekce, motto v patičce.
- Ensō má od commitu d158405 hodně suchý konec (varianta C, vybral uživatel nad náhledy A/A2/B/C). Opravený je i hrot v rozích obrysu (_bezier, nulová tečna v rozích), který měly ensō i podtah. Text banneru zůstal vedle kruhu (uživatel nerozhodl, ponechána doporučená varianta).
- W-ilustration-banner.png smazán (d965581, pokyn uživatele), na webu 404.
- Push po „pushni“, Action run 38085643598 success, živý web ověřen curl (enso.svg 31 967 B, tah.svg 9 772 B).
- Karty projektů: světlá plocha #f6f5f2 s oblými rohy 16 px, bez rámečku (rozhodnutí uživatele).
- Hlavní projekty (6 karet) jsou od 004090c nejvýš po 3 na řádek = 2 řady po 3 (pokyn „rozděl na 3x3“), dřív 4 + 2. Stejný vzorec jako archiv. Push po „pushni“, run 38089255740 success, živé CSS ověřeno curl.
- Box Domácí server: místo „Videa“ je „Jednotné přihlášení“ (4e96b24, popis z repa asus-server-prihlaseni). Pushnuto, synchronizace puštěna ručně po deployi, živá data ověřena curl.
- Velké monitory (pokyny uživatele 11. 10.): na konci style.css 15 stupňů zoomu od 1540 do 7200 px, obsah drží 75–85 % šířky okna až po 8K. Hranice 1800 a 2800 zadal uživatel (dříve stupně 1800 / 1,25 a 2800 / 2), zoom na nich je teď 1,31 a 2,04. Změřeno snímky v Chromu na 12 šířkách. Detail a čísla jsou ve Stavu nahoře. nadpis.js změřen při zoomu 1,25, vyšší stupně jen snímkem. Pushnuto po „pushni“ (4e0b484..6f0b8a6), Action run 38118066585 success, Pages build hotový, živé style.css ověřeno curl (15 stupňů). Firefox neověřen.
- Barvy z původního banneru (11. 10., docs/plans/2026-10-11-barvy-design.md): opar z rozostřených třpytek za ensō, hlavní karty mají každá jinou barvu (pole barva v projekty.json, PALETA a obarvi v tools/projekty.py). Domácí server zůstává černobílý, starší projekty šedé. Pushnuto po „pushni“ (a2fcefd..5774f16), Action run 38120224099 success. Po deployi ručně sync.sh v 09:06:29 (pushnuto 81b69b4), Pages build 81b69b4 hotový. Živá data ověřena curl: 6 karet, 6 různých barev podle projekty.json; box, archiv ani starší barvu nemají. Snímek živé stránky v čistém headless Chromu: barvy na kartách. Uživatel mezitím viděl karty šedé: otevřel stránku mezi deployem kódu a syncem dat. Kód a data se nasazují zvlášť.
- Testy: 59 Python + 10 JS zelených. tests/test_stranka.py hlídá kontrakt vzhledu, že img/*.svg = výstup tools/enso.py, roh obrysu bez přestřelu, 8 cest ensō (tělo + 7 vláken), mřížku po 3 (test_hlavni_projekty_po_trech) a stupně zoomu 75–85 % (TestVelkyMonitor), barvy palety a opar (TestBarvyBanneru). tests/test_projekty.py třída Barvy hlídá unikátnost a přiřazení v projekty.json.
- Další práce není zadaná. Nic nedělat bez pokynu uživatele.

Otevřené (čeká na rozhodnutí uživatele):
- (5) Token na GitHub API (~/.config/lukaswana-web/token na asus-server) platí do 2027-01-08. Po vypršení cron padá s tracebackem a na webu stojí datum „Aktualizováno“. Tři varianty řešení jsou v docs/plans/2026-10-10-projekty.md, bod (5). Uživatel: „zatím neřeším“.
- Text banneru pod kruhem i na desktopu: náhled ukázán 10. 10., uživatel nevybral. Kdyby chtěl: v .enso-banner flex-direction: column + text-align: center (jako v @media pro mobil).

Užitečné příkazy:
- Testy: python -m pytest -q tests/ (BEZ -I, s ním spadne na importu pygments) a node --test tests/projekty_js.test.js
- Log cronu: ssh asus-server 'tail -n 12 ~/.local/state/lukaswana-web/sync.log | cut -c1-200'
- Náhled: data z webu do data/projekty.generated.json (gitignored), python -m http.server 8790 --bind 127.0.0.1 (ne 8765 — API EmailRatoru). Snímky headless Chromem, mobil přes iframe 400 px (Task 6 Step 3; --window-size=400 dá ve skutečnosti ~500 px). Desktop: okno má uvnitř o 16 px méně (--window-size=1936 → 1920), na hranici zoomu 1800 tedy okno 1816. S --hide-scrollbars odečet neplatí (okno 2800 = uvnitř 2800). Podíl obsahu na šířce okna: snímek s výškou ~1100 × zoom, v dolních 40 % hledat krajní sloupce barvy karty (246, 245, 242) a vydělit šířkou okna. Měření nadpisu se zoomem: kopie index.html do data/ s <base href="/"> a skriptem, který po 1,5 s vypíše Range rects nadpisu a podtitulu, číst přes --dump-dom.
- Varianty vzhledu k porovnání: kopie index.html do data/var-X.html s <base href="/"> a přepisem CSS v <style> — repo zůstane čisté. Varianty tahu: skript, který importuje tools/enso.py a zapíše SVG do data/. Detail tahu snímkuj s --force-device-scale-factor=2 (v 1× se hrot v rohu obrysu přehlédl).

Důležité:
- Push do main = hned živý web. Pushovat jen po výslovném schválení uživatele.
- Po pushi změny tools/projekty.py nebo projekty.json: počkej na deploy, pusť ručně sync.sh (příkaz v paměti web-nasazeni), počkej na Pages build commitu ze syncu a ověř živá data curl s ?v=$RANDOM. Jinak je nový kód živě bez nových dat až do dalšího běhu cronu v :17 (11. 10. to uživatel nahlásil jako chybu).
- Repo LukasWana/web je výstup nasazení. NEMAZAT, ručně neupravovat.
- Token nikdy do chatu a nikdy do souboru rourou z PowerShellu.
- Kód a texty se zpětným lomítkem piš jen přes Write/Edit. Zprávy commitů piš do souboru přes Write a commituj s git commit -F.
- img/enso.svg a img/tah.svg se ručně neupravují, mění se parametry v tools/enso.py (test to hlídá).
- Pravidlo každé session (~/.claude/rules/konec-session.md): dokumentaci aktualizuj průběžně, na konci přepiš tuto sekci a commitni, před „hotovo“ udělej kontrolu do nuly.
```

---

### Task 1: Generátor tahů štětcem `tools/enso.py`

**Files:**
- Create: `tools/enso.py`, `img/enso.svg`, `img/tah.svg` (výstup generátoru)
- Create: `tests/test_stranka.py`

**Step 1: Failing test** — `tests/test_stranka.py` (celý soubor, další tasky do něj přidávají třídy):
```python
"""Kontrakt vzhledu webu podle docs/plans/2026-10-10-prezentace-design.md.

Čte index.html, style.css a img/*.svg jako text — vzhled se ověřuje snímkem, tady jen to,
co se dá říct jistě: co na stránce být má a co z ní zmizelo.
"""
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOREN / "tools"))
import enso  # noqa: E402


def text(cesta):
    return (KOREN / cesta).read_text(encoding="utf-8")


def pravidla(css, selektor):
    """Těla všech CSS pravidel, jejichž seznam selektorů obsahuje `selektor` (i uvnitř @media)."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    tela = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        selektory = [s.strip() for s in m.group(1).split(",")]
        if selektor in selektory:
            tela.append(m.group(2))
    return tela


class TestEnso(unittest.TestCase):
    def test_soubory_odpovidaji_generatoru(self):
        # img/*.svg se needitují ručně: musí být přesně výstupem tools/enso.py
        self.assertEqual(text("img/enso.svg"), enso.svg(enso.enso(400), 400, 400))
        self.assertEqual(text("img/tah.svg"), enso.svg(enso.podtah(240, 24), 240, 24))

    def test_generator_je_deterministicky(self):
        self.assertEqual(enso.enso(400), enso.enso(400))

    def test_platne_svg_cerny_inkoust(self):
        for cesta, viewbox in (("img/enso.svg", "0 0 400 400"), ("img/tah.svg", "0 0 240 24")):
            koren = ET.fromstring(text(cesta))
            self.assertEqual(koren.get("viewBox"), viewbox, cesta)
            ns = "{http://www.w3.org/2000/svg}"
            self.assertEqual(koren.find(ns + "g").get("fill"), "#000", cesta)
            cesty = koren.findall(f".//{ns}path")
            self.assertGreaterEqual(len(cesty), 4, cesta)  # tělo + aspoň 3 vlákna suchého konce
            for p in cesty:
                self.assertTrue(p.get("d").startswith("M") and p.get("d").endswith("Z"), cesta)

    def test_bez_filtru(self):
        # návrh: tah je kreslený obrys, ne roztřesení filtrem
        for cesta in ("img/enso.svg", "img/tah.svg"):
            self.assertNotIn("filter", text(cesta))
            self.assertNotIn("stroke", text(cesta))


if __name__ == "__main__":
    unittest.main()
```

**Step 2:** `python -m pytest -q tests/test_stranka.py` → FAIL (`ModuleNotFoundError: No module named 'enso'`).

**Step 3:** `tools/enso.py` — přesně tento kód (odzkoušený ve scratchpadu 10. 10.):
```python
"""Generátor inkoustových tahů štětcem (ensō a podtah) jako SVG s vyplněným obrysem.

Tah = středová křivka c(t) a šířka w(t), t ∈ [0, 1]. Obrys = levý okraj tam, pravý zpět,
převedený Catmull-Rom → kubické Bézierovy křivky. Suchý konec štětce = vlákna: na začátku
dojezdu společně pokrývají celou šířku tahu, pak se každé zužuje ke svému středu a končí
jinde, takže mezi nimi postupně prosvítá papír. Bez náhody — výstup je deterministický.

Použití: python tools/enso.py   → zapíše img/enso.svg a img/tah.svg
"""
import math
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent


def _f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def _bezier(body):
    """Uzavřená Catmull-Rom křivka přes body → SVG path z kubických Bézierových segmentů."""
    n = len(body)
    d = [f"M{_f(body[0][0])} {_f(body[0][1])}"]
    for i in range(n):
        p0, p1, p2, p3 = body[i - 1], body[i], body[(i + 1) % n], body[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(p2[0])} {_f(p2[1])}")
    return "".join(d) + "Z"


def _hladka(t, a, b):
    """Hladký přechod 0 → 1 mezi a a b (smoothstep)."""
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    u = (t - a) / (b - a)
    return u * u * (3 - 2 * u)


def obrys(stred, sirka, t0, t1, vzorku, pas=lambda t: (0.0, 1.0), cepicka=False):
    """Vyplněný obrys tahu mezi t0 a t1.

    stred(t) → (x, y); sirka(t) → šířka těla v px; pas(t) → (od, do), zlomky šířky těla
    (0 = levý okraj, 1 = pravý), které tento obrys pokrývá — celé tělo je (0, 1), vlákno užší pás.
    cepicka=True přidá na začátek kulaté nasazení štětce (půlkruh za bodem t0).
    """
    levy, pravy = [], []
    for i in range(vzorku + 1):
        t = t0 + (t1 - t0) * i / vzorku
        x, y = stred(t)
        (xa, ya), (xb, yb) = stred(max(0.0, t - 1e-4)), stred(min(1.0, t + 1e-4))
        delka = math.hypot(xb - xa, yb - ya) or 1.0
        nx, ny = -(yb - ya) / delka, (xb - xa) / delka
        w = sirka(t)
        od, do = pas(t)
        levy.append((x + nx * (od - 0.5) * w, y + ny * (od - 0.5) * w))
        pravy.append((x + nx * (do - 0.5) * w, y + ny * (do - 0.5) * w))
    body = levy + pravy[::-1]
    if cepicka:
        x, y = stred(t0)
        (xa, ya), (xb, yb) = stred(t0), stred(t0 + 1e-4)
        delka = math.hypot(xb - xa, yb - ya) or 1.0
        tx, ty = (xb - xa) / delka, (yb - ya) / delka  # směr tahu
        r = sirka(t0) / 2
        zacatek_uhlu = math.atan2(tx, -ty)  # normála k pravému okraji; +π vede přes zadní stranu k levému
        for k in range(1, 8):
            u = zacatek_uhlu + math.pi * k / 8
            body.append((x + r * math.cos(u) - tx * r * 0.3 * math.sin(math.pi * k / 8),
                         y + r * math.sin(u) - ty * r * 0.3 * math.sin(math.pi * k / 8)))
    return _bezier(body)


def _vlakna(stred, sirka, zacatek, specifikace, vzorku):
    """Suché vlákno: (střed pásu, výsledná šířka pásu, kde skončí). Na začátku pokrývají celou šířku."""
    cesty = []
    n = len(specifikace)
    for k, (m, h_konec, konec) in enumerate(specifikace):
        h0 = 0.5 / n + 0.06  # překryv sousedů na začátku dojezdu → žádná náhlá mezera
        m0 = (k + 0.5) / n

        def pas(t, m=m, m0=m0, h0=h0, h_konec=h_konec, konec=konec):
            u = _hladka(t, zacatek, konec)
            stred_pasu = m0 + (m - m0) * u
            pul = h0 + (h_konec / 2 - h0) * min(1.0, u * 1.6)
            pul *= 1 - u ** 3  # na konci se vlákno ztratí do nuly
            return stred_pasu - pul, stred_pasu + pul

        cesty.append(obrys(stred, sirka, zacatek, konec, vzorku, pas))
    return cesty


def enso(velikost=400):
    """Ensō: kruh jedním tahem; nasazení vlevo, tah po směru hodin, mezera a suchý konec vlevo dole."""
    s = velikost
    cx, cy, R = s / 2, s / 2, s * 0.37
    zacatek, oblouk = math.radians(195), math.radians(318)
    W = s * 0.072

    def stred(t):
        uhel = zacatek - oblouk * t
        r = R * (1 + 0.03 * math.sin(2 * math.pi * (0.85 * t + 0.1)) - 0.035 * t)
        return cx + r * math.cos(uhel), cy - r * math.sin(uhel)

    def sirka(t):
        nasazeni = 0.75 + 0.55 * _hladka(t, 0.0, 0.05) - 0.3 * _hladka(t, 0.05, 0.22)
        dech = 1 + 0.1 * math.sin(2 * math.pi * (1.3 * t + 0.35))
        dojezd = 1 - 0.35 * _hladka(t, 0.5, 0.95)
        return W * nasazeni * dech * dojezd

    zacatek_suche = 0.8
    cesty = [obrys(stred, sirka, 0.0, zacatek_suche + 0.01, 100, cepicka=True)]
    cesty += _vlakna(stred, sirka, zacatek_suche,
                     [(0.08, 0.1, 0.99), (0.33, 0.16, 0.95), (0.55, 0.08, 1.0), (0.8, 0.14, 0.9)], 40)
    return cesty


def podtah(sirka_px=240, vyska_px=24):
    """Krátký vodorovný tah pod nadpis: mírný oblouk, nasazení vlevo, suchý konec vpravo."""
    W = vyska_px * 0.4

    def stred(t):
        return sirka_px * (0.04 + 0.92 * t), vyska_px * (0.56 - 0.16 * math.sin(math.pi * t))

    def sirka(t):
        return W * (0.8 + 0.3 * _hladka(t, 0.0, 0.06) - 0.45 * _hladka(t, 0.45, 0.95))

    cesty = [obrys(stred, sirka, 0.0, 0.79, 60, cepicka=True)]
    cesty += _vlakna(stred, sirka, 0.78, [(0.12, 0.14, 0.97), (0.5, 0.12, 1.0), (0.85, 0.16, 0.92)], 30)
    return cesty


def svg(cesty, sirka_px, vyska_px):
    d = "".join(f'<path d="{c}"/>' for c in cesty)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sirka_px} {vyska_px}">'
            f'<g fill="#000">{d}</g></svg>\n')


def main():
    (KOREN / "img").mkdir(exist_ok=True)
    for jmeno, obsah in (("img/enso.svg", svg(enso(400), 400, 400)),
                         ("img/tah.svg", svg(podtah(240, 24), 240, 24))):
        with open(KOREN / jmeno, "w", encoding="utf-8", newline="\n") as f:
            f.write(obsah)
        print(f"zapsáno {jmeno}: {len(obsah)} B")


if __name__ == "__main__":
    main()
```
Pozn.: ve scratchpadu ležel prototyp v `…/scratchpad/proto/tools/enso.py`. Scratchpad je vázaný na session, proto platí kód výše, ne ten soubor.

**Step 4:** `python tools/enso.py` → `zapsáno img/enso.svg: 18453 B`, `zapsáno img/tah.svg: 9755 B`.

**Step 5:** `python -m pytest -q tests/` → všechno zelené (28 + 4 nové = 32).

**Step 6:** Commit (lokálně, bez push): `tools/enso.py`, `img/enso.svg`, `img/tah.svg`, `tests/test_stranka.py` — „ensō: generátor tahů štětcem a test kontraktu stránky“.

---

### Task 2: Písmo Inter Tight a hlavička s kontaktem

**Files:** Modify: `index.html:1-17`, `style.css:7-58`, `tests/test_stranka.py`

**Step 1: Failing testy** — přidat do `tests/test_stranka.py` (před `if __name__`):
```python
class TestHlavicka(unittest.TestCase):
    def setUp(self):
        self.html = text("index.html")
        self.css = text("style.css")

    def test_pismo_se_opravdu_nacita(self):
        self.assertIn("https://fonts.googleapis.com/css2?family=Inter+Tight", self.html)
        self.assertIn("display=swap", self.html)
        telo = pravidla(self.css, "body")[0]
        self.assertIn("font-family: 'Inter Tight'", telo)

    def test_kontakt_v_hlavicce(self):
        hlavicka = self.html.split('<header class="header">')[1].split("</header>")[0]
        self.assertIn('href="mailto:qwanap@gmail.com"', hlavicka)
        self.assertIn(">qwanap@gmail.com</a>", hlavicka)  # adresa je vidět jako text

    def test_podtitul_zkraceny(self):
        self.assertIn('<p class="subtitle">vibecoder · rychlé prototypy · technická řešení</p>', self.html)

    def test_pryc_cara_a_tagline(self):
        self.assertNotIn('class="divider"', self.html)
        self.assertNotIn('class="tagline"', self.html)
        self.assertEqual(pravidla(self.css, ".divider"), [])
        self.assertEqual(pravidla(self.css, ".tagline"), [])
```

**Step 2:** `python -m pytest -q tests/test_stranka.py` → 4 FAIL.

**Step 3: `index.html`** — do `<head>` za `<meta name="viewport" …>`:
```html
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;600;700&display=swap">
```
(API css2 vrací `@font-face` pro každou podmnožinu s vlastním `unicode-range`, takže latin-ext s českou diakritikou se stáhne sám, když je na stránce potřeba.)

Hlavičku nahradit:
```html
        <header class="header">
            <h1 class="main-title">Lukáš Wana</h1>
            <p class="subtitle">vibecoder · rychlé prototypy · technická řešení</p>
            <a class="kontakt" href="mailto:qwanap@gmail.com">qwanap@gmail.com</a>
        </header>
```

**Step 4: `style.css`**
- `body`: `font-family: 'Inter Tight', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;`
- `.subtitle`: `font-size: 22px; color: #333; margin-bottom: 14px; font-weight: 300;`
- Smazat celá pravidla `.divider` a `.tagline`.
- Přidat za `.subtitle`:
```css
.kontakt {
    font-size: 16px;
    color: #000;
    text-decoration: none;
    border-bottom: 1px solid currentColor;
    padding-bottom: 1px;
}

.kontakt:hover {
    border-bottom-color: transparent;
}
```
(Tohle podtržení odkazu není „zbytečná čára“, ukazuje, že na adresu jde kliknout. Pokud bude na náhledu rušit, nahradí se `text-decoration: underline`.)

**Step 5:** Testy → zelené. **Step 6:** Commit „hlavička: Inter Tight, kratší podtitul, kontakt; pryč čára a tagline“.

---

### Task 3: Banner s ensō místo třpytivé fotky

**Files:** Modify: `index.html:19-25`, `style.css` (pravidla `.hero-image` … `.hero-subtext`, `@media`), `tests/test_stranka.py`

**Step 1: Failing testy:**
```python
class TestBanner(unittest.TestCase):
    def setUp(self):
        self.html = text("index.html")
        self.css = text("style.css")

    def test_enso_v_banneru(self):
        banner = self.html.split('<section class="enso-banner">')[1].split("</section>")[0]
        self.assertIn('src="img/enso.svg"', banner)
        self.assertIn("<h2>Deep work creator</h2>", banner)
        self.assertIn("introvertní technicko-kreativní tvůrce", banner)
```
Pravidla `.hero-*` v CSS zatím zůstanou, protože je do Tasku 5 používá spodní banner. Test, že zmizela, je v Tasku 5.

**Step 2:** `python -m pytest -q tests/test_stranka.py` → 1 FAIL (`test_enso_v_banneru`).

**Step 3: `index.html`** — horní `<section class="hero-image">…</section>` **i s komentářem `<!-- Hero Image Section -->` nad ním** nahradit:
```html
        <!-- Banner: ensō (img/enso.svg z tools/enso.py) -->
        <section class="enso-banner">
            <img class="enso" src="img/enso.svg" alt="" width="400" height="400">
            <div class="enso-text">
                <h2>Deep work creator</h2>
                <p>introvertní technicko-kreativní tvůrce</p>
            </div>
        </section>
```

**Step 4: `style.css`** — přidat za pravidla hlavičky:
```css
/* Banner: jeden tah štětcem, žádný rámeček */
.enso-banner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 48px;
    margin: 56px 0 80px;
}

.enso {
    width: 300px;
    max-width: 70vw;
    height: auto;
}

.enso-text h2 {
    font-size: 44px;
    font-weight: 600;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 8px;
}

.enso-text p {
    font-size: 18px;
    color: #555;
}
```
a do `@media (max-width: 768px)`:
```css
    .enso-banner {
        flex-direction: column;
        gap: 24px;
        text-align: center;
        margin: 40px 0 56px;
    }

    .enso {
        width: 220px;
    }

    .enso-text h2 {
        font-size: 32px;
    }
```

**Step 5:** Testy → zelené. **Step 6:** Commit „banner: ensō místo třpytivé fotky“.

---

### Task 4: Pryč čáry, podtah pod nadpisem sekce

**Files:** Modify: `style.css` (`.section-title`, `.projekty-karta`, `.projekty-karta footer`, `.projekty-aplikace li`, `.projekty-archiv`, `.projekty-archiv .projekty-karta`), `tests/test_stranka.py`

**Step 1: Failing testy:**
```python
class TestBezCar(unittest.TestCase):
    def setUp(self):
        self.css = text("style.css")

    def test_zrusene_cary(self):
        for sel in (".section-title", ".projekty-karta footer", ".projekty-aplikace li", ".projekty-archiv"):
            for telo in pravidla(self.css, sel):
                self.assertNotRegex(telo, r"border(-top|-bottom)?\s*:", sel)

    def test_podtah_pod_nadpisem(self):
        tela = pravidla(self.css, ".section-title::after")
        self.assertEqual(len(tela), 1)
        self.assertIn("url('img/tah.svg')", tela[0])

    def test_nadpis_sekce_bez_verzalek(self):
        telo = pravidla(self.css, ".section-title")[0]
        self.assertNotIn("uppercase", telo)
```

**Step 2:** → 3 FAIL.

**Step 3: `style.css`:**
- `.section-title` nahradit:
```css
.section-title {
    font-size: 32px;
    font-weight: 600;
    letter-spacing: -0.01em;
    text-align: center;
    margin-bottom: 48px;
}

/* Podtah stejným štětcem jako ensō (img/tah.svg z tools/enso.py) místo černé čáry */
.section-title::after {
    content: '';
    display: block;
    width: 120px;
    height: 12px;
    margin: 10px auto 0;
    background: url('img/tah.svg') center / contain no-repeat;
}
```
- V `@media` u `.section-title` smazat `letter-spacing: 2px;` (zůstane `font-size: 24px`).
- `.projekty-karta`: `border: 1px solid #d6d6d6;` (místo `#000`).
- Druhé pravidlo `.projekty-karta footer` (s `margin-top: auto`): smazat `border-top` a `padding-top` nahradit `padding-top: 4px;`.
- `.projekty-aplikace li`: smazat `border-top` a `padding-top`. Aplikace oddělí mezera mřížky (`gap: 20px 30px`), na náhledu případně zvětšit na `28px 30px`.
- `.projekty-archiv`: smazat `border-top` a `padding-top`, `margin-top` nechat 40px.
- `.projekty-archiv .projekty-karta`: `border-color: #e6e6e6;` (dál světlejší než aktivní karty).

**Step 4:** Testy → zelené. Zkontrolovat, že grafy aktivity zůstaly: JS testy `node --test tests/projekty_js.test.js` → 9 zelených.

**Step 5:** Commit „projekty: pryč čáry, světlejší rámečky, podtah štětcem pod nadpisem“.

---

### Task 5: Patička — věta místo spodního banneru

**Files:** Modify: `index.html:247-253`, `style.css` (smazat zbylá pravidla `.hero-*`, `.glitter-overlay`, `.bottom-hero` a jejich řádky v `@media`), `tests/test_stranka.py`

**Step 1: Failing test:**
```python
class TestPaticka(unittest.TestCase):
    def test_veta_misto_banneru(self):
        html = text("index.html")
        self.assertIn('<p class="motto">Kvalitní práce v klidu — bez tlaku, bez stresu, bez přetvářky.</p>', html)
        self.assertNotIn("KVALITNÍ PRÁCE V KLIDU", html)

    def test_trpytiva_fotka_pryc(self):
        html, css = text("index.html"), text("style.css")
        self.assertNotIn("W-ilustration-banner.png", css)
        self.assertNotIn("hero-image", html)
        self.assertNotIn("glitter-overlay", html)
        for sel in (".hero-image", ".hero-image::before", ".glitter-overlay", ".hero-text", ".hero-subtext", ".bottom-hero"):
            self.assertEqual(pravidla(css, sel), [], sel)
```

**Step 2:** → 2 FAIL.

**Step 3: `index.html`** — spodní `<section class="hero-image bottom-hero">…</section>` **i s komentářem `<!-- Bottom Hero Image -->` nad ním** nahradit:
```html
        <!-- Motto: jedna věta s malým tahem štětce (img/tah.svg) -->
        <p class="motto">Kvalitní práce v klidu — bez tlaku, bez stresu, bez přetvářky.</p>
```

**Step 4: `style.css`** — smazat pravidla `.hero-image`, `.hero-image::before`, `.glitter-overlay`, `.hero-text`, `.hero-subtext`, `.bottom-hero`, jejich komentáře `/* Hero Image Sections */` a `/* Bottom Hero */` a v `@media` bloky `.hero-text`, `.hero-subtext`, `.hero-image`. Přidat:
```css
.motto {
    text-align: center;
    font-size: 18px;
    color: #333;
    margin: 24px 0 40px;
}

.motto::before {
    content: '';
    display: block;
    width: 72px;
    height: 8px;
    margin: 0 auto 14px;
    background: url('img/tah.svg') center / contain no-repeat;
}
```

**Step 5:** `python -m pytest -q tests/` → vše zelené, `node --test tests/projekty_js.test.js` → 9 zelených. Kontrola, že v CSS nezůstal mrtvý selektor: `grep -ni "hero\|glitter\|divider\|tagline" style.css index.html` → nic (`-i` kvůli komentářům „Hero“).

**Step 6:** Commit „patička: motto místo třpytivého banneru“.

---

### Task 6: Náhled, schválení uživatelem, push

**Step 1: Data pro náhled.** `data/` je v `.gitignore`, takže živá data stáhni z webu:
`mkdir -p data && curl -s -o data/projekty.generated.json https://lukaswana.github.io/web/data/projekty.generated.json`

**Step 2: Server** na jiném portu než 8765 (ten drží API EmailRatoru), na pozadí:
`python -m http.server 8790 --bind 127.0.0.1` (z kořene repa, `run_in_background`).

**Step 3: Snímky** headless Chromem do scratchpadu. Plné výšky stránky jsou 3200 px u desktopu a 4200 px u mobilu (bílá plocha pod obsahem je jen výška okna, ne vada).

**Pozor, ověřeno 10. 10.:** `--window-size=400,…` NEDÁ 400 px. Headless Chrome na Windows má minimální šířku okna, stránka se vykreslí asi na 500 px a snímek se vpravo ořízne. Na živém webu to ukázalo useknuté „LUKÁŠ WAN“, tedy falešnou chybu mobilu. Mobil proto snímej přes obal s `<iframe>` širokým přesně 400 px. Obal zapiš přes Write do `<scratchpad>/mobil.html`:
```html
<!doctype html><body style="margin:0"><iframe src="http://127.0.0.1:8790/" width="400" height="4200" style="border:0;display:block"></iframe></body>
```
```
"C:/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --hide-scrollbars --virtual-time-budget=8000 --screenshot=<scratchpad>/n1280.png --window-size=1280,3200 http://127.0.0.1:8790/
"C:/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --hide-scrollbars --virtual-time-budget=8000 --screenshot=<scratchpad>/n400.png --window-size=600,4200 "file:///<scratchpad>/mobil.html"
```
`--virtual-time-budget` počká na písmo a `projekty.js`. Snímky prohlédni nástrojem Read. U mobilu je napravo od iframe bílý pruh široký 200 px, to je jen okno.

**Step 4: Kontrola nad snímky:**
- ensō ostré, suchý konec čitelný i v 220 px na mobilu,
- jméno vyplňuje šířku podtitulu (`nadpis.js`) a není menší než ~48 px na desktopu, jinak zvětši `.subtitle`,
- na stránce není žádná šedá ani černá vodorovná čára kromě podtržení e-mailu,
- karty, grafy aktivity, box Domácí server a „Starší projekty (N)“ fungují jako dřív,
- písmo je Inter Tight (ne Arial), diakritika „Lukáš“, „přetvářky“ je ve stejném písmu.

**Step 5: Ukázat oba snímky uživateli** (cesty k PNG + krátký popis) a počkat na **výslovné schválení**. Úpravy podle připomínek dělej v `tools/enso.py` (parametry) nebo v CSS, po každé změně generátoru spusť `python tools/enso.py` a testy.

**Step 6: Po schválení:** zastavit server (TaskStop), `rm -r data` (je jen náhled, ignorovaný gitem), `git push`. Ověřit, že GitHub Action doběhla (`gh run list -R LukasWana/LukasWana -L 1` → `success`) a web vrací 200 s novým obsahem: `curl -s https://lukaswana.github.io/web/ | grep -c 'enso-banner'` → 1. Push kolem :17 se potká s cronem. Oprava v `sync.sh` to ustojí, ale v logu pak bude řádek o odmítnutém pushi.

---

### Task 7: Dokumentace

- `docs/plans/2026-10-10-prezentace-design.md`: stav → „implementováno <datum>, commit <hash>“, odchylky 1–4 z tohoto plánu.
- `docs/plans/2026-10-10-projekty.md`: bod (6) v „Otevřené“ přeškrtnout s odkazem na tento plán.
- Paměť `web-nasazeni.md` (`C:\Users\WANA\.claude\projects\C--work-projects-LukasWana\memory\`): jedna věta o tom, že `img/enso.svg` a `img/tah.svg` se generují příkazem `python tools/enso.py` a ručně se neupravují.
- Stav a předávka tohoto plánu podle `~/.claude/rules/konec-session.md`.
