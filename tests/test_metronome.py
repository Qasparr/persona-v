# ☉ in 3° 54′ Libra  ☽ in 7° 31′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for thelemic.py and metronome.py (Phase 1).

Strategy: test the Metronome's *mechanics* with synthetic inputs
(exact longitudes, known equinoxes) so the tests are deterministic --
they must pass on any machine, in any year, without depending on the
live sky. One regression anchor pins the real stamp for 2026-09-26.

Run:  python3 tests/test_metronome.py
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v import thelemic          # noqa: E402
from persona_v.metronome import (       # noqa: E402
    Metronome, Reading, civil_date, decan_of, in_anchorage, moon_phase,
    sothic_position,
)

NY = ZoneInfo("America/New_York")
PASS = 0


def check(label, fn):
    global PASS
    try:
        fn()
    except AssertionError as e:
        print(f"FAIL  {label}: {e}")
        raise SystemExit(1)
    PASS += 1
    print(f"pass  {label}")


# ---- decans -----------------------------------------------------------

def t_decan_boundaries():
    assert decan_of(0.0).number == 1
    assert decan_of(9.999).number == 1
    assert decan_of(10.0).number == 2
    assert decan_of(29.999).number == 3
    assert decan_of(30.0).number == 4      # first decan of Taurus
    assert decan_of(350.0).number == 36
    assert decan_of(359.999).number == 36
    assert decan_of(360.0).number == 1     # wraps cleanly


def t_decan_signs():
    assert decan_of(5).sign == "Aries"
    assert decan_of(35).sign == "Taurus"
    assert decan_of(65).sign == "Gemini"
    assert decan_of(185).sign == "Libra"
    assert decan_of(355).sign == "Pisces"
    d = decan_of(42)
    assert (d.start_deg, d.end_deg) == (40.0, 50.0)


# ---- lunar phases -----------------------------------------------------

def t_moon_phases():
    assert moon_phase(0, 0) == "New Moon"
    assert moon_phase(0, 90) == "First Quarter"
    assert moon_phase(0, 180) == "Full Moon"
    assert moon_phase(0, 270) == "Last Quarter"
    assert moon_phase(0, 45) == "Waxing Crescent"
    assert moon_phase(0, 135) == "Waxing Gibbous"
    assert moon_phase(0, 225) == "Waning Gibbous"
    assert moon_phase(0, 315) == "Waning Crescent"
    # wrap-around: elongation 350 deg is still the New Moon's span
    assert moon_phase(10, 0) == "New Moon"


# ---- thelemic stamp ----------------------------------------------------

def t_stamp_regression():
    # 2026-09-26 was a Saturday: dies saturnii, Anno V:xii (year 122).
    dt = datetime(2026, 9, 26, 19, 45, tzinfo=NY)
    m = thelemic.thelemic_moment(dt)
    assert m.latin_day == "Dies Saturnii", m.latin_day
    assert m.thelemic_year == 122, m.thelemic_year
    assert m.anno == "Anno V:xii", m.anno
    for token in ("\u2609", "\u263d", "dies saturnii", "Anno V:xii e.n."):
        assert token in m.stamp, f"stamp missing {token!r}: {m.stamp}"


def t_stamp_known_longitudes():
    # J2000: Sun near 280.38 deg (late Capricorn). Deterministic check
    # that the vendored astronomy still reproduces the verified value.
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert abs(thelemic.sun_longitude(dt) - 280.38) < 0.05


# ---- civil calendar -----------------------------------------------------

def t_civil_new_year():
    eq = thelemic.march_equinox_utc(2026).astimezone(NY)
    c = civil_date(eq)
    assert (c.month, c.day) == (1, 1), f"{c.month}/{c.day}"
    assert c.epagomenal is None and not c.intercalary
    assert c.day_of_year == 0
    assert c.days_until_audit == c.year_length - 5


def t_civil_month_rolls():
    eq = thelemic.march_equinox_utc(2026).astimezone(NY)
    assert civil_date(eq + timedelta(days=29)).day == 30
    m2 = civil_date(eq + timedelta(days=30))
    assert (m2.month, m2.day) == (2, 1), f"{m2.month}/{m2.day}"
    last_month_day = civil_date(eq + timedelta(days=359))
    assert (last_month_day.month, last_month_day.day) == (12, 30)


def t_civil_epagomenal():
    # The five Shadow-Audit days are the LAST five days before the next
    # equinox -- verified against the real computed equinoxes.
    eq_next = thelemic.march_equinox_utc(2027).astimezone(NY)
    for i in range(1, 6):
        c = civil_date(eq_next - timedelta(days=6 - i))
        assert c.epagomenal == i, f"expected audit day {i}, got {c}"
        assert c.is_audit
        assert c.days_until_audit == 0
    # The day before the audit is month 12, day 30 (or the drift-day).
    before = civil_date(eq_next - timedelta(days=6))
    assert before.epagomenal is None
    assert before.days_until_audit == 1


def t_civil_audit_is_outside_months():
    eq_next = thelemic.march_equinox_utc(2027).astimezone(NY)
    c = civil_date(eq_next - timedelta(days=3))
    assert c.month is None and c.day is None and c.epagomenal == 3


# ---- sothic --------------------------------------------------------------

def t_sothic_range():
    for dt in (datetime(2026, 9, 26, tzinfo=NY),
               datetime(1904, 3, 21, tzinfo=NY),
               datetime(2100, 1, 1, tzinfo=NY)):
        s = sothic_position(dt)
        assert 0 <= s < 1460, s


# ---- full reading ----------------------------------------------------------

def t_reading_now():
    r = Metronome.now(datetime(2026, 9, 26, 19, 45, tzinfo=NY))
    assert 1 <= r.solar_decan.number <= 36
    assert 1 <= r.lunar_decan.number <= 36
    assert r.moon_phase in ("New Moon", "Waxing Crescent", "First Quarter",
                            "Waxing Gibbous", "Full Moon", "Waning Gibbous",
                            "Last Quarter", "Waning Crescent")
    text = r.describe()
    assert "Shadow-Audit" in text and "Sothic" in text
    print("---\n" + text + "\n---")


def t_reading_naive_defaults():
    r = Metronome.now()  # now, default tz; just must not raise
    assert r.civil.year_length in (365, 366)


# ---- the Anchorage (XIII) ------------------------------------------------
# The Cusp of Power: 55.0 <= longitude < 65.0 -- five degrees either side
# of the Taurus/Gemini boundary at 60 deg. A cusp region, not a
# thirteenth 30-degree sign: the twelve signs stand untouched.

def t_anchorage_boundaries():
    assert not in_anchorage(54.999)
    assert in_anchorage(55.0)
    assert in_anchorage(60.0)       # the cusp itself
    assert in_anchorage(64.999)
    assert not in_anchorage(65.0)
    assert not in_anchorage(0.0)
    assert not in_anchorage(180.0)
    assert in_anchorage(360.0 + 60.0)  # wraps cleanly
    assert not in_anchorage(360.0 + 65.0)


def t_anchorage_nativity():
    # The author's own chart (PERSONA_V.md II.3): Sun 3 deg 14' Gemini,
    # Moon 21 deg 7' Taurus -- the Sun stands upon the Cusp of Power.
    sun = 60.0 + 3.0 + 14.0 / 60.0
    moon = 30.0 + 21.0 + 7.0 / 60.0
    assert in_anchorage(sun)
    assert not in_anchorage(moon)


def t_anchorage_reading():
    # A luminary in the Anchorage is reported; others are not.
    moment = thelemic.ThelemicMoment(
        sun_lon=63.0, moon_lon=200.0, latin_day="Dies Jovis",
        anno="Anno V:xii", thelemic_year=122, stamp="test stamp")
    dt = datetime(2026, 5, 24, 12, 0, tzinfo=NY)
    r = Reading(moment=moment,
                solar_decan=decan_of(moment.sun_lon),
                moon_phase=moon_phase(moment.sun_lon, moment.moon_lon),
                lunar_decan=decan_of(moment.moon_lon),
                civil=civil_date(dt),
                sothic_year=sothic_position(dt),
                sun_in_anchorage=in_anchorage(moment.sun_lon),
                moon_in_anchorage=in_anchorage(moment.moon_lon))
    assert r.sun_in_anchorage and not r.moon_in_anchorage
    text = r.describe()
    assert "Anchorage" in text and "Cusp of Power" in text
    assert "Sun stands in the Anchorage" in text
    # And a reading with neither luminary inside says nothing of it.
    moment2 = thelemic.ThelemicMoment(
        sun_lon=200.0, moon_lon=300.0, latin_day="Dies Jovis",
        anno="Anno V:xii", thelemic_year=122, stamp="test stamp")
    r2 = Reading(moment=moment2,
                 solar_decan=decan_of(moment2.sun_lon),
                 moon_phase=moon_phase(moment2.sun_lon, moment2.moon_lon),
                 lunar_decan=decan_of(moment2.moon_lon),
                 civil=civil_date(dt),
                 sothic_year=sothic_position(dt),
                 sun_in_anchorage=in_anchorage(moment2.sun_lon),
                 moon_in_anchorage=in_anchorage(moment2.moon_lon))
    assert "Anchorage" not in r2.describe()


if __name__ == "__main__":
    check("decan boundaries (36 x 10 deg)", t_decan_boundaries)
    check("decan signs and spans", t_decan_signs)
    check("eight lunar phases", t_moon_phases)
    check("stamp regression 2026-09-26", t_stamp_regression)
    check("vendored astronomy: J2000 Sun", t_stamp_known_longitudes)
    check("civil year opens month 1 day 1 at equinox", t_civil_new_year)
    check("month rolls at 30-day marks", t_civil_month_rolls)
    check("five epagomenal audit days before next equinox", t_civil_epagomenal)
    check("audit days are outside the months", t_civil_audit_is_outside_months)
    check("sothic position in 0-1459", t_sothic_range)
    check("full metronome reading", t_reading_now)
    check("Metronome.now() defaults", t_reading_naive_defaults)
    check("anchorage boundaries (55-65 deg)", t_anchorage_boundaries)
    check("anchorage: author's nativity", t_anchorage_nativity)
    check("anchorage reported in reading", t_anchorage_reading)
    print(f"\n{PASS} tests passed. The Metronome keeps true time.")
