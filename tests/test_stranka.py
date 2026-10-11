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

    def test_roh_obrysu_neprestreli(self):
        # rovně useknutý konec tahu (a začátek vlákna) je ostrý roh; Catmull-Rom v něm přestřelil
        # ven z tahu a na ensō vznikl hrot (nalezeno 10. 10. ve 2× náhledu)
        d = enso.obrys(lambda t: (100 + 100 * t, 50.0), lambda t: 20.0, 0.0, 1.0, 10)
        y = [float(c) for c in re.findall(r"-?\d+(?:\.\d+)?", d)[1::2]]
        self.assertGreaterEqual(min(y), 40.0)
        self.assertLessEqual(max(y), 60.0)

    def test_suchy_konec_varianta_c(self):
        # rozhodnutí uživatele 10. 10. nad náhledy A/A2/B/C: C (hodně suchý) = tělo + 7 vláken
        self.assertEqual(len(enso.enso(400)), 8)

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


class TestBanner(unittest.TestCase):
    def setUp(self):
        self.html = text("index.html")
        self.css = text("style.css")

    def test_enso_v_banneru(self):
        banner = self.html.split('<section class="enso-banner">')[1].split("</section>")[0]
        self.assertIn('src="img/enso.svg"', banner)
        self.assertIn("<h2>Deep work creator</h2>", banner)
        self.assertIn("introvertní technicko-kreativní tvůrce", banner)


class TestBezCar(unittest.TestCase):
    def setUp(self):
        self.css = text("style.css")

    def test_zrusene_cary(self):
        for sel in (".section-title", ".projekty-karta footer", ".projekty-aplikace li", ".projekty-archiv"):
            for telo in pravidla(self.css, sel):
                self.assertNotRegex(telo, r"border(-top|-bottom)?\s*:", sel)

    def test_karta_je_plocha_ne_ramecek(self):
        # rozhodnutí uživatele 2026-10-10: varianta B — světlý teplý podklad s oblými rohy, žádný rámeček
        telo = pravidla(self.css, ".projekty-karta")[0]
        self.assertNotRegex(telo, r"border\s*:")
        self.assertIn("background-color: #f6f5f2", telo)
        self.assertRegex(telo, r"border-radius:\s*\d+px")
        for sel in (".projekty-karta:hover", ".projekty-archiv .projekty-karta"):
            self.assertNotIn("border", pravidla(self.css, sel)[0], sel)
        self.assertNotIn("box-shadow", pravidla(self.css, ".projekty-karta:hover")[0])

    def test_podtah_pod_nadpisem(self):
        tela = pravidla(self.css, ".section-title::after")
        self.assertEqual(len(tela), 1)
        self.assertIn("url('img/tah.svg')", tela[0])

    def test_nadpis_sekce_bez_verzalek(self):
        telo = pravidla(self.css, ".section-title")[0]
        self.assertNotIn("uppercase", telo)


class TestMrizka(unittest.TestCase):
    def test_hlavni_projekty_po_trech(self):
        # pokyn uživatele 2026-10-10: 6 hlavních projektů jako 3 × 3 (dvě řady po třech), na užším displeji méně sloupců
        tela = pravidla(text("style.css"), ".projekty-grid")
        self.assertEqual(len(tela), 1)
        self.assertIn("calc((100% - 60px) / 3)", tela[0])
        self.assertIn("gap: 30px", tela[0])


class TestVelkyMonitor(unittest.TestCase):
    """Pokyn uživatele 2026-10-11: na velkých monitorech až po 8K drží obsah 75–85 % šířky okna.

    Obsah = 1160 px × zoom: kontejner 1200 minus padding 2 × 20 (změřeno na snímcích z Chromu — model
    s 1200 dával na konci stupňů ve skutečnosti 72,9 %). Stupně jsou `@media (min-width: N) { html { zoom: Z } }`.
    """

    OBSAH = 1160

    def stupne(self):
        css = re.sub(r"/\*.*?\*/", "", text("style.css"), flags=re.S)
        nalezy = re.findall(r"@media \(min-width: (\d+)px\)\s*\{\s*html\s*\{\s*zoom:\s*([\d.]+);\s*\}\s*\}", css)
        self.assertEqual(len(nalezy), css.count("zoom"), "každý zoom musí být ve tvaru stupně")
        return [(int(h), float(z)) for h, z in nalezy]

    def test_stupne_vzestupne(self):
        # stejná specificita → platí poslední pravidlo; širší stupeň musí stát níž
        hranice = [h for h, _ in self.stupne()]
        self.assertEqual(hranice, sorted(hranice))
        self.assertEqual(len(hranice), len(set(hranice)))

    def test_podil_75_az_85_procent(self):
        stupne = self.stupne()
        # pod první hranicí platí zoom 1; 1160 px je v pásmu jen do 1546 px okna
        self.assertGreaterEqual(self.OBSAH / (stupne[0][0] - 1), 0.75)
        konce = [h for h, _ in stupne[1:]] + [7681]  # poslední stupeň drží aspoň do 8K (7680 px)
        for (hranice, zoom), konec in zip(stupne, konce):
            obsah = self.OBSAH * zoom
            self.assertLessEqual(obsah / hranice, 0.85, f"{hranice} px: {obsah / hranice:.3f}")
            self.assertGreaterEqual(obsah / (konec - 1), 0.75, f"{konec - 1} px: {obsah / (konec - 1):.3f}")

    def test_hranice_od_uzivatele(self):
        # 1800 (velké monitory) a 2800 (4K) zadal uživatel; zůstávají hranicemi stupňů
        hranice = [h for h, _ in self.stupne()]
        self.assertIn(1800, hranice)
        self.assertIn(2800, hranice)


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


if __name__ == "__main__":
    unittest.main()
