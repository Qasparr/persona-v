# ☉ in 4° 34′ Libra  ☽ in 16° 47′ Aries  dies solis  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for anchorage.py -- the Zero-Trust Anchorage
(Oz x Duty + TRVVTH) as code.

Run:  python3 tests/test_anchorage.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.anchorage import (  # noqa: E402
    ASSERTION,
    CITATION,
    FALSEHOOD,
    NUMBER,
    QUOTE,
    TRVVTH,
    UNRESOLVED,
    Claim,
    admit,
    cardinal_rules,
    weigh_claim,
    weigh_rights,
)

PASS = 0


def check(label, fn):
    global PASS
    try:
        fn()
    except AssertionError as e:
        print(f"FAIL  {label}: {e}")
        raise SystemExit(1)
    PASS += 1
    print(f"pass  {label}")


MURDOCK_SOURCE = (
    "A state may not impose a charge for the enjoyment of a right "
    "granted by the Federal Constitution."
)


def t_quote_verbatim_is_trvvth():
    a = weigh_claim(Claim("A state may not impose a charge for the enjoyment",
                          kind=QUOTE, proof={"source": MURDOCK_SOURCE}))
    assert a.verdict == TRVVTH, a.note


def t_quote_absent_from_source_is_falsehood():
    a = weigh_claim(Claim("A state may not impose a charge upon the enjoyment",
                          kind=QUOTE, proof={"source": MURDOCK_SOURCE}))
    assert a.verdict == FALSEHOOD, a.note  # checked and failed: disproven


def t_quote_without_source_is_unresolved():
    a = weigh_claim(Claim("something quoted", kind=QUOTE))
    assert a.verdict == UNRESOLVED, a.note


def t_number_recomputed_is_trvvth():
    a = weigh_claim(Claim("342", kind=NUMBER,
                          proof={"recompute": lambda: 40 + 1 + 1 + 300,
                                 "expected": 342}))
    assert a.verdict == TRVVTH, a.note


def t_number_mismatch_is_falsehood():
    a = weigh_claim(Claim("342", kind=NUMBER,
                          proof={"recompute": lambda: 341, "expected": 342}))
    assert a.verdict == FALSEHOOD, a.note


def t_number_without_recompute_is_unresolved():
    a = weigh_claim(Claim("342", kind=NUMBER))
    assert a.verdict == UNRESOLVED, a.note


def t_number_raising_recompute_is_unresolved():
    def boom():
        raise ValueError("nope")
    a = weigh_claim(Claim("342", kind=NUMBER,
                          proof={"recompute": boom, "expected": 342}))
    assert a.verdict == UNRESOLVED, a.note


def t_citation_plausible_is_unresolved_not_trvvth():
    a = weigh_claim(Claim("319 U.S. 105 (1943)", kind=CITATION))
    assert a.verdict == UNRESOLVED, a.note
    assert "red pen" in a.note  # format is never truth


def t_citation_malformed_is_falsehood():
    a = weigh_claim(Claim("Murdock v. Pennsylvania, some year", kind=CITATION))
    assert a.verdict == FALSEHOOD, a.note


def t_assertion_is_unresolved():
    a = weigh_claim(Claim("the stars are many", kind=ASSERTION))
    assert a.verdict == UNRESOLVED, a.note


def t_unknown_kind_is_falsehood():
    a = weigh_claim(Claim("x", kind="rumor"))
    assert a.verdict == FALSEHOOD, a.note


def t_balance_holds_when_duties_named():
    b = weigh_rights([
        Claim("speak", right="free speech", duty="no coercion of another's orbit"),
        Claim("live", right="life by one's own law", duty="abstain from interference"),
    ])
    assert b.holds, b.unbalanced
    assert b.unbalanced == []


def t_balance_fails_on_naked_right():
    b = weigh_rights([Claim("take", right="all property")])
    assert not b.holds
    assert b.unbalanced == ["all property"]


def t_clean_working_admitted():
    w = admit([
        Claim("Love worketh no ill to his neighbour",
              kind=QUOTE, proof={"source": "Love worketh no ill to his neighbour"}),
        Claim("319 U.S. 105 (1943)", kind=CITATION),
        Claim("speak", right="free speech", duty="no coercion"),
    ])
    assert w.admitted, w.report()
    assert w.stamp, "stamp missing"
    assert isinstance(w.sun_in_anchorage, bool)
    assert "admitted: True" in w.report()


def t_falsehood_refuses_admission():
    w = admit([Claim("wrong quote", kind=QUOTE, proof={"source": "other text"})])
    assert not w.admitted
    assert w.assessments[0].verdict == FALSEHOOD


def t_unbalanced_right_refuses_admission():
    w = admit([Claim("take", kind=ASSERTION, right="all property")])
    assert not w.admitted, w.report()
    assert w.balance.unbalanced == ["all property"]


def t_unresolved_marks_never_upgrades():
    w = admit([Claim("319 U.S. 105 (1943)", kind=CITATION)])
    assert w.admitted  # UNRESOLVED is admitted as UNRESOLVED
    assert w.assessments[0].verdict == UNRESOLVED


def t_cardinal_rules():
    rules = cardinal_rules()
    assert len(rules) == 6, rules
    assert any("red pen" in r for r in rules)


if __name__ == "__main__":
    check("quote verbatim in source is TRVVTH", t_quote_verbatim_is_trvvth)
    check("quote absent from source is FALSEHOOD", t_quote_absent_from_source_is_falsehood)
    check("quote without source is UNRESOLVED", t_quote_without_source_is_unresolved)
    check("number recomputed is TRVVTH", t_number_recomputed_is_trvvth)
    check("number mismatch is FALSEHOOD", t_number_mismatch_is_falsehood)
    check("number without recompute is UNRESOLVED", t_number_without_recompute_is_unresolved)
    check("raising recompute is UNRESOLVED", t_number_raising_recompute_is_unresolved)
    check("plausible citation is UNRESOLVED, never TRVVTH", t_citation_plausible_is_unresolved_not_trvvth)
    check("malformed citation is FALSEHOOD", t_citation_malformed_is_falsehood)
    check("assertion is UNRESOLVED", t_assertion_is_unresolved)
    check("unknown kind is FALSEHOOD", t_unknown_kind_is_falsehood)
    check("balance holds when duties named", t_balance_holds_when_duties_named)
    check("balance fails on naked right", t_balance_fails_on_naked_right)
    check("clean working admitted", t_clean_working_admitted)
    check("falsehood refuses admission", t_falsehood_refuses_admission)
    check("unbalanced right refuses admission", t_unbalanced_right_refuses_admission)
    check("unresolved marks, never upgrades", t_unresolved_marks_never_upgrades)
    check("cardinal rules", t_cardinal_rules)
    print(f"\n{PASS} tests passed")
