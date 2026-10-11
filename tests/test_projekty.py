import datetime as dt
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import projekty as p  # noqa: E402

DNES = dt.date(2026, 10, 10)  # sobota; tento týden začal po 5. 10.


def c(sha, datum, autor="qwanap", zprava="práce"):
    return {"sha": sha, "datum": datum + "T10:00:00Z", "autor": autor, "zprava": zprava}


def repo(nazev, okno=(), hlavni=(), soukrome=True, jazyk="Python"):
    return {"nazev": nazev, "soukrome": soukrome, "jazyk": jazyk,
            "url": "https://github.com/LukasWana/" + nazev,
            "commity_okno": list(okno), "commity_hlavni": list(hlavni)}


class Cisteni(unittest.TestCase):
    def test_duplicity_pres_vetve_se_pocitaji_jednou(self):
        commity = [c("a", "2026-10-09"), c("a", "2026-10-09"), c("b", "2026-10-08")]
        self.assertEqual([x["sha"] for x in p.ciste_commity(commity, set(), set())], ["a", "b"])

    def test_automat_se_vynecha(self):
        commity = [c("a", "2026-10-09", autor="ENT AutoBackup"), c("b", "2026-10-08")]
        self.assertEqual([x["sha"] for x in p.ciste_commity(commity, {"ENT AutoBackup"}, set())], ["b"])

    def test_hromadny_commit_v_peti_repech(self):
        po_repech = {f"r{i}": [c(f"s{i}", "2026-10-09", zprava="CLAUDE.md: agent pushuje sám")] for i in range(5)}
        self.assertEqual(p.hromadne_zpravy(po_repech), {("2026-10-09", "CLAUDE.md: agent pushuje sám")})

    def test_stejna_zprava_ve_ctyrech_repech_neni_hromadna(self):
        po_repech = {f"r{i}": [c(f"s{i}", "2026-10-09", zprava="oprava")] for i in range(4)}
        self.assertEqual(p.hromadne_zpravy(po_repech), set())

    def test_hromadny_se_pozna_podle_prvni_radky(self):
        hromadne = {("2026-10-09", "CLAUDE.md: agent pushuje sám")}
        commity = [c("a", "2026-10-09", zprava="CLAUDE.md: agent pushuje sám" + chr(10) + chr(10) + "tělo")]
        self.assertEqual(p.ciste_commity(commity, set(), hromadne), [])


class Aktivita(unittest.TestCase):
    def test_tydny_ukotvene_na_pondeli(self):
        commity = [c("a", "2026-10-05"), c("b", "2026-10-04"), c("d", "2026-10-04")]
        tydny, dni, posledni = p.aktivita(commity, DNES)
        self.assertEqual(len(tydny), 12)
        self.assertEqual(tydny[-1], 1)   # po 5. 10. = tento týden
        self.assertEqual(tydny[-2], 2)   # ne 4. 10. = minulý týden
        self.assertEqual(dni, 2)
        self.assertEqual(posledni, "2026-10-05")

    def test_mimo_okno_neni_aktivita(self):
        # okno začíná po 20. 7. 2026 (12 týdnů včetně tohoto)
        self.assertIsNone(p.aktivita([c("a", "2026-07-19")], DNES))
        self.assertIsNotNone(p.aktivita([c("a", "2026-07-20")], DNES))

    def test_bez_prace_se_vystup_v_ramci_tydne_nemeni(self):
        commity = [c("a", "2026-09-30")]
        self.assertEqual(p.aktivita(commity, dt.date(2026, 10, 5)), p.aktivita(commity, dt.date(2026, 10, 11)))


class Sestav(unittest.TestCase):
    NAST = {"skupiny": {"asus-server-": {"nazev": "Domácí server", "popis": "služby"}},
            "automaty": ["ENT AutoBackup"], "skryt": ["web"],
            "projekty": {"EmailRator": {"nazev": "EmailRator", "popis": "třídění e-mailů"}}}

    def test_soukrome_repo_nema_url_a_ma_jen_povolena_pole(self):
        d = p.sestav([repo("EmailRator", okno=[c("a", "2026-10-09")])], self.NAST, set(), DNES)
        karta = d["aktivni"][0]
        self.assertNotIn("url", karta)
        self.assertLessEqual(set(karta), set(p.POLE_KARTA))
        self.assertEqual(karta["popis"], "třídění e-mailů")

    def test_verejne_repo_ma_url(self):
        d = p.sestav([repo("Dychani", okno=[c("a", "2026-10-09")], soukrome=False)], self.NAST, set(), DNES)
        self.assertEqual(d["aktivni"][0]["url"], "https://github.com/LukasWana/Dychani")

    def test_skupina_slouci_repa_a_ukaze_stitky(self):
        repa = [repo("asus-server-zvuk", okno=[c("a", "2026-10-09")]),
                repo("asus-server-trezor", okno=[c("b", "2026-10-02")], jazyk="JavaScript", soukrome=False)]
        d = p.sestav(repa, self.NAST, set(), DNES)
        self.assertEqual(len(d["aktivni"]), 1)
        karta = d["aktivni"][0]
        self.assertEqual(karta["nazev"], "Domácí server")
        self.assertEqual(karta["stitky"], ["trezor", "zvuk"])
        self.assertEqual(karta["dni_prace"], 2)
        self.assertNotIn("url", karta)   # skupina nikdy neodkazuje

    def test_skryti_z_nastaveni_i_ze_souboru(self):
        repa = [repo("web", okno=[c("a", "2026-10-09")]), repo("Tajne", okno=[c("b", "2026-10-09")])]
        d = p.sestav(repa, self.NAST, {"Tajne"}, DNES)
        self.assertEqual(d["aktivni"] + d["archiv"], [])

    def test_repo_jen_s_automatem_jde_do_archivu(self):
        r = repo("zaloha", okno=[c("a", "2026-10-09", autor="ENT AutoBackup")])
        d = p.sestav([r], self.NAST, set(), DNES)
        self.assertEqual(d["aktivni"], [])
        self.assertEqual(d["archiv"][0]["nazev"], "zaloha")

    def test_poradi_podle_posledni_prace(self):
        repa = [repo("Stare", okno=[c("a", "2026-09-01")]), repo("Nove", okno=[c("b", "2026-10-09")]),
                repo("Archiv", hlavni=[c("x", "2025-03-01")])]
        d = p.sestav(repa, self.NAST, set(), DNES)
        self.assertEqual([k["nazev"] for k in d["aktivni"]], ["Nove", "Stare"])
        self.assertEqual(d["archiv"][0]["posledni"], "2025-03-01")
        self.assertEqual(set(d), {"aktivni", "archiv", "samostatne", "starsi"})   # nic dalšího na nejvyšší úrovni

    def test_prazdne_repo_se_neukaze(self):
        # PDFValidator, Projects: repo bez commitů (API 409) není projekt
        d = p.sestav([repo("Prazdne")], self.NAST, set(), DNES)
        self.assertEqual(d["aktivni"] + d["archiv"], [])

    def test_archiv_ma_jen_povolena_pole(self):
        d = p.sestav([repo("Archiv", hlavni=[c("x", "2025-03-01")])], self.NAST, set(), DNES)
        self.assertLessEqual(set(d["archiv"][0]), set(p.POLE_ARCHIV))

    def test_nad_limit_aktivnich_jdou_nejstarsi_do_archivu(self):
        repa = [repo(f"P{i}", okno=[c(str(i), f"2026-09-{10 + i}")]) for i in range(10)]
        repa.append(repo("Archiv", hlavni=[c("x", "2025-03-01")]))
        d = p.sestav(repa, dict(self.NAST, max_aktivnich=8), set(), DNES)
        self.assertEqual([k["nazev"] for k in d["aktivni"]], [f"P{i}" for i in range(9, 1, -1)])
        self.assertEqual([k["nazev"] for k in d["archiv"]], ["P1", "P0", "Archiv"])
        for k in d["archiv"]:
            self.assertLessEqual(set(k), set(p.POLE_ARCHIV))

    def test_doplnit_zaplni_volna_mista_z_archivu(self):
        repa = [repo("Akt1", okno=[c("a", "2026-10-09")]), repo("Akt2", okno=[c("b", "2026-10-01")]),
                repo("A", hlavni=[c("x", "2026-05-04")]), repo("B", hlavni=[c("y", "2026-03-21")]),
                repo("C", hlavni=[c("z", "2025-01-01")])]
        nast = dict(self.NAST, max_aktivnich=4, doplnit=["B", "Neexistuje", "A", "C"],
                    projekty={"B": {"nazev": "Bé", "popis": "popis B"}})
        d = p.sestav(repa, nast, set(), DNES)
        self.assertEqual([k["nazev"] for k in d["aktivni"]], ["Akt1", "Akt2", "Bé", "A"])
        self.assertEqual([k["nazev"] for k in d["archiv"]], ["C"])
        doplneny = d["aktivni"][2]
        self.assertEqual((doplneny["popis"], doplneny["posledni"]), ("popis B", "2026-03-21"))
        self.assertNotIn("tydny", doplneny)
        self.assertLessEqual(set(doplneny), set(p.POLE_KARTA))

    def test_doplnit_ustoupi_aktivnim(self):
        repa = [repo(f"P{i}", okno=[c(str(i), f"2026-10-0{i + 1}")]) for i in range(4)]
        repa.append(repo("B", hlavni=[c("y", "2026-03-21")]))
        d = p.sestav(repa, dict(self.NAST, max_aktivnich=4, doplnit=["B"]), set(), DNES)
        self.assertNotIn("B", [k["nazev"] for k in d["aktivni"]])
        self.assertEqual([k["nazev"] for k in d["archiv"]], ["B"])


class Starsi(unittest.TestCase):
    NAST = {"starsi": [
        {"nazev": "Jídelníček", "popis": "jídlo", "repa": ["jid-ios", "jid-android"]},
        {"nazev": "Haluzátor", "popis": "projekce", "repa": ["Halu-stable", "Halu.eu"]},
        {"nazev": "Chybí", "popis": "žádné repo", "repa": ["neni"]}]}

    def test_vybrane_aplikace_v_poradi_z_nastaveni_a_mimo_prehled(self):
        repa = [repo("jid-ios", hlavni=[c("a", "2025-02-09")], jazyk="JavaScript"),
                repo("jid-android", hlavni=[c("b", "2024-10-08")], jazyk="Vue"),
                repo("Halu.eu", hlavni=[c("c", "2026-04-23")], soukrome=False, jazyk="JavaScript"),
                repo("Halu-stable", okno=[c("d", "2026-10-01")], soukrome=False, jazyk="TypeScript"),
                repo("Jine", hlavni=[c("e", "2025-01-01")])]
        d = p.sestav(repa, self.NAST, set(), DNES)
        self.assertEqual([k["nazev"] for k in d["starsi"]], ["Jídelníček", "Haluzátor"])
        jid, halu = d["starsi"]
        self.assertEqual(jid["posledni"], "2025-02-09")
        self.assertNotIn("url", jid)   # obě repa soukromá
        self.assertEqual(halu["url"], "https://github.com/LukasWana/Halu-stable")   # první veřejné podle nastavení
        self.assertEqual(halu["posledni"], "2026-10-01")
        for k in d["starsi"]:
            self.assertLessEqual(set(k), set(p.POLE_STARSI))
        self.assertEqual(d["aktivni"], [])
        self.assertEqual([k["nazev"] for k in d["archiv"]], ["Jine"])

    def test_zivy_web_z_nastaveni(self):
        nast = {"starsi": [{"nazev": "Kaligrafie", "popis": "web", "repa": ["Zvuk"], "web": "https://zvukstetce.cz"},
                           {"nazev": "Bez webu", "popis": "x", "repa": ["Jine"]}],
                "projekty": {"Akt": {"nazev": "Akt", "web": "https://akt.example"}}}
        repa = [repo("Zvuk", hlavni=[c("a", "2025-11-10")]), repo("Jine", hlavni=[c("b", "2025-01-01")]),
                repo("Akt", okno=[c("c", "2026-10-09")])]
        d = p.sestav(repa, nast, set(), DNES)
        self.assertEqual([k.get("web") for k in d["starsi"]], ["https://zvukstetce.cz", None])
        self.assertEqual(d["aktivni"][0]["web"], "https://akt.example")

    def test_dalsi_odkazy_z_nastaveni(self):
        odkazy = [{"nazev": "App Store", "url": "https://apps.apple.com/app/id1", "navic": "nejde ven"},
                   {"nazev": "Google Play", "url": "https://play.google.com/store/apps/details?id=x"}]
        nast = {"starsi": [{"nazev": "Jidelnicek", "popis": "x", "repa": ["Jid", "JidA"], "web": "https://j.example",
                            "odkazy": odkazy},
                           {"nazev": "Bez odkazů", "popis": "x", "repa": ["Jine"]}],
                "projekty": {"Akt": {"nazev": "Akt", "odkazy": odkazy[:1]}}}
        repa = [repo("Jid", hlavni=[c("a", "2025-11-10")]), repo("JidA", hlavni=[c("d", "2025-12-01")]),
                repo("Jine", hlavni=[c("b", "2025-01-01")]), repo("Akt", okno=[c("c", "2026-10-09")])]
        d = p.sestav(repa, nast, set(), DNES)
        ciste = [{"nazev": "App Store", "url": "https://apps.apple.com/app/id1"},
                 {"nazev": "Google Play", "url": "https://play.google.com/store/apps/details?id=x"}]
        self.assertEqual([k.get("odkazy") for k in d["starsi"]], [ciste, None])
        self.assertEqual(d["starsi"][0]["web"], "https://j.example")   # web zůstává vedle dalších odkazů
        self.assertEqual(d["starsi"][0]["posledni"], "2025-12-01")      # jedna karta za všechna repa
        self.assertEqual(d["aktivni"][0]["odkazy"], ciste[:1])


class Samostatne(unittest.TestCase):
    NAST = {"skupiny": {"asus-server-": {
        "nazev": "Domácí server", "popis": "služby", "samostatne": True,
        "aplikace": [{"nazev": "Knihy", "popis": "e-knihy", "repo": "bookshelf", "port": 7787},
                     {"nazev": "Zvuk", "popis": "hudba"}]}},
        "max_aktivnich": 1}

    def test_skupina_jde_do_vlastniho_boxu_mimo_prehled(self):
        repa = [repo("asus-server-zvuk", okno=[c("a", "2026-10-09")]),
                repo("asus-server-stav", okno=[c("b", "2026-10-02")]),
                repo("Dychani", okno=[c("c", "2026-10-01")])]
        d = p.sestav(repa, self.NAST, set(), DNES)
        self.assertEqual([k["nazev"] for k in d["aktivni"]], ["Dychani"])   # limit se na box nevztahuje
        self.assertEqual(d["archiv"], [])
        box = d["samostatne"][0]
        self.assertEqual(box["nazev"], "Domácí server")
        self.assertEqual(box["dni_prace"], 2)
        self.assertLessEqual(set(box), set(p.POLE_SAMOSTATNE))
        self.assertNotIn("stitky", box)   # jména repozitářů na web nejdou, jen vybrané aplikace

    def test_aplikace_jen_nazev_a_popis(self):
        d = p.sestav([repo("asus-server-zvuk", okno=[c("a", "2026-10-09")])], self.NAST, set(), DNES)
        self.assertEqual(d["samostatne"][0]["aplikace"],
                         [{"nazev": "Knihy", "popis": "e-knihy"}, {"nazev": "Zvuk", "popis": "hudba"}])

    def test_neaktivni_box_zustane_bez_grafu(self):
        d = p.sestav([repo("asus-server-zvuk", hlavni=[c("x", "2025-03-01")])], self.NAST, set(), DNES)
        box = d["samostatne"][0]
        self.assertEqual(box["posledni"], "2025-03-01")
        self.assertNotIn("tydny", box)
        self.assertEqual(d["archiv"], [])


class Barvy(unittest.TestCase):
    """Pokyn uživatele 2026-10-11: hlavní projekty mají barvy z původního banneru, každý jinou;
    Domácí server a starší projekty zůstávají černobílé (docs/plans/2026-10-11-barvy-design.md)."""

    NAST = {"skupiny": {"asus-server-": {"nazev": "Domácí server", "popis": "služby"}},
            "projekty": {"EmailRator": {"nazev": "EmailRator", "popis": "e-maily", "barva": "fialova"}}}

    def test_paleta_osmi_barev_z_banneru(self):
        self.assertEqual(len(p.PALETA), 8)
        self.assertEqual(len(set(p.PALETA)), 8)
        self.assertIn("barva", p.POLE_KARTA)

    def test_barva_z_nastaveni_projde_na_kartu(self):
        d = p.sestav([repo("EmailRator", okno=[c("a", "2026-10-09")])], self.NAST, set(), DNES)
        self.assertEqual(d["aktivni"][0]["barva"], "fialova")

    def test_karta_bez_barvy_dostane_volnou(self):
        repa = [repo("EmailRator", okno=[c("a", "2026-10-09")]), repo("Dychani", okno=[c("b", "2026-10-08")])]
        d = p.sestav(repa, self.NAST, set(), DNES)
        barvy = [k["barva"] for k in d["aktivni"]]
        self.assertEqual(barvy[0], "fialova")
        self.assertIn(barvy[1], p.PALETA)
        self.assertNotEqual(barvy[1], "fialova")

    def test_osm_karet_osm_ruznych_barev(self):
        repa = [repo(f"P{i}", okno=[c(str(i), f"2026-09-{10 + i}")]) for i in range(10)]
        repa.append(repo("EmailRator", okno=[c("e", "2026-10-09")]))
        d = p.sestav(repa, dict(self.NAST, max_aktivnich=8), set(), DNES)
        barvy = [k["barva"] for k in d["aktivni"]]
        self.assertEqual(len(barvy), 8)
        self.assertEqual(sorted(barvy), sorted(p.PALETA))

    def test_doplnena_karta_ma_barvu(self):
        repa = [repo("Akt", okno=[c("a", "2026-10-09")]), repo("B", hlavni=[c("y", "2026-03-21")])]
        d = p.sestav(repa, dict(self.NAST, max_aktivnich=4, doplnit=["B"]), set(), DNES)
        barvy = [k.get("barva") for k in d["aktivni"]]
        self.assertEqual(len(set(barvy)), 2)
        self.assertTrue(set(barvy) <= set(p.PALETA))

    def test_skupina_archiv_a_starsi_bez_barvy(self):
        repa = [repo("asus-server-zvuk", okno=[c("a", "2026-10-09")]), repo("Stare", hlavni=[c("x", "2025-03-01")]),
                repo("ACRS", hlavni=[c("y", "2025-02-01")])]
        nast = dict(self.NAST, starsi=[{"nazev": "ACRS", "popis": "bannery", "repa": ["ACRS"]}])
        d = p.sestav(repa, nast, set(), DNES)
        self.assertEqual(d["aktivni"][0]["nazev"], "Domácí server")
        self.assertNotIn("barva", d["aktivni"][0])
        self.assertNotIn("barva", d["archiv"][0])
        self.assertNotIn("barva", d["starsi"][0])

    def test_skutecne_nastaveni(self):
        nast = json.loads((Path(__file__).resolve().parent.parent / "projekty.json").read_text(encoding="utf-8"))
        barvy = {k: v.get("barva") for k, v in nast["projekty"].items()}
        self.assertEqual(barvy, {"EmailRator": "fialova", "Gramps": "tyrkys", "WanGP_SD_wholepipeline": "zlata",
                                 "whisper-sk-transcriber": "zelena", "NakupUX": "malina", "meditation-app": "azur"})
        self.assertLessEqual(nast["max_aktivnich"], len(p.PALETA))   # víc karet než barev = unikátnost nejde
        for skupina in nast["skupiny"].values():
            self.assertNotIn("barva", skupina)


class Strankovani(unittest.TestCase):
    def test_dalsi_stranka(self):
        link = '<https://api.github.com/x?page=2>; rel="next", <https://api.github.com/x?page=5>; rel="last"'
        self.assertEqual(p.dalsi_stranka(link), "https://api.github.com/x?page=2")
        self.assertIsNone(p.dalsi_stranka('<https://api.github.com/x?page=1>; rel="prev"'))
        self.assertIsNone(p.dalsi_stranka(""))


class Razitko(unittest.TestCase):
    """Rozhodnutí uživatele 2026-10-11: „Aktualizováno“ s časem poslední změny dat. Nový čas jen při změně dat
    nebo v novém dni (UTC), jinak zůstane starý → soubor se nezmění a sync.sh necommituje (nejvýš 1 commit denně navíc)."""

    TED = dt.datetime(2026, 10, 11, 12, 17, 5, tzinfo=dt.timezone.utc)

    def test_bez_stareho_souboru_novy_cas(self):
        self.assertEqual(p.razitko(None, {"a": 1}, self.TED), "2026-10-11T12:17Z")

    def test_stejna_data_stejny_den_stary_cas(self):
        stara = {"a": 1, "aktualizovano": "2026-10-11T01:17Z"}
        self.assertEqual(p.razitko(stara, {"a": 1}, self.TED), "2026-10-11T01:17Z")

    def test_zmenena_data_novy_cas(self):
        stara = {"a": 1, "aktualizovano": "2026-10-11T01:17Z"}
        self.assertEqual(p.razitko(stara, {"a": 2}, self.TED), "2026-10-11T12:17Z")

    def test_novy_den_novy_cas(self):
        stara = {"a": 1, "aktualizovano": "2026-10-10T23:17Z"}
        self.assertEqual(p.razitko(stara, {"a": 1}, self.TED), "2026-10-11T12:17Z")

    def test_stary_format_bez_casu_prepise(self):
        # data z doby před časem (jen datum): první běh zapíše čas i beze změny dat
        stara = {"a": 1, "aktualizovano": "2026-10-11"}
        self.assertEqual(p.razitko(stara, {"a": 1}, self.TED), "2026-10-11T12:17Z")


if __name__ == "__main__":
    unittest.main()
