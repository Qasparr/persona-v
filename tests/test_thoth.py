# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for thoth.py -- the Thoth tarot as a first-class
PERSONA V component: the 22 trumps as data, readings, elemental
dignities, the engine-stamped horoscope, and the adapted Book T
First Operation.

Nothing here is verified against the printed Book of Thoth: the
tests check the TRANSCRIPTION (internal consistency, the recorded
Heh/Tzaddi switch, determinism under seed), not Crowley's text.
Every user-facing surface must carry the transcription notice.

Run:  python3 tests/test_thoth.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.thoth import (  # noqa: E402
    HONEST_NOTICE,
    STAMP,
    TRANSCRIPTION_NOTICE,
    TRUMPS,
    Trump,
    dignity,
    draw,
    first_operation,
    horoscope,
    reading,
    trump_by_number,
    trump_by_title,
)

PASS = 0


def check(name, cond):
    global PASS
    assert cond, f"FAILED: {name}"
    PASS += 1
    print(f"  ok: {name}")


# -- the deck ----------------------------------------------------------
check("22 trumps", len(TRUMPS) == 22)
check("numbers 0-21 in order", [t.number for t in TRUMPS] == list(range(22)))
check("all are Trump", all(isinstance(t, Trump) for t in TRUMPS))
check("titles unique", len({t.title for t in TRUMPS}) == 22)
check("22 glyphs unique", len({t.hebrew_glyph for t in TRUMPS}) == 22)
check("no empty glyphs", all(t.hebrew_glyph.strip() for t in TRUMPS))

# -- Crowley spot titles (transcribed, UNRESOLVED) ---------------------
check("0 The Fool", TRUMPS[0].title == "The Fool")
check("1 The Magus", TRUMPS[1].title == "The Magus")
check("2 The Priestess", TRUMPS[2].title == "The Priestess")
check("8 Adjustment", TRUMPS[8].title == "Adjustment")
check("11 Lust", TRUMPS[11].title == "Lust")
check("14 Art", TRUMPS[14].title == "Art")
check("20 The Aeon", TRUMPS[20].title == "The Aeon")
check("21 The Universe", TRUMPS[21].title == "The Universe")

# -- the Heh/Tzaddi switch, recorded both ways, never repaired --------
emperor = TRUMPS[4]
check("Emperor hebrew Tzaddi", emperor.hebrew == "Tzaddi")
check("Emperor glyph Tzaddi", emperor.hebrew_glyph == "צ")
check("Emperor traditional Heh",
      emperor.hebrew_traditional == "Heh (ה)")
star = TRUMPS[17]
check("Star hebrew Heh", star.hebrew == "Heh")
check("Star glyph Heh", star.hebrew_glyph == "ה")
check("Star traditional Tzaddi",
      star.hebrew_traditional == "Tzaddi (צ)")
check("no other switches",
      all(t.hebrew_traditional is None
          for t in TRUMPS if t.number not in (4, 17)))

# -- elements derived from attributions ---------------------------------
check("Fool Air", TRUMPS[0].element == "Air")
check("Aeon Fire", TRUMPS[20].element == "Fire")
check("Hanged Man Water", TRUMPS[12].element == "Water")
check("Empress Venus -> Earth", TRUMPS[3].element == "Earth")
check("Magus Mercury -> Air", TRUMPS[1].element == "Air")
check("Emperor Aries -> Fire", emperor.element == "Fire")
check("Star Aquarius -> Air", star.element == "Air")
check("elements valid set",
      all(t.element in ("Fire", "Water", "Air", "Earth")
          for t in TRUMPS))

# -- transcription notice -------------------------------------------------
check("transcription notice non-empty",
      isinstance(TRANSCRIPTION_NOTICE, str) and TRANSCRIPTION_NOTICE.strip())
check("transcription notice names the book",
      "verify against the printed Book of Thoth" in TRANSCRIPTION_NOTICE)
check("transcription notice UNRESOLVED",
      "UNRESOLVED" in TRANSCRIPTION_NOTICE)

# -- lookup: case-insensitive, never invents ------------------------------
check("by number", trump_by_number(11).title == "Lust")
check("by number zero", trump_by_number(0).title == "The Fool")
check("by number unknown -> None", trump_by_number(99) is None)
check("by title exact", trump_by_title("The Magus").number == 1)
check("by title lower", trump_by_title("the magus").number == 1)
check("by title upper", trump_by_title("ADJUSTMENT").number == 8)
check("by title unknown -> None",
      trump_by_title("The Grandmaster") is None)
check("by title empty -> None", trump_by_title("   ") is None)
check("by title None -> None", trump_by_title(None) is None)

# -- readings: seeded, deterministic, upright -----------------------------
r1 = reading(3, seed=1234)
r2 = reading(3, seed=1234)
check("reading deterministic under seed",
      [c.title for c in r1.cards] == [c.title for c in r2.cards])
check("reading length 3", len(r1.cards) == 3)
check("reading length 1", len(reading(1, seed=7).cards) == 1)
check("reading length 5", len(reading(5, seed=7).cards) == 5)
check("reading no repeats",
      len({c.number for c in r1.cards}) == len(r1.cards))
check("reading upright only",
      "no reversals" in r1.orientation.lower()
      and "upright" in r1.orientation.lower())
check("reading carries notice",
      "printed Book of Thoth" in r1.notice)
check("draw correct lengths", len(draw(5, seed=1)) == 5)
check("draw does not mutate deck",
      [t.number for t in TRUMPS] == list(range(22)))
try:
    reading(2, seed=1)
    check("spread 2 rejected", False)
except ValueError:
    check("spread 2 rejected", True)
try:
    draw(7)
    check("spread 7 rejected", False)
except ValueError:
    check("spread 7 rejected", True)

# -- elemental dignities (Golden Dawn rules) -------------------------------
same = dignity(trump_by_title("The Emperor"), trump_by_title("Lust"))
check("same element strengthens", same[0] == "strengthened")
check("dignity reason one line", "\n" not in same[1] and same[1].strip())
foes = dignity(trump_by_title("The Emperor"),
               trump_by_title("The Hanged Man"))
check("Fire-Water weakens", foes[0] == "weakened")
friends = dignity(trump_by_title("The Emperor"),
                  trump_by_title("The Fool"))
check("Fire-Air strengthens", friends[0] == "strengthened")
check("dignity symmetric",
      dignity(trump_by_title("The Hanged Man"),
              trump_by_title("The Emperor"))[0] == "weakened")
neut = dignity(trump_by_title("The Fool"), trump_by_title("The Empress"))
check("Air-Earth weakens (enemies)", neut[0] == "weakened")
neut2 = dignity(trump_by_title("The Priestess"),
                trump_by_title("The Lovers"))
check("Water-Air neutral", neut2[0] == "neutral")
check("dignity valid statuses",
      dignity(TRUMPS[0], TRUMPS[0])[0] == "strengthened")

# -- First Operation --------------------------------------------------------
op = first_operation("The Magus", seed=42)
check("significator resolved", op.significator.title == "The Magus")
check("four piles", sorted(op.piles) == ["Heh", "Heh-final", "Vau", "Yod"])
check("piles cover 22", sum(len(p) for p in op.piles.values()) == 22)
check("retained holds significator",
      any(c.number == 1 for c in op.retained))
check("discarded are the other three",
      sorted(op.discarded) == sorted(set(op.piles) - {op.retained_name}))
check("discarded reported",
      sum(len(p) for p in op.discarded.values())
      == 22 - len(op.retained))
check("significator not discarded",
      all(c.number != 1 for pile in op.discarded.values() for c in pile))
check("magus counts 1", op.count == 1)
check("counted is significator (count 1)",
      op.counted.title == "The Magus")
horseshoe = list(op.retained)
check("paired is next, wrapping",
      op.paired == horseshoe[(horseshoe.index(op.counted) + 1)
                             % len(horseshoe)])
check("pair dignity labeled", op.pairs[0].status in
      ("strengthened", "weakened", "neutral"))
check("pair dignity consistent",
      op.pairs[0].status == dignity(op.pairs[0].first,
                                   op.pairs[0].second)[0])
check("honest notice on result", op.notice == HONEST_NOTICE)

# -- the Fool counts as 22 ----------------------------------------------------
fool_op = first_operation("The Fool", seed=42)
check("Fool counts as 22", fool_op.count == 22)
hs = list(fool_op.retained)
sig_idx = next(i for i, c in enumerate(hs) if c.number == 0)
expected = hs[(sig_idx + 22 - 1) % len(hs)]
check("Fool count lands correctly", fool_op.counted == expected)
check("Fool by number works", first_operation(0, seed=42).count == 22)

# -- significator validation ----------------------------------------------------
try:
    first_operation("The Grandmaster", seed=1)
    check("unknown significator rejected", False)
except ValueError:
    check("unknown significator rejected", True)
try:
    first_operation(99, seed=1)
    check("unknown number rejected", False)
except ValueError:
    check("unknown number rejected", True)
check("first operation deterministic",
      [c.title for c in first_operation(20, seed=9).retained]
      == [c.title for c in first_operation(20, seed=9).retained])

# -- honest notice --------------------------------------------------------------
check("honest notice non-empty",
      isinstance(HONEST_NOTICE, str) and HONEST_NOTICE.strip())
check("honest notice names the Key",
      "Opening of the Key" in HONEST_NOTICE)
check("honest notice scopes II-V",
      "Operations II-V" in HONEST_NOTICE
      and "minor arcana" in HONEST_NOTICE)

# -- horoscope: the real engine, non-voting --------------------------------------
h = horoscope()
check("stamp doctrine",
      h.stamp == "the heavens stamp the moment but never vote.")
check("stamp constant", STAMP == h.stamp)
signs = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn",
         "Aquarius", "Pisces")
check("sun sign valid", h.sun_sign in signs)
check("moon sign valid", h.moon_sign in signs)
check("longitudes in range",
      0.0 <= h.sun_lon < 360.0 and 0.0 <= h.moon_lon < 360.0)
check("latin weekday", h.latin_weekday.strip())
check("thelemic date line", "Anno" in h.thelemic_date)
check("horoscope carries notice", "printed Book of Thoth" in h.notice)

print(f"\n{PASS} thoth tests passed.")
