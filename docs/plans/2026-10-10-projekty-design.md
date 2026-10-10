# Přehled projektů na webu — návrh

Datum: 2026-10-10 · Stav: návrh schválen uživatelem, implementace nezačala

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
- Pořadí podle poslední práce; mřížka `auto-fill`, mobil 1 sloupec, desktop 3.
- Archiv: `<details>` „Starší projekty (N)“ — název, jazyk, měsíc/rok.
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
