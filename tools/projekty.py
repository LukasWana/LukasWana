"""Přehled projektů pro https://lukaswana.github.io/web/ — generátor dat.

Čte GitHub API tokenem jen pro čtení a zapíše data/projekty.generated.json.
Do výstupu jdou jen povolená pole (POLE_KARTA, POLE_ARCHIV, POLE_SAMOSTATNE, POLE_APLIKACE, POLE_STARSI): informace o práci,
nikdy obsah repozitářů. Návrh: docs/plans/2026-10-10-projekty-design.md
"""
import argparse
import collections
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.github.com"
TYDNU = 12
HROMADNY_PRAH = 5
POLE_KARTA = ("nazev", "popis", "jazyk", "posledni", "dni_prace", "tydny", "stitky", "url", "web", "odkazy", "barva")
# Barvy třpytek z původního banneru (docs/plans/2026-10-11-barvy-design.md); RGB je v style.css.
# Hlavních karet je nejvýš max_aktivnich = 8, takže každá dostane jinou.
PALETA = ("fialova", "tyrkys", "zlata", "zelena", "malina", "azur", "modra", "purpur")
POLE_ARCHIV = ("nazev", "jazyk", "posledni", "url")
POLE_SAMOSTATNE = ("nazev", "popis", "posledni", "dni_prace", "tydny", "aplikace")
POLE_APLIKACE = ("nazev", "popis")
POLE_ODKAZ = ("nazev", "url")
POLE_STARSI = ("nazev", "popis", "jazyk", "posledni", "url", "web", "odkazy")
KOREN = Path(__file__).resolve().parent.parent
VYSTUP = KOREN / "data" / "projekty.generated.json"
NASTAVENI = KOREN / "projekty.json"


def prvni_radka(zprava):
    return zprava.splitlines()[0].strip() if zprava else ""


def klic(commit):
    return (commit["datum"][:10], prvni_radka(commit["zprava"]))


def hromadne_zpravy(commity_po_repech, prah=HROMADNY_PRAH):
    """Množina (den, první řádka) commitů, které se týž den objevily v >= prah repech."""
    repa = collections.defaultdict(set)
    for nazev, commity in commity_po_repech.items():
        for commit in commity:
            repa[klic(commit)].add(nazev)
    return {k for k, r in repa.items() if len(r) >= prah}


def ciste_commity(commity, automaty, hromadne):
    """Bez duplicit (podle SHA), bez autorů-automatů a bez hromadných commitů."""
    videne, vysledek = set(), []
    for commit in commity:
        if commit["sha"] in videne:
            continue
        videne.add(commit["sha"])
        if commit["autor"] in automaty or klic(commit) in hromadne:
            continue
        vysledek.append(commit)
    return vysledek


def pondeli(den):
    return den - dt.timedelta(days=den.weekday())


def zacatek_okna(dnes, tydnu=TYDNU):
    return pondeli(dnes) - dt.timedelta(weeks=tydnu - 1)


def aktivita(commity, dnes, tydnu=TYDNU):
    """(tydny, dni_prace, posledni) za kalendářní týdny po–ne, nejstarší první; None = žádná práce.

    Týdny jsou ukotvené na pondělí: bez nové práce se výstup mění nejvýš jednou týdně
    (žádné zbytečné commity dat)."""
    tento = pondeli(dnes)
    tydny, dny = [0] * tydnu, set()
    for commit in commity:
        den = dt.date.fromisoformat(commit["datum"][:10])
        index = tydnu - 1 - (tento - pondeli(den)).days // 7
        if den > dnes or not 0 <= index < tydnu:
            continue
        tydny[index] += 1
        dny.add(den)
    if not dny:
        return None
    return tydny, len(dny), max(dny).isoformat()


def posledni_prace(commity, automaty, hromadne):
    """Datum poslední skutečné práce; když je všechno automat/hromadné, datum nejnovějšího commitu."""
    zdroj = ciste_commity(commity, automaty, hromadne) or commity
    return max(c["datum"][:10] for c in zdroj) if zdroj else None


def jen_pole(zaznam, pole):
    """Seznam povolených polí: nic jiného do veřejného JSON nesmí projít."""
    return {k: zaznam[k] for k in pole if zaznam.get(k) not in (None, "", [])}


def dalsi_odkazy(info):
    """Další odkazy karty (App Store, Google Play, nápověda) z nastavení, jen povolená pole."""
    return [jen_pole(o, POLE_ODKAZ) for o in info.get("odkazy", [])]


def sestav(repa, nastaveni, skryt, dnes):
    """repa: [{nazev, soukrome, jazyk, url, commity_okno, commity_hlavni}] → data pro web."""
    automaty = set(nastaveni.get("automaty", []))
    skupiny = nastaveni.get("skupiny", {})
    popisy = nastaveni.get("projekty", {})
    skryte = set(nastaveni.get("skryt", [])) | set(skryt)
    repa = [r for r in repa if r["nazev"] not in skryte]
    hromadne = hromadne_zpravy({r["nazev"]: r["commity_okno"] for r in repa})

    # Starší vybrané aplikace (poslední řádek webu): jejich repa do přehledu ani archivu nejdou.
    vyber = nastaveni.get("starsi", [])
    podle_jmena = {r["nazev"]: r for r in repa}
    ve_vyberu = {jmeno for a in vyber for jmeno in a.get("repa", [])}
    starsi = [s for s in (starsi_karta(a, [podle_jmena[j] for j in a.get("repa", []) if j in podle_jmena],
                                       automaty, hromadne) for a in vyber) if s]
    repa = [r for r in repa if r["nazev"] not in ve_vyberu]

    karty = {}
    for r in repa:
        predpona = next((s for s in skupiny if r["nazev"].startswith(s)), None)
        karty.setdefault(predpona or r["nazev"], []).append(r)

    aktivni, archiv, samostatne = [], [], []
    neaktivni = {}   # klíč karty → plný záznam, pro doplnění volných míst
    bez_barvy = set()   # názvy karet skupin: zůstávají černobílé
    for klic_karty, clenove in karty.items():
        skupina = klic_karty in skupiny
        info = skupiny[klic_karty] if skupina else popisy.get(klic_karty, {})
        if info.get("samostatne"):
            samostatne.append(box(info, klic_karty, clenove, automaty, hromadne, dnes))
            continue
        jazyky = collections.Counter(r["jazyk"] for r in clenove if r["jazyk"])
        zaklad = {
            "nazev": info.get("nazev") or klic_karty.rstrip("-"),
            "popis": info.get("popis", ""),
            "jazyk": jazyky.most_common(1)[0][0] if jazyky else "",
            "url": None if skupina or clenove[0]["soukrome"] else clenove[0]["url"],
            "stitky": sorted(r["nazev"][len(klic_karty):] for r in clenove) if skupina else [],
            "web": info.get("web"),   # živý web: celá karta na něj odkazuje
            "odkazy": dalsi_odkazy(info),
            "barva": None if skupina else info.get("barva"),
        }
        if skupina:
            bez_barvy.add(zaklad["nazev"])
        okno = [c for r in clenove for c in ciste_commity(r["commity_okno"], automaty, hromadne)]
        akt = aktivita(okno, dnes)
        if akt:
            zaklad["tydny"], zaklad["dni_prace"], zaklad["posledni"] = akt
            aktivni.append(jen_pole(zaklad, POLE_KARTA))
        else:
            data = [posledni_prace(r["commity_okno"] + r["commity_hlavni"], automaty, hromadne) for r in clenove]
            zaklad["posledni"] = max((d for d in data if d), default=None)
            if zaklad["posledni"]:   # prázdné repo (žádný commit) není projekt
                neaktivni[klic_karty] = zaklad

    # Volná místa do limitu doplní vybrané neaktivní projekty (v pořadí z nastavení); aktivní mají přednost.
    limit = nastaveni.get("max_aktivnich")
    volno = float("inf") if limit is None else limit - len(aktivni)
    doplnene = []
    for klic in nastaveni.get("doplnit", []):
        if len(doplnene) >= volno:
            break
        if klic in neaktivni:
            doplnene.append(jen_pole(neaktivni.pop(klic), POLE_KARTA))
    archiv = [jen_pole(z, POLE_ARCHIV) for z in neaktivni.values()]

    for seznam in (aktivni, archiv):
        seznam.sort(key=lambda k: k["nazev"].lower())
        seznam.sort(key=lambda k: k.get("posledni", ""), reverse=True)
    if limit is not None and len(aktivni) > limit:
        # Nejstarší aktivní jsou pořád novější než celý archiv, proto jdou na jeho začátek.
        archiv[:0] = [jen_pole(k, POLE_ARCHIV) for k in aktivni[limit:]]
        del aktivni[limit:]
    aktivni += doplnene
    obarvi(aktivni, bez_barvy)
    return {"aktivni": aktivni, "archiv": archiv, "samostatne": samostatne, "starsi": starsi}


def obarvi(karty, bez_barvy):
    """Karta bez barvy z nastavení dostane první barvu palety, kterou nemá žádná jiná karta.
    Barva z nastavení má přednost; skupiny (bez_barvy) zůstávají černobílé. Dojdou-li barvy, karta zůstane bez."""
    volne = [b for b in PALETA if b not in {k.get("barva") for k in karty}]
    for k in karty:
        if "barva" not in k and k["nazev"] not in bez_barvy and volne:
            k["barva"] = volne.pop(0)


def starsi_karta(info, clenove, automaty, hromadne):
    """Starší vybraná aplikace: název a popis z nastavení, jazyk a poslední práce z jejích rep."""
    data = [posledni_prace(r["commity_okno"] + r["commity_hlavni"], automaty, hromadne) for r in clenove]
    posledni = max((d for d in data if d), default=None)
    if not posledni:
        return None
    jazyky = collections.Counter(r["jazyk"] for r in clenove if r["jazyk"])
    verejne = [r["url"] for r in clenove if not r["soukrome"]]
    return jen_pole({
        "nazev": info.get("nazev", ""),
        "popis": info.get("popis", ""),
        "jazyk": jazyky.most_common(1)[0][0] if jazyky else "",
        "posledni": posledni,
        "url": verejne[0] if verejne else None,
        "web": info.get("web"),
        "odkazy": dalsi_odkazy(info),
    }, POLE_STARSI)


def box(info, klic_karty, clenove, automaty, hromadne, dnes):
    """Projekt s vlastním boxem přes celý řádek: místo jmen repozitářů ukazuje vybrané aplikace."""
    zaklad = {
        "nazev": info.get("nazev") or klic_karty.rstrip("-"),
        "popis": info.get("popis", ""),
        "aplikace": [jen_pole(a, POLE_APLIKACE) for a in info.get("aplikace", [])],
    }
    okno = [c for r in clenove for c in ciste_commity(r["commity_okno"], automaty, hromadne)]
    akt = aktivita(okno, dnes)
    if akt:
        zaklad["tydny"], zaklad["dni_prace"], zaklad["posledni"] = akt
    else:
        data = [posledni_prace(r["commity_okno"] + r["commity_hlavni"], automaty, hromadne) for r in clenove]
        zaklad["posledni"] = max((d for d in data if d), default=None)
    return jen_pole(zaklad, POLE_SAMOSTATNE)


def dalsi_stranka(link):
    for cast in link.split(","):
        if 'rel="next"' in cast:
            return cast[cast.index("<") + 1:cast.index(">")]
    return None


def api(cesta, token, parametry=None):
    """GET na GitHub API; seznamy projde přes všechny stránky. Prázdné repo (HTTP 409) = []."""
    url = API + cesta + ("?" + urllib.parse.urlencode(parametry) if parametry else "")
    vysledek = []
    while url:
        pozadavek = urllib.request.Request(url, headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "lukaswana-web-projekty",
        })
        try:
            with urllib.request.urlopen(pozadavek, timeout=30) as odpoved:
                data = json.load(odpoved)
                odkaz = odpoved.headers.get("Link", "")
        except urllib.error.HTTPError as chyba:
            if chyba.code == 409:
                return []
            raise
        if not isinstance(data, list):
            return data
        vysledek += data
        url = dalsi_stranka(odkaz)
    return vysledek


def commit_z_api(c):
    autor = c["commit"]["author"]
    return {"sha": c["sha"], "datum": autor["date"], "autor": autor["name"], "zprava": c["commit"]["message"]}


def stahni(token, dnes):
    """Vlastní repa bez forků; u rep s pushem v okně commity ze všech větví, jinak 30 z hlavní větve."""
    od = zacatek_okna(dnes)
    repa = []
    for r in api("/user/repos", token, {"affiliation": "owner", "per_page": 100}):
        if r["fork"]:
            continue
        cesta = "/repos/" + r["full_name"]
        okno = []
        if r["pushed_at"] and r["pushed_at"][:10] >= od.isoformat():
            for vetev in api(cesta + "/branches", token, {"per_page": 100}):
                okno += api(cesta + "/commits", token,
                            {"sha": vetev["name"], "since": od.isoformat() + "T00:00:00Z", "per_page": 100})
        hlavni = [] if okno else api(cesta + "/commits", token, {"per_page": 30})
        repa.append({
            "nazev": r["name"], "soukrome": r["private"], "jazyk": r["language"] or "",
            "url": r["html_url"],
            "commity_okno": [commit_z_api(c) for c in okno],
            "commity_hlavni": [commit_z_api(c) for c in hlavni],
        })
    return repa


def nacti_skryt(cesta):
    if not cesta or not Path(cesta).exists():
        return set()
    radky = Path(cesta).read_text(encoding="utf-8").splitlines()
    return {r.strip() for r in radky if r.strip() and not r.startswith("#")}


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Generátor přehledu projektů pro web.")
    parser.add_argument("--nanecisto", action="store_true", help="jen vypsat JSON, nic nezapisovat")
    parser.add_argument("--token-soubor", help="soubor s tokenem (jinak proměnná GITHUB_TOKEN)")
    parser.add_argument("--skryt-soubor", help="repa ke skrytí, jedno na řádek (# = komentář)")
    parser.add_argument("--vystup", default=str(VYSTUP), help="kam zapsat JSON (sync.sh: klon repa web)")
    a = parser.parse_args(argv)
    if a.token_soubor:
        token = Path(a.token_soubor).read_text(encoding="utf-8").strip()
    else:
        token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        sys.exit("chybí token: --token-soubor nebo GITHUB_TOKEN")
    nastaveni = json.loads(NASTAVENI.read_text(encoding="utf-8"))
    dnes = dt.datetime.now(dt.timezone.utc).date()
    data = sestav(stahni(token, dnes), nastaveni, nacti_skryt(a.skryt_soubor), dnes)
    # den generování (ne čas): bez změny dat nejvýš 1 commit denně; na webu „Aktualizováno …“
    data["aktualizovano"] = dnes.isoformat()
    # chr(10) a newline="": LF i na Windows a v kódu žádné zpětné lomítko (Git Bash)
    text = json.dumps(data, ensure_ascii=False, indent=1) + chr(10)
    if a.nanecisto:
        sys.stdout.write(text)
        return
    vystup = Path(a.vystup)
    vystup.parent.mkdir(parents=True, exist_ok=True)
    vystup.write_text(text, encoding="utf-8", newline="")
    print(f"zapsáno {vystup}: {len(data['aktivni'])} aktivních, {len(data['archiv'])} v archivu")


if __name__ == "__main__":
    main()
