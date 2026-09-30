# ☉ in 6° 16′ Libra  ☽ in 11° 3′ Taurus  dies martis  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for mothers.py -- the Three Mothers pipeline
(Babalon -> Lilith -> Mary/Liberty -> Action).

Run:  python3 tests/test_mothers.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.mothers import (  # noqa: E402
    MOTHERS,
    babalon_absorb,
    get_mother,
    lilith_filter,
    mary_synthesize,
    mother_keys,
    run_pipeline,
)

PASS = 0


def check(name, cond):
    global PASS
    assert cond, f"FAILED: {name}"
    PASS += 1
    print(f"  ok: {name}")


# -- the registry -------------------------------------------------------
check("three mothers", len(MOTHERS) == 3)
check("keys in pipeline order", mother_keys() == ["babalon", "lilith", "mary"])
check("orders", [MOTHERS[k].order for k in mother_keys()] == [1, 2, 3])
check("offices",
      [MOTHERS[k].office for k in mother_keys()] ==
      ["Absorb & Fuel", "Assert Sovereignty & Filter",
       "Prudent Synthesis & Output"])
check("get_mother by key", get_mother("lilith").title.startswith("Lilith"))
check("get_mother case-insensitive", get_mother("BABALON").key == "babalon")
check("get_mother by alias", get_mother("the veto").key == "lilith")
check("get_mother by alias (liberty)", get_mother("lady liberty").key == "mary")
check("get_mother unknown is None", get_mother("eve") is None)
check("get_mother empty is None", get_mother("") is None)

# -- Babalon: absorb & fuel -- never refuses -----------------------------
fuel = babalon_absorb("first line\n\nsecond line\n   \nthird")
check("babalon takes all non-empty segments",
      fuel.segments == ("first line", "second line", "third"))
check("babalon mass is the gross charge", fuel.mass == len("first line\n\nsecond line\n   \nthird"))
check("babalon raw preserved", fuel.raw.startswith("first line"))
empty = babalon_absorb("   \n  ")
check("babalon on empty input: no segments, still no refusal",
      empty.segments == () and empty.mass > 0)
check("babalon deterministic",
      babalon_absorb("x\ny").segments == babalon_absorb("x\ny").segments)

# -- Lilith: assert sovereignty & filter -- the veto ----------------------
no_duty = lilith_filter(fuel)
check("lilith with no duty refuses everything",
      no_duty.admitted == () and len(no_duty.refused) == 3)
check("lilith no-duty reason names the veto",
      all("veto" in r.reason for r in no_duty.refused))
bad_duty = lilith_filter(fuel, duty="duty to mars")
check("lilith with unresolvable duty refuses everything",
      bad_duty.admitted == () and len(bad_duty.refused) == 3)
check("lilith bad-duty reason says so",
      all("does not resolve" in r.reason for r in bad_duty.refused))
good = lilith_filter(fuel, duty="self")
check("lilith with resolvable duty admits everything",
      good.admitted == fuel.segments and good.refused == ())
check("lilith records the duty key", good.duty_key == "self")
check("lilith duty aliases resolve",
      lilith_filter(fuel, duty="Duty to Others").duty_key == "others")

# -- Mary: prudent synthesis & output -- terminates in a verdict ---------
restraint = mary_synthesize(no_duty)
check("mary on empty filtrate: restraint, not invention",
      restraint.restraint is True)
check("mary restraint says no action",
      restraint.action == "No action: nothing passed the filter.")
acted = mary_synthesize(good)
check("mary on admitted matter: action, not restraint",
      acted.restraint is False)
check("mary action carries the admitted matter",
      "first line" in acted.action and "duty 'self'" in acted.action)
check("mary note names prudent synthesis", "Prudent synthesis" in acted.note)

# -- the full pipeline ----------------------------------------------------
r = run_pipeline("a\nb", duty="mankind")
check("pipeline stages in canonical order",
      [m.key for m in r.stages()] == ["babalon", "lilith", "mary"])
check("pipeline admits under duty", r.filtrate.admitted == ("a", "b"))
check("pipeline terminates in action", r.verdict.restraint is False)
r2 = run_pipeline("a\nb")
check("pipeline without duty: total refusal, prudent restraint",
      r2.filtrate.admitted == () and r2.verdict.restraint is True)
check("pipeline deterministic",
      run_pipeline("a", duty="self").verdict.action ==
      run_pipeline("a", duty="self").verdict.action)
check("pipeline order is babalon-first: fuel independent of duty",
      run_pipeline("z", duty="self").fuel.segments ==
      run_pipeline("z").fuel.segments == ("z",))

print(f"\n{PASS} checks passed.")
