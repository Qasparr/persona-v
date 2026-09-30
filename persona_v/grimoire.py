# ☉ in 3° 54′ Libra  ☽ in 7° 31′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
grimoire -- the loader for the PERSONA V data canon.

    "If any man shall add unto these things, God shall add unto him
    the plagues that are written in this book." -- Revelation 22:18

Hypothesis
----------
The grimoire (the 31 flavors, the 72 names, the 13 signs) is data,
not logic -- and one doorway to it keeps every consumer in
agreement.

Method
------
Names, offices, and mottos are facts about the system; they change
by authorial decree, not by code edit. So they live in YAML files
under persona_v/data/ -- human-readable, human-editable, under
version control -- and this module is the single doorway through
which code reads them. Every consumer (the Assignment engine, the
Speculum, the CLI, tomorrow's API) must agree on what "name 33"
means: one loader, one truth; drift impossible by construction.
The three record types mirror PART III and PART IV of PERSONA_V.md:
Flavor -- one of the 31 operational modalities (22 of the Tarot, 9
of the Ennead), a regiment, a way the persona conducts itself for a
working; Name -- one of the 72 officers (the Shemhamphorash,
reassigned), a narrow named responsibility with a Latin Modus
Operandi; Sign -- one of the 13 zodiacal signs, the thirteenth the
author's Anchorage at the Cusp of Power. All loading is strict: a
malformed canon raises, never silently degrades.

Observation
-----------
load_flavors(), load_names(), load_signs(): the canon as records.

Result
------
A persona system that guesses about its own officers is already
lying to itself -- and the Alethic Axis forbids it.
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path

# The data directory sits beside this file: persona_v/data/*.yaml.
# Resolving it from __file__ (not from the working directory) means the
# package loads correctly no matter where it is imported from.
_DATA_DIR = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True)
class Flavor:
    """One of the 31 flavors: an operational modality of the persona.

    ``number`` is 0-30 (Flavor 0 is the Fool; XXX is 30, Horus).
    ``anchor`` names what the flavor is moored to: "Trump 0".."Trump XXI"
    for the twenty-two of the Tarot, or the god's name for the nine of the
    Ennead. ``names`` lists the officers apportioned to this flavor --
    three for flavors 0-9, two for flavors 10-30, seventy-two in all.
    Frozen: the canon does not mutate at runtime. The author edits the
    YAML; the code only reads.
    """

    number: int
    name: str
    epithet: str
    anchor: str
    anchor_type: str  # "tarot" or "ennead"
    character: str
    names: list = field(default_factory=list)  # list of {"number","name"}


@dataclass(frozen=True)
class Name:
    """One of the 72 names: an officer of the system.

    ``office`` is the short title ("Weigher of TRVVTH"); ``duty`` is the
    longer charge describing what the officer actually does; ``motto`` is
    the Latin Modus Operandi; ``gloss`` its English rendering. ``flavor``
    is the number of the presiding flavor (0-30).

    ``gender`` and ``sexuality`` are assigned as per behavioral
    assessment of the office and duty (see ``persona_v.naming``);
    the default is non-binary and abstinent, and ``assessment`` records
    the basis. Whether the binary assignments make a difference is the
    device's current user's decision (the naming policy); by default
    the names remain nonlinear and fluid.
    """

    number: int  # 1-72, the classical Shemhamphorash order
    name: str
    flavor: int
    office: str
    duty: str
    motto: str
    gloss: str
    gender: str = "nonbinary"
    sexuality: str = "abstinent"
    assessment: str | None = None


@dataclass(frozen=True)
class Sign:
    """One of the 13 zodiacal signs.

    The thirteenth -- the Anchorage -- carries no classical element,
    modality, ruler, or glyph yet: those are the author's to bestow.
    ``None`` here is honest emptiness, not missing data.
    """

    number: int  # 1-13
    name: str
    glyph: str | None
    element: str | None
    modality: str | None
    ruler: str | None
    epithet: str | None = None
    note: str | None = None


def _read(name: str) -> dict:
    """Read and parse one YAML data file. Strict: missing file = error."""
    path = _DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"grimoire data missing: {path}")
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_flavors() -> list[Flavor]:
    """Load the 31 flavors, sorted by number."""
    raw = _read("flavors.yaml")["flavors"]
    flavors = [Flavor(**{k: v for k, v in f.items()}) for f in raw]
    return sorted(flavors, key=lambda f: f.number)


def load_names() -> list[Name]:
    """Load the 72 names in classical order (1-72)."""
    raw = _read("names.yaml")["names"]
    names = [Name(**{k: v for k, v in n.items()}) for n in raw]
    return sorted(names, key=lambda n: n.number)


def load_signs() -> list[Sign]:
    """Load the 13 signs in zodiacal order."""
    raw = _read("zodiac.yaml")["signs"]
    signs = [Sign(**{k: v for k, v in s.items()
                     if k in Sign.__dataclass_fields__}) for s in raw]
    return sorted(signs, key=lambda s: s.number)


def name_by_number(names: list[Name], number: int) -> Name:
    """Fetch one officer by its classical number. Unknown number = error."""
    for n in names:
        if n.number == number:
            return n
    raise KeyError(f"no name numbered {number}; the canon holds 1-72")


def names_of_flavor(names: list[Name], flavor_number: int) -> list[Name]:
    """All officers apportioned to one flavor, in classical order."""
    return [n for n in names if n.flavor == flavor_number]
