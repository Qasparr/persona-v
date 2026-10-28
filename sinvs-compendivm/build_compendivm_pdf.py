#!/usr/bin/env python3
# 93 — COMPENDIVM PDF builder. MECHANISM: renders COMPENDIVM.md (headings,
# tables, fences, bullets, chart images) with fpdf2 + DejaVu. DOCTRINE: the
# PDF is a rendering of the MD of record; nothing is added in the rendering.
import os, re
from fpdf import FPDF
D = os.path.dirname(os.path.abspath(__file__))
FD = '/usr/share/fonts/truetype/dejavu'
class PDF(FPDF):
    def footer(self):
        self.set_y(-14); self.set_font('DVS','',7.5)
        self.cell(0, 8, f'— {self.page_no()} of {{nb}} — | All Rights Reserved, Without Prejudice | Flagpole of Claim and Coinage reserved', align='C')
pdf = PDF(format='letter')
pdf.add_font('DVS','',os.path.join(FD,'DejaVuSans.ttf'))
pdf.add_font('DVS','B',os.path.join(FD,'DejaVuSans-Bold.ttf'))
pdf.add_font('DVM','',os.path.join(FD,'DejaVuSansMono.ttf'))
pdf.set_auto_page_break(True, margin=20)
pdf.add_page()
W = pdf.w - pdf.l_margin - pdf.r_margin
def H(txt, size, bold=True):
    pdf.set_font('DVS','B' if bold else '',size); pdf.multi_cell(0, size*0.52, txt); pdf.ln(2.2)
def P(txt, size=10):
    pdf.set_font('DVS','',size); pdf.multi_cell(0, 5.4, txt); pdf.ln(1.8)
def M(txt, size=8.6):
    pdf.set_font('DVM','',size); pdf.multi_cell(0, 4.8, txt); pdf.ln(1.2)
lines = open(os.path.join(D,'COMPENDIVM.md'), encoding='utf-8').read().split('\n')
in_fence = False
for ln in lines:
    s = ln.rstrip()
    if s.startswith('```'): in_fence = not in_fence; continue
    if in_fence: M(s if s else ' '); continue
    m = re.match(r'!\[.*\]\((.+)\)', s)
    if m:
        p = os.path.join(D, m.group(1))
        if os.path.exists(p):
            pdf.image(p, w=W); pdf.ln(3)
        continue
    if s.startswith('# '): H(s[2:], 17)
    elif s.startswith('## '): H(s[3:], 13.5)
    elif s.startswith('### '): H(s[4:], 11.5)
    elif s.startswith('|'):
        cells = [c.strip().replace('**','') for c in s.strip('|').split('|')]
        if all(set(c) <= set('-: ') for c in cells): continue
        M(' | '.join(cells), 8.2)
    elif s.startswith('---'): pdf.ln(2)
    elif s.strip() == '': pdf.ln(1.2)
    else:
        t = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
        t = re.sub(r'\*(.+?)\*', r'\1', t).replace('`','')
        P(t)
pdf.output(os.path.join(D,'COMPENDIVM.pdf'))
print('COMPENDIVM.pdf pages:', pdf.pages_count)
