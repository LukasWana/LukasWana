# Web jako prezentace: ensō a jeden tah štětcem (návrh)

Datum: 2026-10-10 · Stav: **návrh schválený uživatelem („uprav plán“), neimplementováno**
Repo: `c:/work/graphic/LukasWana` (zdroj webu https://lukaswana.github.io/web/, nasazení viz paměť `web-nasazeni.md`).

## Zadání uživatele

„Udělat z toho profesionální prezentaci, drž se jednoduchosti, odstraň zbytečné linky a slaď nějak vršek
s ručně kreslenými ikonami od sociálních sítí, bude kreativní, výsledek musí vypadat jednoduše a profesionálně.“

Rozhodnutí v brainstormingu:
1. Vršek: **ruční kresba v banneru** (ne jen tah pod jménem, ne ikony nahoru).
2. Kresbu **nakreslí Claude v SVG** (ne dodá uživatel, ne jen ručně psaný nápis).
3. První verze návrhu (fixové písmo, roztřesení filtrem `feTurbulence`, motivy tužka/sluchátka/monitor)
   byla na otázku uživatele „je to nejlepší možný plán?“ **zamítnuta sebekritikou**: tři styly najednou,
   motivy působí jako klipart, roztřesení filtrem je napodobenina tahu štětcem vedle skutečných ikon.
   Uživatel pak řekl „uprav plán“ → platí verze níže.

## Myšlenka

Bílá stránka, jméno, **jeden výrazný tah štětcem** a pak práce. Ručně kreslené je jen inkoust, všechno
ostatní je čistá typografie.

**Ensō** (zenový kruh jedním tahem štětce) je z rodiny inkoustových koleček kolem ikon v patičce
(`img/social/*.svg`) a nese obsah: soustředění = „deep work“, klid = „kvalitní práce v klidu“, a sedí
k meditačním aplikacím v projektech.

## Části stránky

### Hlavička
- Jméno **Lukáš Wana** velké, jedním písmem (viz Typografie). `nadpis.js` (jméno na šířku podtitulu) zůstává.
- Podtitul zkrácen: „vibecoder · rychlé prototypy · technická řešení“ (místo pomlček a „hezky a funkčně“).
- **Pryč:** šedá čára `.divider`, tagline „KREATIVNÍ PROFESIONÁL, KTERÝ DĚLÁ KVALITNÍ A MODERNÍ PRÁCI“
  (výplň, opakuje banner).
- **Kontakt — OTEVŘENÉ:** profesionální prezentace potřebuje jasnou cestu, jak oslovit. Návrh: e-mail jako
  jediný výrazný odkaz v hlavičce. **Uživatel zatím neřekl, jaký e-mail (nebo žádný).** Do rozhodnutí se
  kontakt nepřidává; implementace na to musí počkat nebo ho vynechat.

### Banner (místo třpytivé fotky)
- Bílá plocha, žádný rámeček boxu. Velké **ensō** jako inline SVG: jeden tah s proměnlivou šířkou
  (výplň obrysu, ne `stroke`), nasazení a „suchý“ konec štětce (2–3 tenké vlákna na konci, mezera
  v kruhu), černá `#000` jako ikony.
- Tah se kreslí ručně jako cesta (obrys z Bézierových křivek), **ne filtrem** `feTurbulence`/`feDisplacementMap`.
- Text uvnitř nebo vedle kruhu, čistě vysázený: **Deep work creator**, pod ním „introvertní
  technicko-kreativní tvůrce“.
- `W-ilustration-banner.png` (třpytivá fotka) se přestane používat. Soubor zůstává v repu, dokud uživatel
  neřekne jinak (smazání je mimo zadání).
- Mobil: kruh se zmenší a text jde pod něj, kdyby se dovnitř nevešel.

### Na čem pracuju
- Nadpis bez silné černé čáry (`border-bottom: 2px` v `style.css` ~ř. 221). Místo ní krátký ručně
  kreslený podtah stejným štětcem (malé inline SVG).
- Karty: rámeček tenčí a světlejší (nebo jen světlé pozadí — rozhodne se nanečisto podle náhledu).
  Pryč šedá čára nad „naposledy …“. Grafy aktivity zůstávají.
- Box Domácí server: pryč čáry mezi aplikacemi; oddělí je mezera.
- Pryč šedá čára nad „Starší projekty (N)“.
- Sekce odděluje bílé místo, ne čáry.
- Selektory zrušených čar (`style.css`, stav `bebc809`): `.divider` (ř. 44), `.section-title` `border-bottom`
  (ř. 221), `.projekty-karta footer` `border-top` (ř. 597), `.projekty-aplikace li` `border-top` (ř. 632),
  `.projekty-archiv` `border-top` (ř. 650).

### Patička
- Ikony sociálních sítí beze změny.
- Spodní třpytivý banner „KVALITNÍ PRÁCE V KLIDU“ nahradí **jedna věta bez rámečku**:
  „Kvalitní práce v klidu — bez tlaku, bez stresu, bez přetvářky.“ s malým tahem štětce (druhý velký
  banner by ensō nahoře zdvojoval).
- Pozn.: velká bílá plocha pod stránkou na snímku z 10. 10. byla jen výška okna headless Chrome
  (3200 px), ne vada stránky.

## Typografie
- **Jedno písmo na celý web**, 2–3 velikosti. `style.css:8` deklaruje `'Inter'`, ale žádný `<link>` ho
  nenačítá → dnes se ve skutečnosti kreslí Arial. Návrh: načíst *Inter Tight* (nebo *Inter*) z Google Fonts
  s `latin-ext` (česká diakritika), `display=swap`.
- **Žádné ručně psané písmo.** Ruční je jen inkoust.
- Méně verzálek s širokým prostrkáním (dnes tagline, hero, nadpis sekce) — zůstat jen tam, kde nesou
  hierarchii.

## Co se nemění
- Data a skripty přehledu projektů (`projekty.js`, `tools/`, `data/`, cron na asus-server), struktura karet.
- Skrytý `div.stary-obsah` (starý obsah, `hidden`) — mimo zadání, nesahá se na něj.
- Nasazení: push do `main` → Action do repa web.

## Ověření
- Testy beze změny musí projít: `python -m pytest -q tests/` (bez `-I`) a `node --test tests/projekty_js.test.js`.
  Testy na `index.html`/`style.css` nezávisí (jen `test_sync.py` vytváří vlastní `index.html`).
- Vzhled: lokální náhled (`python -m http.server` na jiném portu než 8765) + headless Chrome snímky
  v šířce 1280 a 400 px (`chrome --headless=new --screenshot`), se skutečnými daty z repa web.
- Kontrola, že na stránce nezůstala žádná ze zrušených čar (výčet výše) a že ensō je ostré a čitelné
  na mobilu.
- Uživatel schvaluje vzhled podle snímku **před** pushem do `main` (push = okamžitě živý web).
