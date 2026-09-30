# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
The Thoth Tarot as a first-class PERSONA V component.

Hypothesis
----------
Crowley's Thoth tarot (The Book of Thoth, 1944) can be carried inside
PERSONA V as a working instrument -- titles, Hebrew letters, and
astrological attributions as data; readings, elemental dignities, the
horoscope stamp, and an adapted Book T First Operation as functions --
without ever pretending the engine's transcription was checked against
a printed copy. Text only: no artwork is reproduced, referenced, or
stored anywhere in this module.

Method
------
The 22 trumps are embedded as module data (``TRUMPS``), transcribed
from the deck table ``~/workspace/taro/thoth.yaml`` -- which is itself
a transcription, not a scan of the book. The module does NOT import
from ``~/workspace/taro`` and does NOT reach outside the package at
runtime: it is self-contained apart from ``persona_v.thelemic``, the
package's own real Sun/Moon engine, which the horoscope uses instead
of the deleted applet's simplified lunar theory (the engine's
low-precision Schlyter positions are honestly better, and honestly
still approximate -- see the celestial non-voting doctrine below).

The Heh/Tzaddi switch -- Crowley's "double loop" (Emperor = Tzaddi
with traditional Heh; Star = Heh with traditional Tzaddi) -- is
recorded exactly as transcribed: ``hebrew`` carries the switched
letter, ``hebrew_traditional`` carries the traditional one. The break
is recorded; it is never silently repaired, and never "verified".

Observation
-----------
Everything Crowley-shaped in this module (titles, letters,
attributions) stands UNRESOLVED in the Anchorage sense: it is a
transcription, admitted for work but never quoted as verified against
the printed Book of Thoth. Every user-facing surface carries the
transcription notice. The horoscope's ``stamp`` field records the
doctrine that the heavens stamp the moment but never vote: computed
positions inform, they do not decide.

Result
------
A dependency-free instrument (stdlib + ``persona_v.thelemic`` only):
``trump_by_number`` / ``trump_by_title`` (never invents; None on
unknown), seeded ``draw`` / ``reading`` (upright only -- no reversals
in this system), Golden Dawn ``dignity`` (elemental dignities), a
``horoscope`` stamped by the real engine, and ``first_operation`` --
Book T's First Operation adapted for the 22 trumps, with the honest
notice that Operations II-V and the minor arcana are outside this
working.

Coinage/Discovery: none here -- Crowley is the author; the engine is
the transcriber. His words would be his; these letters and titles are
his, transcribed by the machine.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone

from persona_v.thelemic import thelemic_moment

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TRANSCRIPTION_NOTICE = (
    "Transcription by the engine; verify against the printed Book of Thoth. "
    "Titles and letters stand UNRESOLVED."
)

HONEST_NOTICE = (
    "Adapted First Operation for the 22 trumps. The full Opening of the Key "
    "uses 78 cards over five operations; Operations II-V and the minor "
    "arcana are outside this working."
)

# The celestial non-voting doctrine, carried on every horoscope and reading.
STAMP = "the heavens stamp the moment but never vote."

# No reversals in this system. Stated once, carried by every Reading.
ORIENTATION_NOTE = "Upright. No reversals are used in this system."

FIRE = "Fire"
WATER = "Water"
AIR = "Air"
EARTH = "Earth"

STRENGTHENED = "strengthened"
WEAKENED = "weakened"
NEUTRAL = "neutral"

ZODIAC = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn",
          "Aquarius", "Pisces")

_SIGN_ELEMENTS = {
    "Aries": FIRE, "Taurus": EARTH, "Gemini": AIR, "Cancer": WATER,
    "Leo": FIRE, "Virgo": EARTH, "Libra": AIR, "Scorpio": WATER,
    "Sagittarius": FIRE, "Capricorn": EARTH, "Aquarius": AIR,
    "Pisces": WATER,
}

# Element of each attribution. Elemental attributions (Air, Water, Fire)
# and the zodiacal sign triplicities are traditional Golden Dawn
# correspondences. The PLANET elements below are the ENGINE'S OWN
# CONVENTION for dignity work -- marked UNRESOLVED, like everything
# transcribed: Mercury quicksilver -> Air; Moon -> Water; Venus -> Earth;
# Jupiter, Mars, Sun -> Fire; Saturn -> Earth.
_ATTRIBUTION_ELEMENTS = {
    "Air": AIR, "Water": WATER, "Fire": FIRE,
    "Mercury": AIR, "Moon": WATER, "Venus": EARTH,
    "Jupiter": FIRE, "Mars": FIRE, "Sun": FIRE, "Saturn": EARTH,
}


def _element_for(attribution: str) -> str:
    """Derive a trump's element from its attribution.

    Order: direct element attribution, then zodiac sign triplicity,
    then the engine's planetary convention. Unknown -> raise, never
    invent: every attribution in the table is known.
    """
    if attribution in _ATTRIBUTION_ELEMENTS:
        return _ATTRIBUTION_ELEMENTS[attribution]
    if attribution in _SIGN_ELEMENTS:
        return _SIGN_ELEMENTS[attribution]
    raise ValueError(f"unknown attribution (refusing to invent): {attribution!r}")


# ---------------------------------------------------------------------------
# The 22 trumps
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Trump:
    """One trump of the Thoth deck, as transcribed.

    ``hebrew_traditional`` is None except where Crowley switches the
    letters (Emperor, Star), where it records the traditional letter --
    the break, kept visible.
    """
    number: int
    title: str
    hebrew: str
    hebrew_glyph: str
    hebrew_traditional: str | None
    attribution: str
    element: str
    kind: str          # "capability" | "capacity" (the TARO deck pairing)
    working: str       # working title
    operation: str     # the paired upgrade operation
    script: str        # executable card filename under ~/workspace/taro/cards/


def _trump(number, title, hebrew, glyph, attribution, kind, working,
           operation, script, hebrew_traditional=None):
    return Trump(number=number, title=title, hebrew=hebrew,
                 hebrew_glyph=glyph, hebrew_traditional=hebrew_traditional,
                 attribution=attribution, element=_element_for(attribution),
                 kind=kind, working=working, operation=operation,
                 script=script)


# Transcribed from ~/workspace/taro/thoth.yaml. Verify against the
# printed Book of Thoth -- these stand UNRESOLVED.
TRUMPS: tuple[Trump, ...] = (
    _trump(0, "The Fool", "Aleph", "א", "Air", "capability",
           "The Leap",
           "bootstrap -- verify adb link and userdebug build fingerprint",
           "00-fool.sh"),
    _trump(1, "The Magus", "Beth", "ב", "Mercury", "capability",
           "The Working",
           "NDK/SDK toolchain probe -- push and run a native hello-jni",
           "01-magician.sh"),
    _trump(2, "The Priestess", "Gimel", "ג", "Moon", "capability",
           "The Veil",
           "hidden system properties and secret settings readout",
           "02-high-priestess.sh"),
    _trump(3, "The Empress", "Daleth", "ד", "Venus", "capacity",
           "The Garden",
           "storage audit, fstrim, and cache reclamation",
           "03-empress.sh"),
    _trump(4, "The Emperor", "Tzaddi", "צ", "Aries", "capacity",
           "The Throne",
           "7.3 Zen 6 kernel turbo -- scheduler, cpufreq, and perf profiles",
           "04-emperor.sh",
           hebrew_traditional="Heh (ה)"),
    _trump(5, "The Hierophant", "Vau", "ו", "Taurus", "capability",
           "The Teaching",
           "SELinux denial audit and userdebug policy guidance",
           "05-hierophant.sh"),
    _trump(6, "The Lovers", "Zain", "ז", "Gemini", "capability",
           "The Bond",
           "multi-user and work-profile inventory and pairing",
           "06-lovers.sh"),
    _trump(7, "The Chariot", "Cheth", "ח", "Cancer", "capability",
           "The March",
           "network stack -- Wi-Fi, tethering, and DNS state",
           "07-chariot.sh"),
    _trump(8, "Adjustment", "Lamed", "ל", "Libra", "capacity",
           "The Reservoir",
           "battery, thermal zones, and Zen 6 thermal headroom",
           "08-strength.sh"),
    _trump(9, "The Hermit", "Yod", "י", "Virgo", "capability",
           "The Lantern",
           "observability -- logcat and tracing capture",
           "09-hermit.sh"),
    _trump(10, "Fortune", "Kaph", "כ", "Jupiter", "capability",
           "The Turning",
           "OTA/update engine state readout",
           "10-wheel.sh"),
    _trump(11, "Lust", "Teth", "ט", "Leo", "capability",
           "The Audit",
           "runtime permission audit -- the TRVVTH card",
           "11-justice.sh"),
    _trump(12, "The Hanged Man", "Mem", "מ", "Water", "capacity",
           "The Release",
           "debloat -- list and suspend bloatware (--apply to act)",
           "12-hanged-man.sh"),
    _trump(13, "Death", "Nun", "נ", "Scorpio", "capacity",
           "The Passage",
           "full backup before transformation",
           "13-death.sh"),
    _trump(14, "Art", "Samekh", "ס", "Sagittarius", "capacity",
           "The Blending",
           "zram/zswap and Zen 6 VM tunables -- readout and apply",
           "14-temperance.sh"),
    _trump(15, "The Devil", "Ayin", "ע", "Capricorn", "capability",
           "The Chain",
           "userdebug root capabilities -- adb root and su probe",
           "15-devil.sh"),
    _trump(16, "The Tower", "Peh", "פ", "Mars", "capability",
           "The Fall",
           "bootloader/fastboot state -- read-only, never flashes",
           "16-tower.sh"),
    _trump(17, "The Star", "Heh", "ה", "Aquarius", "capacity",
           "The Waters",
           "backup verification and restore dry-run",
           "17-star.sh",
           hebrew_traditional="Tzaddi (צ)"),
    _trump(18, "The Moon", "Qoph", "ק", "Pisces", "capability",
           "The Dream",
           "developer options deep settings",
           "18-moon.sh"),
    _trump(19, "The Sun", "Resh", "ר", "Sun", "capability",
           "The Light",
           "display and GPU visibility -- refresh rate and stats",
           "19-sun.sh"),
    _trump(20, "The Aeon", "Shin", "ש", "Fire", "capability",
           "The Reckoning",
           "TRVVTH audit -- re-verify all twenty-two operations, "
           "kernel turbo included",
           "20-judgement.sh"),
    _trump(21, "The Universe", "Tau", "ת", "Saturn", "capacity",
           "The Crown",
           "final integration -- capabilities, capacity, and kernel "
           "state report",
           "21-world.sh"),
)

_BY_NUMBER = {t.number: t for t in TRUMPS}
_BY_TITLE = {t.title.lower(): t for t in TRUMPS}


def trump_by_number(n: int) -> Trump | None:
    """Return the trump numbered ``n`` (0-21), or None if unknown.

    Never invents: an unknown number is None, not a guess.
    """
    return _BY_NUMBER.get(n)


def trump_by_title(name: str | None) -> Trump | None:
    """Return the trump titled ``name`` (case-insensitive), or None.

    Never invents: an unknown title is None, not the nearest match.
    """
    if not name or not name.strip():
        return None
    return _BY_TITLE.get(name.strip().lower())


# ---------------------------------------------------------------------------
# Readings
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Reading:
    """A drawn spread. ``spread`` is one of (1, 3, 5); ``cards`` the
    trumps in draw order; ``orientation`` the standing rule: upright,
    no reversals."""
    spread: int
    cards: tuple[Trump, ...]
    orientation: str = ORIENTATION_NOTE
    notice: str = TRANSCRIPTION_NOTICE


def draw(n: int, seed: int | None = None) -> list[Trump]:
    """Shuffle the 22 trumps with ``seed`` and take ``n``.

    ``n`` must be one of (1, 3, 5) -- the spreads this system knows.
    Deterministic under ``seed`` (``random.Random``); unseeded draws
    are honest chance, not reproducible. The deck is never mutated.
    ValueError on any other ``n``: this system does not deal reversals
    and does not deal spreads it was not given.
    """
    if n not in (1, 3, 5):
        raise ValueError(
            f"spread must be one of (1, 3, 5); got {n!r}")
    rng = random.Random(seed)
    deck = list(TRUMPS)
    rng.shuffle(deck)
    return deck[:n]


def reading(spread: int, seed: int | None = None) -> Reading:
    """Draw a ``spread`` (1, 3, or 5 cards) under ``seed``.

    Convenience wrapper over ``draw`` that carries the orientation
    rule and the transcription notice with the cards.
    """
    return Reading(spread=spread, cards=tuple(draw(spread, seed)))


# ---------------------------------------------------------------------------
# Elemental dignities (Golden Dawn)
# ---------------------------------------------------------------------------

_FRIENDLY = frozenset({(FIRE, AIR), (WATER, EARTH)})
_ENEMIES = frozenset({(FIRE, WATER), (AIR, EARTH)})


def dignity(a: Trump, b: Trump) -> tuple[str, str]:
    """Elemental dignity of trump ``a`` with trump ``b``.

    Golden Dawn rules: same element strengthens; Fire-Air and
    Water-Earth are friendly (strengthen); Fire-Water and Air-Earth
    are enemies (weaken); all other pairings are neutral. Returns
    (status, one-line reason); status is one of "strengthened",
    "weakened", "neutral".
    """
    pair = frozenset({a.element, b.element})
    if a.element == b.element:
        return (STRENGTHENED,
                f"same element ({a.element}) -- mutual strength")
    if (a.element, b.element) in _FRIENDLY or (b.element, a.element) in _FRIENDLY:
        return (STRENGTHENED,
                f"friendly elements ({a.element} and {b.element}) -- strengthen")
    if (a.element, b.element) in _ENEMIES or (b.element, a.element) in _ENEMIES:
        return (WEAKENED,
                f"enemy elements ({a.element} and {b.element}) -- weaken")
    return (NEUTRAL,
            f"neither friendly nor contrary ({a.element} and {b.element})")


# ---------------------------------------------------------------------------
# Horoscope
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Horoscope:
    """The moment, stamped by the real engine.

    Positions are COMPUTED (Schlyter low-precision, tropical) --
    honest approximations, better than the deleted applet's
    simplified lunar theory, and still not ephemeris-grade. They
    inform; they do not vote (``stamp``).
    """
    sun_sign: str
    moon_sign: str
    sun_lon: float
    moon_lon: float
    latin_weekday: str
    thelemic_date: str   # the engine's canonical stamp line
    stamp: str = STAMP
    notice: str = TRANSCRIPTION_NOTICE


def _sign_of(lon: float) -> str:
    return ZODIAC[int(lon // 30) % 12]


def horoscope(dt: datetime | None = None) -> Horoscope:
    """Compute the horoscope for ``dt`` (now, UTC, if omitted).

    Uses ``persona_v.thelemic.thelemic_moment`` -- the package's own
    real Sun/Moon engine -- for the luminaries, the Latin weekday,
    and the Thelemic date line. The heavens stamp the moment but
    never vote: this is a stamp, not a verdict.
    """
    moment = thelemic_moment(dt or datetime.now(timezone.utc))
    return Horoscope(
        sun_sign=_sign_of(moment.sun_lon),
        moon_sign=_sign_of(moment.moon_lon),
        sun_lon=moment.sun_lon,
        moon_lon=moment.moon_lon,
        latin_weekday=moment.latin_day,
        thelemic_date=moment.stamp,
    )


# ---------------------------------------------------------------------------
# Book T First Operation, adapted for the 22 trumps
# ---------------------------------------------------------------------------

PILE_NAMES = ("Yod", "Heh", "Vau", "Heh-final")


@dataclass(frozen=True)
class PairDignity:
    """A counted card and its horseshoe neighbour, with their dignity."""
    first: Trump
    second: Trump
    status: str   # STRENGTHENED | WEAKENED | NEUTRAL
    reason: str


@dataclass(frozen=True)
class FirstOperation:
    """The adapted First Operation, step by step.

    ``piles``: the four piles in dealing order (Yod, Heh, Vau,
    Heh-final). ``retained``: the horseshoe laid from the pile holding
    the significator; ``discarded``: the other three piles, reported,
    not hidden. ``count``: the significator's trump number, the Fool
    counting as 22. ``counted``: the card reached by counting from the
    significator around the horseshoe (wrapping); ``paired``: the next
    card after it (wrapping). ``pairs``: the dignity reading of the
    counted pair.
    """
    significator: Trump
    seed: int | None
    piles: dict
    retained_name: str
    retained: tuple
    discarded: dict
    count: int
    counted: Trump
    paired: Trump
    pairs: tuple
    notice: str = HONEST_NOTICE


def _resolve_significator(significator: int | str) -> Trump:
    if isinstance(significator, int):
        trump = trump_by_number(significator)
    elif isinstance(significator, str):
        trump = trump_by_title(significator)
    else:
        trump = None
    if trump is None:
        raise ValueError(
            f"unknown significator {significator!r}: choose a trump number "
            f"(0-21) or a Crowley title; refusing to invent one")
    return trump


def first_operation(significator: int | str,
                    seed: int | None = None) -> FirstOperation:
    """Perform Book T's First Operation, adapted for the 22 trumps.

    The querent chooses the ``significator`` (trump number or title).
    The pack -- significator still in it -- is shuffled under ``seed`` and dealt round by
    round into four piles -- Yod, Heh, Vau, Heh-final. The pile holding
    the significator is retained and laid as a horseshoe; the other
    three are discarded (and reported). Counting from the significator
    by its trump number (the Fool counts as 22), the reached card is
    paired with the next card in the horseshoe, wrapping; their
    elemental dignity is read.

    ValueError on an unknown significator. ``HONEST_NOTICE`` rides
    with the result: this is the First Operation only.
    """
    sig = _resolve_significator(significator)

    # The significator stays in the pack: Book T's working finds the
    # pile that *contains* it. Shuffle all 22 under the seed.
    rng = random.Random(seed)
    pack = list(TRUMPS)
    rng.shuffle(pack)

    # Deal round-robin: 22 cards -> Yod 6, Heh 6, Vau 5, Heh-final 5.
    piles: dict[str, list[Trump]] = {name: [] for name in PILE_NAMES}
    for i, card in enumerate(pack):
        piles[PILE_NAMES[i % 4]].append(card)

    retained_name = next(name for name, pile in piles.items()
                         if any(c.number == sig.number for c in pile))
    retained = tuple(piles[retained_name])
    discarded = {name: tuple(pile)
                 for name, pile in piles.items() if name != retained_name}

    # Count from the significator by its trump number; the Fool is 0
    # on the card but counts as 22 in the working (Book T's rule).
    count = sig.number if sig.number != 0 else 22
    sig_idx = next(i for i, c in enumerate(retained)
                   if c.number == sig.number)
    counted_idx = (sig_idx + count - 1) % len(retained)
    paired_idx = (counted_idx + 1) % len(retained)
    counted = retained[counted_idx]
    paired = retained[paired_idx]

    status, reason = dignity(counted, paired)
    pairs = (PairDignity(first=counted, second=paired,
                         status=status, reason=reason),)

    return FirstOperation(
        significator=sig, seed=seed,
        piles={n: tuple(p) for n, p in piles.items()},
        retained_name=retained_name, retained=retained,
        discarded=discarded, count=count,
        counted=counted, paired=paired, pairs=pairs,
    )
