# ☉ in 3° 54′ Libra  ☽ in 7° 37′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for alethic.py -- the Alethic Axis as code (Phase 4).

Run:  python3 tests/test_alethic.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.alethic import (  # noqa: E402
    FALSEHOOD, TRVVTH, UNRESOLVED, assess_ledger, alethic_balance,
)
from persona_v.speculum import Ledger  # noqa: E402

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


def tmp_ledger(wid):
    tmp = tempfile.TemporaryDirectory()
    return Ledger.open(wid, ledger_dir=tmp.name), tmp


def t_verified_claim_is_trvvth():
    L, _ = tmp_ledger("a1")
    with L:
        L.tool_call("ping", "ping the host")
        L.tool_result("ping", True, "0% loss")
        L.claim("The host is reachable.", grounds="ping tool output: 0% loss")
    bal = assess_ledger(L)
    assert bal.counts[TRVVTH] == 1, bal.report()
    assert bal.assessments[0].strength == "verified"


def t_weak_grounds_unresolved_not_falsehood():
    # The cardinal rule: unproven is never convicted.
    L, _ = tmp_ledger("a2")
    with L:
        L.claim("The cache is warm.", grounds="probably warm by now")
    bal = assess_ledger(L)
    a = bal.assessments[0]
    assert a.verdict == UNRESOLVED, bal.report()
    assert a.verdict != FALSEHOOD
    assert a.strength == "weak"


def t_orphan_citation_is_falsehood():
    L, _ = tmp_ledger("a3")
    with L:
        L.claim("The query returned 42 rows.",
                grounds="tool output shows 42 rows")
    bal = assess_ledger(L)
    a = bal.assessments[0]
    assert a.verdict == FALSEHOOD, bal.report()
    assert "does not exist" in " ".join(a.reasons)


def t_retracted_claim_is_falsehood():
    L, _ = tmp_ledger("a4")
    with L:
        L.claim("Migration complete.", grounds="script exited 0")
        L.thought("Actually, that was wrong -- rows are missing.")
    bal = assess_ledger(L)
    assert bal.assessments[0].verdict == FALSEHOOD, bal.report()


def t_stated_grounds_unresolved():
    L, _ = tmp_ledger("a5")
    with L:
        L.claim("Assuming flavor 11.", grounds="explicit instruction")
    bal = assess_ledger(L)
    a = bal.assessments[0]
    assert a.verdict == UNRESOLVED and a.strength == "stated"


def t_balance_and_standing():
    L, _ = tmp_ledger("a6")
    with L:
        L.claim("Rows: 42.", grounds="tool output shows 42")     # FALSEHOOD
        L.tool_call("ping", "ping")
        L.tool_result("ping", True, "ok")
        L.claim("Host up.", grounds="ping tool output ok")      # TRVVTH
        L.claim("Cache warm.", grounds="probably")               # UNRESOLVED
    bal = assess_ledger(L)
    assert bal.counts == {TRVVTH: 1, UNRESOLVED: 1, FALSEHOOD: 1}
    assert bal.total == 3
    standing = bal.standing()
    assert "compromised" in standing and "remedy required" in standing
    print("\n" + bal.report())


def t_clean_standing():
    L, _ = tmp_ledger("a7")
    with L:
        L.tool_call("ping", "ping")
        L.tool_result("ping", True, "ok")
        L.claim("Host up.", grounds="ping tool output ok")
    bal = assess_ledger(L)
    assert "word is good" in bal.standing()


def t_empty_ledger():
    L, _ = tmp_ledger("a8")
    with L:
        pass
    bal = assess_ledger(L)
    assert bal.total == 0 and "nothing to weigh" in bal.standing()


def t_seq_citation_is_stated():
    L, _ = tmp_ledger("a9")
    with L:
        L.tool_call("ping", "ping")
        L.tool_result("ping", True, "ok")
        L.claim("Host up.", grounds="ping tool output ok")
        L.claim("Proceeding.", grounds="per seq 3, the host is up")
    bal = assess_ledger(L)
    assert bal.assessments[1].strength == "stated"
    assert bal.assessments[1].verdict == UNRESOLVED


if __name__ == "__main__":
    check("verified claim -> TRVVTH", t_verified_claim_is_trvvth)
    check("weak grounds -> UNRESOLVED, never FALSEHOOD", t_weak_grounds_unresolved_not_falsehood)
    check("orphan citation -> FALSEHOOD", t_orphan_citation_is_falsehood)
    check("retracted claim -> FALSEHOOD", t_retracted_claim_is_falsehood)
    check("stated grounds -> UNRESOLVED", t_stated_grounds_unresolved)
    check("balance counts + compromised standing", t_balance_and_standing)
    check("clean working: word is good", t_clean_standing)
    check("empty ledger: nothing to weigh", t_empty_ledger)
    check("seq citation -> stated", t_seq_citation_is_stated)
    print(f"\n{PASS} tests passed. TRVVTH is weighed, not assumed.")
