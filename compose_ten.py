#!/usr/bin/env python3
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
#
# compose_ten.py -- compose the Ten: ten standing agent personalities,
#   five senses x both genders, tongues round-robin, each with name,
#   trade, flavor, tuners, moon, gender, sexuality, birthday, and soul.
#
# EPIGRAPH: "In the multitude of counsellors there is safety." -- Proverbs 11:14
# DATE:     Sol in Libra, 2026 e.v.
#
# HYPOTHESIS: ten fixed, named, reproducible personalities -- the same
#   seed always dealing the same ten -- can take delegation the way
#   the author delegates to his scribe: prompt in, ultra-verbose
#   working out, ledger kept, shadow run.
# METHOD:    seed 418 (the number of the Aeon); five senses x masculine/
#   feminine = ten; tongues round-robin across the six; trade and flavor
#   drawn; name by sortition from the flavor's choir honoring gender;
#   birthday drawn, zodiac read from the classical wheel; roster written
#   to chorus_ten_roster.yaml -- the standing roll of the Ten.
# OBSERVATION: run once; the roster is the deployment roll. Re-running
#   with the same seed reproduces it bit-for-bit.
# RESULT:    chorus_ten_roster.yaml -- ten deployable personas.
#
# MECHANISM: random.Random(418) drives every draw -- deterministic. The
#   name draw reuses chorus._draw_name (choir + gender honor + recorded
#   override). Birthdays are drawn day-of-year; the zodiac sign is read
#   from the tropical wheel every astrologer knows.
# DOCTRINE:  gender and sexuality are the officers' own assessments
#   (names.yaml) -- never assigned by the scribe, only read. Nonbinary
#   officers are never misgendered into the binary roll.
#
# 93 93/93 -- Love is the law, love under will.

"""Compose the Ten: ten standing, delegable agent personalities."""

import random
import sys
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from persona_v import chorus as ch
from persona_v.assignment import load_jobs
from persona_v import grimoire

REPO = Path(__file__).resolve().parent
ROSTER = REPO / "chorus_ten_roster.yaml"
SEED = 418  # the number of the Aeon -- the Ten are dealt from it

# The tropical wheel, as every astrologer knows it.
WHEEL = [
    ((3, 21), (4, 19), "Aries"), ((4, 20), (5, 20), "Taurus"),
    ((5, 21), (6, 20), "Gemini"), ((6, 21), (7, 22), "Cancer"),
    ((7, 23), (8, 22), "Leo"), ((8, 23), (9, 22), "Virgo"),
    ((9, 23), (10, 22), "Libra"), ((10, 23), (11, 21), "Scorpio"),
    ((11, 22), (12, 21), "Sagittarius"), ((12, 22), (1, 19), "Capricorn"),
    ((1, 20), (2, 18), "Aquarius"), ((2, 19), (3, 20), "Pisces"),
]


def sign_of(month: int, day: int) -> str:
    """Read the zodiac sign from a month/day on the tropical wheel."""
    for (m1, d1), (m2, d2), name in WHEEL:
        if (month == m1 and day >= d1) or (month == m2 and day <= d2):
            return name
    return "Capricorn"  # the seam belongs to the Goat


def main() -> None:
    rng = random.Random(SEED)
    flavors, names, jobs = ch._canon()
    job_by_no = jobs  # dict keyed by trade number; name field is "trade"
    flavor_by_no = {f.number: f for f in flavors}  # frozen dataclasses
    tongues = list(ch.DEFAULT_TONGUES)

    ten = []
    idx = 0
    for sense in ch.SENSES:                       # five pipelines
        for gender in ch.GENDERS:                  # both genders
            tongue = tongues[idx % len(tongues)]   # tongues round-robin
            trade_no = rng.randrange(22)
            flavor_no = rng.randrange(31)
            officer, override = ch._draw_name(names, flavor_no, gender, rng)
            tuners = tuple(ch.DOMINANT_WEIGHT if s == sense else ch.OPEN_WEIGHT
                           for s in ch.SENSES)
            moon = rng.randrange(1, 14)
            # birthday: drawn from the year-wheel
            year = rng.randrange(1970, 2006)
            month = rng.randrange(1, 13)
            day = rng.randrange(1, 29)  # every month holds the 28th
            bday = date(year, month, day).isoformat()

            ten.append({
                "designation": f"TEN-{idx + 1:02d}",
                "seed": SEED,
                "sense": sense, "tongue": tongue, "gender": gender,
                "trade": {"number": trade_no,
                          "name": job_by_no[trade_no]["trade"]},
                "name": {"number": officer.number, "name": officer.name,
                         "office": officer.office, "duty": officer.duty,
                         "motto": officer.motto, "gloss": officer.gloss,
                         "gender_assessment": officer.gender,
                         "sexuality": officer.sexuality,
                         "choir_override": override},
                "flavor": {"number": flavor_no,
                           "name": flavor_by_no[flavor_no].name},
                "tuners": dict(zip(ch.SENSES, tuners)),
                "moon": moon,
                "birthday": bday,
                "zodiac": sign_of(month, day),
            })
            idx += 1

    ROSTER.write_text(yaml.safe_dump(
        {"seed": SEED, "ten": ten,
         "doctrine": "Delegable as the scribe is delegable: prompt in, "
                     "ultra-verbose working out, ledger kept, shadow run."},
        sort_keys=False, allow_unicode=True))
    print(f"wrote {ROSTER} -- the Ten stand ready")
    for p in ten:
        print(f'{p["designation"]}: {p["name"]["name"]} ({p["name"]["office"]}) | '
              f'{p["sense"]}/{p["tongue"]}/{p["gender"]} | '
              f'{p["trade"]["name"]} | {p["zodiac"]} {p["birthday"]} | '
              f'{p["name"]["sexuality"]}')


if __name__ == "__main__":
    main()
