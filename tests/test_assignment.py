# ☉ in 3° 54′ Libra  ☽ in 7° 35′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for assignment.py -- the Assignment engine (Phase 2).

Run:  python3 tests/test_assignment.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.assignment import (  # noqa: E402
    CONFLICTS, DIMENSIONS, FUNCTIONS, LAYERS, Assignment, AssignmentEngine,
    AptitudeAssignmentEngine, HeuristicAssignmentEngine,
    _elect, classify_job, load_aptitudes, load_jobs, probe_demands,
    resolve_job, validate_demands,
)
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


def engine():
    return AptitudeAssignmentEngine()


def t_judgement_for_audit():
    # Judgement's character *is* "the audit" -- the aptitude test agrees.
    a = engine().assign("audit the deployment logs", seed=1)
    assert a.flavor == 20, f"got flavor {a.flavor}"
    assert a.names == (51, 52)  # Judgement's apportioned choir
    assert a.engine == "aptitude-v1"
    assert a.function == "Ti" and a.layer == "ego"
    assert a.margin >= 0 and a.scores[20] == max(a.scores.values())


def t_fool_for_beginning():
    a = engine().assign("begin a new working")
    assert a.flavor == 0, f"got flavor {a.flavor}"
    # sortition: 2 of the Fool's 3 drawn, no duplicates, all canonical
    assert len(a.names) == 2 and set(a.names) <= {1, 2, 3}
    assert len(set(a.names)) == 2


def t_tower_for_debugging():
    # the model collapsed -> the Tower (sudden collapse of false models)
    a = engine().assign("debug the crash fast - the model collapsed",
                        seed=1)
    assert a.flavor == 16, f"got flavor {a.flavor}"
    assert a.names == (43, 44)
    assert a.function == "Ti"


def t_isis_for_remedy():
    # structured demands: the caller states what the work needs
    a = engine().assign("remedy work",
                        demands={"anima": 2, "self": 2, "precision": 2,
                                 "Ti": 1, "Si": 1}, seed=1)
    assert a.flavor == 28, f"got flavor {a.flavor}"
    assert a.names == (67, 68)
    assert "structured" in a.rationale


def t_default_when_no_match():
    # no probe catches the task: all-zero demands elect the Fool
    # through the tie-break, not a special case
    a = engine().assign("xyzzy plugh", seed=1)
    assert a.flavor == 0
    assert all(v == 0 for v in a.demands.values())
    assert "none detected" in a.rationale


def t_elect_unit():
    # breadth of fit beats raw score ties; lowest number breaks the rest
    from persona_v.assignment import DIMENSIONS
    full = lambda **kw: {d: kw.get(d, 0) for d in DIMENSIONS}
    w, s, c = _elect(full(Ti=1, Si=1),
                     {1: full(Ti=2), 2: full(Ti=1, Si=1)})
    assert w == 2, f"breadth should win, got {w}"  # both score 2
    w, s, c = _elect(full(Ti=1), {5: full(Ti=2), 9: full(Ti=2)})
    assert w == 5, f"lowest should win, got {w}"
    w, s, c = _elect(full(), {3: full(), 0: full()})
    assert w == 0


def t_deterministic():
    e = engine()
    # the election itself is deterministic even unseeded ...
    a1 = e.assign("verify the deployment pipeline")
    a2 = e.assign("verify the deployment pipeline")
    assert (a1.flavor, a1.function, a1.layer) == \
        (a2.flavor, a2.function, a2.layer)
    # ... and seeded lots reproduce exactly
    b1 = e.assign("verify the deployment pipeline", seed=5)
    b2 = e.assign("verify the deployment pipeline", seed=5)
    assert (b1.flavor, b1.names) == (b2.flavor, b2.names)


def t_empty_task_refused():
    for bad in ("", "   "):
        try:
            engine().assign(bad)
            assert False, "empty task assigned"
        except ValueError:
            pass


def t_assignment_bounds():
    e = engine()
    for task in ["audit everything", "build the tower", "heal and begin",
                 "watch the shadows gather"]:
        a = e.assign(task)
        assert 0 <= a.flavor <= 30
        assert all(1 <= n <= 72 for n in a.names)
        assert a.stamp and "Anno" in a.stamp


def t_logged_with_grounds():
    tmp = tempfile.TemporaryDirectory()
    L = Ledger.open("a1", ledger_dir=tmp.name)
    a = engine().assign("weigh the evidence fairly", ledger=L)
    claims = L.events(kind=Kind.CLAIM)
    assert len(claims) == 1
    assert f"flavor {a.flavor}" in claims[0].detail
    assert "aptitude-v1" in claims[0].meta["grounds"]
    assert claims[0].flavor == a.flavor


def t_abstract_contract():
    try:
        AssignmentEngine()
        assert False, "abstract engine instantiated"
    except TypeError:
        pass
    # the contract is substitutable: a custom engine plugs in cleanly
    class JohnsEngine(AssignmentEngine):
        name = "johns-true-system"
        def assign(self, task, ledger=None):
            return Assignment(flavor=11, names=(33, 34),
                              rationale="the author's own rules",
                              engine=self.name, stamp="stamp")
    a = JohnsEngine().assign("anything")
    assert a.engine == "johns-true-system" and a.flavor == 11


def t_describe():
    from persona_v.grimoire import load_flavors
    flavors = {f.number: f for f in load_flavors()}
    a = engine().assign("audit the deployment logs", seed=1)
    text = a.describe(flavors)
    assert "aptitude-v1" in text and "Judgement" in text
    assert "function Ti" in text and "layer ego" in text
    assert "Scores:" in text
    assert "flavor 20" in a.describe()  # also renders without the dict


def t_sortition_seeded_deterministic():
    e1 = HeuristicAssignmentEngine(seed=42)
    e2 = HeuristicAssignmentEngine(seed=42)
    a1 = e1.assign("begin a new working")
    a2 = e2.assign("begin a new working")
    assert a1.names == a2.names  # same seed, same lots
    # per-call seed overrides the engine default
    a3 = HeuristicAssignmentEngine().assign("begin a new working", seed=42)
    assert a3.names == a1.names
    assert "seed=42" in a1.rationale and "sortition" in a1.rationale


def t_sortition_unseeded_varies_honestly():
    # Without a seed the lots fall from entropy: not asserted to differ
    # (that would be flaky), only asserted to be well-formed every time.
    e = HeuristicAssignmentEngine()
    for _ in range(50):
        a = e.assign("begin a new working")
        assert len(a.names) == 2 and set(a.names) <= {1, 2, 3}
        assert a.names == tuple(sorted(a.names))


def t_devil_never_invokes_contradiction():
    # Flavor 15's entire choir IS the conflict pair {41, 42}: the repair
    # path must drop one, every time, for every seed.
    for s in range(200):
        a = AptitudeAssignmentEngine(seed=s).assign(
            "confront the pattern",
            demands={"shadow": 2, "gravity": 2, "Fi": 1})
        assert a.flavor == 15, f"seed {s}: got flavor {a.flavor}"
        assert not ({41, 42} <= set(a.names)), f"seed {s}: contradiction"
        assert len(a.names) == 1  # one dropped, one remains


def t_conflicts_table_is_complete():
    # Survey 2026-09-26 (author's leave): all 31 choirs read for
    # intra-choir contradiction. The bar is direct verbal opposition of
    # commanded acts within one chair (bind/sever, name-the-chain /
    # break-the-chain). Productive tension (Rehael's mixing, Atum's
    # being/becoming, Set's wielded-and-honored storm) is not
    # contradiction, and cross-choir pairs could never fire because the
    # draw pool is one flavor's apportioned names. Pin the table: a new
    # opposition enters only deliberately, meeting the bar.
    assert CONFLICTS == frozenset({frozenset({20, 21}),
                                   frozenset({41, 42})}), CONFLICTS


def t_lovers_never_binds_and_severs():
    # Flavor 6's choir {19,20,21} contains the pair {20,21}: draws must
    # never hold both, across many seeds.
    for s in range(200):
        a = AptitudeAssignmentEngine(seed=s).assign(
            "choose and decide what I truly value")
        assert a.flavor == 6, f"seed {s}: got flavor {a.flavor}"
        assert not ({20, 21} <= set(a.names)), f"seed {s}: contradiction"
        assert len(a.names) == 2


def t_n_officers_clamped_and_validated():
    e = HeuristicAssignmentEngine()
    a = e.assign("audit the deployment logs", n_officers=99)  # clamped
    assert set(a.names) == {51, 52}
    for bad in (0, -3):
        try:
            e.assign("audit the books", n_officers=bad)
            assert False, f"n_officers={bad} accepted"
        except ValueError:
            pass
    try:
        HeuristicAssignmentEngine(n_officers=0)
        assert False, "engine accepted n_officers=0"
    except ValueError:
        pass


def t_probe_battery():
    d = probe_demands("debug the crash fast, and be precise about it")
    assert d["Ti"] >= 1 and d["swiftness"] >= 1 and d["precision"] >= 1
    # hits cap at 2, never above
    d2 = probe_demands("debug debug debug analyze analyze model model")
    assert d2["Ti"] == 2
    assert set(d) == set(d2) and all(v in (0, 1, 2) for v in d2.values())


def t_structured_demands_verbatim():
    e = engine()
    a = e.assign("any words at all", demands={"Ti": 2}, seed=1)
    assert a.demands["Ti"] == 2
    assert all(v == 0 for k, v in a.demands.items() if k != "Ti")
    assert "structured" in a.rationale
    # same demands, same election, regardless of the task text
    b = e.assign("completely different words", demands={"Ti": 2}, seed=1)
    assert (a.flavor, a.names) == (b.flavor, b.names)


def t_structured_demands_invalid():
    e = engine()
    for bad in ({"Nope": 1}, {"Ti": 5}, {"Ti": -1}, {"Ti": "high"},
                {"Ti": True}, "Ti", [("Ti", 2)]):
        try:
            e.assign("task", demands=bad)
            assert False, f"accepted {bad!r}"
        except ValueError:
            pass
    # constructor-level defaults are validated too
    try:
        AptitudeAssignmentEngine(demands={"Ti": 9})
        assert False, "engine accepted bad default demands"
    except ValueError:
        pass


def t_engine_default_demands():
    e = AptitudeAssignmentEngine(demands={"Fe": 2})
    a = e.assign("any words", seed=1)
    assert a.demands["Fe"] == 2 and "engine default" in a.rationale
    # per-call demands override the engine default
    b = e.assign("any words", demands={"Ti": 2}, seed=1)
    assert b.demands["Ti"] == 2 and "structured" in b.rationale


def t_function_and_layer_elected():
    a = engine().assign("comfort a grieving friend", seed=1)
    assert a.function == "Fe", f"got {a.function}"
    assert a.layer == "anima", f"got {a.layer}"
    assert a.function in FUNCTIONS and a.layer in LAYERS


def t_scorecard_in_rationale():
    a = engine().assign("audit the deployment logs", seed=1)
    assert "margin" in a.rationale and "runner-up" in a.rationale
    assert a.scores[a.flavor] == max(a.scores.values())
    assert a.margin == a.scores[a.flavor] - sorted(
        a.scores.values(), reverse=True)[1]


def t_job_classification():
    # the Auditor's charter (doctrine) replaces the rough probed vector
    a = engine().assign("audit the deployment logs", seed=1)
    assert a.job == "The Auditor", f"got {a.job}"
    assert a.demands == load_jobs()[20]["charter"]
    assert "charter of The Auditor" in a.rationale
    assert a.flavor == 20  # the charter elects Judgement


def t_explicit_job():
    e = engine()
    a = e.assign("do it", job="The Confessor", seed=1)
    assert a.job == "The Confessor" and a.flavor == 15
    b = e.assign("do it", job=15, seed=1)
    assert (a.flavor, a.names) == (b.flavor, b.names)  # name == number
    # explicit demands outrank a named job
    c = e.assign("do it", job="The Confessor", demands={"Ti": 2}, seed=1)
    assert c.job is None and c.demands["Ti"] == 2
    for bad in ("The Cobbler", 99, -1, True, 2.5):
        try:
            e.assign("do it", job=bad)
            assert False, f"accepted job {bad!r}"
        except ValueError:
            pass
    try:
        AptitudeAssignmentEngine(job="The Cobbler")
        assert False, "engine accepted bad default job"
    except ValueError:
        pass


def t_job_no_fit_falls_back():
    # nothing classifiable: probed demands, the Fool by tie-break
    a = engine().assign("xyzzy plugh", seed=1)
    assert a.job is None and a.flavor == 0


def t_classify_job_unit():
    from persona_v.assignment import DIMENSIONS
    full = lambda **kw: {d: kw.get(d, 0) for d in DIMENSIONS}
    jobs = {0: {"trade": "A", "charter": full(Ti=2)},
            1: {"trade": "B", "charter": full(Ti=2)}}
    num, scores = classify_job(full(Ti=1), jobs)
    assert num == 0  # tie -> lowest trade number
    num, _ = classify_job(full(), jobs)
    assert num is None  # no fit at all -> None
    assert resolve_job("the auditor") == 20  # case-insensitive names


def t_job_charters_elect_patrons():
    # every trade's charter should elect its own patron: the common
    # case stays intelligible; the author tunes the exceptions
    jobs, profs = load_jobs(), load_aptitudes()
    for num in range(22):
        w, _, _ = _elect(jobs[num]["charter"], profs)
        assert w == jobs[num]["patron"], (
            f"{jobs[num]['trade']}: charter elects {w}, "
            f"patron is {jobs[num]['patron']}")


def t_draw_officers_unit():
    import random
    from persona_v.assignment import _draw_officers
    rng = random.Random(7)
    for _ in range(100):
        d = _draw_officers([19, 20, 21], 2, rng)
        assert len(d) == 2 and not ({20, 21} <= set(d))
        assert d == tuple(sorted(d)) and len(set(d)) == 2
        assert all(1 <= x <= 72 for x in d)
    # clamping: asking for more than the pool gives the pool
    assert set(_draw_officers([33, 34], 5, rng)) == {33, 34}


if __name__ == "__main__":
    check("audit task -> Judgement (XX)", t_judgement_for_audit)
    check("beginning task -> Fool (0)", t_fool_for_beginning)
    check("debugging task -> Tower (XVI)", t_tower_for_debugging)
    check("healing task -> Isis (XXVIII)", t_isis_for_remedy)
    check("no match -> Fool by default", t_default_when_no_match)
    check("election: breadth then lowest wins", t_elect_unit)
    check("probe battery: demands 0-2", t_probe_battery)
    check("structured demands used verbatim", t_structured_demands_verbatim)
    check("structured demands validated hard", t_structured_demands_invalid)
    check("engine default demands + override", t_engine_default_demands)
    check("function and layer elected", t_function_and_layer_elected)
    check("scorecard in rationale", t_scorecard_in_rationale)
    check("job classified; charter rules", t_job_classification)
    check("explicit job by name/number", t_explicit_job)
    check("no trade fit falls back", t_job_no_fit_falls_back)
    check("classify_job unit behavior", t_classify_job_unit)
    check("charters elect their patrons", t_job_charters_elect_patrons)
    check("deterministic assignments", t_deterministic)
    check("empty task refused", t_empty_task_refused)
    check("assignments within canon bounds", t_assignment_bounds)
    check("assignment logged as claim with grounds", t_logged_with_grounds)
    check("abstract contract + custom engine", t_abstract_contract)
    check("describe renders", t_describe)
    check("sortition: seeded draws reproducible", t_sortition_seeded_deterministic)
    check("sortition: unseeded draws well-formed", t_sortition_unseeded_varies_honestly)
    check("Devil: contradiction never invoked", t_devil_never_invokes_contradiction)
    check("Lovers: never binds and severs", t_lovers_never_binds_and_severs)
    check("conflict table complete at two pairs", t_conflicts_table_is_complete)
    check("n_officers clamped and validated", t_n_officers_clamped_and_validated)
    check("_draw_officers unit behavior", t_draw_officers_unit)
    print(f"\n{PASS} tests passed. The regiment is assigned.")
