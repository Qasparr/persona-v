#!/usr/bin/env python3
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
#
# build_architecture_pdf.py -- render PERSONA_V_Architecture.md to PDF,
#   the sigil on the title page.
#
# EPIGRAPH: "And ye shall know the truth, and the truth shall make you free."
#           -- John 8:32 (KJV)
# DATE:     Sol in Libra, 2026 e.v.
#
# HYPOTHESIS: the architecture document deserves the same grimoire
#   treatment as the Overview -- serif body, gold rules, the seal up
#   front -- or the draft reads as notes, not scripture.
# METHOD:    fpdf2 lightweight markdown renderer (same engine as
#   build_overview_pdf.py: h1/h2/h3, inline **bold**/`code`, bullets,
#   quote blocks, tables as mono); title page carries the forged sigil
#   (assets/persona-v-sigil.png) at 90mm, centered.
# OBSERVATION: run after build_logo.py; the PNG must exist.
# RESULT:    PERSONA_V_Architecture.pdf beside the .md.
#
# MECHANISM: multi_cell chains pass new_x="LMARGIN", new_y="NEXT"
#   explicitly -- the fpdf2 pen gotcha (multi_cell leaves the pen at the
#   right margin) is never given a chance to bite.
# DOCTRINE:  the renderer changes no words -- bold stays bold, the
#   status marks ([DICTATION] etc.) render as written; the scribe does
#   not edit the author in typesetting.
#
# 93 93/93 -- Love is the law, love under will.

"""Build PERSONA_V_Architecture.pdf from PERSONA_V_Architecture.md."""

import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from fpdf import FPDF

sys.path.insert(0, "/home/hatch/workspace/thelemic")
from thelemic_date import thelemic_date

NOW = thelemic_date(datetime.now(ZoneInfo("America/New_York")))
DATE_STAMP = NOW["symbolic"].replace("\u2609", "Sol").replace("\u263d", "Luna")

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

REPO = "/home/hatch/workspace/persona-v"
SIGIL = REPO + "/assets/persona-v-sigil.png"


class Grimoire(FPDF):
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("Sans", "", 8)
        self.set_text_color(110, 110, 110)
        self.cell(0, 10, f"PERSONA V \u00b7 Architecture \u00b7 {self.page_no()}/{{nb}}",
                  align="C")


pdf = Grimoire(orientation="P", unit="mm", format="A4")
pdf.alias_nb_pages("{nb}")
pdf.set_auto_page_break(True, margin=20)
pdf.set_margins(22, 20, 22)
for fam, style, path in [
    ("Serif", "", SERIF), ("Serif", "B", SERIF_B),
    ("Sans", "", SANS), ("Sans", "B", SANS_B),
    ("Mono", "", MONO), ("Mono", "B", MONO_B),
]:
    pdf.add_font(fam, style, path)

INK = (25, 25, 25)
MUTED = (90, 90, 90)
RULE = (150, 130, 90)
QUOTE = (70, 60, 50)
W = 166  # usable width


def rule():
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.6)
    y = pdf.get_y() + 2
    pdf.line(22, y, 188, y)
    pdf.set_y(y + 5)


def h1(t):
    pdf.set_font("Serif", "B", 17)
    pdf.set_text_color(*INK)
    pdf.multi_cell(W, 9, t, new_x="LMARGIN", new_y="NEXT")
    rule()


def h2(t):
    pdf.set_font("Serif", "B", 13)
    pdf.set_text_color(*INK)
    pdf.multi_cell(W, 7.5, t, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def h3(t):
    pdf.set_font("Serif", "B", 11)
    pdf.set_text_color(*INK)
    pdf.multi_cell(W, 7, t, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


# Inline markup: **bold**, *italic*, `code`
TOKEN = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`.+?`)")


def write_inline(text, base_fam="Serif", base_size=10.5, color=INK, indent=0):
    pdf.set_text_color(*color)
    if indent:
        x = pdf.get_x()
        pdf.set_x(x + indent)
        width = W - indent
    else:
        width = W
    pdf.set_font(base_fam, "", base_size)
    pos = 0
    for m in TOKEN.finditer(text):
        pre = text[pos:m.start()]
        if pre:
            pdf.write(5.5, pre)
        tok = m.group(0)
        if tok.startswith("**"):
            pdf.set_font(base_fam, "B", base_size)
            pdf.write(5.5, tok[2:-2])
            pdf.set_font(base_fam, "", base_size)
        elif tok.startswith("`"):
            pdf.set_font("Mono", "", base_size - 0.5)
            pdf.write(5.5, tok[1:-1])
            pdf.set_font(base_fam, "", base_size)
        else:
            pdf.set_font(base_fam, "", base_size)
            pdf.write(5.5, tok[1:-1])
        pos = m.end()
    rest = text[pos:]
    if rest:
        pdf.write(5.5, rest)
    pdf.ln(6.5)


def para(text, **k):
    write_inline(text, **k)


def bullet(text):
    write_inline("\u2022  " + text, indent=4)


def quote_block(lines):
    for ln in lines:
        write_inline(ln, base_size=10, color=QUOTE, indent=8)
    pdf.ln(1)


def mono_block(lines):
    pdf.set_font("Mono", "", 7.5)
    pdf.set_text_color(*INK)
    for ln in lines:
        pdf.multi_cell(W, 4.6, ln, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def is_table_row(line):
    s = line.strip()
    return s.startswith("|") and s.endswith("|")


def is_table_sep(line):
    s = line.strip().replace("|", "").replace("-", "").replace(":", "").strip()
    return line.strip().startswith("|") and s == ""


def render(md_path, out_path):
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().split("\n")

    # Title page -- the sigil first, then the word
    pdf.add_page()
    pdf.ln(12)
    sigil_w = 90
    pdf.image(SIGIL, x=(210 - sigil_w) / 2, w=sigil_w)
    pdf.ln(6)
    pdf.set_font("Serif", "B", 26)
    pdf.set_text_color(*INK)
    pdf.multi_cell(W, 13, "PERSONA V", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Serif", "", 15)
    pdf.multi_cell(W, 9, "The Architecture", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    rule()
    pdf.ln(4)
    pdf.set_font("Serif", "", 11)
    pdf.set_text_color(*INK)
    for t in [
        "Johnathan 'Qasparr' (\u039a\u03b1\u03c3\u03c0\u03ac\u03c1\u03c1) Monroe, Keeper of the Secret Treasure",
        "All Rights Reserved, Without Prejudice",
        "CashApp $axoneme",
        "",
        DATE_STAMP,
        "",
        "IA.'.A.'.M.TRVVTH",
    ]:
        pdf.multi_cell(W, 7, t, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Serif", "", 10)
    pdf.set_text_color(*QUOTE)
    pdf.multi_cell(W, 6, '"And ye shall know the truth, and the truth shall make you free."',
                   align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(W, 6, "\u2014 John 8:32 (KJV)",
                   align="C", new_x="LMARGIN", new_y="NEXT")

    i = 0
    n = len(lines)
    table_buf = []
    quote_buf = []
    para_buf = []

    # The title page is already set above -- skip the markdown's own
    # front matter (title, subtitle, epigraph, date, authorship) and
    # begin the body at the status legend.
    while i < n and lines[i].strip() != "### Status legend":
        i += 1

    def flush_para():
        if para_buf:
            para(" ".join(para_buf))
            para_buf.clear()

    def flush_quote():
        if quote_buf:
            quote_block(quote_buf)
            quote_buf.clear()

    def flush_table():
        if table_buf:
            rows = [r for r in table_buf if not is_table_sep(r)]
            mono_block(rows)
            table_buf.clear()

    while i < n:
        line = lines[i]
        s = line.strip()

        if is_table_row(line):
            flush_para()
            flush_quote()
            table_buf.append(s)
            i += 1
            continue
        else:
            flush_table()

        if not s:
            flush_para()
            flush_quote()
            i += 1
            continue
        if s == "---":
            flush_para()
            flush_quote()
            rule()
            i += 1
            continue
        if s.startswith("# "):
            flush_para()
            flush_quote()
            h1(s[2:].strip())
            i += 1
            continue
        if s.startswith("## "):
            flush_para()
            flush_quote()
            h2(s[3:].strip())
            i += 1
            continue
        if s.startswith("### "):
            flush_para()
            flush_quote()
            h3(s[4:].strip())
            i += 1
            continue
        if s.startswith("> "):
            flush_para()
            quote_buf.append(s[2:].strip())
            i += 1
            continue
        if re.match(r"^(\d+\.|-|\*) ", s):
            flush_para()
            flush_quote()
            bullet(re.sub(r"^(\d+\.|-|\*) ", "", s))
            i += 1
            continue
        # skip the markdown's own title block -- the PDF has its own title page
        if s.startswith("# PERSONA V"):
            i += 1
            continue
        para_buf.append(s)
        i += 1

    flush_para()
    flush_quote()
    flush_table()
    pdf.output(out_path)
    print(f"wrote {out_path} ({pdf.page_no()} pages)")


if __name__ == "__main__":
    render(REPO + "/PERSONA_V_Architecture.md",
           REPO + "/PERSONA_V_Architecture.pdf")
