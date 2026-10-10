import datetime as dt
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


if __name__ == "__main__":
    unittest.main()
