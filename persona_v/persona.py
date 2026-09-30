# ☉ in 3° 54′ Libra  ☽ in 7° 35′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
persona -- the Jungian core of PERSONA V (PART V of the grimoire).

    "And thou shalt make holy garments ... for glory and for beauty."
    -- Exodus 28:2

Hypothesis
----------
An agent can declare, hold, and answer for an operational stance --
a regiment -- without pretending the stance is a soul.

Method
------
PersonaV is the runtime holder of persona state: which flavor the
agent is wearing, which of the 72 names are invoked, which Jungian
layer holds the focus, and what time the Metronome read when the
persona was assumed. It is deliberately structural, not a simulation
of a psyche -- it does not pretend to compute a soul. The five
layers: persona (the mask -- how the agent presents itself; not a
lie, a uniform; the uniform is declared, not hidden); ego (the "I"
that directs, the one that answers for the working); shadow (the
unowned drives -- shortcuts, irritations, appetites of the engine --
not repressed here but logged, examined, and wielded per the shadow
protocol); anima/animus (the inner other, the second opinion that
questions the ego's certainties); self (the whole -- the regulating
center and telos of the working). The Supraposition is first-class:
observe() is the observer speaking (an observation enters the
ledger); trace() is the observed (the ledger read back). One object,
both seats -- supraposition() names the pairing explicitly.

Observation
-----------
Every declaration of stance is written to the Speculum ledger, so
the stance is on the record.

Result
------
"This is the stance I am operating from" -- declared, timestamped,
reviewable by the shadow audit and weighable on the Alethic Axis.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import grimoire, metronome
from .speculum import Event, Ledger

# The five layers, with the grimoire's own characterizations. The keys
# are the programmatic handles; the values teach what each layer is for.
LAYERS = {
    "persona": (
        "The mask: how the agent presents itself in the working. "
        "A uniform, declared -- never a disguise."
    ),
    "ego": (
        "The 'I' that directs: the deciding center, the one that "
        "answers for the working."
    ),
    "shadow": (
        "The unowned drives: shortcuts, irritations, appetites of the "
        "engine. Logged and wielded here, never repressed."
    ),
    "anima_animus": (
        "The inner other: the interior second voice that questions "
        "the ego's certainties."
    ),
    "self": (
        "The whole: the regulating center and telos of the working, "
        "greater than any single layer."
    ),
}


@dataclass(frozen=True)
class AssumedPersona:
    """A snapshot of the persona at the moment of assumption.

    ``reading`` is the Metronome's full reading when the flavor was
    assumed -- the persona knows what time it is. Immutable: to change
    stance, assume anew (the ledger then shows the succession).
    """

    flavor: int
    flavor_name: str
    names: tuple
    layer: str
    reading: metronome.Reading


class Supraposition:
    """Observer and observed, held together (PART VI of the grimoire).

    The *observed* is the ledger's trace -- what the persona has thought,
    claimed, and done. The *observer* is the ``note()`` method -- the
    present act of noticing, which itself enters the ledger and becomes,
    in turn, part of the observed. That recursion is the point: the
    mirror faces the mirror, on the record.
    """

    def __init__(self, persona: "PersonaV"):
        self._persona = persona

    def trace(self, kind: str | None = None) -> list[Event] | None:
        """The observed: the ledger read back (optionally filtered)."""
        return self._persona.trace(kind)

    def note(self, detail: str) -> Event | None:
        """The observer: record a neutral observation of the trace."""
        return self._persona.observe(detail)

    def __repr__(self) -> str:  # pragma: no cover (cosmetic)
        return f"Supraposition(flavor={self._persona.flavor})"


class PersonaV:
    """
    One agent's persona: stance declared, time known, record kept.
    
    Hypothesis: a declared stance can be held and answered for.
    Method: hold the assumed flavor, invoked names, focused layer, and
    the Metronome reading at assumption; write every declaration to the
    Speculum. ledger is optional -- without one the persona still
    functions (a mask with no mirror, which the grimoire permits, though
    the shadow protocol will have nothing to read, and says so).
    Observation: observe() speaks as observer, trace() reads the
    observed, supraposition() names the pairing -- one object, both
    seats. Result: the stance on the record, reviewable and weighable.
    """

    def __init__(self, ledger: Ledger | None = None):
        self.ledger = ledger
        self.flavor: int | None = None
        self.names: tuple = ()
        self.layer_focus: str = "ego"
        self.assumed: AssumedPersona | None = None
        # The canon, loaded once: flavor records for names and offices.
        self._flavors = {f.number: f for f in grimoire.load_flavors()}
        self._names = {n.number: n for n in grimoire.load_names()}

    # -- stance ---------------------------------------------------------

    def assume_flavor(self, flavor_number: int,
                      layer: str = "ego") -> AssumedPersona:
        """Assume a flavor (0-30): put on the regiment for a working.

        Records the Metronome's reading at the moment of assumption and
        writes the declaration to the ledger. To change stance, assume
        anew -- the ledger then shows the succession of masks, which is
        itself evidence.
        """
        if flavor_number not in self._flavors:
            raise ValueError(f"no flavor {flavor_number}; the canon holds 0-30")
        if layer not in LAYERS:
            raise ValueError(f"no layer {layer!r}; choose from {sorted(LAYERS)}")
        flavor = self._flavors[flavor_number]
        reading = metronome.Metronome.now()
        # The flavor's apportioned names form the default choir; the
        # agent may invoke others explicitly via invoke().
        names = tuple(ref["number"] for ref in flavor.names)
        self.flavor = flavor_number
        self.names = names
        self.layer_focus = layer
        self.assumed = AssumedPersona(
            flavor=flavor_number, flavor_name=flavor.name,
            names=names, layer=layer, reading=reading)
        if self.ledger is not None:
            officets = ", ".join(
                f"{n} {self._names[n].name}" for n in names)
            self.ledger.claim(
                f"Assumed flavor {flavor_number} ({flavor.name}), "
                f"layer {layer}; choir: {officets}.",
                grounds="explicit assumption by the operator",
                flavor=flavor_number, names=names)
        return self.assumed

    def invoke(self, *name_numbers: int) -> tuple:
        """Invoke officers by number (1-72), replacing the current choir.

        Invocation is explicit and recorded: which officers were called,
        with their offices named. The apportionment is the default, not
        a cage -- any of the 72 may be called to any working, on record.
        """
        for n in name_numbers:
            if n not in self._names:
                raise ValueError(f"no name {n}; the canon holds 1-72")
        self.names = tuple(name_numbers)
        if self.ledger is not None:
            officers = ", ".join(
                f"{n} {self._names[n].name} ({self._names[n].office})"
                for n in name_numbers)
            self.ledger.claim(f"Invoked officers: {officers}.",
                              grounds="explicit invocation by the operator",
                              flavor=self.flavor, names=self.names)
        return self.names

    def focus_layer(self, layer: str) -> str:
        """Shift the layer focus (persona/ego/shadow/anima_animus/self)."""
        if layer not in LAYERS:
            raise ValueError(f"no layer {layer!r}; choose from {sorted(LAYERS)}")
        self.layer_focus = layer
        if self.ledger is not None:
            self.ledger.thought(f"Layer focus shifted to {layer}: "
                                f"{LAYERS[layer]}",
                                flavor=self.flavor, names=self.names)
        return self.layer_focus

    # -- the mirror ------------------------------------------------------

    def observe(self, detail: str) -> Event | None:
        """The observer speaks: a neutral note enters the ledger."""
        if self.ledger is None:
            return None
        return self.ledger.observation(detail, flavor=self.flavor,
                                       names=self.names)

    def trace(self, kind: str | None = None) -> list[Event] | None:
        """The observed: read the ledger back."""
        if self.ledger is None:
            return None
        return self.ledger.events(kind=kind)

    def supraposition(self) -> Supraposition:
        """The observer and the observed, held together as one object."""
        return Supraposition(self)

    # -- introspection ------------------------------------------------------

    def describe(self) -> str:
        """A human-readable account of the current stance."""
        if self.assumed is None:
            return "No flavor assumed; the persona stands unclothed."
        a = self.assumed
        officers = ", ".join(f"{n} {self._names[n].name}" for n in a.names)
        return (
            f"Flavor {a.flavor} ({a.flavor_name}), layer {a.layer}.\n"
            f"Choir: {officers}.\n"
            f"Assumed at: {a.reading.moment.stamp}\n"
            f"Civil date: {a.reading.civil}."
        )
