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
