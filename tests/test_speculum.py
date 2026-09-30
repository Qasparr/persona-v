# ☉ in 3° 54′ Libra  ☽ in 7° 31′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for speculum.py -- the observer's ledger (Phase 2b).

The ledger's promises under test: append-only framing, hash-chained
integrity (including tamper detection), grounded claims, office
validation, verbosity filtering, resume semantics, and honest closing.

Run:  python3 tests/test_speculum.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.speculum import Event, Kind, Ledger, Verbosity  # noqa: E402

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


def fresh_dir():
    return tempfile.TemporaryDirectory()


def _ledger_at(path):
    """A Ledger bound to an existing file, for verify()-only use."""
    ledger = Ledger.__new__(Ledger)
    ledger._path = Path(path)
    return ledger


def t_lifecycle():
    tmp = fresh_dir()
    with Ledger.open("w1", ledger_dir=tmp.name, purpose="test") as L:
        L.thought("Considering the approach.", flavor=0, names=(1, 2))
        L.claim("The parser handles wraps.", grounds="test run",
                flavor=1, names=(4,))
        L.tool_call("exec", "ran the tests", flavor=1)
        L.tool_result("exec", True, "12 passed", flavor=1)
    path = Path(tmp.name) / "w1.jsonl"
    assert path.exists()
    events = L.events()
    assert events[0].kind == Kind.WORKING_OPENED
    assert events[-1].kind == Kind.WORKING_CLOSED
    assert [e.seq for e in events] == list(range(len(events)))
    # every line is valid JSON with the chain fields
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        assert r["hash"] and r["prev_hash"] is not None
    # stamp, working id, offices carried on every event
    assert all(e.stamp and "Anno" in e.stamp for e in events)
    assert all(e.working_id == "w1" for e in events)
    assert events[1].flavor == 0 and events[1].names == (1, 2)


def t_chain_verifies():
    tmp = fresh_dir()
    with Ledger.open("w2", ledger_dir=tmp.name) as L:
        L.thought("a")
        L.shadow_flag("unverified claim at seq 1", detected_by="audit")
        L.remedy("added grounds", resolves="seq 2")
    ok, msg = L.verify()
    assert ok, msg
    assert "5 events" in msg, msg  # opened, thought, flag, remedy, closed


def t_tamper_detected():
    tmp = fresh_dir()
    with Ledger.open("w3", ledger_dir=tmp.name) as L:
        L.thought("original thought")
        L.close()
    path = Path(tmp.name) / "w3.jsonl"
    lines = open(path, encoding="utf-8").readlines()
    r = json.loads(lines[1])
    r["detail"] = "altered thought"  # the past, edited
    lines[1] = json.dumps(r) + "\n"
    open(path, "w", encoding="utf-8").writelines(lines)
    # verify against the tampered file directly (no constructor needed):
    ok, msg = _ledger_at(path).verify()
    assert not ok, "tampering went undetected!"
    assert "seq 1" in msg, msg
    # and a second, untampered ledger still verifies:
    with Ledger.open("w3b", ledger_dir=tmp.name):
        pass
    ok2, _ = _ledger_at(Path(tmp.name) / "w3b.jsonl").verify()
    assert ok2


def t_claim_requires_grounds():
    tmp = fresh_dir()
    with Ledger.open("w4", ledger_dir=tmp.name) as L:
        try:
            L.claim("ungrounded assertion", grounds="  ")
            assert False, "ungrounded claim was accepted"
        except ValueError:
            pass
        L.claim("grounded", grounds="tool output")


def t_offices_validated():
    tmp = fresh_dir()
    with Ledger.open("w5", ledger_dir=tmp.name) as L:
        for bad in (lambda: L.thought("x", flavor=31),
                    lambda: L.thought("x", flavor=-1),
                    lambda: L.thought("x", names=(0,)),
                    lambda: L.thought("x", names=(73,))):
            try:
                bad()
                assert False, "impossible office was recorded"
            except ValueError:
                pass
        L.thought("valid", flavor=30, names=(72,))  # boundary: accepted


def t_verbosity():
    tmp = fresh_dir()
    with Ledger.open("terse", ledger_dir=tmp.name,
                     verbosity=Verbosity.TERSE) as L:
        L.thought("dropped at terse")
        L.thought("kept at verbose", minor=True)
        L.claim("kept", grounds="g")
        L.tool_call("exec", "dropped at terse")
        L.tool_result("exec", True, "dropped at terse")
        L.tool_result("exec", False, "failures are never dropped")
        L.shadow_flag("kept")
    kinds = [e.kind for e in L.events()]
    assert Kind.THOUGHT not in kinds, kinds
    assert Kind.TOOL_CALL not in kinds
    assert kinds.count(Kind.TOOL_RESULT) == 1
    assert L.events(kind=Kind.TOOL_RESULT)[0].meta["ok"] is False
    assert Kind.CLAIM in kinds and Kind.SHADOW_FLAG in kinds

    with Ledger.open("verb", ledger_dir=tmp.name,
                     verbosity=Verbosity.VERBOSE) as L2:
        L2.thought("minor kept", minor=True)
    assert any(e.detail == "minor kept" for e in L2.events())

    with Ledger.open("norm", ledger_dir=tmp.name,
                     verbosity=Verbosity.NORMAL) as L3:
        L3.thought("minor dropped", minor=True)
        L3.thought("ordinary kept")
    details = [e.detail for e in L3.events()]
    assert not any("minor dropped" in d for d in details)
    assert any("ordinary kept" in d for d in details)


def t_resume():
    tmp = fresh_dir()
    with Ledger.open("w6", ledger_dir=tmp.name) as L:
        L.thought("before the pause")
    # reopening without resume=True must refuse: no silent merges
    try:
        Ledger.open("w6", ledger_dir=tmp.name)
        assert False, "silent merge allowed"
    except FileExistsError:
        pass
    with Ledger.open("w6", ledger_dir=tmp.name, resume=True) as L2:
        L2.thought("after the pause")
    events = L2.events()
    kinds = [e.kind for e in events]
    assert kinds[0] == Kind.WORKING_OPENED
    assert Kind.WORKING_RESUMED in kinds
    assert [e.seq for e in events] == list(range(len(events)))
    ok, msg = L2.verify()
    assert ok, msg  # the chain survived the pause


def t_exception_close():
    tmp = fresh_dir()
    try:
        with Ledger.open("w7", ledger_dir=tmp.name) as L:
            L.thought("about to fail")
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    last = L.events()[-1]
    assert last.kind == Kind.WORKING_CLOSED
    assert "RuntimeError" in last.detail and "boom" in last.detail


def t_event_roundtrip():
    e = Event(seq=0, ts="t", stamp="s", working_id="w", flavor=None,
              names=(), kind=Kind.THOUGHT, detail="d")
    e2 = Event.from_json(e.to_json())
    assert (e2.seq, e2.kind, e2.detail, e2.names) == (0, "thought", "d", ())


def t_shadow_workflow_in_ledger():
    tmp = fresh_dir()
    with Ledger.open("w8", ledger_dir=tmp.name) as L:
        L.claim("All tests pass.", grounds="test run output")
        L.shadow_flag("Claim 'all' overstates: 11 of 12 passed.",
                      detected_by="self-review", names=(33,))
        L.remedy("Corrected the claim to '11 of 12 pass.'",
                 resolves="shadow_flag above", names=(51,))
    flags = L.events(kind=Kind.SHADOW_FLAG)
    remedies = L.events(kind=Kind.REMEDY)
    assert len(flags) == 1 and len(remedies) == 1
    assert flags[0].seq < remedies[0].seq  # the remedy FOLLOWS the flag
    assert flags[0].names == (33,)
    assert isinstance(flags[0].names[0], int)  # ints, not strings


if __name__ == "__main__":
    check("open/thought/claim/tool/close lifecycle", t_lifecycle)
    check("hash chain verifies", t_chain_verifies)
    check("tampering is detected", t_tamper_detected)
    check("claims require grounds", t_claim_requires_grounds)
    check("impossible offices refused", t_offices_validated)
    check("verbosity filtering (terse/normal/verbose)", t_verbosity)
    check("resume continues the chain; no silent merges", t_resume)
    check("exception closes honestly", t_exception_close)
    check("event JSON roundtrip", t_event_roundtrip)
    check("shadow_flag -> remedy ordering in-ledger", t_shadow_workflow_in_ledger)
    print(f"\n{PASS} tests passed. The mirror holds.")
