"""Generátor inkoustových tahů štětcem (ensō a podtah) jako SVG s vyplněným obrysem.

Tah = středová křivka c(t) a šířka w(t), t ∈ [0, 1]. Obrys = levý okraj tam, pravý zpět,
převedený Catmull-Rom → kubické Bézierovy křivky. Suchý konec štětce = vlákna: na začátku
dojezdu společně pokrývají celou šířku tahu, pak se každé zužuje ke svému středu a končí
jinde, takže mezi nimi postupně prosvítá papír. Bez náhody — výstup je deterministický.

Použití: python tools/enso.py   → zapíše img/enso.svg a img/tah.svg
"""
import math
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
# Inkoust celé stránky: o kousek stažená černá místo #000 (pokyn uživatele 2026-10-11). Stejná hodnota
# je v style.css jako --inkoust; test tests/test_stranka.py hlídá, že se shodují.
INKOUST = "#1a1a1a"


def _f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def _roh(a, b, c, prah=math.radians(50)):
    """Je bod b ostrý roh (obrys v něm zatočí o víc než prah, nebo sousedí s nulovou délkou)?"""
    v1, v2 = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
    d1, d2 = math.hypot(*v1), math.hypot(*v2)
    if d1 < 1e-6 or d2 < 1e-6:
        return True
    cos = (v1[0] * v2[0] + v1[1] * v2[1]) / (d1 * d2)
    return math.acos(max(-1.0, min(1.0, cos))) > prah


def _bezier(body):
    """Uzavřená Catmull-Rom křivka přes body → SVG path z kubických Bézierových segmentů.

    V ostrém rohu (useknutý konec tahu, začátek vlákna) je tečna nulová — jinak by křivka
    přestřelila ven z tahu a na obrysu by vyčníval hrot.
    """
    n = len(body)
    rohy = [_roh(body[i - 1], body[i], body[(i + 1) % n]) for i in range(n)]
    d = [f"M{_f(body[0][0])} {_f(body[0][1])}"]
    for i in range(n):
        j = (i + 1) % n
        p0, p1, p2, p3 = body[i - 1], body[i], body[j], body[(i + 2) % n]
        c1 = p1 if rohy[i] else (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = p2 if rohy[j] else (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(p2[0])} {_f(p2[1])}")
    return "".join(d) + "Z"


def _hladka(t, a, b):
    """Hladký přechod 0 → 1 mezi a a b (smoothstep)."""
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    u = (t - a) / (b - a)
    return u * u * (3 - 2 * u)


def obrys(stred, sirka, t0, t1, vzorku, pas=lambda t: (0.0, 1.0), cepicka=False):
    """Vyplněný obrys tahu mezi t0 a t1.

    stred(t) → (x, y); sirka(t) → šířka těla v px; pas(t) → (od, do), zlomky šířky těla
    (0 = levý okraj, 1 = pravý), které tento obrys pokrývá — celé tělo je (0, 1), vlákno užší pás.
    cepicka=True přidá na začátek kulaté nasazení štětce (půlkruh za bodem t0).
    """
    levy, pravy = [], []
    for i in range(vzorku + 1):
        t = t0 + (t1 - t0) * i / vzorku
        x, y = stred(t)
        (xa, ya), (xb, yb) = stred(max(0.0, t - 1e-4)), stred(min(1.0, t + 1e-4))
        delka = math.hypot(xb - xa, yb - ya) or 1.0
        nx, ny = -(yb - ya) / delka, (xb - xa) / delka
        w = sirka(t)
        od, do = pas(t)
        levy.append((x + nx * (od - 0.5) * w, y + ny * (od - 0.5) * w))
        pravy.append((x + nx * (do - 0.5) * w, y + ny * (do - 0.5) * w))
    body = levy + pravy[::-1]
    if cepicka:
        x, y = stred(t0)
        (xa, ya), (xb, yb) = stred(t0), stred(t0 + 1e-4)
        delka = math.hypot(xb - xa, yb - ya) or 1.0
        tx, ty = (xb - xa) / delka, (yb - ya) / delka  # směr tahu
        r = sirka(t0) / 2
        zacatek_uhlu = math.atan2(tx, -ty)  # normála k pravému okraji; +π vede přes zadní stranu k levému
        for k in range(1, 8):
            u = zacatek_uhlu + math.pi * k / 8
            body.append((x + r * math.cos(u) - tx * r * 0.3 * math.sin(math.pi * k / 8),
                         y + r * math.sin(u) - ty * r * 0.3 * math.sin(math.pi * k / 8)))
    return _bezier(body)


def _vlakna(stred, sirka, zacatek, specifikace, vzorku):
    """Suché vlákno: (střed pásu, výsledná šířka pásu, kde skončí). Na začátku pokrývají celou šířku."""
    cesty = []
    n = len(specifikace)
    for k, (m, h_konec, konec) in enumerate(specifikace):
        h0 = 0.5 / n + 0.06  # překryv sousedů na začátku dojezdu → žádná náhlá mezera
        m0 = (k + 0.5) / n

        def pas(t, m=m, m0=m0, h0=h0, h_konec=h_konec, konec=konec):
            u = _hladka(t, zacatek, konec)
            stred_pasu = m0 + (m - m0) * u
            pul = h0 + (h_konec / 2 - h0) * min(1.0, u * 1.6)
            pul *= 1 - u ** 3  # na konci se vlákno ztratí do nuly
            return max(0.0, stred_pasu - pul), min(1.0, stred_pasu + pul)  # nevyčnívat z těla

        cesty.append(obrys(stred, sirka, zacatek, konec, vzorku, pas))
    return cesty


def enso(velikost=400):
    """Ensō: kruh jedním tahem; nasazení vlevo, tah po směru hodin, mezera a suchý konec vlevo dole."""
    s = velikost
    cx, cy, R = s / 2, s / 2, s * 0.37
    zacatek, oblouk = math.radians(195), math.radians(318)
    W = s * 0.072

    def stred(t):
        uhel = zacatek - oblouk * t
        r = R * (1 + 0.03 * math.sin(2 * math.pi * (0.85 * t + 0.1)) - 0.035 * t)
        return cx + r * math.cos(uhel), cy - r * math.sin(uhel)

    def sirka(t):
        nasazeni = 0.75 + 0.55 * _hladka(t, 0.0, 0.05) - 0.3 * _hladka(t, 0.05, 0.22)
        dech = 1 + 0.1 * math.sin(2 * math.pi * (1.3 * t + 0.35))
        dojezd = 1 - 0.45 * _hladka(t, 0.5, 0.95)
        return W * nasazeni * dech * dojezd

    # hodně suchý konec (varianta C, rozhodnutí uživatele 10. 10.): štětec vysychá už od 0,6,
    # 7 tenkých vláken končí na různých místech, takže tah se postupně rozpadá
    zacatek_suche = 0.6
    cesty = [obrys(stred, sirka, 0.0, zacatek_suche + 0.01, 100, cepicka=True)]
    cesty += _vlakna(stred, sirka, zacatek_suche,
                     [(0.03, 0.06, 0.98), (0.17, 0.10, 0.80), (0.32, 0.05, 1.0), (0.48, 0.09, 0.74),
                      (0.63, 0.05, 0.93), (0.79, 0.08, 0.84), (0.95, 0.06, 0.70)], 50)
    return cesty


def podtah(sirka_px=240, vyska_px=24):
    """Krátký vodorovný tah pod nadpis: mírný oblouk, nasazení vlevo, suchý konec vpravo."""
    W = vyska_px * 0.4

    def stred(t):
        return sirka_px * (0.04 + 0.92 * t), vyska_px * (0.56 - 0.16 * math.sin(math.pi * t))

    def sirka(t):
        return W * (0.8 + 0.3 * _hladka(t, 0.0, 0.06) - 0.45 * _hladka(t, 0.45, 0.95))

    cesty = [obrys(stred, sirka, 0.0, 0.79, 60, cepicka=True)]
    cesty += _vlakna(stred, sirka, 0.78, [(0.12, 0.14, 0.97), (0.5, 0.12, 1.0), (0.85, 0.16, 0.92)], 30)
    return cesty


def svg(cesty, sirka_px, vyska_px):
    d = "".join(f'<path d="{c}"/>' for c in cesty)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sirka_px} {vyska_px}">'
            f'<g fill="{INKOUST}">{d}</g></svg>\n')


def main():
    (KOREN / "img").mkdir(exist_ok=True)
    for jmeno, obsah in (("img/enso.svg", svg(enso(400), 400, 400)),
                         ("img/tah.svg", svg(podtah(240, 24), 240, 24))):
        with open(KOREN / jmeno, "w", encoding="utf-8", newline="\n") as f:
            f.write(obsah)
        print(f"zapsáno {jmeno}: {len(obsah)} B")


if __name__ == "__main__":
    main()
