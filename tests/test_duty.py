# ☉ in 5° 12′ Libra  ☽ in 18° 03′ Aries  dies lunae  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for duty.py -- Crowley's "Duty" as a core component
(the obligations pan of the Oz x Duty scale), and its Anchorage wiring.

Run:  python3 tests/test_duty.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.duty import (  # noqa: E402
    DUTIES,
    CanonicalReview,
    OzDutyPair,
    canonical_review,
    duty_keys,
    get_duty,
    oz_x_duty,
    resolve_duty,
    weigh_pair,
)

PASS = 0


def check(name, cond):
    global PASS
    assert cond, f"FAILED: {name}"
    PASS += 1
    print(f"  ok: {name}")


# -- the registry -------------------------------------------------------
check("four duties", len(DUTIES) == 4)
check("keys in essay order", duty_keys() == ["self", "others", "mankind", "all"])
check("titles", [d.title for d in DUTIES.values()] ==
      ["Duty to Self", "Duty to Others", "Duty to Mankind",
       "Duty to All Beings and Things"])

# -- verbatim Crowley lines (verified 2026-09-27, Ma'at red-pen pass) ---
check("self keystone", any("centre of your own Universe" in l
                           for l in DUTIES["self"].crowley))
check("others keystone", "Beware lest any force another, King against King!"
      in DUTIES["others"].crowley)
check("mankind keystone",
      "He who violated any right declares magically that it does not "
      "exist; therefore it no longer does so, for him."
      in DUTIES["mankind"].crowley)
check("all keystone", any("unflinchingly" in l for l in DUTIES["all"].crowley))
check("glosses marked", all(d.obligation.startswith("[gloss]")
                            for d in DUTIES.values()))
check("crowley lines are not gloss",
      all(not l.startswith("[gloss]") for d in DUTIES.values()
          for l in d.crowley))

# -- resolution ----------------------------------------------------------
check("resolve key", resolve_duty("self") is DUTIES["self"])
check("resolve title", resolve_duty("Duty to Mankind") is DUTIES["mankind"])
check("resolve title case-insensitive",
      resolve_duty("duty to all beings and things") is DUTIES["all"])
check("resolve alias", resolve_duty("other men and women") is DUTIES["others"])
check("resolve prefixed", resolve_duty("your duty to self") is DUTIES["self"])
check("resolve letter", resolve_duty("c") is DUTIES["mankind"])
check("resolve unknown -> None", resolve_duty("be excellent") is None)
check("resolve None -> None", resolve_duty(None) is None)
check("resolve empty -> None", resolve_duty("   ") is None)

# -- get_duty ------------------------------------------------------------
check("get_duty", get_duty("others").title == "Duty to Others")
try:
    get_duty("bogus")
    check("get_duty KeyError", False)
except KeyError:
    check("get_duty KeyError", True)

# -- weighing ------------------------------------------------------------
p = weigh_pair("free speech", "duty to others")
check("weigh_pair resolves", isinstance(p, OzDutyPair) and p.resolves)
check("weigh_pair factor 1.0", p.factor == 1.0)
q = weigh_pair("free speech", "vibes")
check("weigh_pair unresolved", not q.resolves and q.factor == 0.0)
check("oz_x_duty all canonical",
      oz_x_duty([("a", "self"), ("b", "Duty to Mankind")]) == 1.0)
check("oz_x_duty one bad zeroes",
      oz_x_duty([("a", "self"), ("b", "vibes")]) == 0.0)
check("oz_x_duty vacuous", oz_x_duty([]) == 1.0)

# -- canonical review -----------------------------------------------------
rev = canonical_review([("speak", "duty to others"), ("live", "vibes")])
check("review type", isinstance(rev, CanonicalReview))
check("review product", rev.product == 0.0)
check("review unresolved", rev.unresolved == ["live"])
check("review report", "UNRESOLVED" in rev.report()
      and "Duty to Others" in rev.report())

# -- Anchorage wiring ----------------------------------------------------
from persona_v.anchorage import Balance, Claim, admit  # noqa: E402

b = Balance(pairs=[("speak", "duty to others"), ("live", "vibes")])
check("balance holds (presence)", b.holds)
check("canonical_pairs", b.canonical_pairs()[0][2] is DUTIES["others"]
      and b.canonical_pairs()[1][2] is None)
check("unresolved_duties", b.unresolved_duties == ["live"])

w = admit([Claim("speak", right="free speech", duty="duty to others")])
check("admit canonical stays admitted", w.admitted)
check("report no unresolved note",
      "canonical duties unresolved" not in w.report())

w2 = admit([Claim("speak", right="free speech",
                 duty="no coercion of another's orbit")])
check("admit free-text duty still admitted", w2.admitted)
check("report names unresolved",
      "canonical duties unresolved: free speech" in w2.report()
      or "canonical duties unresolved: speak" in w2.report())

# -- package exports ------------------------------------------------------
import persona_v  # noqa: E402

check("package exports Duty", persona_v.Duty is not None)
check("package exports resolve_duty",
      persona_v.resolve_duty("self").key == "self")
check("version bumped", persona_v.__version__ == "0.21.0")

# -- CLI ------------------------------------------------------------------
from persona_v.cli import main  # noqa: E402

check("cli duty list", main(["duty"]) == 0)
check("cli duty one", main(["duty", "self"]) == 0)
check("cli duty unknown", main(["duty", "bogus"]) == 1)

print(f"\n{PASS} duty tests passed.")
