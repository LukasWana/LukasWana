"""Generátor textury pozadí Papír (inspirace uživatele 2026-10-11: starý béžový papír).

Dlaždice 640 × 640: jemné zrno (feTurbulence), tenké mírně zakřivené škrábance a smítka.
Škrábanec, který přesahuje okraj dlaždice, se kreslí i posunutý o dlaždici, takže šev není vidět.
Ztmavené strany a tón od motivu nejsou v SVG — jsou v skiny.css nad touto texturou.
Náhoda má pevné semínko, výstup je deterministický.

Použití: python tools/papir.py   → zapíše img/papir-svetly.svg a img/papir-tmavy.svg
"""
import math
import random
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
W = H = 640


def svg(svetly, seed=7):
    r = random.Random(seed)
    el = []
    # zrno: drobné (frekvence 1.6), v alfě jen slabě; tmavý režim světlé zrno, světlý hnědé
    if svetly:
        zrno = "0 0 0 0 .38 0 0 0 0 .30 0 0 0 0 .16 0 0 0 .55 -.17"
    else:
        zrno = "0 0 0 0 1 0 0 0 0 .95 0 0 0 0 .85 0 0 0 .26 -.09"
    el.append("<filter id='z'><feTurbulence type='fractalNoise' baseFrequency='1.6' numOctaves='2' "
              f"stitchTiles='stitch'/><feColorMatrix values='{zrno}'/></filter>")
    el.append(f"<rect width='{W}' height='{H}' filter='url(#z)'/>")
    # škrábance: světlé (odřený povrch) i tmavší
    for _ in range(90):
        x0, y0 = r.uniform(0, W), r.uniform(0, H)
        delka = r.choice([r.uniform(30, 120), r.uniform(120, 420)])
        uhel = r.uniform(0, 3.1416)
        dx, dy = math.cos(uhel) * delka, math.sin(uhel) * delka
        cx = x0 + dx / 2 + r.uniform(-25, 25)
        cy = y0 + dy / 2 + r.uniform(-25, 25)
        svetla = r.random() < 0.65
        if svetly:
            barva = "#fff" if svetla else "#8a6a3a"
            op = r.uniform(.35, .7) if svetla else r.uniform(.10, .22)
        else:
            barva = "#fff" if svetla else "#000"
            op = r.uniform(.05, .11) if svetla else r.uniform(.15, .3)
        sw = r.uniform(.35, .9)
        d = f"M{x0:.0f} {y0:.0f}Q{cx:.0f} {cy:.0f} {x0 + dx:.0f} {y0 + dy:.0f}"
        xs, ys = (x0, cx, x0 + dx), (y0, cy, y0 + dy)
        for ox in (-W, 0, W):
            for oy in (-H, 0, H):
                if max(xs) + ox < 0 or min(xs) + ox > W or max(ys) + oy < 0 or min(ys) + oy > H:
                    continue
                t = "" if ox == oy == 0 else f" transform='translate({ox} {oy})'"
                el.append(f"<path d='{d}'{t} stroke='{barva}' stroke-opacity='{op:.2f}' "
                          f"stroke-width='{sw:.2f}' fill='none'/>")
    # smítka
    for _ in range(160):
        x, y = r.uniform(0, W), r.uniform(0, H)
        rr = r.choice([r.uniform(.3, .7), r.uniform(.7, 1.4)])
        barva = "#7a5a2e" if svetly else "#e8dcc4"
        op = r.uniform(.15, .45) if svetly else r.uniform(.06, .16)
        el.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{rr:.1f}' fill='{barva}' fill-opacity='{op:.2f}'/>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}'>" + "".join(el) + "</svg>"


if __name__ == "__main__":
    for nazev, svetly in (("papir-svetly.svg", True), ("papir-tmavy.svg", False)):
        (KOREN / "img" / nazev).write_text(svg(svetly), encoding="utf-8", newline="")
