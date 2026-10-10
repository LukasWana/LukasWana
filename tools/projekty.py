"""Přehled projektů pro https://lukaswana.github.io/web/ — generátor dat.

Čte GitHub API tokenem jen pro čtení a zapíše data/projekty.generated.json.
Do výstupu jdou jen povolená pole (POLE_KARTA, POLE_ARCHIV): informace o práci,
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
POLE_KARTA = ("nazev", "popis", "jazyk", "posledni", "dni_prace", "tydny", "stitky", "url")
POLE_ARCHIV = ("nazev", "jazyk", "posledni", "url")
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


def sestav(repa, nastaveni, skryt, dnes):
    """repa: [{nazev, soukrome, jazyk, url, commity_okno, commity_hlavni}] → data pro web."""
    automaty = set(nastaveni.get("automaty", []))
    skupiny = nastaveni.get("skupiny", {})
    popisy = nastaveni.get("projekty", {})
    skryte = set(nastaveni.get("skryt", [])) | set(skryt)
    repa = [r for r in repa if r["nazev"] not in skryte]
    hromadne = hromadne_zpravy({r["nazev"]: r["commity_okno"] for r in repa})

    karty = {}
    for r in repa:
        predpona = next((s for s in skupiny if r["nazev"].startswith(s)), None)
        karty.setdefault(predpona or r["nazev"], []).append(r)

    aktivni, archiv = [], []
    for klic_karty, clenove in karty.items():
        skupina = klic_karty in skupiny
        info = skupiny[klic_karty] if skupina else popisy.get(klic_karty, {})
        jazyky = collections.Counter(r["jazyk"] for r in clenove if r["jazyk"])
        zaklad = {
            "nazev": info.get("nazev") or klic_karty.rstrip("-"),
            "popis": info.get("popis", ""),
            "jazyk": jazyky.most_common(1)[0][0] if jazyky else "",
            "url": None if skupina or clenove[0]["soukrome"] else clenove[0]["url"],
            "stitky": sorted(r["nazev"][len(klic_karty):] for r in clenove) if skupina else [],
        }
        okno = [c for r in clenove for c in ciste_commity(r["commity_okno"], automaty, hromadne)]
        akt = aktivita(okno, dnes)
        if akt:
            zaklad["tydny"], zaklad["dni_prace"], zaklad["posledni"] = akt
            aktivni.append(jen_pole(zaklad, POLE_KARTA))
        else:
            data = [posledni_prace(r["commity_okno"] + r["commity_hlavni"], automaty, hromadne) for r in clenove]
            zaklad["posledni"] = max((d for d in data if d), default=None)
            if zaklad["posledni"]:   # prázdné repo (žádný commit) není projekt
                archiv.append(jen_pole(zaklad, POLE_ARCHIV))

    for seznam in (aktivni, archiv):
        seznam.sort(key=lambda k: k["nazev"].lower())
        seznam.sort(key=lambda k: k.get("posledni", ""), reverse=True)
    return {"aktivni": aktivni, "archiv": archiv}
