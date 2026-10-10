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


if __name__ == "__main__":
    unittest.main()
