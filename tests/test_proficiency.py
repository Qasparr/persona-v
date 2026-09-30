# ☉ in 3° 57′ Libra  ☽ in 8° 36′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for proficiency.py -- the apprentice's arc.

The score is recorded practice hours; the apex is mastery, by two
paths only: 1200 hours of intentional practice (attainment), or the
working Master's promotion (with grounds).

Run:  python3 tests/test_proficiency.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.proficiency import (  # noqa: E402
    MASTERY_HOURS, ProficiencyLedger,
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


def fresh():
    tmp = tempfile.mkdtemp()
    return ProficiencyLedger(Path(tmp) / "proficiency.json")


def t_mastery_hours_is_1200():
    assert MASTERY_HOURS == 1200.0, "the author's number is 1200"


def t_practice_accumulates():
    p = fresh()
    p.record_practice(0, 40.0, "w1", "cross-examined the Master's audit")
    p.record_practice(0, 2.5, "w2", "named the bondage pattern aloud")
    assert p.hours(0) == 42.5
    assert not p.is_master(0)
    s = p.standing(0)
    assert s["hours"] == 42.5 and s["practices"] == 2
    assert abs(s["progress"] - 42.5 / 1200.0) < 1e-9
    assert abs(s["remaining"] - (1200.0 - 42.5)) < 1e-9
    assert s["path"] is None


def t_attainment_at_1200():
    # The hours themselves confer it: crossing the threshold writes
    # the apex event, once, naming attainment.
    p = fresh()
    p.record_practice(11, 1199.0, "w1", "a year of cross-examinations")
    assert not p.is_master(11)
    event = p.record_practice(11, 1.0, "w2", "the final hour")
    assert event["kind"] == "mastery_attained"
    assert event["path"] == "attainment"
    assert p.is_master(11)
    assert p.path_to_mastery(11) == "attainment"
    # Hours keep counting past the apex; mastery is not re-conferred.
    p.record_practice(11, 50.0, "w3", "practice after mastery")
    assert p.hours(11) == 1250.0
    attained = [e for e in p.events(11)
                if e["kind"] == "mastery_attained"]
    assert len(attained) == 1


def t_promotion_path():
    # The Master's promotion confers mastery immediately, whatever
    # the hours -- with grounds, on the record.
    p = fresh()
    p.record_practice(3, 10.0, "w1", "counseled the grieving")
    p.promote(3, 20, "w1",
              "her cross-examination found what my audit buried")
    assert p.is_master(3)
    assert p.path_to_mastery(3) == "promotion"
    assert p.hours(3) == 10.0  # promotion is not hours
    s = p.standing(3)
    assert s["is_master"] and s["promotions"] == 1


def t_ungrounded_promotion_refused():
    # Exactly as the Speculum refuses a claim without grounds.
    p = fresh()
    for bad in ("", "   "):
        try:
            p.promote(3, 20, "w1", bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"grounds {bad!r} accepted")
    assert not p.is_master(3)


def t_unattested_practice_refused():
    # Intentionality without a witness is just a claim.
    p = fresh()
    for hours, note in [(0, "x"), (-3, "x"), (float("inf"), "x"),
                         (2, ""), (2, "   ")]:
        try:
            p.record_practice(0, hours, "w1", note)
        except ValueError:
            pass
        else:
            raise AssertionError(f"practice ({hours!r}, {note!r}) "
                                 f"accepted")
    assert p.hours(0) == 0.0


def t_invalid_flavors_refused():
    p = fresh()
    for bad in (-1, 31, 99, "0", 3.5, True):
        try:
            p.record_practice(bad, 1.0, "w1", "x")
        except ValueError:
            pass
        else:
            raise AssertionError(f"flavor {bad!r} accepted")
    try:
        p.promote(5, 5, "w1", "self-dealing")
    except ValueError:
        pass
    else:
        raise AssertionError("self-promotion accepted")


def t_registry_persists():
    # The log is append-only and rehydratable: totals derive from
    # history, so the record cannot drift from itself.
    tmp = tempfile.mkdtemp()
    path = Path(tmp) / "proficiency.json"
    p1 = ProficiencyLedger(path)
    p1.record_practice(7, 100.0, "w1", "drove the chariot's audit")
    p1.promote(7, 1, "w1", "he held the line I could not")
    p2 = ProficiencyLedger(path)
    assert p2.hours(7) == 100.0
    assert p2.is_master(7) and p2.path_to_mastery(7) == "promotion"
    assert len(p2.events()) == 3  # practice, promotion, mastery
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["mastery_hours"] == 1200.0


def t_describe_renders():
    p = fresh()
    text = p.describe(0)
    assert "apprentice" in text and "1200" in text
    p.record_practice(0, 1200.0, "w1", "the long road")
    text = p.describe(0)
    assert "MASTER by attainment" in text


def t_promotion_names_sponsor_and_working():
    # Lineage: the mastery event names the conferring Master and
    # the working; standing and describe surface them.
    p = fresh()
    p.promote(3, 20, "w9", "her cross-examination found what I buried")
    s = p.standing(3)
    assert s["sponsor"] == 20
    assert s["apex_working"] == "w9"
    assert s["apex_witness"] is None  # no witness on the promotion path
    text = p.describe(3)
    assert "conferred by Master 20" in text and "w9" in text
    assert "Lineage" in text and "3" in text and "20" in text


def t_attainment_records_working_and_witness():
    # The hours confer -- but the record keeps the provenance: the
    # working where the apex was crossed, and the witnessing Master.
    # A witness is not a sponsor.
    p = fresh()
    p.record_practice(11, 1199.0, "w1", "a year of cross-examinations",
                      master=20)
    event = p.record_practice(11, 1.0, "w2", "the final hour", master=20)
    assert event["kind"] == "mastery_attained"
    assert event["working_id"] == "w2"
    assert event["under_master"] == 20
    s = p.standing(11)
    assert s["sponsor"] is None
    assert s["apex_working"] == "w2"
    assert s["apex_witness"] == 20
    text = p.describe(11)
    assert "conferred by the hours themselves" in text
    assert "witnessed by Master 20" in text


def t_attainment_without_witness():
    p = fresh()
    event = p.record_practice(5, 1200.0, "w1", "the long road")
    assert event["under_master"] is None
    s = p.standing(5)
    assert s["sponsor"] is None and s["apex_witness"] is None
    assert s["apex_working"] == "w1"


def t_lineage_walks_sponsor_chain():
    # Who raised whom: 11 raised 20, 20 raised 3.
    p = fresh()
    p.promote(11, 4, "w1", "grounds for eleven")
    p.promote(20, 11, "w2", "grounds for twenty")
    p.promote(3, 20, "w3", "grounds for three")
    chain = p.lineage(3)
    assert [(l["flavor"], l["sponsor"]) for l in chain] == [
        (3, 20), (20, 11), (11, 4)]
    assert all(l["path"] == "promotion" for l in chain)
    # A flavor with no mastery has no lineage.
    assert p.lineage(7) == []


def t_lineage_cycle_safe():
    # A promotion ring is reported once, not followed forever.
    p = fresh()
    p.promote(1, 2, "w1", "grounds")
    p.promote(2, 1, "w2", "grounds")
    chain = p.lineage(1)
    assert [(l["flavor"], l["sponsor"]) for l in chain] == [
        (1, 2), (2, 1)]


def t_invalid_witness_refused():
    p = fresh()
    for bad in (-1, 31, "20", 2.5):
        try:
            p.record_practice(0, 1.0, "w1", "x", master=bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"witness master {bad!r} accepted")


def main():
    check("mastery threshold is the author's 1200", t_mastery_hours_is_1200)
    check("practice accumulates; standing math", t_practice_accumulates)
    check("1200 hours confers mastery by attainment, once",
          t_attainment_at_1200)
    check("Master's promotion confers mastery, with grounds",
          t_promotion_path)
    check("ungrounded promotion refused", t_ungrounded_promotion_refused)
    check("unattested practice refused", t_unattested_practice_refused)
    check("invalid flavors and self-promotion refused",
          t_invalid_flavors_refused)
    check("registry persists; totals derive from history",
          t_registry_persists)
    check("describe() renders both states", t_describe_renders)
    check("promotion names sponsor and working", t_promotion_names_sponsor_and_working)
    check("attainment records working and witness",
          t_attainment_records_working_and_witness)
    check("attainment without witness", t_attainment_without_witness)
    check("lineage walks the sponsor chain", t_lineage_walks_sponsor_chain)
    check("lineage is cycle-safe", t_lineage_cycle_safe)
    check("invalid witness refused", t_invalid_witness_refused)
    print(f"{PASS} tests passed. The apprentice walks; the hours count.")


if __name__ == "__main__":
    main()
