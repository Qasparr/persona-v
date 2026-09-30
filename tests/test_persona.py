# ☉ in 3° 54′ Libra  ☽ in 7° 35′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for persona.py -- the Jungian core (Phase 2).

Run:  python3 tests/test_persona.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.persona import LAYERS, PersonaV  # noqa: E402
from persona_v.speculum import Kind, Ledger  # noqa: E402

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


def tmp_ledger(wid="ptest"):
    tmp = tempfile.TemporaryDirectory()
    return Ledger.open(wid, ledger_dir=tmp.name), tmp


def t_layers_documented():
    assert set(LAYERS) == {"persona", "ego", "shadow", "anima_animus", "self"}
    assert all(v.strip() for v in LAYERS.values())


def t_assume_flavor():
    L, _ = tmp_ledger("p1")
    p = PersonaV(ledger=L)
    a = p.assume_flavor(0)
    assert a.flavor == 0 and a.flavor_name == "The Fool"
    assert a.names == (1, 2, 3)  # the Fool's apportioned choir
    assert a.layer == "ego"
    assert a.reading is not None and "Anno" in a.reading.moment.stamp
    assert p.flavor == 0 and p.names == (1, 2, 3)
    # the assumption is on the record, attributed
    claims = L.events(kind=Kind.CLAIM)
    assert any("Assumed flavor 0" in c.detail for c in claims)
    assert claims[-1].flavor == 0 and claims[-1].names == (1, 2, 3)


def t_assume_rejects_impossible():
    L, _ = tmp_ledger("p2")
    p = PersonaV(ledger=L)
    for bad in (lambda: p.assume_flavor(31), lambda: p.assume_flavor(-1)):
        try:
            bad()
            assert False, "impossible flavor assumed"
        except ValueError:
            pass
    try:
        p.assume_flavor(0, layer="superego")
        assert False, "impossible layer focused"
    except ValueError:
        pass


def t_invoke():
    L, _ = tmp_ledger("p3")
    p = PersonaV(ledger=L)
    p.assume_flavor(11)
    assert p.names == (33, 34)
    p.invoke(51, 52)  # the auditors, called to a working of Justice
    assert p.names == (51, 52)
    claims = L.events(kind=Kind.CLAIM)
    assert any("51 Hahasiah" in c.detail for c in claims)
    try:
        p.invoke(73)
        assert False, "impossible name invoked"
    except ValueError:
        pass


def t_focus_layer():
    L, _ = tmp_ledger("p4")
    p = PersonaV(ledger=L)
    p.assume_flavor(8)
    assert p.focus_layer("shadow") == "shadow"
    thoughts = L.events(kind=Kind.THOUGHT)
    assert any("shadow" in t.detail for t in thoughts)
    try:
        p.focus_layer("id")
        assert False, "impossible layer focused"
    except ValueError:
        pass


def t_supraposition():
    L, _ = tmp_ledger("p5")
    p = PersonaV(ledger=L)
    p.assume_flavor(14)
    p.observe("The blend is holding; neither drowned nor dry.")
    sp = p.supraposition()
    trace = sp.trace()
    assert trace is not None and len(trace) >= 2  # opened + assumption
    obs = sp.trace(kind=Kind.OBSERVATION)
    assert len(obs) == 1 and "blend" in obs[0].detail
    # the observer's note is itself observed: it entered the trace
    sp.note("Second look: still holding.")
    assert len(sp.trace(kind=Kind.OBSERVATION)) == 2


def t_no_ledger_graceful():
    p = PersonaV()  # no mirror: the mask with no record
    p.assume_flavor(21)
    assert p.flavor == 21
    assert p.observe("unrecorded") is None
    assert p.trace() is None
    assert p.invoke(72) == (72,)


def t_describe():
    L, _ = tmp_ledger("p6")
    p = PersonaV(ledger=L)
    assert "unclothed" in p.describe()
    p.assume_flavor(30)
    d = p.describe()
    assert "Horus" in d and "71 Haiaiel" in d and "72 Mumiah" in d


if __name__ == "__main__":
    check("five layers documented", t_layers_documented)
    check("assume_flavor: choir, reading, record", t_assume_flavor)
    check("impossible flavors/layers refused", t_assume_rejects_impossible)
    check("invoke: explicit officers, on record", t_invoke)
    check("focus_layer shifts and records", t_focus_layer)
    check("supraposition: trace and note", t_supraposition)
    check("no ledger: graceful degradation", t_no_ledger_graceful)
    check("describe renders the stance", t_describe)
    print(f"\n{PASS} tests passed. The mask is declared.")
