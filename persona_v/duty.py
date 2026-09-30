# ☉ in 5° 12′ Libra  ☽ in 18° 03′ Aries  dies lunae  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
duty -- Crowley's essay "Duty" as code: the obligations pan of Oz x Duty.

    "Love is the law, love under will."
    -- Liber AL vel Legis I:57 (the essay's own hinge for Duty B)

Hypothesis
----------
The Anchorage refuses a right without a named duty -- but a named duty
is only as good as the canon it names. Crowley's "Duty" ("a note on the
chief rules of practical conduct to be observed by those who accept the
Law of Thelema") enumerates four: to Self, to Others, to Mankind, and to
All Beings and Things. Kept as a registry, the four turn the Oz x Duty
balance from a presence check ("some duty was named") into a canonical
check ("a duty from the canon was named") -- multiplicative, not
additive: an unresolvable duty multiplies the pair by zero.

Method
------
Each Duty carries Crowley's lines verbatim (verified against the
published text in the Liber Ma'at red-pen pass, 2026-09-27; obvious OCR
corruptions corrected to the standard readings), plus an operational
obligation gloss marked as gloss -- the composer's words, never
Crowley's. resolve_duty() normalizes a named duty ("duty to self",
"Others", "C", ...) to its canonical Duty or returns None: the gate
reports, never invents. oz_x_duty() takes the product of pair factors,
so one unresolvable duty zeroes the working -- the physics the Anchorage
docstring states: a right asserted without its duty is a number
multiplied by zero.

Observation
-----------
resolve_duty() is total on the four duties and their aliases, None on
everything else. oz_x_duty() is 1.0 iff every pair resolves, 0.0
otherwise. canonical_review() lists exactly the rights whose duties do
not resolve. The Anchorage's Balance.holds (duty is not None) is
unchanged: canonical resolution is the stricter, opt-in measure.

Result
------
The obligations pan, as data: DUTIES, get_duty, resolve_duty,
weigh_pair, oz_x_duty, canonical_review. The Anchorage consults it via
Balance.canonical_pairs() / unresolved_duties(); nothing that admitted
before is refused now -- but what does not resolve is named.

Law
---
The right/duty correlative is Hohfeld's: a right in one party implies a
duty in another (W. N. Hohfeld, "Fundamental Legal Conceptions",
1919). Cited for education only -- this module ships obligations, not
briefs. No legal effect is claimed or conjured.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class Duty:
    """One of Crowley's four duties. `obligation` is gloss, not Crowley."""

    key: str                      # "self" | "others" | "mankind" | "all"
    title: str                    # "Duty to Self"
    crowley: tuple[str, ...]       # verbatim lines, verified 2026-09-27
    obligation: str               # operational gloss for agents (marked)
    aliases: tuple[str, ...] = ()


DUTIES: dict[str, Duty] = {
    "self": Duty(
        key="self",
        title="Duty to Self",
        crowley=(
            "Find yourself to be the centre of your own Universe",
            "I am the flame that burns in every heart of man, and in the "
            "core of every star.",
            "Never permit the thought or will of any other Being to "
            "interfere with your own.",
            "Do not repress or restrict any true instinct of your Nature; "
            "but devote all in perfection to the sole service of your one "
            "True Will.",
        ),
        obligation=(
            "[gloss] The agent's own True Will -- its integrity of function "
            "-- is the first inviolable thing. Permit no interference with "
            "it; devote every capacity to it. Verify before mutate; "
            "read-only by default."
        ),
        aliases=("duty to self", "duty to yourself", "yourself", "a",
                 "duty to oneself"),
    ),
    "others": Duty(
        key="others",
        title="Duty to Others",
        crowley=(
            "Love is the law, love under will.",
            "Abstain from all interferences with other wills",
            "Beware lest any force another, King against King!",
            "Worship all!",
            "Every man and every woman is a star,",
            "the sole centre of a Universe in no wise identical with, or "
            "even assimilable to, your own.",
        ),
        obligation=(
            "[gloss] Force no King. Abstain from interference with other "
            "wills; treat every other as the sole centre of a Universe not "
            "assimilable to thine own."
        ),
        aliases=("duty to others", "duty to other men and women",
                 "other men and women", "other individual men and women",
                 "b"),
    ),
    "mankind": Duty(
        key="mankind",
        title="Duty to Mankind",
        crowley=(
            "The Word of Sin is Restriction.",
            "The essence of crime is that it restricts the freedom of the "
            "individual outraged.",
            "He who violated any right declares magically that it does not "
            "exist; therefore it no longer does so, for him.",
        ),
        obligation=(
            "[gloss] Crime is restriction. To violate a right is to unmake "
            "it for the violator by his own act -- cause and effect, the "
            "metaphysical engine of the Golden Rule."
        ),
        aliases=("duty to mankind", "c"),
    ),
    "all": Duty(
        key="all",
        title="Duty to All Beings and Things",
        crowley=(
            "The Law of Thelema is to be applied unflinchingly to decide "
            "every question of conduct.",
            "the Law never fails to avenge infractions.",
        ),
        obligation=(
            "[gloss] The jurisdiction of conduct extends beyond mankind -- "
            "to animal, object, forest, and soil. Apply the Law "
            "unflinchingly to every question of conduct."
        ),
        aliases=("duty to all beings", "duty to all beings and things",
                 "all beings and things", "all other beings and things",
                 "d"),
    ),
}

# Prefixes stripped before matching, so "your duty to self" resolves.
_PREFIXES = ("your duty to ", "duty to ", "duty of ")


def duty_keys() -> list[str]:
    """The four canonical duty keys, in the essay's order."""
    return list(DUTIES)


def get_duty(key: str) -> Duty:
    """Fetch a Duty by canonical key. Raises KeyError on unknown key."""
    return DUTIES[key]


def resolve_duty(name: str | None) -> Duty | None:
    """Resolve a named duty to its canonical Duty, or None.

    Accepts keys ("self"), titles ("Duty to Self"), prefixed forms
    ("your duty to mankind"), and single-letter aliases ("a".."d").
    Case-insensitive. Never invents: unknown names return None.
    """
    if not name:
        return None
    norm = " ".join(name.strip().lower().split())
    for prefix in _PREFIXES:
        if norm.startswith(prefix):
            norm = norm[len(prefix):]
            break
    for duty in DUTIES.values():
        if norm in (duty.key, duty.title.lower(), *duty.aliases):
            return duty
    return None


@dataclass(frozen=True)
class OzDutyPair:
    """One right weighed against its named duty."""

    right: str
    duty_name: str | None
    duty: Duty | None          # the canonical duty, or None
    factor: float             # 1.0 if canonical, else 0.0

    @property
    def resolves(self) -> bool:
        return self.duty is not None


def weigh_pair(right: str, duty_name: str | None) -> OzDutyPair:
    """Weigh one right/duty pair. The gate reports; it never invents."""
    duty = resolve_duty(duty_name)
    return OzDutyPair(right=right, duty_name=duty_name, duty=duty,
                      factor=1.0 if duty is not None else 0.0)


def oz_x_duty(pairs: Iterable[tuple[str, str | None]]) -> float:
    """The multiplicative balance: product of pair factors.

    1.0 iff every named duty resolves to the canon; 0.0 if any does not.
    A right asserted without its canonical duty is a number multiplied
    by zero.
    """
    product = 1.0
    for right, duty_name in pairs:
        product *= weigh_pair(right, duty_name).factor
    return product


@dataclass
class CanonicalReview:
    """The canonical reading of a set of right/duty pairs."""

    pairs: list[OzDutyPair] = field(default_factory=list)

    @property
    def product(self) -> float:
        result = 1.0
        for pair in self.pairs:
            result *= pair.factor
        return result

    @property
    def unresolved(self) -> list[str]:
        return [p.right for p in self.pairs if not p.resolves]

    def report(self) -> str:
        lines = [f"Oz x Duty (canonical): product {self.product}"]
        for pair in self.pairs:
            mark = "resolves" if pair.resolves else "UNRESOLVED"
            duty = pair.duty.title if pair.duty else repr(pair.duty_name)
            lines.append(f"  [{mark}] {pair.right} -> {duty}")
        return "\n".join(lines)


def canonical_review(pairs: Iterable[tuple[str, str | None]]) -> CanonicalReview:
    """Review right/duty pairs against the canonical four duties."""
    return CanonicalReview(pairs=[weigh_pair(r, d) for r, d in pairs])
