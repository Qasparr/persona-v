# ☉ in 3° 57′ Libra  ☽ in 8° 36′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Analytical regression tests -- the healed doctrine, pinned.

These tests compute LIVE from the engine and the doctrine files
(the same method as analyze_persona.py); nothing is hand-tabulated.
They pin the analytical remedy's targets:

  1. exactly one native-Fe flavor (rating 2): the Empress (3);
  2. Justice (11) / Judgement (20) stand at Manhattan distance 4;
  3. self-election 31/31 -- every flavor's own aptitude profile,
     run as a demand vector, elects itself;
  4. all 22 trade charters elect their patron with margin >= 1
     (no margin-zero charters).

Run:  python3 tests/test_analysis.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.assignment import (  # noqa: E402
    DIMENSIONS, _elect, load_aptitudes, load_jobs,
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


def _ranked(scores, coverage):
    """The election's own tie-break order: score, coverage, lowest number."""
    return sorted(scores.items(), key=lambda kv: (-kv[1], -coverage[kv[0]],
                                                  kv[0]))


def _manhattan(a, b):
    return sum(abs(a.get(d, 0) - b.get(d, 0)) for d in DIMENSIONS)


def t_native_fe():
    # The system's one native Fe: the Empress (3). The remedy gave
    # her Fe:2; no other flavor may hold a native Fe.
    profiles = load_aptitudes()
    natives = sorted(n for n, p in profiles.items()
                     if p.get("Fe", 0) == 2)
    assert natives == [3], \
        f"native-Fe flavors (rating 2) must be exactly [3], got {natives}"


def t_justice_judgement_distance():
    # The remedy divided their jurisdictions (valuation/execution vs
    # audit/record): Manhattan distance exactly 4, never 2 again.
    profiles = load_aptitudes()
    d = _manhattan(profiles[11], profiles[20])
    assert d == 4, \
        f"Justice/Judgement distance must be 4, got {d}"


def t_self_election():
    # Every flavor's own profile elects itself. The imprint
    # recognizes itself -- 31/31, no absorptions.
    profiles = load_aptitudes()
    failures = []
    for n in sorted(profiles):
        winner, scores, coverage = _elect(profiles[n], profiles)
        if winner != n:
            failures.append((n, winner))
    assert not failures, \
        "self-election failures (flavor -> elected): " + ", ".join(
            f"{n}->{w}" for n, w in failures)


def t_charter_margins():
    # Every charter elects its patron, by a margin of at least 1.
    profiles = load_aptitudes()
    jobs = load_jobs()
    assert len(jobs) == 22, f"expected 22 trades, got {len(jobs)}"
    bad = []
    for j in sorted(jobs):
        charter = jobs[j]["charter"]
        patron = jobs[j]["patron"]
        winner, scores, coverage = _elect(charter, profiles)
        ranked = _ranked(scores, coverage)
        assert ranked[0][0] == winner, "ranking disagrees with _elect"
        margin = ranked[0][1] - ranked[1][1]
        if winner != patron or margin < 1:
            bad.append((jobs[j]["trade"], patron, winner, margin))
    assert not bad, \
        "charters failing patron/margin: " + ", ".join(
            f"{t} (patron {p}, elected {w}, margin {m})"
            for t, p, w, m in bad)


def main():
    check("exactly one native-Fe flavor: the Empress (3)", t_native_fe)
    check("Justice/Judgement Manhattan distance == 4",
          t_justice_judgement_distance)
    check("self-election 31/31", t_self_election)
    check("22 charters elect patrons with margin >= 1", t_charter_margins)
    print(f"{PASS} tests passed. The doctrine holds its shape.")


if __name__ == "__main__":
    main()
