# ☉ in 4° 34′ Libra  ☽ in 16° 47′ Aries  dies solis  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
anchorage -- the Zero-Trust Anchorage wired to the persona.

The gate itself now lives in the standalone ``trvvth`` package,
importable by any agent. This module wires it to the persona's own
furniture: Crowley's four duties as the canonical registry
(``resolve_duty``) and the thelemic metronome as the stamp
(``Metronome.now()``). Every right asserted is still multiplied by
its duty (Oz x Duty, not Oz + Duty); the heavens still stamp the
moment but never vote.

    "Prove all things; hold fast that which is good."
    -- 1 Thessalonians 5:21
"""

from __future__ import annotations

from dataclasses import dataclass

from trvvth.anchorage import (  # noqa: F401 -- the standalone gate
    ASSERTION,
    CITATION,
    KINDS,
    NUMBER,
    QUOTE,
    AnchoredWorking,
    Assessment,
    Claim,
    cardinal_rules,
    weigh_claim,
)
from trvvth.anchorage import Balance as _CoreBalance
from trvvth.anchorage import admit as _core_admit
from trvvth.anchorage import weigh_rights as _core_weigh_rights
from trvvth.alethic import FALSEHOOD, TRVVTH, UNRESOLVED  # noqa: F401

from .duty import resolve_duty
from .metronome import Metronome


@dataclass
class Balance(_CoreBalance):
    """Oz x Duty with the canonical registry wired as the default.

    The standalone gate leaves ``duty_resolver`` open; the persona
    closes it on Crowley's four duties -- the original contract.
    """

    def __post_init__(self):
        if self.duty_resolver is None:
            self.duty_resolver = resolve_duty


def weigh_rights(claims: list[Claim]) -> Balance:
    """Oz x Duty with the canonical registry wired in."""
    return _core_weigh_rights(claims, duty_resolver=resolve_duty)


def admit(claims: list[Claim], dt=None) -> AnchoredWorking:
    """Run claims through the gate; stamp with the metronome.

    ``dt`` is passed to ``Metronome.now`` (None for now). The stamp
    authenticates when, never whether.
    """
    reading = Metronome.now(dt)
    return _core_admit(
        claims,
        duty_resolver=resolve_duty,
        stamp=reading.moment.stamp,
        sun_in_anchorage=reading.sun_in_anchorage,
        moon_in_anchorage=reading.moon_in_anchorage,
    )
