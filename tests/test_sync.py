"""tools/sync.sh proti skutečnému gitu: lokální holé repozitáře místo GitHubu, generátor nahrazený stubem."""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SYNC = Path(__file__).resolve().parent.parent / "tools" / "sync.sh"
SH = shutil.which("sh")

# Stub generátoru: zapíše data. S proměnnou SOUBEH_ORIGIN navíc při prvním volání pushne
# do webu cizí commit — tak, jako by mezitím doběhl deploy z repa LukasWana.
STUB = '''import os, subprocess, sys
args = sys.argv[1:]
vystup = args[args.index("--vystup") + 1]
os.makedirs(os.path.dirname(vystup), exist_ok=True)
with open(vystup, "w", encoding="utf-8", newline="") as f:
    f.write('{"projekty": ["novy"]}' + chr(10))
origin = os.environ.get("SOUBEH_ORIGIN")
znacka = os.environ.get("SOUBEH_ZNACKA")
if origin and not os.path.exists(znacka):
    open(znacka, "w").close()
    d = os.path.join(os.path.dirname(znacka), "deploy-klon")
    subprocess.run(["git", "clone", "--quiet", origin, d], check=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="") as f:
        f.write("deploy" + chr(10))
    subprocess.run(["git", "-C", d, "commit", "--quiet", "-am", "deploy"], check=True)
    subprocess.run(["git", "-C", d, "push", "--quiet"], check=True)
'''


IDENTITA = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                          env=dict(os.environ, **IDENTITA), text=True, encoding="utf-8").stdout


def smaz(cesta):
    # Git zakládá objekty jen pro čtení a rmtree je na Windows bez chmod nesmaže.
    def oprav(funkce, p, _):
        os.chmod(p, stat.S_IWRITE)
        funkce(p)
    shutil.rmtree(cesta, onexc=oprav)


def zapis(cesta, text):
    cesta.parent.mkdir(parents=True, exist_ok=True)
    with open(cesta, "w", encoding="utf-8", newline="") as f:
        f.write(text)


@unittest.skipIf(SH is None, "chybí sh")
class Sync(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(smaz, self.tmp)
        t = self.tmp
        self.env = dict(os.environ, **IDENTITA, HOME=t.joinpath("home").as_posix(),
                        GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=t.joinpath("gitconfig").as_posix())
        zapis(t / "gitconfig", "")
        self.origin = t / "web.git"
        git("init", "--quiet", "--bare", "-b", "main", str(self.origin))
        zdroj_origin = t / "zdroj.git"
        git("init", "--quiet", "--bare", "-b", "main", str(zdroj_origin))
        domov = t / "home" / "lukaswana-web"
        for nazev, origin, soubory in (
                ("web", self.origin, {"index.html": "puvodni\n", "data/projekty.generated.json": "{}\n"}),
                ("zdroj", zdroj_origin, {"tools/projekty.py": STUB})):
            d = domov / nazev
            git("clone", "--quiet", str(origin), str(d))
            for jmeno, text in soubory.items():
                zapis(d / jmeno, text)
            git("add", "-A", cwd=d)
            git("commit", "--quiet", "-m", "start", cwd=d)
            git("push", "--quiet", "-u", "origin", "main", cwd=d)
        konfig = t / "home" / ".config" / "lukaswana-web"
        zapis(konfig / "token", "x\n")
        zapis(konfig / "skryt.txt", "")
        # python3 je na Windows stub Microsoft Storu; přesměruj ho na tento interpret.
        zapis(t / "bin" / "python3", "#!/bin/sh\nexec \"%s\" \"$@\"\n" % Path(sys.executable).as_posix())
        self.env["PATH"] = str(t / "bin") + os.pathsep + self.env["PATH"]
        self.log = t / "home" / ".local" / "state" / "lukaswana-web" / "sync.log"

    def spust(self):
        return subprocess.run([SH, SYNC.as_posix()], env=self.env, capture_output=True,
                              text=True, encoding="utf-8")

    def origin_soubor(self, jmeno):
        return git("--git-dir", str(self.origin), "show", "main:" + jmeno)

    def test_bez_soubehu_data_pushne(self):
        r = self.spust()
        self.assertEqual(r.returncode, 0, self.log.read_text(encoding="utf-8"))
        self.assertIn("novy", self.origin_soubor("data/projekty.generated.json"))
        self.assertIn("pushnuto", self.log.read_text(encoding="utf-8"))

    def test_soubeh_s_deployem_data_presto_dojdou(self):
        self.env["SOUBEH_ORIGIN"] = self.origin.as_posix()
        self.env["SOUBEH_ZNACKA"] = (self.tmp / "soubeh-hotov").as_posix()
        r = self.spust()
        log = self.log.read_text(encoding="utf-8")
        self.assertEqual(r.returncode, 0, log)
        self.assertEqual(self.origin_soubor("index.html"), "deploy\n")
        self.assertIn("novy", self.origin_soubor("data/projekty.generated.json"))
        self.assertIn("pushnuto", log)


if __name__ == "__main__":
    unittest.main()
