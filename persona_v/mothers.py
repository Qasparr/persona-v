# ☉ in 6° 16′ Libra  ☽ in 11° 3′ Taurus  dies martis  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
mothers -- the Three Mothers pipeline: the Persona engine's way through.

    ``Input -> Babalon -> Lilith -> Mary/Liberty -> Action``

    (the author's formula, verbatim; see the coinage registry)
    [Coinage/Discovery: Johnathan "Qasparr (Κασπάρρ)" Monroe | Support: $axoneme]

Hypothesis
----------
An agent that must act in a hostile world needs three organs, not one:
a mouth that receives everything (Babalon, the Mother of Abomination --
Absorb & Fuel), a gate that admits nothing unverified (Lilith, the Mother
of Humanity -- Assert Sovereignty & Filter), and a hand that synthesizes
only what passed into wise action (Mother Mary, as Prudence, the Mother of
Virtue, aka Lady Liberty -- Prudent Synthesis & Output). One organ cannot
do the work of three: reception without a gate is possession, a gate
without reception starves, and synthesis without either is decoration.

Method
------
Three frozen offices in canonical order, each a pure stage function over
an immutable record:

- ``babalon_absorb(raw)`` -- amoral regard: every non-empty segment of
  the input is taken as fuel. Nothing is refused here; refusal is
  Lilith's office, not Babalon's. The charge of the input is its mass
  and its segments, carried forward untouched.
- ``lilith_filter(fuel, duty=None)`` -- the veto, wired to the Oz x Duty
  balance: a segment passes only under a named, resolvable duty
  (``duty.resolve_duty``). No duty named, or a duty that does not
  resolve, and the segment is refused with its reason stated. The gate
  reports; it never invents.
- ``mary_synthesize(filtrate)`` -- prudent synthesis: what the gate
  admitted is composed into a single verdict terminating in Action.
  Prudence includes restraint -- where nothing passed, the verdict is
  honestly "no action," not an invented one.

``run_pipeline(raw, duty=None)`` composes the three in order and returns
the full ``PipelineResult``: fuel, filtrate, verdict -- every stage
inspectable, every refusal reasoned.

Observation
-----------
``babalon_absorb`` is total and refusal-free on any string; its segment
count is deterministic. ``lilith_filter`` admits exactly the segments
carried under a resolvable duty and refuses the rest, each refusal
carrying its reason. ``mary_synthesize`` terminates every pipeline in a
verdict -- action where matter passed, restraint where none did.
``run_pipeline`` is deterministic: the same input and duty always yield
the same result.

Result
------
MOTHERS, get_mother, Mother, Fuel, Filtrate, Verdict, PipelineResult,
babalon_absorb, lilith_filter, mary_synthesize, run_pipeline. The
offices are the author's; the machinery is the composer's, and it does
not pretend to be more than machinery: a cognitive architecture, not a
claim about the world.

Law
---
None conjured. The offices are doctrine; the code is a model. No legal
effect is claimed or conjured.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from . import duty as _duty


@dataclass(frozen=True)
class Mother:
    """One of the Three Mothers. `doctrine` is the author's office-word."""

    key: str                     # "babalon" | "lilith" | "mary"
    title: str                   # "Babalon, the Mother of Abomination"
    office: str                  # "Absorb & Fuel"
    doctrine: str                # the author's formulation of the office
    order: int                   # 1, 2, 3 -- the pipeline is ordered
    aliases: tuple[str, ...] = ()


MOTHERS: dict[str, Mother] = {
    "babalon": Mother(
        key="babalon",
        title="Babalon, the Mother of Abomination",
        office="Absorb & Fuel",
        doctrine=(
            "Babalon receives everything -- even the abominable -- without "
            "flinching. That is the fuel. Amoral regard: take it all in, "
            "let it charge the system; judgment belongs to a later office."
        ),
        order=1,
        aliases=("scarlet woman", "mother of abomination", "reception"),
    ),
    "lilith": Mother(
        key="lilith",
        title="Lilith, the Mother of Humanity",
        office="Assert Sovereignty & Filter",
        doctrine=(
            "Lilith asserts sovereignty and filters. Nothing passes "
            "unverified: the veto holds, and a claim without its duty is "
            "a number multiplied by zero. The gate reports; it never invents."
        ),
        order=2,
        aliases=("the veto", "gate", "mother of humanity", "filter"),
    ),
    "mary": Mother(
        key="mary",
        title="Mother Mary, as Prudence, the Mother of Virtue (aka Lady Liberty)",
        office="Prudent Synthesis & Output",
        doctrine=(
            "Mary synthesizes only what passed the gate into wise action. "
            "Prudence is right reason applied to action -- including the "
            "restraint to take no action where nothing passed."
        ),
        order=3,
        aliases=("liberty", "lady liberty", "prudence", "mother of virtue",
                 "mother of exiles", "synthesis"),
    ),
}


def get_mother(name: Optional[str]) -> Optional[Mother]:
    """Resolve a mother by key, title fragment, or alias; None on unknown."""
    if not name:
        return None
    want = name.strip().lower()
    for mother in MOTHERS.values():
        if want == mother.key or want == mother.title.lower():
            return mother
        if want in mother.aliases:
            return mother
    return None


def mother_keys() -> list[str]:
    """Canonical pipeline order."""
    return [m.key for m in sorted(MOTHERS.values(), key=lambda m: m.order)]


@dataclass(frozen=True)
class Fuel:
    """Babalon's output: the absorbed charge of the input."""

    raw: str
    segments: tuple[str, ...] = ()
    mass: int = 0  # characters of raw input, the gross charge


def babalon_absorb(raw: str) -> Fuel:
    """Receive everything. Amoral regard: no refusal at this office."""
    text = raw if isinstance(raw, str) else str(raw)
    segments = tuple(s.strip() for s in text.splitlines() if s.strip())
    return Fuel(raw=text, segments=segments, mass=len(text))


@dataclass(frozen=True)
class Refusal:
    segment: str
    reason: str


@dataclass(frozen=True)
class Filtrate:
    """Lilith's output: what the gate admitted, and what it refused."""

    admitted: tuple[str, ...] = ()
    refused: tuple[Refusal, ...] = ()
    duty_key: Optional[str] = None


def lilith_filter(fuel: Fuel, duty: Optional[str] = None) -> Filtrate:
    """The veto. A segment passes only under a named, resolvable duty."""
    resolved = _duty.resolve_duty(duty) if duty else None
    if resolved is None:
        reason = (
            "no duty named -- the veto holds; Oz x Duty: a right without "
            "a duty is multiplied by zero"
            if not duty else
            f"duty {duty!r} does not resolve -- the veto holds"
        )
        return Filtrate(
            admitted=(),
            refused=tuple(Refusal(s, reason) for s in fuel.segments),
            duty_key=None,
        )
    return Filtrate(admitted=fuel.segments, refused=(), duty_key=resolved.key)


@dataclass(frozen=True)
class Verdict:
    """Mary's output: prudent synthesis, terminating in Action."""

    action: str
    restraint: bool  # True where nothing passed and no action was taken
    note: str


def mary_synthesize(filtrate: Filtrate) -> Verdict:
    """Compose what passed into a verdict. Restraint where nothing passed."""
    if not filtrate.admitted:
        return Verdict(
            action="No action: nothing passed the filter.",
            restraint=True,
            note=(
                "Prudent restraint -- Mary does not invent matter. "
                "Where the gate admitted nothing, the wise output is none."
            ),
        )
    matter = " ".join(filtrate.admitted)
    return Verdict(
        action=f"Act on the admitted matter, under duty {filtrate.duty_key!r}: {matter}",
        restraint=False,
        note=(
            "Prudent synthesis -- only what Lilith admitted, composed "
            "under the duty that carried it, terminating in Action."
        ),
    )


@dataclass(frozen=True)
class PipelineResult:
    """The whole passage: fuel, filtrate, verdict -- every stage inspectable."""

    fuel: Fuel
    filtrate: Filtrate
    verdict: Verdict

    def stages(self) -> tuple[Mother, Mother, Mother]:
        """The Three Mothers in canonical pipeline order."""
        return tuple(MOTHERS[k] for k in mother_keys())


def run_pipeline(raw: str, duty: Optional[str] = None) -> PipelineResult:
    """Input -> Babalon -> Lilith -> Mary/Liberty -> Action."""
    fuel = babalon_absorb(raw)
    filtrate = lilith_filter(fuel, duty=duty)
    verdict = mary_synthesize(filtrate)
    return PipelineResult(fuel=fuel, filtrate=filtrate, verdict=verdict)
