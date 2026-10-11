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
import papir  # noqa: E402
import projekty  # noqa: E402


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


class TestPapir(unittest.TestCase):
    """Pozadí Papír podle inspirace uživatele 2026-10-11: škrábance, smítka, jemné zrno,
    měkce ztmavené strany a tón od hlavní barvy motivu (Inkoust bez tónu)."""

    def test_soubory_odpovidaji_generatoru(self):
        self.assertEqual(text("img/papir-svetly.svg"), papir.svg(True))
        self.assertEqual(text("img/papir-tmavy.svg"), papir.svg(False))

    def test_css_bere_textury_a_ton_motivu(self):
        css = text("skiny.css")
        svetly = pravidla(css, '[data-pozadi="papir"][data-rezim="svetly"]')[0]
        tmavy = pravidla(css, '[data-pozadi="papir"][data-rezim="tmavy"]')[0]
        self.assertIn('url("img/papir-svetly.svg")', svetly)
        self.assertIn('url("img/papir-tmavy.svg")', tmavy)
        for telo in (svetly, tmavy):
            self.assertIn("linear-gradient(90deg", telo)  # ztmavené strany
            self.assertIn("var(--motiv-akcent)", telo)
        # síla tónu patří motivu a dědí se: čtvereček Papír v panelu nese jen data-pozadi a data-rezim
        self.assertIn("--papir-dotyk: 0%", pravidla(css, ":root")[0])
        self.assertIn("--papir-dotyk: 30%", pravidla(css, '[data-skin]:not([data-skin="inkoust"])')[0])
        self.assertFalse(any("--papir-dotyk" in t for t in pravidla(css, '[data-pozadi="papir"]')))

    def test_platne_svg_cerny_inkoust(self):
        for cesta, viewbox in (("img/enso.svg", "0 0 400 400"), ("img/tah.svg", "0 0 240 24")):
            koren = ET.fromstring(text(cesta))
            self.assertEqual(koren.get("viewBox"), viewbox, cesta)
            ns = "{http://www.w3.org/2000/svg}"
            self.assertEqual(koren.find(ns + "g").get("fill"), enso.INKOUST, cesta)
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

    def test_kontakt_v_paticce_za_aktualizaci(self):
        # pokyn uživatele 2026-10-11: e-mail ze shora za čas aktualizace, na mobilu pod něj
        hlavicka = self.html.split('<header class="header">')[1].split("</header>")[0]
        self.assertNotIn("mailto:", hlavicka)
        self.assertEqual(self.html.count("mailto:qwanap@gmail.com"), 1)
        paticka = self.html.split('<p class="paticka-info">')[1].split("</p>")[0]
        self.assertLess(paticka.index('id="projekty-data-k"'), paticka.index('href="mailto:qwanap@gmail.com"'))
        self.assertIn(">qwanap@gmail.com</a>", paticka)  # adresa je vidět jako text
        self.assertGreater(self.html.index('<p class="paticka-info">'), self.html.index('<p class="motto">'))
        # oddělovač jen když je datum (bez dat zůstane samotný e-mail); na mobilu pod sebou bez oddělovače
        self.assertIn("display: none;", pravidla(self.css, ".projekty-data-k:empty + .paticka-oddelovac")[0])
        # na střed i na mobilu: hlavní pravidlo stojí v CSS za @media, jeho align-items platí i tam
        self.assertTrue(any("align-items: center;" in t for t in pravidla(self.css, ".paticka-info")))
        self.assertFalse(any("align-items: baseline;" in t for t in pravidla(self.css, ".paticka-info")))
        mobil = self.css.split("@media (max-width: 768px)")[1]
        self.assertIn("flex-direction: column;", pravidla(mobil, ".paticka-info")[0])
        self.assertIn("display: none;", pravidla(mobil, ".paticka-oddelovac")[0])

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
        # ensō je maska (barvu dává skin), ne <img> (docs/plans/2026-10-11-skiny-design.md)
        self.assertIn('<div class="enso" aria-hidden="true"></div>', banner)
        self.assertIn("mask: url('img/enso.svg')", pravidla(self.css, ".enso")[0])
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
        self.assertIn("background-color: var(--plocha);", telo)
        self.assertIn("--plocha: #f6f5f2;", pravidla(self.css, ":root")[1])  # výchozí Inkoust
        # pokyn 2026-10-11 nad náhledem skinů: obrysy všude pryč (ani barevný okraj, ani linka)
        self.assertNotIn("box-shadow", telo)
        self.assertRegex(telo, r"border-radius:\s*\d+px")
        for sel in (".projekty-karta:hover", ".projekty-archiv .projekty-karta"):
            self.assertNotIn("border", pravidla(self.css, sel)[0], sel)
        self.assertNotIn("box-shadow", pravidla(self.css, ".projekty-karta:hover")[0])

    def test_podtah_pod_nadpisem(self):
        tela = pravidla(self.css, ".section-title::after")
        self.assertEqual(len(tela), 1)
        self.assertIn("mask: url('img/tah.svg')", tela[0])

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


class TestBarvyBanneru(unittest.TestCase):
    """Pokyn uživatele 2026-10-11: barvy z původního banneru — opar za ensō a barevné hlavní karty
    (docs/plans/2026-10-11-barvy-design.md)."""

    RGB = {"fialova": "168, 34, 196", "tyrkys": "60, 193, 154", "zlata": "224, 184, 58", "zelena": "54, 196, 102",
           "malina": "205, 52, 91", "azur": "32, 152, 227", "modra": "81, 135, 244", "purpur": "172, 50, 148"}

    def test_trida_pro_kazdou_barvu_palety(self):
        self.assertEqual(set(self.RGB), set(projekty.PALETA))
        css = text("style.css")
        for nazev, rgb in self.RGB.items():
            tela = pravidla(css, f".barva-{nazev}")
            self.assertEqual(len(tela), 1, nazev)
            self.assertIn(f"--barva: {rgb};", tela[0], nazev)

    def test_barevna_karta_bokeh_a_sloupce(self):
        css = text("style.css")
        tela = pravidla(css, ".projekty-barevna")
        self.assertEqual(len(tela), 1)
        self.assertIn("radial-gradient", tela[0])
        self.assertIn("var(--barva)", tela[0])
        # jen background-image: barva pozadí karty a její :hover zůstanou
        self.assertIn("background-image:", tela[0])
        self.assertNotRegex(tela[0], r"background\s*:")
        # sloupce mají fill="currentColor" (projekty.js), barvu dává color grafu
        sloupce = pravidla(css, ".projekty-barevna .projekty-graf")
        self.assertEqual(len(sloupce), 1)
        self.assertIn("color: rgb(var(--barva));", sloupce[0])

    def test_opar_za_enso(self):
        css = text("style.css")
        banner = pravidla(css, ".enso-banner")
        self.assertTrue(any("isolation: isolate" in t and "position: relative" in t for t in banner))
        opar = pravidla(css, ".enso-banner::before")
        self.assertEqual(len(opar), 1)
        for nazev in ("fialova", "tyrkys", "zlata", "azur"):
            self.assertIn(self.RGB[nazev], opar[0], nazev)
        self.assertIn("filter: blur(", opar[0])
        self.assertIn("mask-image: radial-gradient(", opar[0])
        self.assertIn("z-index: -1", opar[0])
        self.assertIn("inset: -60px 0;", opar[0])   # do stran nepřesahuje → na mobilu žádný vodorovný posuvník


class TestInkoust(unittest.TestCase):
    """Pokyn uživatele 2026-10-11: všude místo čisté černé #000 o kousek stažená off-black (--inkoust)."""

    def test_jedna_hodnota_v_css_i_v_generatoru(self):
        # výchozí skin Inkoust, světlý režim (style.css); img/*.svg jsou masky, ale hodnotu drží stejnou
        tela = pravidla(text("style.css"), '[data-skin="inkoust"][data-rezim="svetly"]')
        self.assertEqual(len(tela), 1)
        self.assertIn(f"--inkoust: {enso.INKOUST};", tela[0])
        self.assertNotEqual(enso.INKOUST.lower(), "#000")
        self.assertNotEqual(enso.INKOUST.lower(), "#000000")

    def test_nikde_cista_cerna(self):
        css = re.sub(r"/\*.*?\*/", "", text("style.css") + text("skiny.css"), flags=re.S)
        # výjimka: masky (#000 tam znamená neprůhlednost, ne barvu)
        bez_masek = "\n".join(r for r in css.splitlines() if "mask" not in r)
        self.assertNotRegex(bez_masek, r"#000\b|#000000|\bblack\b")
        self.assertNotIn("#000", text("projekty.js"))
        self.assertNotIn("#000", text("index.html"))
        self.assertNotIn("#000", text("nadpis.js"))
        for cesta in ("img/enso.svg", "img/tah.svg"):
            self.assertNotIn('"#000"', text(cesta))

    def test_ikony_paticky_jako_maska(self):
        # Skiny 2026-10-11: ikona = maska „tvar minus bílý symbol (luminance)“, barvu dává --inkoust nebo barva značky.
        # Tahy proto musí být čistě černé: jas #1a1a1a (~10 %) by maska odečetla a inkoust by vyšel světlejší
        # (změřeno: rgb(49,49,49) místo (26,26,26)).
        ikony = sorted((KOREN / "img" / "social").glob("*.svg"))
        self.assertEqual(len(ikony), 8)
        html, css = text("index.html"), text("style.css")
        for cesta in ikony:
            koren = ET.fromstring(cesta.read_text(encoding="utf-8"))
            self.assertEqual(koren.get("fill"), "#000", cesta.name)
            self.assertIn(f'<i class="ikona-{cesta.stem}"></i>', html)
            self.assertIn(f"--ikona: url('img/social/{cesta.stem}.svg');", pravidla(css, f".ikona-{cesta.stem}")[0])
        self.assertNotIn('src="img/social/', html)
        telo = pravidla(css, ".social-icon i")[0]
        self.assertIn("luminance", telo)
        self.assertIn("mask-composite: subtract", telo)

    def test_body_a_graf_v_inkoustu(self):
        css = text("style.css")
        self.assertTrue(any("color: var(--inkoust);" in t for t in pravidla(css, "body")))
        self.assertTrue(any("color: var(--inkoust);" in t for t in pravidla(css, ".projekty-graf")))

    CB = ':root:not([data-skin]:not([data-skin="inkoust"])):not([data-akcent])'

    def test_vychozi_inkoust_cernobily(self):
        # pokyn uživatele 2026-10-11 „defaultní motiv bude černobílý“ (plán skiny-zuzeni, Task 6) a „když zvolím
        # inkoust a černou, bude stránka plně černobílá“: bez oparu a bokehu, grafy v inkoustu, v obou režimech;
        # barvu dostane Inkoust až po výběru Základní barvy. Ikony patičky jsou v inkoustu už bez pravidla.
        css = text("style.css")
        koren = pravidla(css, self.CB)
        self.assertEqual(len(koren), 1)
        self.assertIn("--opar-sila: 0;", koren[0])
        self.assertIn("--bokeh-sila: 0;", koren[0])
        self.assertIn("color: var(--inkoust);", pravidla(css, self.CB + " .projekty-graf")[0])


class TestStarsiInverzne(unittest.TestCase):
    """Pokyn uživatele 2026-10-11: karty starších projektů inverzně (negativ) — plocha v barvě koleček ikon dole,
    světlý text. Krátký pokus o průhledné karty téhož dne uživatel vrátil („mělo to zůstat negativní“)."""

    def test_karta_v_barve_ikon_text_svetly(self):
        css = text("style.css")
        tela = pravidla(css, ".projekty-archiv .projekty-karta")
        self.assertEqual(len(tela), 1)
        # „jen vzít stejnou barvu jako z ikon“: stejná proměnná jako kolečka ikon
        # --ikony = --inkoust spočtený na :root (kolečka ikon); přepnutí --inkoust v kartě Inkoustu plochu nezmění
        self.assertIn("background-color: var(--ikony);", tela[0])
        self.assertTrue(any("--ikony: var(--inkoust);" in t for t in pravidla(css, ":root")))
        self.assertIn("var(--inkoust)) var(--znacky), var(--inkoust));", pravidla(css, ".social-icon i")[0])
        self.assertIn("color: var(--inv-text);", tela[0])
        hover = pravidla(css, ".projekty-archiv .projekty-karta:hover")
        self.assertEqual(len(hover), 1)
        self.assertIn("var(--inv-plocha-hover)", hover[0])

    def test_sedy_text_a_odkazy_svetle(self):
        css = text("style.css")
        for selektor in (".projekty-archiv .projekty-popis", ".projekty-archiv .projekty-jazyk",
                         ".projekty-archiv .projekty-karta footer", ".projekty-archiv .projekty-odkaz",
                         ".projekty-archiv .projekty-dalsi", ".projekty-archiv .projekty-web:focus-visible"):
            tela = pravidla(css, selektor)
            self.assertEqual(len(tela), 1, selektor)
            self.assertIn("var(--inv-text", tela[0], selektor)


class TestInkoustKartyInverzne(unittest.TestCase):
    """Pokyn uživatele 2026-10-11: v tmavém Inkoustu jsou všechny karty obráceně jako kolečka ikon — plocha
    v inkoustu, světlý text. Přepnutím proměnných v kartě, ne výčtem prvků. Večer téhož dne: ve světlém Inkoustu
    (výchozí vzhled) mají projekty a Domácí server světlou plochu a černý text, obráceně jsou jen Starší projekty
    a ikony; se Základní barvou se podbarvení mění podle ní."""

    SEL = '[data-skin="inkoust"][data-rezim="tmavy"] .projekty-karta'
    SVETLY = '[data-skin="inkoust"][data-rezim="svetly"]'

    def test_karta_prepne_promenne(self):
        tela = pravidla(text("style.css"), self.SEL)
        self.assertEqual(len(tela), 1)
        for deklarace in ("--plocha: var(--ikony);", "--plocha-hover: var(--inv-plocha-hover);",
                          "--text: var(--inv-text-2);", "--text-popisek: var(--inv-text-3);",
                          "--inkoust: var(--inv-text);", "color: var(--inv-text);"):
            self.assertIn(deklarace, tela[0])

    def test_svetly_karty_nejsou_inverzni(self):
        css = re.sub(r"/\*.*?\*/", "", text("style.css"), flags=re.S)
        self.assertNotIn(':root:not([data-skin]:not([data-skin="inkoust"])) .projekty-karta', css)
        self.assertNotIn("--plocha: var(--ikony)", "".join(pravidla(css, self.SVETLY + " .projekty-karta")))

    def test_svetly_se_zakladni_barvou_podbarvi(self):
        s = self.SVETLY + "[data-akcent]"
        tela = pravidla(text("style.css"), s + " .projekty-karta")
        self.assertEqual(len(tela), 1)
        self.assertIn("rgb(var(--akcent))", tela[0])
        skiny = text("skiny.css")
        for n in range(1, 9):
            self.assertEqual(len(pravidla(skiny, s + " .social-icon:nth-child(%d) i" % n)), 1, n)
        self.assertEqual(len(pravidla(skiny, s + " .projekty-archiv .projekty-karta")), 1)


class TestVeseleBarevne(unittest.TestCase):
    """Pokyn uživatele 2026-10-11: v motivu Veselé ikony a Starší projekty barevně jako ilustrace (ensō modrá →
    fialová → oranžová). Vybrána varianta A z náhledu: plné barvy po krocích přechodu, ne přechod v každé."""

    V = '[data-skin="teple"] '

    def test_ikony_po_krocich_prechodu(self):
        css = text("skiny.css")
        for n in range(1, 9):
            tela = pravidla(css, self.V + ".social-icon:nth-child(%d) i" % n)
            self.assertEqual(len(tela), 1, n)
            self.assertIn("var(--akcent", tela[0], n)
        self.assertIn("background-color: rgb(var(--akcent));", pravidla(css, self.V + ".social-icon:nth-child(1) i")[0])
        self.assertIn("background-color: rgb(var(--akcent-3));", pravidla(css, self.V + ".social-icon:nth-child(8) i")[0])

    def test_starsi_projekty_jeden_prechod_shora_dolu(self):
        """Druhý pokyn téhož dne: místo tří barev po sloupcích jeden přechod shora dolů přes všechny karty;
        výřez karty dává projekty.js prechodPresKarty() (--prechod-h, --prechod-y)."""
        css = text("skiny.css")
        self.assertNotIn("nth-child(3n", css)
        tela = pravidla(css, self.V + ".projekty-archiv .projekty-karta")
        self.assertEqual(len(tela), 1)
        self.assertIn("linear-gradient(180deg, rgb(var(--akcent)), rgb(var(--akcent-2)), rgb(var(--akcent-3)))", tela[0])
        self.assertIn("background-size: 100% var(--prechod-h, 100%);", tela[0])
        self.assertIn("background-position: 0 calc(-1 * var(--prechod-y, 0px));", tela[0])
        # šedé popisky by na oranžové zanikly: odvozené z --inv-text
        self.assertIn("--inv-text-2: color-mix(in srgb, var(--inv-text)", tela[0])
        self.assertIn("--inv-text-3: color-mix(in srgb, var(--inv-text)", tela[0])


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


def ids(js, seznam):
    """id položek pole `seznam` ve skin.js (var SKINY = [ { id: 'x', … }, … ];)."""
    blok = js.split(f"var {seznam} = [")[1].split("];")[0]
    return re.findall(r"\{ id: '([a-z]*)'", blok)


def promenne(telo):
    return dict(re.findall(r"(--[a-z0-9-]+):\s*([^;]+);", telo))


def jas(hex_):
    h = hex_.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    kanaly = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in kanaly]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def kontrast(a, b):
    ja, jb = sorted((jas(a), jas(b)), reverse=True)
    return (ja + 0.05) / (jb + 0.05)


class TestSkiny(unittest.TestCase):
    """Skiny 2026-10-11 (docs/plans/2026-10-11-skiny-design.md): tlačítko Vzhled s panelem, 4 motivy (zúženo 2026-10-11) × světlý/tmavý,
    Základní barvy a Pozadí jako volby nad motivem. Barvy jsou jen v CSS, skin.js nese seznamy id."""

    ROLE = ("--pozadi", "--inkoust", "--text", "--text-tlumeny", "--text-popisek", "--plocha", "--plocha-hover",
            "--inv-plocha", "--inv-plocha-hover", "--inv-text", "--inv-text-2", "--inv-text-3",
            "--motiv-akcent", "--motiv-akcent-2", "--motiv-akcent-3")

    def test_vzhled_jede_s_rolovanim(self):
        # pokyn uživatele 2026-10-11 „ať se nastavení témat scroluje nahoře s celou stránkou“ + „Vzhled se nescroluje“:
        # tlačítko zůstává při rolování nahoře (fixed); panel pak musí mít vlastní posuvník, jinak by se jeho
        # spodek v nízkém okně nedal dočíst
        css = text("style.css")
        self.assertIn("position: fixed;", pravidla(css, ".vzhled")[0])
        self.assertNotIn("background: none;", pravidla(css, ".vzhled-tlacitko")[0])  # nad obsahem musí mít podklad
        panel = pravidla(css, ".vzhled-panel")[0]
        self.assertIn("max-height: calc(100vh - 80px);", panel)
        self.assertIn("overflow-y: auto;", panel)

    def setUp(self):
        self.js = text("skin.js")
        self.css = text("style.css") + text("skiny.css")

    def blok(self, skin, rezim):
        tela = pravidla(self.css, f'[data-skin="{skin}"][data-rezim="{rezim}"]')
        self.assertEqual(len(tela), 1, (skin, rezim))
        return promenne(tela[0])

    def test_kazdy_motiv_ma_svetly_i_tmavy_se_vsemi_rolemi(self):
        skiny = ids(self.js, "SKINY")
        self.assertEqual(skiny, ["inkoust", "teple", "hluboka", "priroda"])
        for skin in skiny:
            for rezim in ("svetly", "tmavy"):
                p = self.blok(skin, rezim)
                for role in self.ROLE:
                    self.assertIn(role, p, (skin, rezim, role))
                self.assertIn(f"color-scheme: {'light' if rezim == 'svetly' else 'dark'}",
                              pravidla(self.css, f'[data-skin="{skin}"][data-rezim="{rezim}"]')[0], (skin, rezim))

    def test_bez_osirelych_pravidel(self):
        # zúžení 2026-10-11: v CSS nesmí zůstat pravidla motivů, barev a pozadí, které panel nenabízí
        bez_komentaru = re.sub(r"/\*.*?\*/", "", self.css, flags=re.S)   # hlavička skiny.css ukazuje [data-skin="id"]
        for atribut, seznam in (("data-skin", "SKINY"), ("data-akcent", "AKCENTY"), ("data-pozadi", "POZADI")):
            v_css = set(re.findall(rf'\[{atribut}="([a-z]+)"\]', bez_komentaru))
            self.assertEqual(v_css, set(ids(self.js, seznam)), atribut)

    def test_jmeno_a_podtitul_plnou_barvou(self):
        # revize 2026-10-11: text vyplněný přechodem se hůř čte a test kontrastu ho neumí změřit
        skiny = text("skiny.css")
        self.assertNotIn("--nadpis", skiny)
        self.assertNotIn("--podtitul", skiny)

    def test_zakladni_barvy_ve_ctyrech_sloupcich(self):
        # 7 barev + „podle motivu“ = dvě plné řady po 4, stejně široké jako Pozadí
        self.assertIn("grid-template-columns: repeat(4, 1fr);",
                      pravidla(text("style.css"), ".vzhled-barvy .vzhled-mrizka")[0])

    def test_kontrast_textu_wcag_aa(self):
        # text na pozadí i na ploše karty a světlý text na inverzní kartě: aspoň 4,5 : 1 (WCAG AA)
        for skin in ids(self.js, "SKINY"):
            for rezim in ("svetly", "tmavy"):
                p = self.blok(skin, rezim)
                for podklad in ("--pozadi", "--plocha", "--plocha-hover"):
                    for popredi in ("--inkoust", "--text", "--text-tlumeny", "--text-popisek"):
                        k = kontrast(p[popredi], p[podklad])
                        self.assertGreaterEqual(k, 4.5, (skin, rezim, popredi, podklad, round(k, 2)))
                inv = p["--inv-plocha"] if p["--inv-plocha"].startswith("#") else p["--inkoust"]
                for popredi in ("--inv-text", "--inv-text-2", "--inv-text-3"):
                    k = kontrast(p[popredi], inv)
                    self.assertGreaterEqual(k, 4.5, (skin, rezim, popredi, round(k, 2)))

    def test_vychozi_inkoust_ve_style_css(self):
        # stránka se vykreslí i bez skiny.css: obecná pravidla a světlý Inkoust jsou ve style.css
        styl = text("style.css")
        self.assertEqual(len(pravidla(styl, '[data-skin="inkoust"][data-rezim="svetly"]')), 1)
        self.assertTrue(any("--akcent: var(--volba-akcent, var(--motiv-akcent));" in t for t in pravidla(styl, "[data-skin]")))

    def test_zakladni_barvy_a_pozadi_maji_pravidla(self):
        for akcent in ids(self.js, "AKCENTY"):
            telo = pravidla(self.css, f'[data-akcent="{akcent}"]')
            self.assertEqual(len(telo), 1, akcent)
            for v in ("--volba-akcent:", "--volba-akcent-2:", "--volba-akcent-3:"):
                self.assertIn(v, telo[0], akcent)
        for pozadi in ids(self.js, "POZADI"):
            # vzor po režimech má přednost (Papír má i holé pravidlo, ale jen se silou tónu)
            tela = (pravidla(self.css, f'[data-pozadi="{pozadi}"][data-rezim="svetly"]')
                    + pravidla(self.css, f'[data-pozadi="{pozadi}"][data-rezim="tmavy"]')
                    or pravidla(self.css, f'[data-pozadi="{pozadi}"]'))
            self.assertIn(len(tela), (1, 2), pozadi)
            self.assertTrue(all("--volba-vzor:" in t for t in tela), pozadi)

    def test_skript_v_hlavicce_pred_styly(self):
        html = text("index.html")
        hlava = html.split("</head>")[0]
        # atributy se nastaví dřív, než se načte CSS → tmavý režim nebliká světle
        self.assertLess(hlava.index("localStorage.getItem"), hlava.index('href="style.css"'))
        self.assertLess(hlava.index('href="style.css"'), hlava.index('href="skiny.css"'))
        for klic in ("'skin'", "'rezim'", "'akcent'", "'pozadi'"):
            self.assertIn(klic, hlava)
        self.assertIn('<script src="skin.js" defer></script>', html)
        self.assertIn('<div class="vzhled" hidden>', html)   # bez JS tlačítko nezobrazovat

    def test_bez_obrysu(self):
        # pokyn uživatele 2026-10-11: „ty outline dej všude pryč“ — karty bez okraje, panel a vzorníky bez linky;
        # zůstává jen prstenec vybrané volby a obrys fokusu z klávesnice
        for sel in (".projekty-karta", ".vzhled-ctverec", ".vzhled-motiv", ".vzhled-panel"):
            for t in pravidla(self.css, sel):
                self.assertNotRegex(t, r"border\s*:|inset 0 0 0 1px|0 0 0 1px", sel)
        self.assertNotIn("--okraj-sila", self.css)
        self.assertNotIn("--linka", self.css)


if __name__ == "__main__":
    unittest.main()
