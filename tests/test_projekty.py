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


if __name__ == "__main__":
    unittest.main()
