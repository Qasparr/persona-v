#!/usr/bin/env python3
"""Build PERSONA_V_Doctrine_Review.pdf — the draft doctrine for the author's red pen.

Covers the two draft doctrine files behind aptitude-v1:
  persona_v/data/aptitudes.yaml  (31 flavor aptitude profiles)
  persona_v/data/jobs.yaml       (22 trade charters)

All tables are computed live from the engine (load_aptitudes, load_jobs,
_elect), so the document cannot drift from the code it reviews.
"""
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from fpdf import FPDF

sys.path.insert(0, "/home/hatch/workspace/persona-v")
sys.path.insert(0, "/home/hatch/workspace/thelemic")
from thelemic_date import thelemic_date
from persona_v.assignment import (
    DIMENSIONS, FUNCTIONS, LAYERS, OPERATIONAL,
    AptitudeAssignmentEngine, load_aptitudes, load_jobs, _elect,
)
from persona_v import grimoire

NOW = thelemic_date(datetime.now(ZoneInfo("America/New_York")))
DATE_STAMP = NOW["symbolic"]

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class Review(FPDF):
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("Sans", "", 8)
        self.set_text_color(110, 110, 110)
        self.cell(0, 10, f"PERSONA V \u00b7 Doctrine Review \u00b7 "
                         f"{self.page_no()}/{{nb}}", align="C")


pdf = Review(orientation="P", unit="mm", format="A4")
pdf.alias_nb_pages("{nb}")
pdf.set_auto_page_break(True, margin=20)
pdf.set_margins(22, 20, 22)
for fam, style, path in [("Serif", "", SERIF), ("Serif", "B", SERIF_B),
                         ("Sans", "", SANS), ("Sans", "B", SANS_B)]:
    pdf.add_font(fam, style, path)


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
    pdf.set_font("Serif", "" if not italic else "B", 10.5)
    pdf.set_text_color(*INK)
    mc(0, 6, t)
    pdf.ln(1)


def vec(d):
    """Compact 'dim:val' rendering of nonzero entries, canonical order."""
    return ", ".join(f"{k}:{d[k]}" for k in DIMENSIONS if d.get(k))


FLAVORS = {f.number: f for f in grimoire.load_flavors()}
PROFILES = load_aptitudes()
JOBS = load_jobs()
NAMES = grimoire.load_names()

# ------------------------------------------------------------ cover
pdf.add_page()
pdf.ln(28)
pdf.set_font("Serif", "B", 24)
pdf.set_text_color(*INK)
mc(0, 12, "Doctrine Record", align="C")
pdf.set_font("Serif", "", 13)
mc(0, 8, "Aptitude Profiles, Trade Charters & the Seventy-Two Names", align="C")
mc(0, 8, "behind aptitude-v1", align="C")
pdf.ln(6)
rule()
pdf.ln(4)
body("This document presents the three doctrine files that drive the "
     "Assignment engine's elections: the 31 flavor aptitude profiles "
     "(aptitudes.yaml), the 22 trade charters (jobs.yaml), and the 72 "
     "Shemhamphorash names (names.yaml) with their offices, Latin "
     "mottos, and assessed gender and sexuality. Every table was "
     "computed live from the engine itself, so what you read is what "
     "the code believes. The doctrine is decided under the author's "
     "leave (2026-09-26) \u2014 each entry carries the line it was "
     "drafted or assessed from, and every red-pen amendment is "
     "annotated in its note, so corrections can still be argued line "
     "by line. Correct the YAML, rerun the tests, and the engine "
     "obeys.")
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

# ------------------------------------------------- I. the dimensions
pdf.add_page()
h1("I \u2014 The Sixteen Dimensions")
body("Every profile and every charter is a vector on the same sixteen "
     "dimensions, each rated 0 (no aptitude; omitted from the tables), 1 "
     "(capable), or 2 (native, excellent). A task is probed for demands on "
     "the same dimensions; the election is \u03a3(demand \u00d7 aptitude) "
     "per candidate.")
h2("The eightfold lens")
body("Te \u2014 organize, execute, order.  Ti \u2014 analyze, model, debug.  "
     "Fe \u2014 harmonize, counsel, persuade.  Fi \u2014 discern values, "
     "hold integrity.  Ne \u2014 branch possibilities, invent.  Ni \u2014 "
     "distill pattern, foresee.  Se \u2014 engage the concrete moment.  "
     "Si \u2014 retain, verify against record.")
h2("The five layers")
body("persona \u2014 the interface.  ego \u2014 will and execution.  "
     "shadow \u2014 facing failure, adversarial honesty.  anima \u2014 "
     "receptivity, inwardness.  self \u2014 integration, wholeness.")
h2("The three operational axes")
body("precision \u2014 care, rigor, exactness.  swiftness \u2014 speed, "
     "urgency.  gravity \u2014 stakes, irreversibility, consequence.")

# --------------------------------------- II. the aptitude profiles
pdf.add_page()
h1("II \u2014 The Thirty-One Aptitude Profiles")
body("Decided under the author's leave (2026-09-26) \u2014 remedy "
     "rounds annotated in each note. The line under each name is what "
     "the ratings were drawn from; argue with that line, and the "
     "ratings follow.", italic=True)
import yaml as _yaml
_raw_apt = _yaml.safe_load(open(
    "/home/hatch/workspace/persona-v/persona_v/data/aptitudes.yaml"))
for num in range(31):
    entry = _raw_apt["profiles"][num]
    f = FLAVORS[num]
    pdf.set_font("Serif", "B", 11)
    pdf.set_text_color(*INK)
    mc(0, 7, f"{num:2d} \u00b7 {f.name} \u2014 {f.epithet}")
    pdf.set_font("Sans", "", 9.5)
    pdf.set_text_color(*DIM_C)
    mc(0, 5.5, vec(PROFILES[num]))
    pdf.set_font("Serif", "", 9.5)
    pdf.set_text_color(80, 80, 80)
    mc(0, 5.5, f"drawn from: \u201c{entry['note']}\u201d")
    pdf.ln(2)

# ------------------------------------------- III. the trade charters
pdf.add_page()
h1("III \u2014 The Twenty-Two Trade Charters")
body("The tarot trumps read as Jobs. A charter states what the trade "
     "*requires* \u2014 not what any flavor is good at, but what the work "
     "itself demands. The pipeline: probe the task for rough demands, "
     "classify the best-fitting trade, and let the charter (doctrine, not "
     "guesswork) drive the flavor election. Each charter currently elects "
     "its own patron trump \u2014 verified below \u2014 though a charter "
     "may in principle elect any flavor: fitness is fitness.",
     italic=True)
_raw_jobs = _yaml.safe_load(open(
    "/home/hatch/workspace/persona-v/persona_v/data/jobs.yaml"))
for num in range(22):
    job = JOBS[num]
    entry = _raw_jobs["jobs"][num]
    w, _, _ = _elect(job["charter"], PROFILES)
    mark = "patron" if w == job["patron"] else \
        f"OFF-PATRON: elects {w} ({FLAVORS[w].name})"
    pdf.set_font("Serif", "B", 11)
    pdf.set_text_color(*INK)
    mc(0, 7, f"{num:2d} \u00b7 {job['trade']}  (patron: "
             f"{FLAVORS[job['patron']].name})  [{mark}]")
    pdf.set_font("Sans", "", 9.5)
    pdf.set_text_color(*DIM_C)
    mc(0, 5.5, vec(job["charter"]))
    pdf.set_font("Serif", "", 9.5)
    pdf.set_text_color(80, 80, 80)
    mc(0, 5.5, f"drawn from: \u201c{entry['note']}\u201d")
    pdf.ln(2)

# ------------------------------------------------- IV. verification
pdf.add_page()
h1("IV \u2014 Verification")
h2("Patron election")
off = []
for num in range(22):
    w, _, _ = _elect(JOBS[num]["charter"], PROFILES)
    if w != JOBS[num]["patron"]:
        off.append((num, w))
if off:
    body("OFF-PATRON charters (tune the charter or accept the election):")
    for num, w in off:
        body(f"\u00b7 {JOBS[num]['trade']}: elects {w} "
             f"({FLAVORS[w].name}), patron {JOBS[num]['patron']}")
else:
    body("All 22 trade charters elect their own patron trump. This is "
         "enforced by the test suite (t_job_charters_elect_patrons): any "
         "future edit to jobs.yaml that breaks a patron election fails "
         "the build.")
h2("End-to-end elections")
body("Four tasks through the full pipeline \u2014 probe, classify, "
     "charter, elect, cast lots \u2014 as the engine rendered them:",
     italic=True)
engine = AptitudeAssignmentEngine()
for task in ["audit the deployment logs",
             "debug the crash fast - the model collapsed",
             "comfort a grieving friend",
             "choose and decide what I truly value"]:
    a = engine.assign(task, seed=1)
    pdf.set_font("Serif", "B", 10.5)
    pdf.set_text_color(*INK)
    mc(0, 6.5, f"\u201c{task}\u201d")
    pdf.set_font("Serif", "", 10)
    mc(0, 6, f"Trade: {a.job}  \u2192  Flavor {a.flavor} "
             f"({FLAVORS[a.flavor].name}), function {a.function}, "
             f"layer {a.layer}, officers {list(a.names)}")
    pdf.set_font("Sans", "", 8.5)
    pdf.set_text_color(*DIM_C)
    mc(0, 5, f"demands: {vec(a.demands)}")
    scores = ", ".join(f"{k}={v}" for k, v in list(a.scores.items())[:3])
    mc(0, 5, f"scores: {scores} (margin {a.margin})")
    pdf.set_text_color(*INK)
    pdf.ln(2)

# ------------------------------------------------- V. how to correct
pdf.add_page()
h1("V \u2014 How to Correct the Doctrine")
body("1. Edit persona_v/data/aptitudes.yaml (what each flavor can do), "
     "persona_v/data/jobs.yaml (what each trade requires), or "
     "persona_v/data/names.yaml (offices, mottos, assessed gender and "
     "sexuality). Ratings are 0\u20132; unknown dimensions and "
     "out-of-range ratings are refused at load with the file and line "
     "named.")
body("2. Run the suite: each tests/test_*.py runs standalone; the "
     "guardian tests are t_job_charters_elect_patrons (every charter "
     "elects its patron) and the analytical regression suite "
     "pinning 31/31 self-election, one native Fe, and zero "
     "margin-zero charters.")
body("3. Rebuild this document: python3 build_doctrine_pdf.py \u2014 it "
     "recomputes every table from the code, so the review always matches "
     "the engine.")
body("Standing rule: the author's hand outranks every draft, and his "
     "leave stands behind every decided entry. A single corrected "
     "rating propagates through classification, election, "
     "function, layer, and rationale with no code changes.",
     italic=True)

# ---------------------------------------- VI. the seventy-two names
pdf.add_page()
h1("VI \u2014 The Seventy-Two Names")
body("Assessed as per behavior of office and duty; the default is "
     "non-binary and abstinent, a binary assignment only where the "
     "assessment positively found a marker, and in doubt the default "
     "stands. Decided 2026-09-26 under the author's leave; reworkable "
     "by the author. The full assessment note lives in names.yaml; "
     "the red-pen inspection view is `persona-v name <1-72>`.",
     italic=True)
census = {}
for nm in NAMES:
    census[(nm.gender, nm.sexuality)] = \
        census.get((nm.gender, nm.sexuality), 0) + 1
body("Census: " + ", ".join(
    f"{g}/{s}: {c}" for (g, s), c in sorted(census.items())) + ".")
pdf.ln(2)
for nm in NAMES:
    pdf.set_font("Serif", "B", 10.5)
    pdf.set_text_color(*INK)
    mc(0, 6.5, f"{nm.number:2d} \u00b7 {nm.name} \u2014 {nm.office}")
    pdf.set_font("Serif", "", 9.5)
    pdf.set_text_color(*DIM_C)
    mc(0, 5.5, f"\u201c{nm.motto}\u201d")
    pdf.set_font("Sans", "", 9)
    pdf.set_text_color(80, 80, 80)
    mc(0, 5, f"gender: {nm.gender}  \u00b7  sexuality: {nm.sexuality}")
    pdf.ln(2)

# ------------------------------------------------------------- closing
pdf.add_page()
pdf.ln(30)
rule()
pdf.ln(6)
pdf.set_font("Serif", "", 11)
pdf.set_text_color(*INK)
mc(0, 7, "Here ends the doctrine record, being the builder's "
          "best reading of the author's grimoire, decided under his "
          "leave and reworkable by his hand. What the author corrects "
          "becomes doctrine; what he leaves stands as decided, labeled "
          "as such wherever the engine reports.",
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

pdf.output("/home/hatch/workspace/persona-v/PERSONA_V_Doctrine_Review.pdf")
print("wrote PERSONA_V_Doctrine_Review.pdf")
