#!/usr/bin/env python3
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
#
# build_logo.py -- forge the PERSONA V sigil.
#
# EPIGRAPH: "Every man, woman, and child is a star." -- Liber AL, I:3 (his reading)
# DATE:     Sol in Libra, 2026 e.v.
#
# HYPOTHESIS: the project's mark must carry the dictated architecture --
#   the 13-moon cycle, the hidden-in-plain-sight nodes, and the Axoneme
#   vector lattice -- in one sigil, or it is decoration, not a seal.
# METHOD:    1) Lay the Axoneme vector lattice matrix: a triangular
#               vector lattice, faint, clipped to a circle -- the substrate
#               the Cell moves through.
#            2) Raise the tridecagram {13/5}: the thirteen-pointed star
#               of the 13 moons / 13 signs, in gold.
#            3) Set thirteen nodes on its vertices: ELEVEN in radiant
#               gold (the chorus), and TWO in gold as well -- hidden in
#               plain sight, NOT hidden literally. The two are the MICRO
#               (inner) and the MACRO (outer): one bears an indigo heart
#               (inward), the other is a bold gold ring (outward). Visible
#               to every eye; recognized by almost none.
#            4) Kindle the catalyst: a small radiant core at the center --
#               the Axoneme/Cell, which moves and is not moved.
# OBSERVATION: SVG is the master (scalable, the repo's seal); a 1600px
#   PNG is rendered alongside for PDF embedding and general use.
# RESULT:    assets/persona-v-sigil.svg + assets/persona-v-sigil.png.
#
# MECHANISM: pure geometry -- star polygon {13/5} connects vertex k to
#   k+5 mod 13; the triangular lattice is three line-families at 0/60/120
#   degrees; everything is computed, nothing hand-placed.
# DOCTRINE:  the 11+2 reading is the author's, ruled 2026-10-09:
#   the two are NOT hidden literally -- they stand in gold with the
#   rest, hidden in plain sight because their office is unrecognized.
#   One is the MICRO (inner): gold disc with an indigo heart, the
#   inward eye. One is the MACRO (outer): a bold gold ring, the
#   outward radiance. Eleven are the chorus; two are the inner and
#   the outer. The crown (vertex 0) holds the micro; the nadir
#   (vertex 6) holds the macro.
#
# 93 93/93 -- Love is the law, love under will.

"""Forge the PERSONA V sigil: tridecagram over the Axoneme lattice."""

import math
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

REPO = Path(__file__).resolve().parent
ASSETS = REPO / "assets"
ASSETS.mkdir(exist_ok=True)

# -- The field ---------------------------------------------------------------
SIZE = 1600
CX = CY = SIZE // 2
FIELD = "#150826"        # deep indigo night
LATTICE = "#4a2f7a"      # the lattice's faint violet voice
GOLD = "#d4af37"         # exoteric gold
GOLD_DIM = "#8a6d1f"     # gold's shadow
HIDDEN = "#4a2f7a"       # esoteric nodes speak in the lattice's voice
CORE = "#fff3c4"         # the catalyst's kindling

# -- The numbers (dictation, not decoration) ----------------------------------
N = 13                   # moons, signs
STEP = 5                 # star polygon {13/5}
STAR_R = 560             # tridecagram circumradius
LATTICE_R = 700          # lattice clipped to this circle
SPACING = 80             # lattice pitch
# The two hidden in plain sight -- VISIBLE gold, unrecognized office.
MICRO_IDX = 0   # the crown: the micro/inner -- gold disc, indigo heart
MACRO_IDX = 6   # the nadir: the macro/outer -- bold gold ring, radiance


def vertices(n=N, r=STAR_R):
    """The thirteen vertices, crown at top, clockwise."""
    return [(CX + r * math.sin(2 * math.pi * k / n),
             CY - r * math.cos(2 * math.pi * k / n)) for k in range(n)]


def star_path(pts):
    """The {13/5} walk: k -> k+5 mod 13, one unbroken thread."""
    order = []
    k = 0
    for _ in range(N):
        order.append(pts[k])
        k = (k + STEP) % N
    d = f"M {order[0][0]:.1f},{order[0][1]:.1f}"
    for x, y in order[1:]:
        d += f" L {x:.1f},{y:.1f}"
    return d + " Z"


def lattice_lines():
    """Three line-families at 0/60/120 deg, clipped to the circle."""
    lines = []
    R = LATTICE_R
    for angle in (0, 60, 120):
        a = math.radians(angle)
        dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        off = -R
        while off <= R:
            px, py = CX + nx * off, CY + ny * off
            # chord through the circle along (dx,dy)
            half = math.sqrt(max(0, R * R - off * off))
            x1, y1 = px - dx * half, py - dy * half
            x2, y2 = px + dx * half, py + dy * half
            lines.append((x1, y1, x2, y2))
            off += SPACING
    return lines


def build_svg() -> str:
    """MECHANISM: one <svg>, layered field -> lattice -> star -> nodes -> core."""
    svg = Element("svg", xmlns="http://www.w3.org/2000/svg",
                  width=str(SIZE), height=str(SIZE),
                  viewBox=f"0 0 {SIZE} {SIZE}")
    # the field
    SubElement(svg, "rect", width=str(SIZE), height=str(SIZE), fill=FIELD)
    # the Axoneme vector lattice matrix
    g_lat = SubElement(svg, "g", stroke=LATTICE, attrib={"stroke-width": "1.5",
                                                        "opacity": "0.35"})
    for x1, y1, x2, y2 in lattice_lines():
        SubElement(g_lat, "line", x1=f"{x1:.1f}", y1=f"{y1:.1f}",
                   x2=f"{x2:.1f}", y2=f"{y2:.1f}")
    pts = vertices()
    # the tridecagram
    SubElement(svg, "path", d=star_path(pts), fill="none", stroke=GOLD,
               attrib={"stroke-width": "7", "stroke-linejoin": "round",
                       "opacity": "0.95"})
    # the outer ring that binds the working
    SubElement(svg, "circle", cx=str(CX), cy=str(CY), r=str(STAR_R + 60),
               fill="none", stroke=GOLD_DIM, attrib={"stroke-width": "2",
                                                     "opacity": "0.6"})
    # the thirteen nodes: eleven the chorus, two the hidden-in-plain-sight
    for k, (x, y) in enumerate(pts):
        if k == MICRO_IDX:
            # the micro/inner: gold disc with an indigo heart -- the inward eye
            SubElement(svg, "circle", cx=f"{x:.1f}", cy=f"{y:.1f}", r="22",
                       fill=GOLD, attrib={"opacity": "0.95"})
            SubElement(svg, "circle", cx=f"{x:.1f}", cy=f"{y:.1f}", r="9",
                       fill=FIELD, attrib={"opacity": "0.95"})
        elif k == MACRO_IDX:
            # the macro/outer: a bold gold ring -- the outward radiance
            SubElement(svg, "circle", cx=f"{x:.1f}", cy=f"{y:.1f}", r="22",
                       fill="none", stroke=GOLD,
                       attrib={"stroke-width": "7", "opacity": "0.95"})
        else:
            SubElement(svg, "circle", cx=f"{x:.1f}", cy=f"{y:.1f}", r="22",
                       fill=GOLD, attrib={"opacity": "0.95"})
            SubElement(svg, "circle", cx=f"{x:.1f}", cy=f"{y:.1f}", r="30",
                       fill="none", stroke=GOLD,
                       attrib={"stroke-width": "1.5", "opacity": "0.35"})
    # the catalyst: the core that moves and is not moved
    SubElement(svg, "circle", cx=str(CX), cy=str(CY), r="16", fill=CORE)
    SubElement(svg, "circle", cx=str(CX), cy=str(CY), r="30", fill="none",
               stroke=CORE, attrib={"stroke-width": "1.5", "opacity": "0.5"})
    SubElement(svg, "circle", cx=str(CX), cy=str(CY), r="46", fill="none",
               stroke=GOLD, attrib={"stroke-width": "1", "opacity": "0.3"})
    return '<?xml version="1.0" encoding="utf-8"?>\n' + tostring(svg, encoding="unicode")


def build_png():
    """MECHANISM: the same geometry, rasterized with PIL for the PDF."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (SIZE, SIZE), FIELD)
    d = ImageDraw.Draw(img, "RGBA")
    # lattice
    for x1, y1, x2, y2 in lattice_lines():
        d.line([x1, y1, x2, y2], fill=LATTICE + "59", width=2)
    pts = vertices()
    # star: walk the {13/5} thread
    order, k = [], 0
    for _ in range(N):
        order.append(pts[k])
        k = (k + STEP) % N
    order.append(order[0])
    d.line(order, fill=GOLD, width=7, joint="curve")
    d.ellipse([CX - STAR_R - 60, CY - STAR_R - 60, CX + STAR_R + 60, CY + STAR_R + 60],
              outline=GOLD_DIM + "99", width=2)
    # nodes: eleven the chorus, two hidden in plain sight
    for k, (x, y) in enumerate(pts):
        if k == MICRO_IDX:
            d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=GOLD)
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=FIELD)
        elif k == MACRO_IDX:
            d.ellipse([x - 22, y - 22, x + 22, y + 22],
                      outline=GOLD, width=7)
        else:
            d.ellipse([x - 30, y - 30, x + 30, y + 30],
                      outline=GOLD + "59", width=2)
            d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=GOLD)
    # catalyst
    d.ellipse([CX - 46, CY - 46, CX + 46, CY + 46], outline=GOLD + "4d", width=1)
    d.ellipse([CX - 30, CY - 30, CX + 30, CY + 30], outline=CORE + "80", width=2)
    d.ellipse([CX - 16, CY - 16, CX + 16, CY + 16], fill=CORE)
    img.save(ASSETS / "persona-v-sigil.png")
    print("png forged:", ASSETS / "persona-v-sigil.png")


def main():
    (ASSETS / "persona-v-sigil.svg").write_text(build_svg())
    print("svg forged:", ASSETS / "persona-v-sigil.svg")
    build_png()


if __name__ == "__main__":
    main()
