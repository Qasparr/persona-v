#!/usr/bin/env python3
"""Wide brute-force search for remedy round 2 (Star 17 + Nut 26 fixes).

17 and 26 are mutually entangled (each other's runner-up), so this
searches them jointly, plus optional targeted charter strengthenings
(v0.11.0 precedent) for the fragile Oracle (trade 2) and Chronicler
(trade 10) charters.

Constraints (no regressions vs v0.11.0 healed state):
  - 31/31 self-election, 17/23/26 margins >= 1
  - 22/22 charters elect patrons with margin >= 1
  - no NEW margin-zero self-elections (baseline {1,2,5,13,18,25})
  - min pairwise Manhattan distance >= 3
  - native Fe == [3]; Justice/Judgement distance == 4
  - 14 (Temperance) keeps self-margin >= 1 (its Alchemist charter
    demands Ni:2/anima:2, so 14 is untouchable)
"""
import importlib.util
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location("ap", "analyze_persona.py")
ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
from persona_v.assignment import DIMENSIONS

a = ap.analyze()
jobs_base = a["jobs"]
base = {n: {d: p.get(d, 0) for d in DIMENSIONS} for n, p in a["profiles"].items()}
# revert 17/26 to pre-round-2; keep 23's verified fix
base[17] = {d: {'Ni': 2, 'Ti': 1, 'Si': 1, 'Fe': 1, 'anima': 1, 'self': 2,
                'persona': 1, 'precision': 1, 'gravity': 1}.get(d, 0) for d in DIMENSIONS}
base[26] = {d: {'Ni': 1, 'Ne': 1, 'Si': 1, 'self': 2, 'persona': 1,
                'anima': 1, 'gravity': 1}.get(d, 0) for d in DIMENSIONS}
BASE_M0 = {1, 2, 5, 13, 18, 25}

# Charter strengthening options: (trade_no, {dim: new_rating})
# Only options that help the patron vs the observed contenders.
CHARTER_OPTS = [
    None,
    (2, {"Fi": 1}),        # Oracle: the unspoken includes the unfelt
    (2, {"shadow": 2}),    # Oracle: deepen the dark already named
    (10, {"swiftness": 2}),  # Chronicler: the record keeps pace
    (10, {"Ne": 2}),       # Chronicler: the turning wheel sees all
]


def check(profiles, jobs):
    se = ap.self_election(profiles)
    if any(not s["self"] for s in se.values()):
        return None
    if se[17]["margin"] < 1 or se[26]["margin"] < 1 or se[23]["margin"] < 1:
        return None
    m0 = {n for n, s in se.items() if s["margin"] < 1}
    if not m0 <= BASE_M0:
        return None
    ca = ap.charter_analysis(profiles, jobs)
    if any(not c["patron_elected"] or c["margin"] < 1 for c in ca.values()):
        return None
    nums = sorted(profiles)
    mind = min(sum(abs(profiles[x][d] - profiles[y][d]) for d in DIMENSIONS)
               for i, x in enumerate(nums) for y in nums[i + 1:])
    if mind < 3:
        return None
    if [n for n in nums if profiles[n]["Fe"] == 2] != [3]:
        return None
    if sum(abs(profiles[11][d] - profiles[20][d]) for d in DIMENSIONS) != 4:
        return None
    if se[14]["margin"] < 1:
        return None
    return {"m17": se[17]["margin"], "m26": se[26]["margin"],
            "m23": se[23]["margin"], "m14": se[14]["margin"], "mind": mind}


def main():
    opts17 = list(itertools.combinations(
        ["anima", "gravity", "Ti", "persona", "Si"], 2))
    dims26 = ["Ne", "Ni", "Si", "persona", "anima", "gravity"]
    opts26 = [c for r in (2, 3) for c in itertools.combinations(dims26, r)]
    valid = []
    total = len(opts17) * len(opts26) * len(CHARTER_OPTS)
    done = 0
    for p17 in opts17:
        for s26 in opts26:
            for copt in CHARTER_OPTS:
                done += 1
                profiles = {n: dict(p) for n, p in base.items()}
                for d in p17:
                    profiles[17][d] = 2
                for d in s26:
                    profiles[26][d] = 2
                jobs = {j: dict(v) for j, v in jobs_base.items()}
                if copt:
                    t, upd = copt
                    ch = dict(jobs[t]["charter"])
                    ch.update(upd)
                    jobs[t] = dict(jobs[t], charter=ch)
                res = check(profiles, jobs)
                if res:
                    # cost: aptitude edits + 2x for charter edits (doctrine weight)
                    cost = 2 * len(p17) + 2 * len(s26) + (4 if copt else 0)
                    valid.append((cost, p17, s26, copt, res))
    valid.sort(key=lambda v: v[0])
    out = [{"cost": v[0], "raise17": list(v[1]), "raise26": list(v[2]),
            "charter": ({"trade": v[3][0], "set": v[3][1]} if v[3] else None),
            "margins": v[4]} for v in valid[:20]]
    print(json.dumps({"searched": total, "valid": len(valid), "best": out}, indent=1))


if __name__ == "__main__":
    main()
