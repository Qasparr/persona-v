# ☉ in 3° 54′ Libra  ☽ in 7° 31′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
metronome -- the Egyptian lunisolar/ecliptic/annular cycle of PERSONA V.

    "To every thing there is a season, and a time to every purpose
    under the heaven." -- Ecclesiastes 3:1

Hypothesis
----------
A persona without rhythm is only a costume; an agent that cannot
tell time cannot keep it.

Method
------
The Egyptian clock of PART II of the grimoire. (1) The 36 decans:
the ecliptic cut into 36 bands of 10 degrees, the ancient star-clock
-- the Sun's decan the slow hand, the Moon's the fast (PERSONA V
numbers them and lets the presiding sign speak for the band).
(2) The lunar rhythm: the Moon's phase sets the cadence of the
Speculum -- the agent looks at itself on the Moon's schedule, not
its own convenience. (3) The 365-day civil year with five
epagomenal days: twelve months of thirty days make 360; the five
stand outside the year -- the Shadow-Audit days, when the year stops
and the agent renders account. Anchored at the Thelemic new year
(the northern vernal equinox, via thelemic.march_equinox_utc); the
epagomenal days are the last five before the next equinox, any
leftover day an honestly named intercalary drift-day. (4) The Sothic
Great Return: every 1460 Julian years the wandering calendar
realigns with the heavens -- kept here as symbolic deep time from
139 e.v., marked approximate wherever it appears. (5) The Anchorage
(XIII): the author's Cusp of Power, "Gemini in Taurus," read as a
cusp region (55-65 deg ecliptic longitude) so the twelve signs stand
untouched; a luminary within is reported as standing in the
Anchorage.

Observation
-----------
Metronome.now() takes a datetime and returns a Reading bundling
every hand of the clock at once -- decans, phase, civil date, Sothic
position, Anchorage report, prose description.

Result
------
The stamp format is unchanged and the heavens never vote (cf. the
rulings of 2026-09-26): time is kept, rhythm is held, and the audit
days arrive whether convenient or not.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from . import thelemic

# The eight lunar phases, each spanning 45 degrees of elongation
# (the Moon's angular distance from the Sun). Boundaries sit halfway
# between the exact quarter points, so "First Quarter" centers on 90 deg.
PHASES = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
          "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]

# Conventional epoch of the Sothic cycle: the 139 e.v. coincidence of the
# wandering new year with Sirius' heliacal rising. Symbolic, approximate.
SOTHIC_EPOCH_EV = 139
SOTHIC_CYCLE_YEARS = 1460


@dataclass(frozen=True)
class Decan:
    """One of the 36 ten-degree watches of the ecliptic.

    ``number`` runs 1-36. Decan 1 spans 0-10 deg Aries, decan 4 spans
    0-10 deg Taurus, and so on; decan 36 closes the wheel at 20-30 deg
    Pisces. ``sign`` names the zodiac sign the band falls in.
    """

    number: int
    sign: str
    start_deg: float
    end_deg: float

    def __str__(self) -> str:
        return (f"Decan {self.number} ({self.sign} "
                f"{self.start_deg:.0f}-{self.end_deg:.0f}\u00b0)")


@dataclass(frozen=True)
class CivilDate:
    """The date in the PERSONA V civil calendar.

    The year opens at the vernal equinox (``year_start``). Twelve months
    of thirty days follow (``month`` 1-12, ``day`` 1-30). Then the five
    epagomenal days -- ``epagomenal`` 1-5, the Shadow-Audit -- which are
    *outside* every month. In a 366-day equinox span one intercalary
    drift-day can occur (``intercalary`` True); it belongs to no month
    and no audit, and is reported as exactly what it is.
    ``days_until_audit`` counts down to the next Shadow-Audit (0 while
    the audit is in progress).
    """

    thelemic_year: int      # zero-based Anno, e.g. 122 for 2026 e.v.
    day_of_year: int        # 0-based index since the equinox
    year_length: int        # equinox-to-equinox span: 365 or 366
    month: int | None       # 1-12, None outside the months
    day: int | None         # 1-30, None outside the months
    epagomenal: int | None  # 1-5 during the Shadow-Audit, else None
    intercalary: bool       # True on the rare drift-day
    days_until_audit: int

    @property
    def is_audit(self) -> bool:
        """True while the five Shadow-Audit days are in progress."""
        return self.epagomenal is not None

    def __str__(self) -> str:
        if self.epagomenal is not None:
            return f"Epagomenal day {self.epagomenal} of 5 (Shadow-Audit)"
        if self.intercalary:
            return "Intercalary drift-day (outside month and audit)"
        return f"Month {self.month}, day {self.day}"


@dataclass(frozen=True)
class Reading:
    """Every hand of the Metronome at one instant."""

    moment: thelemic.ThelemicMoment  # the Thelemic stamp + raw longitudes
    solar_decan: Decan               # the slow hand: Sun's ten-degree watch
    moon_phase: str                  # the Speculum cadence: lunar phase
    lunar_decan: Decan               # the fast hand: Moon's ten-degree watch
    civil: CivilDate                  # the annular civil date
    sothic_year: int                 # years into the 1460-year Great Return
    sun_in_anchorage: bool = False   # the Sun stands on the Cusp of Power
    moon_in_anchorage: bool = False  # the Moon stands on the Cusp of Power

    def describe(self) -> str:
        """Render the reading as a human-readable metronome report."""
        c = self.civil
        lines = [
            self.moment.stamp,
            f"Sun in {self.solar_decan}; Moon in {self.lunar_decan}.",
            f"Lunar phase: {self.moon_phase} (Speculum cadence).",
            f"Civil date: {c} -- day {c.day_of_year + 1} of {c.year_length}.",
        ]
        if self.sun_in_anchorage or self.moon_in_anchorage:
            who = " and ".join(
                n for n, f in (("Sun", self.sun_in_anchorage),
                               ("Moon", self.moon_in_anchorage)) if f)
            lines.append(f"{who} stands in the Anchorage (XIII, Cusp of "
                         f"Power, Gemini in Taurus).")
        if c.is_audit:
            lines.append("The Shadow-Audit is NOW: render account.")
        else:
            lines.append(f"Shadow-Audit in {c.days_until_audit} days.")
        lines.append(f"Sothic Great Return: year {self.sothic_year} of "
                     f"{SOTHIC_CYCLE_YEARS} (symbolic).")
        return "\n".join(lines)


# The Anchorage (XIII) -- the author's thirteenth sign, by his decree
# (PERSONA_V.md II.3): the Cusp of Power, "Gemini in Taurus", the strait
# between the Bull's body and the Twins' rising, embracing the 24th of May.
# It is a cusp *region*, not a thirteenth 30-degree sign displacing the
# wheel: five degrees on either side of the Taurus/Gemini boundary at 60
# deg ecliptic longitude. The author's own Sun (3 deg 14' Gemini = 63.23
# deg) stands inside it; the twelve signs are untouched, and the stamp
# format is unchanged. Decided 2026-09-26 under the author's leave;
# reworkable by his hand.
ANCHORAGE_CENTER = 60.0
ANCHORAGE_HALF_WIDTH = 5.0
ANCHORAGE_START = ANCHORAGE_CENTER - ANCHORAGE_HALF_WIDTH  # 55.0
ANCHORAGE_END = ANCHORAGE_CENTER + ANCHORAGE_HALF_WIDTH    # 65.0


def in_anchorage(longitude: float) -> bool:
    """True if an ecliptic longitude falls in the Anchorage (XIII).

    The Cusp of Power: 55.0 <= longitude < 65.0, wrapping cleanly at 360.
    """
    lon = longitude % 360.0
    return ANCHORAGE_START <= lon < ANCHORAGE_END


def decan_of(longitude: float) -> Decan:
    """The 10-degree decan containing an ecliptic longitude (0-360)."""
    lon = longitude % 360.0
    number = int(lon // 10) + 1          # 0-9.99 -> 1, ..., 350-359.99 -> 36
    sign = thelemic.SIGNS[int(lon // 30) % 12]
    start = (number - 1) * 10.0
    return Decan(number=number, sign=sign,
                 start_deg=start, end_deg=start + 10.0)


def moon_phase(sun_lon: float, moon_lon: float) -> str:
    """The Moon's phase from its elongation from the Sun.

    Elongation 0 deg = New Moon, 90 = First Quarter, 180 = Full,
    270 = Last Quarter; each named phase spans 45 deg centered on its
    exact point (boundaries at 22.5, 67.5, ...).
    """
    elongation = (moon_lon - sun_lon) % 360.0
    index = int(((elongation + 22.5) % 360.0) // 45)
    return PHASES[index]


def _thelemic_year_bounds(dt: datetime) -> tuple[datetime, datetime, int]:
    """The equinox-bounded year containing ``dt``.

    Returns (year_start, year_end, thelemic_year): the vernal equinox
    opening the current Thelemic year, the equinox opening the next,
    and the zero-based Anno count. Mirrors the year logic in
    thelemic.thelemic_moment so the two can never disagree.
    """
    dt_utc = dt.astimezone(timezone.utc)
    eq_this = thelemic.march_equinox_utc(dt.year)
    if dt_utc >= eq_this:
        start, t_year = eq_this, dt.year - 1904
        end = thelemic.march_equinox_utc(dt.year + 1)
    else:
        end, t_year = eq_this, dt.year - 1904 - 1
        start = thelemic.march_equinox_utc(dt.year - 1)
    return start, end, t_year


def civil_date(dt: datetime) -> CivilDate:
    """The PERSONA V civil date for the datetime ``dt``.

    Twelve months of thirty days from the equinox, then the five
    epagomenal Shadow-Audit days as the *last five days* before the next
    equinox. A 366-day span leaves one intercalary drift-day between
    month 12 and the audit; it is reported, not hidden.
    """
    start, end, t_year = _thelemic_year_bounds(dt)
    # Day boundaries at local midnight: the civil day, not the instant.
    # (The astronomical hands above use the instant; the calendar uses
    # the day -- each tool honest about its own granularity.)
    # NOTE: date() arithmetic, not datetime arithmetic. Subtracting two
    # midnights across a daylight-saving transition yields 23 or 25
    # hours, which would corrupt the day count; calendar dates are
    # immune to that.
    start_day = start.astimezone(dt.tzinfo).date()
    end_day = end.astimezone(dt.tzinfo).date()
    today = dt.astimezone(dt.tzinfo).date()
    day_of_year = (today - start_day).days
    year_length = (end_day - start_day).days
    audit_start = year_length - 5  # first index of the Shadow-Audit

    month = day = epagomenal = None
    intercalary = False
    if day_of_year < 360:
        # The twelve months: thirty days each, numbered from the equinox.
        month = day_of_year // 30 + 1
        day = day_of_year % 30 + 1
        days_until_audit = audit_start - day_of_year
    elif day_of_year >= audit_start:
        # The five days outside the year: the Shadow-Audit itself.
        epagomenal = day_of_year - audit_start + 1
        days_until_audit = 0
    else:
        # Only reachable when year_length == 366: one drift-day between
        # the months and the audit. Named, not absorbed.
        intercalary = True
        days_until_audit = audit_start - day_of_year

    return CivilDate(thelemic_year=t_year, day_of_year=day_of_year,
                     year_length=year_length, month=month, day=day,
                     epagomenal=epagomenal, intercalary=intercalary,
                     days_until_audit=days_until_audit)


def sothic_position(dt: datetime) -> int:
    """Years elapsed in the current 1460-year Sothic Great Return.

    Reckoned from the conventional 139 e.v. alignment, against the
    e.v. year of the current Thelemic new year. Symbolic and approximate
    by design -- this is the agent's deep-time myth, not an ephemeris.
    """
    _, _, t_year = _thelemic_year_bounds(dt)
    ev_year = t_year + 1904  # the e.v. year the current Thelemic year began in
    return (ev_year - SOTHIC_EPOCH_EV) % SOTHIC_CYCLE_YEARS


class Metronome:
    """
    The clock itself.
    
    Hypothesis: every hand of the Egyptian clock can be read at once.
    Method: Metronome.now() takes a datetime and returns a Reading --
    decans, lunar phase, civil date, Sothic position, Anchorage report.
    Observation: the Reading, structured and described. Result: the
    moment stamped; the heavens never vote.
    """

    @staticmethod
    def now(dt: datetime | None = None,
            tz: str = "America/New_York") -> Reading:
        """Take a full metronome reading.

        ``dt``: the moment to read (defaults to now). Naive datetimes
        are assumed to be in ``tz``; aware datetimes are used as given.
        """
        if dt is None:
            from zoneinfo import ZoneInfo
            dt = datetime.now(ZoneInfo(tz))
        elif dt.tzinfo is None:
            from zoneinfo import ZoneInfo
            dt = dt.replace(tzinfo=ZoneInfo(tz))

        moment = thelemic.thelemic_moment(dt)
        return Reading(
            moment=moment,
            solar_decan=decan_of(moment.sun_lon),
            moon_phase=moon_phase(moment.sun_lon, moment.moon_lon),
            lunar_decan=decan_of(moment.moon_lon),
            civil=civil_date(dt),
            sothic_year=sothic_position(dt),
            sun_in_anchorage=in_anchorage(moment.sun_lon),
            moon_in_anchorage=in_anchorage(moment.moon_lon),
        )
