#!/usr/bin/env python3
"""analyze_persona.py — quantitative analysis of the PERSONA V aptitude
system (v0.10.0). All figures are computed live from the engine and the
draft doctrine files; nothing is hand-tabulated.

Imprinting is operationalized as four testable properties:
  1. DISTINCTNESS — no two flavor profiles are near-identical
     (pairwise Manhattan distance over the 16 dimensions).
  2. COVERAGE — every dimension has strong (rating-2) representatives
     among flavors, and every dimension is demanded (rating>=1) by at
     least one trade charter.
  3. SELF-ELECTION — a flavor's own aptitude profile, run as a demand
     vector, elects that flavor (the imprint recognizes itself).
  4. DECISIVENESS — each trade charter elects its patron with margin,
     not by a hair.

Run: python3 analyze_persona.py   (prints the text summary)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from persona_v.assignment import (
    DIMENSIONS, FUNCTIONS, LAYERS, OPERATIONAL,
    load_aptitudes, load_jobs, _elect,
)
from persona_v import grimoire


def load():
    flavors = {f.number: f for f in grimoire.load_flavors()}
    return flavors, load_aptitudes(), load_jobs()


def vec(d):
    return [d.get(k, 0) for k in DIMENSIONS]


def manhattan(a, b):
    return sum(abs(x - y) for x, y in zip(vec(a), vec(b)))


def dimension_census(profiles):
    """Per dimension: counts of rating 2 / 1 / 0 and mean rating."""
    out = {}
    for dim in DIMENSIONS:
        vals = [p.get(dim, 0) for p in profiles.values()]
        out[dim] = {
            "n2": sum(1 for v in vals if v == 2),
            "n1": sum(1 for v in vals if v == 1),
            "n0": sum(1 for v in vals if v == 0),
            "mean": sum(vals) / len(vals),
        }
    return out


def nearest_neighbors(profiles, k=8):
    """k most-similar distinct flavor pairs (smallest Manhattan distance)."""
    pairs = []
    nums = sorted(profiles)
    for i, a in enumerate(nums):
        for b in nums[i + 1:]:
            pairs.append((manhattan(profiles[a], profiles[b]), a, b))
    pairs.sort()
    return pairs[:k]


def dominant(profile, dims):
    """Leading dimension in a group; ties break to earliest in order."""
    return max(dims, key=lambda d: (profile.get(d, 0), -dims.index(d)))


def flavor_imprints(profiles):
    """Per flavor: breadth, total weight, dominant function and layer."""
    out = {}
    for n, p in profiles.items():
        out[n] = {
            "breadth": sum(1 for d in DIMENSIONS if p.get(d)),
            "weight": sum(p.get(d, 0) for d in DIMENSIONS),
            "function": dominant(p, FUNCTIONS),
            "layer": dominant(p, LAYERS),
        }
    return out


def _ranked(scores, coverage):
    ranked = sorted(scores.items(),
                    key=lambda kv: (-kv[1], -coverage[kv[0]], kv[0]))
    return ranked


def self_election(profiles):
    """Does each flavor's own profile elect itself?"""
    out = {}
    for n in sorted(profiles):
        w, scores, coverage = _elect(profiles[n], profiles)
        ranked = _ranked(scores, coverage)
        assert ranked[0][0] == w, "ranking disagrees with _elect"
        out[n] = {
            "winner": w,
            "self": w == n,
            "margin": ranked[0][1] - ranked[1][1] if len(ranked) > 1 else 0,
            "runner_up": ranked[1][0] if len(ranked) > 1 else None,
            "runner_score": ranked[1][1] if len(ranked) > 1 else None,
            "own_score": scores[n],
        }
    return out


def charter_analysis(profiles, jobs):
    """Per trade: winner, margin, runner-up, elected function and layer."""
    out = {}
    for j in sorted(jobs):
        charter = jobs[j]["charter"]
        w, scores, coverage = _elect(charter, profiles)
        ranked = _ranked(scores, coverage)
        assert ranked[0][0] == w, "ranking disagrees with _elect"
        fn = dominant(charter, FUNCTIONS)
        layer = dominant(charter, LAYERS)
        out[j] = {
            "trade": jobs[j]["trade"],
            "patron": jobs[j]["patron"],
            "winner": w,
            "patron_elected": w == jobs[j]["patron"],
            "margin": ranked[0][1] - ranked[1][1] if len(ranked) > 1 else 0,
            "runner_up": ranked[1][0],
            "runner_score": ranked[1][1],
            "win_score": scores[w],
            "function": fn,
            "layer": layer,
        }
    return out


def analyze():
    flavors, profiles, jobs = load()
    return {
        "flavors": flavors,
        "profiles": profiles,
        "jobs": jobs,
        "flavor_census": dimension_census(profiles),
        "trade_census": dimension_census(
            {j: jobs[j]["charter"] for j in jobs}),
        "neighbors": nearest_neighbors(profiles),
        "imprints": flavor_imprints(profiles),
        "self_election": self_election(profiles),
        "charters": charter_analysis(profiles, jobs),
    }


def main():
    a = analyze()
    flavors = a["flavors"]
    print("== DIMENSION CENSUS (31 flavors): dim n2 n1 mean ==")
    for d, c in a["flavor_census"].items():
        print(f"  {d:10s} {c['n2']:2d} {c['n1']:2d}  {c['mean']:.2f}")
    print("== DIMENSION CENSUS (22 trade charters) ==")
    for d, c in a["trade_census"].items():
        print(f"  {d:10s} {c['n2']:2d} {c['n1']:2d}  {c['mean']:.2f}")
    print("== NEAREST FLAVOR PAIRS (Manhattan distance) ==")
    for dist, x, y in a["neighbors"]:
        print(f"  d={dist:2d}  {x:2d} {flavors[x].name:12s} ~ "
              f"{y:2d} {flavors[y].name}")
    print("== SELF-ELECTION FAILURES ==")
    fails = [n for n, s in a["self_election"].items() if not s["self"]]
    for n in fails:
        s = a["self_election"][n]
        print(f"  {n:2d} {flavors[n].name:12s} elects {s['winner']:2d} "
              f"{flavors[s['winner']].name:12s} (own {s['own_score']}, "
              f"margin {s['margin']})")
    print(f"  self-electing: {31 - len(fails)}/31")
    print("== CHARTER MARGINS (ascending) ==")
    for j, c in sorted(a["charters"].items(), key=lambda kv: kv[1]["margin"]):
        flag = "" if c["patron_elected"] else "  <-- OFF-PATRON"
        print(f"  margin {c['margin']:2d}  {c['trade']:14s} -> "
              f"{c['winner']:2d} {flavors[c['winner']].name:12s} "
              f"(runner {c['runner_up']:2d}, fn {c['function']}, "
              f"layer {c['layer']}){flag}")
    print("== COGNITIVE CENSUS OF TRADES ==")
    from collections import Counter
    print("  functions:", dict(Counter(c["function"]
                                       for c in a["charters"].values())))
    print("  layers:   ", dict(Counter(c["layer"]
                                       for c in a["charters"].values())))


if __name__ == "__main__":
    main()
