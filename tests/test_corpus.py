"""
Validation tests for corpus.py -- the honest reference-library catalogue
of the eight surveyed PDFs.

House rule under test: toy/placeholder/unverified content must be marked,
never presented as verified or production-ready.

Run:  python3 tests/test_corpus.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.corpus import (  # noqa: E402
    DOCTRINE,
    PROCEDURE,
    REFERENCE,
    REFERENCE_ONLY,
    VALID_VERDICTS,
    Document,
    by_verdict,
    document,
    document_ids,
    honesty_report,
)

PASS = 0


def check(name, cond):
    global PASS
    assert cond, f"FAILED: {name}"
    PASS += 1
    print(f"  ok: {name}")


EXPECTED_IDS = ["codex", "armv93", "sgmek", "byzantine",
                "masterkey", "certgen", "authcert", "magisk"]

# -- the catalogue --------------------------------------------------------
check("eight documents", len(document_ids()) == 8)
check("ids exactly the eight", document_ids() == EXPECTED_IDS)
check("document() each id",
      all(isinstance(document(i), Document) for i in EXPECTED_IDS))
check("verdicts are the four constants",
      all(document(i).verdict in VALID_VERDICTS for i in EXPECTED_IDS))
check("pages are positive ints",
      all(isinstance(document(i).pages, int) and document(i).pages > 0
          for i in EXPECTED_IDS))
check("summaries are 2-4 sentences",
      all(2 <= document(i).summary.count(".") + document(i).summary.count("!")
          <= 4 for i in EXPECTED_IDS))
check("author notes set",
      all(document(i).author_note.strip() for i in EXPECTED_IDS))
check("filenames end .pdf",
      all(document(i).filename.endswith(".pdf") for i in EXPECTED_IDS))

# -- no empty caveats: everything carries its honesty markers --------------
check("no document has an empty caveats list",
      all(document(i).caveats for i in EXPECTED_IDS))
check("caveats are non-empty strings",
      all(c.strip() for i in EXPECTED_IDS for c in document(i).caveats))

# -- doctrine is exactly the codex ----------------------------------------
check("document verdicts",
      [document(i).verdict for i in EXPECTED_IDS] ==
      [DOCTRINE, REFERENCE, REFERENCE_ONLY, REFERENCE,
       REFERENCE, REFERENCE, REFERENCE_ONLY, PROCEDURE])
doctrine = by_verdict("doctrine")
check("by_verdict doctrine is exactly [codex]",
      [d.id for d in doctrine] == ["codex"])
check("by_verdict reference",
      sorted(d.id for d in by_verdict("reference")) ==
      ["armv93", "byzantine", "certgen", "masterkey"])
check("by_verdict reference-only",
      sorted(d.id for d in by_verdict("reference-only")) ==
      ["authcert", "sgmek"])
check("by_verdict procedure",
      [d.id for d in by_verdict("procedure")] == ["magisk"])
check("by_verdict unknown -> empty",
      by_verdict("blessed") == [])

# -- honesty markers on the individual documents ---------------------------
codex = document("codex")
check("codex has Dictum fix note",
      any("Every Man, Woman, and Child" in c for c in codex.caveats)
      or "Every Man, Woman, and Child" in codex.summary)
check("codex records Dictuum typo + exclamation",
      any("Dictuum" in c for c in codex.caveats))
check("codex unresolved cite placeholders",
      any("[cite" in c for c in codex.caveats))

check("armv93 DJB2 toy",
      any("DJB2" in c for c in document("armv93").caveats))
check("armv93 toy modulus",
      any("0xAB" in c for c in document("armv93").caveats))
check("armv93 CJK label",
      any("死循环" in c for c in document("armv93").caveats))
check("armv93 author placeholder",
      any("User Specified Name" in c for c in document("armv93").caveats))
check("armv93 no Armv9.3",
      any("zero Armv9.3" in c for c in document("armv93").caveats))

check("sgmek leaked footer",
      any("Gemini 3.1 Pro" in c for c in document("sgmek").caveats))
check("sgmek leaked prompt",
      any("PROMPT WAS" in c for c in document("sgmek").caveats))
check("sgmek numerology",
      any("numerology" in c.lower() for c in document("sgmek").caveats))

check("byzantine no-op quarantine",
      any("(void)maliciousNodeId" in c for c in document("byzantine").caveats))
check("byzantine no BFT",
      any("no BFT consensus" in c for c in document("byzantine").caveats))
check("byzantine chatbot close",
      any("Where should we direct" in c for c in document("byzantine").caveats))

check("masterkey chatbot opening",
      any("complete blueprint" in c for c in document("masterkey").caveats))
check("masterkey author placeholder",
      any("Your Name" in c for c in document("masterkey").caveats))
check("masterkey sizeof bug",
      any("sizeof(pers_string)" in c for c in document("masterkey").caveats))
check("masterkey dead UART",
      any("UART" in c for c in document("masterkey").caveats))

check("certgen 10-year root",
      any("10-year root" in c for c in document("certgen").caveats))
check("certgen prints private key",
      any("private key over UART" in c for c in document("certgen").caveats))
check("certgen EDL claim",
      any("EDL" in c for c in document("certgen").caveats))

check("authcert 100-year",
      any("36500" in c or "100-year" in c
          for c in document("authcert").caveats))
check("authcert one-bit quantum",
      any("one classical bit" in c for c in document("authcert").caveats))
check("authcert AVB commented out",
      any("avbtool" in c for c in document("authcert").caveats))
check("authcert CN stagecraft",
      any("HNIC Starship Enterprise" in c
          for c in document("authcert").caveats))

check("magisk upsell stripped",
      any("LineageOS GSI" in c for c in document("magisk").caveats))
check("magisk domain-only citations",
      any("domain-only" in c for c in document("magisk").caveats))
check("magisk unverified-by-us",
      any("unverified by us" in c for c in document("magisk").caveats))

# -- resolution ------------------------------------------------------------
check("document('nope') -> None", document("nope") is None)
check("document('') -> None", document("") is None)
check("document(None) -> None", document(None) is None)

# -- honesty_report ---------------------------------------------------------
report = honesty_report()
check("report mentions every id",
      all(i in report for i in EXPECTED_IDS))
check("report line format",
      all(f"{i}: {document(i).verdict} —" in report for i in EXPECTED_IDS))
check("report shows first caveats",
      document("armv93").caveats[0] in report
      and document("sgmek").caveats[0] in report)

# -- the honesty rule on the module source itself ---------------------------
source = Path(__file__).resolve().parent.parent.joinpath(
    "persona_v", "corpus.py").read_text(encoding="utf-8")
check("module never claims production-ready",
      "production-ready" not in source)
check("module never claims verified implementation",
      "verified implementation" not in source)

print(f"\n{PASS} corpus tests passed.")
