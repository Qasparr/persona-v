# ☉ in 3° 54′ Libra  ☽ in 7° 31′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for the PERSONA V data canon (Phase 0).

Educational note: these tests are the machine-readable form of the
grimoire's own claims. PERSONA_V.md asserts "31 flavors" and "72 names";
these tests *prove* it, every time they run. If the author edits the YAML
and breaks the canon -- a duplicated name, a flavor pointing nowhere --
the tests fail loudly instead of letting the engine run on a corrupted
grimoire. Per the Alethic Axis: the system must not operate on falsehood,
including falsehood about itself.

Run:  python3 tests/test_grimoire.py
"""

import sys
from pathlib import Path

# Make persona_v importable whether run from the repo root or anywhere else.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v import (  # noqa: E402
    load_flavors,
    load_names,
    load_signs,
    name_by_number,
    names_of_flavor,
)

PASS = 0


def check(label, fn):
    """Run one test; report PASS/FAIL and keep a global tally."""
    global PASS
    try:
        fn()
    except AssertionError as e:
        print(f"FAIL  {label}: {e}")
        raise SystemExit(1)
    PASS += 1
    print(f"pass  {label}")


def t_flavor_count():
    flavors = load_flavors()
    assert len(flavors) == 31, f"expected 31 flavors, got {len(flavors)}"


def t_flavor_numbers():
    nums = [f.number for f in load_flavors()]
    assert nums == list(range(31)), f"flavors must number 0-30, got {nums}"


def t_flavor_anchors():
    flavors = load_flavors()
    tarot = [f for f in flavors if f.anchor_type == "tarot"]
    ennead = [f for f in flavors if f.anchor_type == "ennead"]
    # 22 of the Tarot (0-21), 9 of the Ennead (22-30): XXXI, the number of AL.
    assert len(tarot) == 22, f"expected 22 tarot flavors, got {len(tarot)}"
    assert len(ennead) == 9, f"expected 9 ennead flavors, got {len(ennead)}"
    assert [f.number for f in tarot] == list(range(22))
    assert [f.number for f in ennead] == list(range(22, 31))


def t_name_count():
    names = load_names()
    assert len(names) == 72, f"expected 72 names, got {len(names)}"


def t_name_numbers_unique():
    nums = [n.number for n in load_names()]
    assert nums == list(range(1, 73)), "names must number 1-72 exactly once"


def t_name_fields_complete():
    for n in load_names():
        for field in ("name", "office", "duty", "motto", "gloss"):
            val = getattr(n, field)
            assert val and val.strip(), f"name {n.number}: empty {field}"


def t_apportionment():
    # Flavors 0-9 bear three names each (30); flavors 10-30 bear two (42).
    names = load_names()
    for f in range(31):
        got = len(names_of_flavor(names, f))
        want = 3 if f < 10 else 2
        assert got == want, f"flavor {f}: expected {want} names, got {got}"


def t_bidirectional_consistency():
    # Every name listed on a flavor must point back to that flavor, and
    # every name's flavor must list it. No orphans, no strangers.
    flavors = {f.number: f for f in load_flavors()}
    names = {n.number: n for n in load_names()}
    for f in flavors.values():
        for ref in f.names:
            assert ref["number"] in names, f"flavor {f.number} lists unknown name {ref['number']}"
            assert names[ref["number"]].flavor == f.number, (
                f"name {ref['number']} disagrees about its flavor")
            assert names[ref["number"]].name == ref["name"], (
                f"name {ref['number']} disagrees about its name")
    for n in names.values():
        assert n.flavor in flavors, f"name {n.number}: flavor {n.flavor} missing"


def t_first_and_last_names():
    names = load_names()
    assert name_by_number(names, 1).name == "Vehuiah"
    assert name_by_number(names, 72).name == "Mumiah"
    assert name_by_number(names, 33).office == "Weigher of TRVVTH"
    assert name_by_number(names, 51).motto == "Redde rationem."


def t_sign_count():
    signs = load_signs()
    assert len(signs) == 13, f"expected 13 signs, got {len(signs)}"
    assert [s.number for s in signs] == list(range(1, 14))


def t_thirteenth_sign():
    thirteenth = load_signs()[12]
    assert thirteenth.name == "The Anchorage", thirteenth.name
    assert "Cusp of Power" in (thirteenth.epithet or "")


def t_twelve_classical_signs():
    signs = load_signs()[:12]
    assert [s.name for s in signs] == [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]
    for s in signs:
        assert s.glyph and s.element and s.modality and s.ruler, (
            f"{s.name}: classical sign missing attributes")


if __name__ == "__main__":
    check("31 flavors load", t_flavor_count)
    check("flavors number 0-30", t_flavor_numbers)
    check("22 tarot + 9 ennead anchors", t_flavor_anchors)
    check("72 names load", t_name_count)
    check("names number 1-72 uniquely", t_name_numbers_unique)
    check("every name complete (office/duty/motto/gloss)", t_name_fields_complete)
    check("apportionment 10x3 + 21x2 = 72", t_apportionment)
    check("flavor<->name bidirectional consistency", t_bidirectional_consistency)
    check("spot checks: Vehuiah, Mumiah, Iehuiah, Hahasiah", t_first_and_last_names)
    check("13 signs load", t_sign_count)
    check("13th sign is the Anchorage", t_thirteenth_sign)
    check("12 classical signs intact", t_twelve_classical_signs)
    print(f"\n{PASS} tests passed. The canon is sound.")
