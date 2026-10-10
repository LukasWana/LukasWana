# Přehled projektů na webu — návrh

Datum: 2026-10-10 · Stav: implementováno 2026-10-10 (Tasky 0–10, viz plán) · plán: `2026-10-10-projekty.md`

> **Revize 2026-10-10 (kontrola před předáním; platí přednostně před textem níže):**
> - Data `data/projekty.generated.json` žijí **jen v repu `web`** — server je pushuje tam (deploy key na `web`),
>   zdroj LukasWana jen čte veřejným https klonem. Důvod: commity serveru do zdroje by odmítaly uživatelovy
>   pushe z PC (non-fast-forward) a zanášely historii. Nasazovací Action si data před nasazením převezme z `web`.
> - Na webu „Aktualizováno D. M. RRRR“ (den generování) místo „Data k“ (datum poslední práce) — jen den
>   generování ukáže, že server stojí. Cena: nejvýš 1 commit denně do `web` navíc.
> - Prázdná repa (bez commitů) se neukazují vůbec.
> - Ověřeno během kontroly: kód plánu prošel testy (17 Python, 5 JS) a během nanečisto proti GitHubu (viz plán, Task 4).
>
> Známá omezení (vědomě přijatá): dny se počítají v UTC (commit v 0:30 SELČ spadne do předchozího dne);
> hromadný commit = stejná první řádka týž den v ≥ 5 repech (skutečná práce se stejnou zprávou v 5 repech
> se odfiltruje taky); závod Action × server se srovná dalším hodinovým během.

## Cíl

Na https://lukaswana.github.io/web/ sekce „Na čem pracuju“, plněná automaticky z GitHubu:
na čem právě pracuju a jak intenzivně, i u soukromých rep — **informace o práci, nikdy zdrojáky**.

## Rozhodnutí (uživatel, 2026-10-10)

| otázka | rozhodnutí | důvod / poznámka |
|---|---|---|
| soukromá repa | ukázat všechna s aktivitou | bez odkazu do repa, bez README/kódu — jen název, jazyk, aktivita |
| výběr | aktivní za 12 týdnů + sbalený archiv starších | forky vynechat |
| asus-server-* (16 rep) | sloučit do jedné karty | předpona → skupina, služby jako štítky |
| popisy | `projekty.json` ve zdroji webu | GitHub popisy chybí; text řídí uživatel |
| umístění | nová sekce na hlavní stránce pod horním obrázkem | ostatní obsah beze změny |
| kde běží | **data na asus-serveru (cron), nasazení Action při pushi** | viz níže |

### Proč ne naplánovaná Action (první návrh, zamítnut)

- Naplánované Actions ve veřejném repu GitHub **vypne po 60 dnech bez aktivity v repu**; commity by šly
  do repa `web`, repo LukasWana by „usnulo“.
- Token s přístupem ke všem soukromým repům by ležel v GitHub secretu.
- Uživatel měl s Actions dřív problémy (příčina neověřena — nejspíš minuty soukromých rep na Free
  plánu nebo právě 60denní vypínání; ověřit nešlo, chybí scope `user`).
- Nasazovací Action zůstává: veřejné repo = minuty zdarma bez limitu, spouští se pushem (ne plánem),
  2× ověřena (2026-10-10).

### Proč ne datum posledního pushe (`pushed_at`)

Ověřeno na datech 2026-10-10 — lže o aktivitě:
- `ent-backup` pushuje automat („ENT AutoBackup“) po minutách.
- Hromadný commit „CLAUDE.md: agent pushuje sám“ (2026-10-09 08:09) v mnoha repech — Gramps a jellyfin
  by vypadaly jako včera rozpracované (skutečná práce 5. 10. a 3. 10.).
- EmailRator: poslední commit v hlavní větvi 1. 10., push 10. 10. — práce je v jiné větvi.

## 1. Data a pravidla

Generátor `tools/projekty.py` (Python, jen standardní knihovna), GitHub REST API s tokenem jen pro čtení.

Vstup od uživatele — `projekty.json`:
```json
{
  "skupiny": { "asus-server-": { "nazev": "Domácí server", "popis": "…" } },
  "automaty": ["ENT AutoBackup"],
  "skryt": ["web", "LukasWana", "ent-backup"],
  "projekty": { "EmailRator": { "nazev": "EmailRator", "popis": "…" } }
}
```
Jména, která mají zůstat utajená, NEPATŘÍ do `projekty.json` (repo je veřejné) — patří do
`~/.config/lukaswana-web/skryt.txt` na serveru.

Pro každé vlastní repo, které není fork:
- **Aktivní** (commit za 12 týdnů): commity ze všech větví, deduplikace podle SHA; vynechat autory
  z `automaty` a hromadné commity (stejná první řádka zprávy týž den v ≥5 repech). Výsledek: commity
  po týdnech (12 čísel), počet dní s prací, datum poslední skutečné práce. Nic nezbude → archiv.
- **Archiv**: datum poslední práce z hlavní větve.
- **Skupina**: repa se stejnou předponou se sloučí, aktivita se sečte, zbytky jmen = štítky.

Výstup `data/projekty.generated.json`, na kartu jen povolená pole:
`nazev, popis, jazyk, posledni, dni_prace, tydny[12], stitky[], url` — `url` jen u veřejných.
Před zápisem průchod seznamem povolených polí (vše ostatní zahodit); hlídá test.

Bez zbytečných commitů: v JSON není čas generování; „data k“ = datum nejnovější práce.
Náročnost ~100–150 dotazů za běh (limit 5 000/h).

## 2. Vzhled

- Sekce „Na čem pracuju“ pod `section.hero-image` (DEEP WORK CREATOR), před `skills-section`.
- Styl stávajícího webu: černobílý, Inter, rámečky `#e2e2e2`, text `#666`, hover jako `.skill-frame`.
- Karta: název + jazyk, popis, 12 sloupků po týdnech (inline SVG s textovým popisem pro čtečky),
  „N dní práce“, „naposledy před X“ (přesné datum v `title`), ↗ jen u veřejných. Skupina má štítky.
- Pořadí podle poslední práce; mřížka `auto-fill`, mobil 1 sloupec, desktop 4 (kontejner 1 160 px, karta min. 260 px; změřeno v Chrome 10. 10.).
- Archiv: `<details>` „Starší projekty (N)“ — název, jazyk, měsíc/rok. *Nahrazeno 10. 10. (`0b5aecb`),
  viz sekce 4: `<details>` obsahuje karty starších aplikací a zbytek archivu se neukazuje.*
- Patička „Data k D. M. RRRR“ (vidět zastavenou aktualizaci).
- `projekty.js` načte JSON a vykreslí; při chybě nebo prázdných datech se sekce celá skryje.
  V `index.html` jen prázdný kontejner + `<script>`.
- Ověření: Chrome, desktop + mobil, snímky uživateli.

## 3. Provoz (asus-server)

- `~/lukaswana-web/` klon repa LukasWana; `~/.config/lukaswana-web/token` (600); `skryt.txt`.
- Přístupy:
  1. čtení — fine-grained token (vytvoří uživatel): vlastník LukasWana, všechna repa,
     *Metadata: read* + *Contents: read*. Hodnota nikdy do chatu.
  2. zápis — nový deploy key vygenerovaný na serveru, write jen do repa LukasWana.
- Cron: `17 * * * *  flock -n /tmp/lukaswana-web.lock ~/lukaswana-web/tools/sync.sh`
  → `git pull --ff-only` → `projekty.py` → při změně JSON commit „data: projekty“ + push
  (spustí nasazovací Action). Pull selže → log, nic nepushnout. Log s rotací.
- Nasazení nekopíruje `tools/`, `tests/`, `docs/`, `projekty.json`.
- Testy `tests/` (unittest, fixtures): automaty, hromadné commity, deduplikace přes větve, skupiny,
  povolená pole (soukromé repo bez `url`). `projekty.py --nanecisto` — nejdřív z PC s `gh` tokenem,
  výstup ukázat uživateli před nasazením na server.

## 4. Změny po nasazení (10. 10. 2026, zadání uživatele)

- **Limit karet:** `"max_aktivnich": 8` v `projekty.json`. Aktivní projekty nad limit (nejstarší podle
  poslední práce) jdou na začátek archivu s poli archivu. Důvod: osiřelá karta na 3. řádku.
- **Samostatný box:** skupina s `"samostatne": true` nejde do karet ani do limitu, ale do pole
  `samostatne` ve výstupu (`POLE_SAMOSTATNE`: `nazev, popis, posledni, dni_prace, tydny, aplikace`).
  Místo štítků (jmen repozitářů) ukazuje ručně vybrané `aplikace` z `projekty.json`, z každé jen
  `nazev` a `popis` (`POLE_APLIKACE`). Na webu box přes celý řádek pod kartami. Používá ho Domácí
  server, aplikace vybral uživatel (jen vlastní, ne obaly cizích jako Jellyfin nebo Nextcloud).
- **Hlavička webu:** pod přehledem projektů je starý statický obsah (dovednosti, obsah, aplikace,
  platformy) skrytý v `<div class="stary-obsah" hidden>`, v HTML zůstává. Podtitul a tagline česky.
  Nadpis „Lukáš Wana“ má přesně šířku podtitulu: `nadpis.js` měří inkoust písmen přes canvas
  (`measureText`), protože šířka závisí na písmu zařízení; bez JS zůstane velikost z CSS.
- **Doplnění volných míst:** `"doplnit": [klíče karet]` — když je aktivních méně než `max_aktivnich`,
  volná místa zaplní tyto neaktivní projekty v uvedeném pořadí (karta bez grafu, „naposledy před X“)
  a zmizí z archivu. Aktivní mají přednost: přibude-li aktivní, doplněný ustoupí do archivu.
  Vybral uživatel: ACRS, Desktop-Voice-Assistant („Hlasový asistent“), TTS-cesky-test („Český TTS“).
  *Od `66d88fd` nevyužito:* všechny tři přešly do starších aplikací, volba `doplnit` z `projekty.json` zmizela
  (kód zůstává).
- **Starší aplikace:** `"starsi": [{nazev, popis, repa[], web?}]` → pole `starsi` ve výstupu
  (`POLE_STARSI`: `nazev, popis, jazyk, posledni, url, web`), pořadí z nastavení. Jazyk = nejčastější z rep,
  poslední práce = nejnovější z rep, `url` = první veřejné repo v pořadí z nastavení. Jejich repa nejdou
  do karet ani do archivu. První výběr (10:43): e-jídelníček, Haluzátor, Mandalátor, Meditácie jako řádek
  „Starší aplikace“.
  **Od `66d88fd` (uživatel):** seznam 17 položek, které uživatel vybral ze starého archivu, každá s jedním
  repem, jménem od uživatele a krátkým popisem. Popisy jsou z README, `package.json` a `index.html`
  a uživatel je zatím neviděl, kromě e-jídelníčku, jehož popis dodal sám. Na webu nejsou
  samostatným řádkem: jsou (od `0b5aecb`) kartami uvnitř rozklikávací sekce `<details>` „Starší projekty (N)“
  (N = počet starších aplikací). Mají šedý rámeček `#c8c8c8` a jsou nejvýš 3 na řádek, aby měly víc
  místa pro popis.
  **Zbytek archivu (repa mimo karty) se na webu neukazuje.** Generátor ho dál zapisuje do pole `archiv`
  a JS ho ignoruje.
- **Meditácie** (`meditation-app`): když vypadla ze starších, stala se aktivní kartou s dosavadním popisem
  (volba uživatele, `66d88fd`). Bez záznamu v `projekty` by se ukázala holá jako „meditation-app“.
- **Živý web (`"web"`)**: u starší aplikace nebo karty z `projekty`. Celá karta je pak odkazem do nového
  tabu: odkaz `.projekty-web` je roztažený přes kartu, ↗ na GitHub leží nad ním (z-index). Weby jsou
  ověřené 10. 10. přes curl a Chrome: ad-radar a test-openclaw-pages (GitHub Pages), zvukstetce.cz,
  e-jidelnicek.cz (iOS i Android) a sunset-apartment.com. **Bez odkazu, protože nefungují:**
  chatavpekle.cz (DNS má A záznam 88.146.221.173, ale web neodpovídá ani v Chrome), haluzator.eu
  a contyco.cz (bez A záznamu; GitHub Pages u Haluzator.eu přitom má jako doménu nastavené
  haluzator.eu). Až weby poběží, stačí doplnit `web`.
- **Skryto na přání uživatele:** `Dychani` a `emailrator-info` (v `skryt`, tedy ani v archivu).
