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
