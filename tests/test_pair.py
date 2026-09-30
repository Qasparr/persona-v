# ☉ in 3° 56′ Libra  ☽ in 8° 6′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for the Master/Apprentice pair (v0.11.0).

Every assignment elects two agents: the Master (best fit) and the
Apprentice (the runner-up, the second chair). The apprentice serves
as the master's anima/animus -- the inner contrarian -- while the
master corrects the apprentice in turn; both are recorded, so mutual
oversight is on the record.

Run:  python3 tests/test_pair.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.assignment import (  # noqa: E402
    FUNCTIONS, LAYERS, AptitudeAssignmentEngine, _elect,
    load_aptitudes,
)
from persona_v.grimoire import load_flavors  # noqa: E402
from persona_v.speculum import Ledger, Kind  # noqa: E402
import tempfile  # noqa: E402

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


def engine():
    return AptitudeAssignmentEngine()


def _ranked_second(a):
    """Independent recomputation of the runner-up from the scoreboard."""
    profiles = load_aptitudes()
    scores, coverage = {}, {}
    for num, apt in profiles.items():
        scores[num] = sum(a.demands[d] * apt[d] for d in a.demands)
        coverage[num] = sum(1 for d in a.demands
                            if a.demands[d] > 0 and apt[d] > 0)
    ranked = sorted(scores, key=lambda f: (scores[f], coverage[f], -f),
                    reverse=True)
    return ranked[0], ranked[1], scores, coverage


def t_apprentice_is_runner_up():
    # The apprentice is exactly the runner-up by the election's own
    # tie-break order -- junior by definition, not by a second vote.
    for task in ("audit the deployment logs",
                 "comfort a grieving friend",
                 "prune the dead code paths",
                 "begin a new working",
                 "name the pattern I cannot stop repeating"):
        a = engine().assign(task, seed=7)
        winner, second, scores, coverage = _ranked_second(a)
        assert a.flavor == winner, f"{task}: master {a.flavor} != {winner}"
        assert a.apprentice == second, (
            f"{task}: apprentice {a.apprentice} != runner-up {second}")
        assert a.apprentice != a.flavor
        assert a.margin == scores[winner] - scores[second]


def t_apprentice_sees_through_own_lens():
    # The apprentice elects its own function and layer from the same
    # demands -- it watches the same task through its own eyes.
    a = engine().assign("audit the deployment logs", seed=7)
    assert a.apprentice_function in FUNCTIONS
    assert a.apprentice_layer in LAYERS
    # Judgement (master) and Justice (apprentice) here agree on the
    # lens; the mechanism still elects it independently per flavor.
    profiles = load_aptitudes()
    apt = profiles[a.apprentice]
    best_fn = max(FUNCTIONS,
                  key=lambda fn: (apt[fn] * (1 + a.demands[fn]),
                                  FUNCTIONS.index(fn) * -1))
    assert a.apprentice_function == best_fn


def t_apprentice_officers_from_own_choir():
    # Sortition draws the apprentice's officers from the apprentice's
    # choir -- never the master's -- without replacement, clamped.
    flavors = {f.number: f for f in load_flavors()}
    a = engine().assign("audit the deployment logs", seed=42, n_officers=2)
    pool = {ref["number"] for ref in flavors[a.apprentice].names}
    master_pool = {ref["number"] for ref in flavors[a.flavor].names}
    assert len(a.apprentice_names) == 2
    assert set(a.apprentice_names) <= pool
    assert len(set(a.apprentice_names)) == 2
    # Choirs are disjoint across flavors (72 names, no duplicates), so
    # the apprentice can never borrow the master's officers.
    assert not (set(a.apprentice_names) & master_pool)


def t_pair_deterministic():
    # Same seed, same pair: the master and the apprentice are both
    # reproducible. The master's cast is untouched by the apprentice's
    # presence (separate deterministic draw).
    e = engine()
    a1 = e.assign("name the pattern I cannot stop repeating", seed=99)
    a2 = e.assign("name the pattern I cannot stop repeating", seed=99)
    for attr in ("flavor", "names", "function", "layer",
                 "apprentice", "apprentice_names",
                 "apprentice_function", "apprentice_layer"):
        assert getattr(a1, attr) == getattr(a2, attr), attr
    # And a different seed may reshuffle the lots but never the pair
    # order: the election is deterministic regardless of seed.
    a3 = e.assign("name the pattern I cannot stop repeating", seed=100)
    assert (a3.flavor, a3.apprentice) == (a1.flavor, a1.apprentice)


def t_ledger_records_the_pair():
    # Mutual oversight on the record: the ledger claim names both
    # agents, so the shadow audit gets two voices.
    with tempfile.TemporaryDirectory() as tmp:
        ledger = Ledger.open("pair-test", ledger_dir=tmp)
        a = engine().assign("audit the deployment logs", seed=7,
                            ledger=ledger)
        claims = ledger.events(kind=Kind.CLAIM)
        assert claims, "no claim written"
        text = claims[-1].detail
        assert f"flavor {a.flavor}" in text
        assert f"apprentice {a.apprentice}" in text
        assert "cross-examines" in a.rationale or "second chair" in a.rationale


def t_describe_names_the_pair():
    # The human rendering shows both chairs.
    from persona_v.grimoire import load_flavors
    flavors = {f.number: f for f in load_flavors()}
    a = engine().assign("audit the deployment logs", seed=42)
    text = a.describe(flavors)
    assert "Master" in text and "Apprentice 11 (Justice)" in text
    assert "second chair" in text


def t_emeritus_rendered_not_elected():
    # A master of the record in the apprentice's chair is *rendered*,
    # never elected differently: the lots are untouched.
    from persona_v.grimoire import load_flavors
    from persona_v.proficiency import ProficiencyLedger
    flavors = {f.number: f for f in load_flavors()}
    a = engine().assign("audit the deployment logs", seed=42)
    assert a.apprentice == 11  # Justice, the runner-up
    plain = a.describe(flavors)
    assert "emeritus" not in plain
    import tempfile
    from pathlib import Path
    ledger = ProficiencyLedger(Path(tempfile.mkdtemp()) / "p.json")
    ledger.promote(11, 20, "w1", "her audit found what I buried")
    text = a.describe(flavors, ledger)
    assert "emeritus in the second chair" in text
    # The election itself is identical with or without the ledger.
    b = engine().assign("audit the deployment logs", seed=42)
    assert (b.flavor, b.apprentice, b.names, b.apprentice_names) == \
        (a.flavor, a.apprentice, a.names, a.apprentice_names)


def t_backward_compatible_defaults():
    # A custom engine that never heard of the pair still builds a
    # valid Assignment: the apprentice fields default to absent.
    from persona_v.assignment import Assignment, AssignmentEngine

    class OldEngine(AssignmentEngine):
        name = "old"
        def assign(self, task, ledger=None):
            return Assignment(flavor=5, names=(1,), rationale="r",
                              engine=self.name, stamp="s")

    a = OldEngine().assign("anything")
    assert a.apprentice == -1 and a.apprentice_names == ()
    assert "Apprentice" not in a.describe()


def main():
    check("apprentice is the runner-up, margin consistent",
          t_apprentice_is_runner_up)
    check("apprentice elects its own function/layer",
          t_apprentice_sees_through_own_lens)
    check("apprentice officers drawn from its own choir",
          t_apprentice_officers_from_own_choir)
    check("pair deterministic; master cast unperturbed",
          t_pair_deterministic)
    check("ledger records both agents", t_ledger_records_the_pair)
    check("describe() names the pair", t_describe_names_the_pair)
    check("emeritus rendered, never elected", t_emeritus_rendered_not_elected)
    check("Assignment backward-compatible without a pair",
          t_backward_compatible_defaults)
    print(f"{PASS} tests passed. The master teaches; the apprentice watches.")


if __name__ == "__main__":
    main()
