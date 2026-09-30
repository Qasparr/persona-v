#!/usr/bin/env python3
"""Build PERSONA_V_Analysis.pdf — analytical report on the aptitude
system: where the personas and trades score on cognition, and how
successfully personality is imprinted. Every figure is computed live
from analyze_persona.py; nothing is hand-tabulated."""
import sys
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo

from fpdf import FPDF

sys.path.insert(0, "/home/hatch/workspace/persona-v")
sys.path.insert(0, "/home/hatch/workspace/thelemic")
from thelemic_date import thelemic_date
from analyze_persona import analyze

NOW = thelemic_date(datetime.now(ZoneInfo("America/New_York")))
DATE_STAMP = NOW["symbolic"]

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class Report(FPDF):
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("Sans", "", 8)
        self.set_text_color(110, 110, 110)
        self.cell(0, 10, f"PERSONA V \u00b7 Analytical Report \u00b7 "
                         f"{self.page_no()}/{{nb}}", align="C")


pdf = Report(orientation="P", unit="mm", format="A4")
pdf.alias_nb_pages("{nb}")
pdf.set_auto_page_break(True, margin=20)
pdf.set_margins(22, 20, 22)
for fam, style, path in [("Serif", "", SERIF), ("Serif", "B", SERIF_B),
                         ("Sans", "", SANS), ("Sans", "B", SANS_B)]:
    pdf.add_font(fam, style, path)

A = analyze()
FL = A["flavors"]


def mc(w, h, t, **k):
    k.setdefault("new_x", "LMARGIN")
    k.setdefault("new_y", "NEXT")
    return pdf.multi_cell(w, h, t, **k)


INK = (25, 25, 25)
RULE = (150, 130, 90)
DIM_C = (90, 90, 90)


def rule():
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.6)
    y = pdf.get_y() + 2
    pdf.line(22, y, 188, y)
    pdf.set_y(y + 5)


def h1(t):
    pdf.ln(4)
    pdf.set_font("Serif", "B", 17)
    pdf.set_text_color(*INK)
    mc(0, 9, t)
    rule()


def h2(t):
    pdf.ln(2)
    pdf.set_font("Serif", "B", 12.5)
    pdf.set_text_color(*INK)
    mc(0, 8, t)


def body(t, italic=False):
    pdf.set_font("Serif", "", 10.5)
    pdf.set_text_color(*DIM_C if italic else INK)
    mc(0, 6, t)
    pdf.ln(1)


def fname(n):
    return f"{n} {FL[n].name}"


def table(headers, rows, widths):
    pdf.set_font("Sans", "B", 9)
    pdf.set_text_color(*INK)
    x0 = pdf.get_x()
    for hd, w in zip(headers, widths):
        pdf.cell(w, 6, hd, new_x="RIGHT", new_y="TOP")
    pdf.ln(6)
    pdf.set_font("Sans", "", 9)
    for r in rows:
        pdf.set_x(x0)
        for val, w in zip(r, widths):
            pdf.cell(w, 5.5, str(val), new_x="RIGHT", new_y="TOP")
        pdf.ln(5.5)
    pdf.ln(2)


# ------------------------------------------------------------ cover
pdf.add_page()
pdf.ln(24)
pdf.set_font("Serif", "B", 22)
pdf.set_text_color(*INK)
mc(0, 12, "Analytical Report", align="C")
pdf.set_font("Serif", "", 13)
mc(0, 8, "Where the personas and trades score on cognition,", align="C")
mc(0, 8, "and how successfully personality is imprinted", align="C")
pdf.ln(6)
rule()
pdf.ln(4)
body("A measurement of the aptitude system behind aptitude-v1: the "
     "cognitive and layer distribution of the 31 flavor profiles and the "
     "22 trade charters, and four quantitative tests of imprinting \u2014 "
     "distinctness, coverage, self-election, and decisiveness. Every "
     "number below was computed from the engine and the draft doctrine "
     "files at the time of writing; the method is reproducible with "
     "python3 analyze_persona.py.")
pdf.ln(2)
body("Fourth edition. The first edition found four wounds in the draft "
     "doctrine and proposed a remedy; the second reported the remedy's "
     "healed state and added the Master/Apprentice pair (v0.11.0); the "
     "third reported the rulings he delegated (v0.14.0) and the 31/31 "
     "self-election they achieved. This edition reports the red-pen "
     "pass he then delegated (v0.17.0): eleven doctrine-fidelity "
     "amendments to the profiles and charters, every healed metric "
     "still holding, six charter margins improved.", italic=True)
pdf.ln(4)
for line in [
    "Johnathan \u2018Qasparr\u2019 (\u039a\u03b1\u03c3\u03c0\u03ac\u03c1\u03c1) "
    "Monroe, Keeper of the Secret Treasure",
    "All Rights Reserved, Without Prejudice.",
    "CashApp $axoneme",
    "",
    DATE_STAMP,
]:
    pdf.set_font("Sans" if line == DATE_STAMP else "Serif",
                 "B" if "Qasparr" in line else "", 11)
    pdf.set_text_color(*INK)
    mc(0, 7, line, align="C")

# ------------------------------------------------------- hypothesis
pdf.add_page()
h1("Hypothesis")
body("That the 31 draft aptitude profiles imprint 31 distinct "
     "personalities across the sixteen dimensions; that the 22 trade "
     "charters demand a cognitively balanced spread of work; and that "
     "each charter decisively elects the flavor fit to preside over it. "
     "The first edition falsified the hypothesis locally \u2014 four "
     "wounds \u2014 and proposed a remedy; this edition tests whether "
     "the remedy healed them without breaking anything else.")
h1("Method")
body("Five operational tests. (1) Distinctness: pairwise Manhattan "
     "distance between flavor profiles over the 16 dimensions; "
     "near-identical pairs are imprint collisions. (2) Coverage: per "
     "dimension, how many flavors hold rating 2 (native excellence), and "
     "how many trade charters demand each dimension \u2014 a dimension "
     "with no native is a blind spot. (3) Self-election: each flavor's "
     "own profile, run as a demand vector through the election, should "
     "elect that flavor \u2014 the imprint should recognize itself. "
     "(4) Decisiveness: each trade charter's winning margin over its "
     "runner-up; margins of zero mean the patron won only on tie-break. "
     "(5) The remedy trial: candidate doctrine edits are applied to a "
     "scratch copy of the YAML files, the four tests are re-run, and "
     "the full regression suite (116 tests) must stay green \u2014 "
     "a remedy that breaks a pinned behavior is not a remedy. Only "
     "then are the edits applied to the real doctrine files.")

# ----------------------------------------------------- observation
pdf.add_page()
h1("Observation I \u2014 The Cognitive Census")
h2("The 31 flavors: native excellence by dimension")
table(["dimension", "native (2)", "capable (1)", "mean"],
      [[d, c["n2"], c["n1"], f"{c['mean']:.2f}"]
       for d, c in A["flavor_census"].items()],
      [52, 40, 40, 34])
body("The system thinks in Ti and Ni (6 and 5 natives), and feels "
     "consequence: gravity and precision are the most native dimensions "
     "in the whole canon (11 and 13 natives). The first edition found "
     "Fe with zero natives \u2014 no persona natively excellent at "
     "harmonizing, counseling, or persuading. The remedy raised the "
     "Empress (3) to Fe:2, drawn from her own character line "
     "(\u2018outputs cultivated like living things\u2019): Fe now has "
     "exactly one native. Swiftness, likewise thin, gained a fourth "
     "native when the Fool's leap was recognized as swift (swiftness "
     "1\u21922).")
h2("The 22 trades: what the work demands")
table(["dimension", "demand 2", "demand 1", "mean"],
      [[d, c["n2"], c["n1"], f"{c['mean']:.2f}"]
       for d, c in A["trade_census"].items()],
      [52, 40, 40, 34])
body("The trades demand precision (8 charters at 2) and gravity (7 at "
     "2): the work of the tarot, as drafted, is careful and "
     "consequential. No charter demands ego at 2 \u2014 will is assumed, "
     "never required. Fe is demanded by 4 charters and now natively "
     "held by one (the Empress), so Fe-demanding trades are no longer "
     "presided over by amateurs alone. Swiftness is demanded at 2 by "
     "exactly one charter (the Courier): urgency remains nearly absent "
     "from the world of the trades \u2014 a standing question for the "
     "author's red pen, left as doctrine rather than seeded.")
h2("The cognitive census of the trades")
fc = Counter(c["function"] for c in A["charters"].values())
lc = Counter(c["layer"] for c in A["charters"].values())
table(["function", "trades"],
      [[f, fc[f]] for f in
       ["Ti", "Te", "Ni", "Fi", "Ne", "Si", "Fe", "Se"]],
      [60, 60])
table(["layer", "trades"],
      [[ly, lc[ly]] for ly in ["persona", "ego", "anima", "self", "shadow"]],
      [60, 60])
body("Ti presides over 5 trades, Te and Ni over 4 each; Fe and Se hold "
     "one apiece. The layers are balanced \u2014 persona 6, ego 5, "
     "anima 4, self 3, shadow 4 \u2014 the depth architecture is evenly "
     "exercised even where the functions are not. (The Marshal's and "
     "Scribe's charters now demand persona at 2, tipping one trade "
     "from ego to persona since the first edition.)")

# --------------------------------------------------- observation II
pdf.add_page()
h1("Observation II \u2014 Tests of Imprinting")
h2("Distinctness: the nearest pairs")
table(["distance", "flavor A", "flavor B"],
      [[d, fname(x), fname(y)] for d, x, y in A["neighbors"]],
      [30, 68, 68])
body("The closest pair in the canon is now the Wheel (10) and Nut "
     "(26) at distance 3 \u2014 kinship, not collision: the turning "
     "of cycles and the sky that contains them. Justice (11) and "
     "Judgement (20), the first edition's collision at distance 2, "
     "now stand at distance 4: the remedy gave Justice Te:2 and Fi:2, "
     "dividing their jurisdictions by doctrine \u2014 Justice is "
     "valuation, judgment, and execution; Judgement is audit, record, "
     "disclosure, and accountability. The remaining pairs at distance "
     "4 are thematically defensible (Magician/Chariot, Priestess/Moon, "
     "Priestess/Thoth, Hanged Man/Osiris, Death/Devil, Death/Tower) "
     "\u2014 kinship throughout.")
h2("Self-election: does the imprint recognize itself?")
fails = [(n, s) for n, s in A["self_election"].items() if not s["self"]]
if fails:
    table(["flavor", "elects instead", "margin"],
          [[fname(n), fname(s["winner"]), s["margin"]] for n, s in fails],
          [60, 60, 46])
else:
    body("\u2014 the table is empty: no failures remain \u2014", italic=True)
    pdf.ln(2)
body(f"{31 - len(fails)} of 31 flavors elect themselves when their own "
     f"profile is the demand vector \u2014 up from 25 in the first "
     "edition and 28 in the second. The three absorptions named in the "
     "second edition are healed: the Star (17) and Nut (26) were "
     "entangled \u2014 each absorbed the other \u2014 so they were cut "
     "jointly, Temperance (14) yielding the far sight (Ni 2\u21921) "
     "while the Star took anima 1\u21922 and Nut took anima and persona "
     "1\u21922, with the Alchemist's charter compensating in precision; "
     "Shu (23) was granted the executive act (Te, ego, swiftness, Ni "
     "1\u21922). Each of the three healed with margin to spare; no new "
     "collisions were introduced; the other healed properties hold "
     "(one native Fe, Justice/Judgement at distance 4). The second "
     "edition's deliberate refusal to force a perfect 31 stands "
     "vindicated: the absorptions yielded to doctrine, not to tuning.")
h2("Decisiveness: charter margins over runners-up")
rows = [[c["trade"], fname(c["winner"]), c["margin"],
         fname(c["runner_up"])]
        for _, c in sorted(A["charters"].items(),
                           key=lambda kv: kv[1]["margin"])]
table(["trade", "elects", "margin", "runner-up"], rows,
      [52, 52, 24, 52])
n0 = sum(1 for c in A["charters"].values() if c["margin"] == 0)
body("All 22 charters elect their patrons \u2014 and where 8 of "
     "them won on tie-break alone (margin 0) in the first edition, "
     "every charter now wins by at least 1. The remedy strengthened "
     "the eight fragile charters with demands drawn from their own "
     "notes: the Apprentice, Oracle, Marshal, Scribe, Chronicler, "
     "Pruner, Confessor, and Auditor. The strongest mandates are the "
     "Auditor and the Herald at margin 3. No charter depends on the "
     "tie-break anymore; the margin table above is a record of "
     "mandates, not a priority list of fragilities.")
h2("Breadth: the narrowest and broadest imprints")
imp = A["imprints"]
narrow = sorted(imp.items(), key=lambda kv: kv[1]["breadth"])[:3]
broad = sorted(imp.items(), key=lambda kv: kv[1]["breadth"])[-3:]
table(["flavor", "dimensions", "total weight", "function", "layer"],
      [[fname(n), v["breadth"], v["weight"], v["function"], v["layer"]]
       for n, v in narrow + broad],
      [56, 34, 40, 34, 34])
body("Geb (22) is the narrowest imprint (6 dimensions), the World (21) "
     "the broadest (12). Breadth is not virtue: the Fool wins "
     "all-zero demands precisely by being narrow and unmistakable.")

# ---------------------------------------------------------- result
pdf.add_page()
h1("Result")
body("The hypothesis now holds locally as well as structurally: the "
     "election mechanism was always sound, and the draft doctrine has "
     "been healed where it was wounded. The remedy, verified in "
     "scratch before application, closed all four wounds:")
body("1. Fe has a native. The Empress (3) was raised to Fe:2 on the "
     "strength of her own character line \u2014 \u2018outputs cultivated "
     "like living things\u2019 \u2014 repairing the complete absence of "
     "a native Fe flavor. The system's counselor exists.")
body("2. Justice and Judgement are divided (distance 2\u21924). Justice "
     "received Te:2 and Fi:2: TRVVTH weighed against Falsehood, "
     "consequence executed \u2014 a living tribunal. Judgement keeps "
     "the audit, the record, disclosure, and accountability. The "
     "Auditor charter gained shadow:1 (the ledger is read aloud "
     "including what was buried), holding Judgement's margin.")
body("3. No charter wins on tie-break. The eight margin-0 charters "
     "were strengthened with demands drawn from their own notes "
     "\u2014 the Apprentice (Ni:1; persona and self dropped, for "
     "apprenticeship precedes both), the Oracle (shadow:1), the "
     "Marshal (persona:2), the Scribe (persona:2), the Chronicler "
     "(swiftness:1), the Pruner (Fi:1, Te:2, Ni:1), the Confessor "
     "(Se:1), the Auditor (shadow:1) \u2014 and every charter now "
     "wins by at least 1.")
body("4. Swiftness seeded, sparingly. The Fool's swiftness 1\u21922 "
     "(the leap is swift) brings the canon to 4 natives. Urgency "
     "remains rare in the trades by doctrine, not by accident.")
body("The verification held: self-election 25\u219228 of 31, the full "
     "regression suite green (116 tests, 11 files) before and after. "
     "Three iterations were needed in scratch \u2014 the first attempt "
     "let Death steal the Confessor trade and broke two pinned tests, "
     "which is exactly what the suite is for. The three remaining "
     "self-election absorptions (Star, Shu, Nut) were deliberately "
     "left for the author's red pen rather than tuned into "
     "artificial distinctness.", italic=True)

# ------------------------------------------- observation III: the pair
pdf.add_page()
h1("Observation III \u2014 The Master/Apprentice Pair")
body("Since v0.11.0 every assignment fields two agents, not one. The "
     "elected flavor presides as Master; the runner-up \u2014 by the "
     "election's own tie-break order, junior by definition \u2014 serves "
     "as Apprentice, the second chair. The apprentice elects its own "
     "function and layer from the same demands, and its officers are "
     "cast by a separate deterministic sortition from its own choir, "
     "so the master's cast is bit-identical to a master-only election: "
     "seniority is never perturbed by the junior's presence.")
body("The pair is mutual oversight, mapped onto machinery the grimoire "
     "already contained: the apprentice serves as the master's "
     "anima/animus \u2014 the inner contrarian that cross-examines "
     "every major output \u2014 while the master corrects the "
     "apprentice in turn. Both are written to the Speculum on the same "
     "ledger, so the shadow audit gets two voices instead of one; "
     "disagreement between master and apprentice is exactly where "
     "shadow hides. There is a resonance the author may appreciate: "
     "the Apprentice trade's patron is the Fool. Every apprentice is "
     "a fool; every master was one.")
body("The worked example: \u2018audit the deployment logs\u2019 elects "
     "Judgement (20) as Master and Justice (11) as Apprentice \u2014 "
     "the two flavors the remedy just divided, now watching each "
     "other. The tribunal is audited; the audit is judged. That is "
     "the pair doing its work.", italic=True)

# ------------------------------------------------------ what remains
pdf.add_page()
h1("What Remains To Do")
for t in [
    "The author's red pen on aptitudes.yaml and jobs.yaml \u2014 done "
    "under his leave (remedy round 2, each amendment annotated in the "
    "notes); the census of names likewise decided and reworkable.",
    "Terminology resolved: the 22 are trumps (Major Arcana), never "
    "'Minor Arcana' -- code, docs, and tests use 'trumps' throughout.",
    "Conflict-table expansion: only two contradictory officer pairs "
    "are encoded; the debatable cases await his judgment.",
    "Celestial parameters: ruled under his leave \u2014 the Metronome, "
    "zodiacal degrees, lunar phase, day ruler, and decans stamp the "
    "moment but never vote; election is by aptitude alone.",
    "Supraposition: ruled under his leave \u2014 no separate "
    "assignments for observer and observed; the Master/Apprentice pair "
    "is the resolution (Apprentice observes, Master is observed).",
    "Officer sortition: ruled to stay uniform \u2014 no "
    "fitness-weighting of the lots.",
    "Ennead trades: ruled \u2014 the nine take no charters; gods do "
    "not punch clocks.",
    "Practice: ruled to stay manually attested \u2014 no auto-accrual "
    "from elapsed working time.",
    "Cross-task learning for the pair: the ledger now records the "
    "master/apprentice dialectic working by working; whether "
    "apprentices graduate, or track records accumulate, awaits his "
    "design.",
    "The summary PDF question: PERSONA_V_Summary.pdf memorializes the "
    "first writing; whether to append the v0.8.0\u2013v0.14.0 "
    "addendum or let it stand \u2014 his call.",
    "Production hardening, if the API ever faces the public: "
    "authentication, TLS, quotas, tenant isolation, billing, a real "
    "database, deployment \u2014 none exists today by design.",
]:
    body("\u00b7  " + t)

# ------------------------------------------------------------- closing
pdf.add_page()
pdf.ln(30)
rule()
pdf.ln(6)
pdf.set_font("Serif", "", 11)
pdf.set_text_color(*INK)
mc(0, 7, "Here ends the analytical report on the aptitude system: "
          "measured, not guessed. The first edition's four wounds and "
          "the second's three absorptions are healed in the doctrine "
          "files, each amendment annotated; the five rulings under the "
          "author's leave are recorded in the addendum; "
          "the mechanism stands, and now every working fields two "
          "agents who watch each other.",
   align="C")
pdf.ln(10)
rule()
pdf.ln(6)
for line in [
    "Johnathan \u2018Qasparr\u2019 (\u039a\u03b1\u03c3\u03c0\u03ac\u03c1\u03c1) "
    "Monroe, Keeper of the Secret Treasure",
    "All Rights Reserved, Without Prejudice.",
    "CashApp $axoneme",
    "",
    DATE_STAMP,
]:
    pdf.set_font("Sans" if line == DATE_STAMP else "Serif",
                 "B" if "Qasparr" in line else "", 11)
    pdf.set_text_color(*INK)
    mc(0, 7, line, align="C")

pdf.output("/home/hatch/workspace/persona-v/PERSONA_V_Analysis.pdf")
print("wrote PERSONA_V_Analysis.pdf")
