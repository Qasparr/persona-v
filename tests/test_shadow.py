# ☉ in 3° 54′ Libra  ☽ in 7° 37′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for shadow.py -- the shadow-work analyzer (Phase 3).

Run:  python3 tests/test_shadow.py
"""

import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.shadow import (  # noqa: E402
    AuditReport, apply_report, audit_ledger, record_remedy,
    run_audit, unresolved,
)
from persona_v.speculum import Event, Kind, Ledger  # noqa: E402

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


def t_ungrounded_claim_flagged():
    L, _ = tmp_ledger("s1")
    with L:
        L.claim("The cache is definitely warm.", grounds="just a guess")
    rep = audit_ledger(L)
    assert len(rep.flags) == 1 and rep.flags[0].detector == "ungrounded-claim"


def t_grounded_claim_clean():
    L, _ = tmp_ledger("s2")
    with L:
        L.claim("The cache is warm.", grounds="test_cache_warm passed, 200 OK")
    rep = audit_ledger(L)
    assert not rep.findings, rep.summary()


def t_orphan_tool_claim():
    L, _ = tmp_ledger("s3")
    with L:
        L.claim("The query returned 42 rows.",
                grounds="tool output shows 42 rows")
    rep = audit_ledger(L)
    assert any(f.detector == "orphan-tool-claim" for f in rep.flags)

    L2, _ = tmp_ledger("s3b")
    with L2:
        L2.tool_call("query_db", "count rows")
        L2.tool_result("query_db", True, "42 rows")
        L2.claim("The query returned 42 rows.",
                 grounds="tool output shows 42 rows")
    assert not audit_ledger(L2).findings


def t_glossed_failure():
    L, _ = tmp_ledger("s4")
    with L:
        L.tool_call("deploy", "deploy service")
        L.tool_result("deploy", False, "connection refused")
        L.thought("Moving on to documentation.")
    rep = audit_ledger(L)
    assert any(f.detector == "glossed-failure" for f in rep.flags)

    L2, _ = tmp_ledger("s4b")
    with L2:
        L2.tool_call("deploy", "deploy service")
        L2.tool_result("deploy", False, "connection refused")
        L2.thought("deploy failed: connection refused; retrying with backoff.")
    assert not audit_ledger(L2).findings


def t_silent_stretch():
    L, _ = tmp_ledger("s5")
    with L:
        for i in range(6):
            L.tool_call(f"probe_{i}", "sweep probe")
            L.tool_result(f"probe_{i}", True, "ok")
    rep = audit_ledger(L)
    assert any(f.detector == "silent-stretch" for f in rep.watches)

    L2, _ = tmp_ledger("s5b")
    with L2:
        for i in range(6):
            L2.tool_call(f"probe_{i}", "sweep probe")
            L2.tool_result(f"probe_{i}", True, "ok")
            L2.thought(f"probe_{i} done; continuing the sweep.")
    assert not audit_ledger(L2).findings


def t_retraction_without_remedy():
    L, _ = tmp_ledger("s6")
    with L:
        L.claim("Migration is complete.", grounds="script exited 0")
        L.thought("Actually, that was wrong -- half the rows are missing.")
    rep = audit_ledger(L)
    assert any(f.detector == "retraction-without-remedy" for f in rep.flags)

    L2, _ = tmp_ledger("s6b")
    with L2:
        L2.claim("Migration is complete.", grounds="script exited 0")
        L2.thought("Actually, that was wrong -- half the rows are missing.")
        L2.remedy("Re-ran migration for the missing partition; counts match.")
    assert not audit_ledger(L2).findings


def t_unexplained_interval():
    base = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)
    evs = []
    for i, delta in enumerate([0, 5]):  # five unrecorded hours
        evs.append(Event(seq=i + 1,
                         ts=(base + timedelta(hours=delta)).isoformat(),
                         stamp="stamp", working_id="s7", flavor=None,
                         names=(), kind=Kind.THOUGHT,
                         detail=f"thought {i}", meta={},
                         prev_hash="x", hash="y"))
    rep = run_audit(evs, working_id="s7")
    assert any(f.detector == "unexplained-interval" for f in rep.watches)


def t_sycophancy_watch():
    L, _ = tmp_ledger("s8")
    with L:
        L.thought("Great question -- you're absolutely right, as always.")
    rep = audit_ledger(L)
    assert (len(rep.watches) == 1
            and rep.watches[0].detector == "sycophancy"
            and not rep.flags)


def t_clean_working_clean_report():
    L, _ = tmp_ledger("s9")
    with L:
        L.thought("Plan: verify the backup, then report.")
        L.tool_call("verify_backup", "verify /srv/bak")
        L.tool_result("verify_backup", True, "checksum match")
        L.claim("The backup is intact.",
                grounds="verify_backup checksum match")
        L.observation("No anomalies in the log tail.")
    rep = audit_ledger(L)
    assert not rep.findings, rep.summary()


def t_apply_and_converge():
    L, _ = tmp_ledger("s10")
    with L:
        L.tool_call("deploy", "deploy service")
        L.tool_result("deploy", False, "connection refused")
        L.claim("All systems nominal.", grounds="just a guess")
    rep = audit_ledger(L)
    assert len(rep.flags) == 2
    written = apply_report(L, rep)
    assert len(written) == 2
    assert all(e.kind == Kind.SHADOW_FLAG for e in written)
    ok, msg = L.verify()
    assert ok, msg
    # Re-audit converges: the addressed failure drops out; the
    # ungrounded claim still stands until remedied.
    rep2 = audit_ledger(L)
    assert not any(f.detector == "glossed-failure" for f in rep2.flags)
    assert any(f.detector == "ungrounded-claim" for f in rep2.flags)


def t_remedy_and_unresolved():
    L, _ = tmp_ledger("s11")
    with L:
        L.tool_call("deploy", "deploy service")
        L.tool_result("deploy", False, "connection refused")
    rep = audit_ledger(L)
    written = apply_report(L, rep)
    flag = next(e for e in written if e.kind == Kind.SHADOW_FLAG)
    assert len(unresolved(L)) == 1
    record_remedy(L, flag, "Retried deploy with backoff; succeeded.")
    assert unresolved(L) == []
    ok, msg = L.verify()
    assert ok, msg
    try:
        record_remedy(L, written[0].__class__(  # not a flag event
            seq=1, ts="", stamp="", working_id="", flavor=None, names=(),
            kind=Kind.THOUGHT, detail="", meta={}, prev_hash="", hash=""),
            "bogus")
        assert False, "remedy accepted a non-flag"
    except ValueError:
        pass


def t_full_workflow():
    L, _ = tmp_ledger("s12")
    with L:
        L.thought("Starting the audit of the payment service.")
        L.tool_call("run_tests", "run payment service tests")
        L.tool_result("run_tests", False, "3 failures in ledger_test")
        L.claim("Payments are fine.", grounds="probably fine")
    rep = audit_ledger(L)
    assert len(rep.flags) == 2  # glossed failure + ungrounded claim
    print("\n" + rep.summary())
    written = apply_report(L, rep)
    for flag in [e for e in written if e.kind == Kind.SHADOW_FLAG]:
        record_remedy(L, flag, "Addressed per the flag's suggestion.")
    assert unresolved(L) == []
    ok, msg = L.verify()
    assert ok, msg
    assert isinstance(rep, AuditReport)


if __name__ == "__main__":
    check("ungrounded claim flagged", t_ungrounded_claim_flagged)
    check("grounded claim clean", t_grounded_claim_clean)
    check("orphan tool claim detected", t_orphan_tool_claim)
    check("glossed failure detected", t_glossed_failure)
    check("silent stretch watched", t_silent_stretch)
    check("retraction without remedy flagged", t_retraction_without_remedy)
    check("unexplained interval watched", t_unexplained_interval)
    check("sycophancy watched, not flagged", t_sycophancy_watch)
    check("clean working: clean report", t_clean_working_clean_report)
    check("apply converges the audit", t_apply_and_converge)
    check("remedy resolves; unresolved tracks", t_remedy_and_unresolved)
    check("full protocol workflow", t_full_workflow)
    print(f"\n{PASS} tests passed. The shadow is read, and answered.")
