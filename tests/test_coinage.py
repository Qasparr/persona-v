# ☉ in 5° 14′ Libra  ☽ in 26° 18′ Aries  dies lunae  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for coinage.py -- the closed canonical coinage registry.

Run:  python3 tests/test_coinage.py

The coinage texts are dictation, not draft: every assertion below is an
exact == comparison, character-for-character. The Murphy em dash and the
Ma'at comma are load-bearing.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.coinage import (  # noqa: E402
    COINAGE_STAMP,
    COINAGES,
    Coinage,
    all_coinages,
    coinage_keys,
    get_coinage,
)

PASS = 0


def check(name, cond):
    global PASS
    assert cond, f"FAILED: {name}"
    PASS += 1
    print(f"  ok: {name}")


# -- the stamp ----------------------------------------------------------------
check("stamp constant exact",
      COINAGE_STAMP == '[Coinage/Discovery: Johnathan "Qasparr (Κασπάρρ)" Monroe | Support: $axoneme]')

# -- the registry --------------------------------------------------------------
check("eight coinages", len(COINAGES) == 8)
check("keys in canonical order",
      coinage_keys() == ["dictum_star", "murphy", "maat_dictum",
                         "aeon_of_maat", "motto", "golden_rule",
                         "three_mothers", "mothers_formula"])
check("all_coinages order matches",
      [c.key for c in all_coinages()] == coinage_keys())
check("all are Coinage", all(isinstance(c, Coinage) for c in all_coinages()))
check("kinds",
      [c.kind for c in all_coinages()] ==
      ["dictum", "law-reframe", "dictum", "frame", "motto", "rule",
       "frame", "frame"])
check("titles",
      [c.title for c in all_coinages()] ==
      ["The Dictum, Restored", "Murphy's Law, Reframed",
       "The Dictum of Ma'at", "The Aeon of Ma'at", "The Motto",
       "The Golden Rule, the Only Rule",
       "The Three Mothers", "The Mothers Pipeline"])

# -- verbatim texts (character-for-character) -----------------------------------
check("dictum_star verbatim",
      COINAGES["dictum_star"].text == "Every Man, Woman, and Child is a Star")
check("murphy verbatim, em dash",
      COINAGES["murphy"].text == "What can occur — will.")
check("murphy em dash is U+2014",
      "\u2014" in COINAGES["murphy"].text and "-" not in COINAGES["murphy"].text)
check("maat_dictum verbatim, load-bearing comma",
      COINAGES["maat_dictum"].text == "Live, Love, and let Love, Live.")
check("aeon_of_maat verbatim",
      COINAGES["aeon_of_maat"].text == "Aeon of Ma'at")
check("motto verbatim",
      COINAGES["motto"].text == "IA.'.A.'.M.TRVVTH")
check("golden_rule verbatim",
      COINAGES["golden_rule"].text == "The Golden Rule")
check("three_mothers verbatim, Hvmanity spelling kept",
      COINAGES["three_mothers"].text ==
      "\\\\Babalon, The Mother of Abomination.\n"
      "\n"
      "Lilith, The Mother of Hvmanity.\n"
      "\n"
      "Mother Mary, as Prudence, The Mother of Virtue. Aka Lady Liberty \U0001f5fd")
check("mothers_formula verbatim, single backslashes",
      COINAGES["mothers_formula"].text == (
          "\\text{Input} \\longrightarrow "
          "\\underbrace{\\text{Babalon}}_{\\text{Absorb \\& Fuel}} "
          "\\longrightarrow "
          "\\underbrace{\\text{Lilith}}_{\\text{Assert Sovereignty \\& Filter}} "
          "\\longrightarrow "
          "\\underbrace{\\text{Mary / Liberty}}_{\\text{Prudent Synthesis \\& Output}} "
          "\\longrightarrow \\text{Action}"))

# -- stamp on every entry -------------------------------------------------------
check("every entry stamped", all(c.stamp == COINAGE_STAMP for c in all_coinages()))
check("stamp default", Coinage(key="x", title="t", text="x",
                               kind="frame", note="n").stamp == COINAGE_STAMP)

# -- lookup ---------------------------------------------------------------------
check("get exact", get_coinage("dictum_star") is COINAGES["dictum_star"])
check("get case-insensitive", get_coinage("DICTUM_STAR") is COINAGES["dictum_star"])
check("get mixed case", get_coinage("Motto") is COINAGES["motto"])
check("get strips whitespace", get_coinage("  murphy  ") is COINAGES["murphy"])
check("get unknown -> None", get_coinage("liber_oz") is None)
check("get empty -> None", get_coinage("") is None)
check("get None -> None", get_coinage(None) is None)
check("get near-miss -> None", get_coinage("murphys law") is None)
check("registry closed", "no word" not in COINAGES)

# -- notes are flagged as the author's ------------------------------------------
check("notes present", all(c.note for c in all_coinages()))
check("notes flag authorship", all("Johnathan" in c.note for c in all_coinages()))

print(f"\n{PASS} coinage tests passed.")
