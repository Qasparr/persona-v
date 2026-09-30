# ☉ in 3° 54′ Libra  ☽ in 7° 31′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
thelemic -- the Thelemic date engine, vendored into PERSONA V.

    "Let there be lights in the firmament of the heaven ... and let
    them be for signs, and for seasons, and for days, and years."
    -- Genesis 1:14

Hypothesis
----------
Sun and Moon, computed truly enough, stamp any moment in the
Thelemic reckoning.

Method
------
The astronomy is taken verbatim from
~/workspace/thelemic/thelemic_date.py (authored 2026-09-26,
verified: J2000 Sun 280.38 deg, 2000-01-21 lunar eclipse elongation
180.02 deg, 2000-01-06 new moon elongation 0.02 deg). It is vendored
-- not imported -- so the persona_v package is self-contained: an
agent carrying PERSONA V must not depend on files outside its own
package. The original was a CLI script returning dicts; here the
same mathematics is exposed as a library around the ThelemicMoment
dataclass. No algorithm was altered.

Observation
-----------
For any moment, the traditional stamp:

    SUN in D deg M' Sign  MOON in D deg M' Sign  dies <latin>  Anno C:y e.n.

Sun and Moon: tropical, geocentric ecliptic longitude, by the
low-precision algorithms of Paul Schlyter (good to a few arcminutes
-- far finer than the whole-degree stamp format). Latin weekday by
planetary ruler (Dies Solis .. Dies Saturnii). Anno: years since the
1904 e.v. reception of Liber AL, in the author's zero-based base-22
system -- uppercase Roman docosade, lowercase Roman year,
colon-separated; the Thelemic year begins at the northern vernal
equinox (solved numerically), never on January 1.

Result
------
The stamp the whole system signs its workings with.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
GLYPHS = ["\u2648", "\u2649", "\u264a", "\u264b", "\u264c", "\u264d",
          "\u264e", "\u264f", "\u2650", "\u2651", "\u2652", "\u2653"]
# Python weekday(): Mon=0..Sun=6 ; the Latin days are Sunday-first,
# so Sunday's name sits at index 6 of this table.
LATIN_DAYS = ["Dies Solis", "Dies Lunae", "Dies Martis", "Dies Mercurii",
              "Dies Jovis", "Dies Veneris", "Dies Saturnii"]
LATIN_BY_WEEKDAY = [LATIN_DAYS[1], LATIN_DAYS[2], LATIN_DAYS[3],
                    LATIN_DAYS[4], LATIN_DAYS[5], LATIN_DAYS[6],
                    LATIN_DAYS[0]]

# d = days since 2000 Jan 0.0 (= Julian Day 2451543.5). All of Schlyter's
# formulae take this single time variable.
_JAN00 = datetime(1999, 12, 31, 0, 0, tzinfo=timezone.utc)


def _day_number(dt_utc: datetime) -> float:
    """Days (fractional) since the J2000-adjacent epoch."""
    return (dt_utc - _JAN00).total_seconds() / 86400.0


def _from_day_number(d: float) -> datetime:
    """Inverse of _day_number: day number back to a UTC datetime."""
    return _JAN00 + timedelta(days=d)


def _kepler(M_deg: float, e: float) -> float:
    """Solve Kepler's equation M = E - e*sin(E) by Newton iteration.

    M: mean anomaly in degrees; e: eccentricity. Returns E, the eccentric
    anomaly, in degrees. Five Newton steps is plenty at this precision.
    """
    M = M_deg % 360.0
    E = M + math.degrees(e) * math.sin(math.radians(M)) \
        * (1.0 + e * math.cos(math.radians(M)))
    for _ in range(5):
        E -= (E - math.degrees(e) * math.sin(math.radians(E)) - M) \
             / (1.0 - e * math.cos(math.radians(E)))
    return E


def sun_position(d: float) -> tuple[float, float, float]:
    """Sun's geocentric ecliptic longitude (degrees, 0-360).

    Returns (longitude, mean anomaly M, longitude of perihelion w).
    The latter two are needed as inputs to the lunar theory.
    """
    w = 282.9404 + 4.70935e-5 * d          # longitude of perihelion
    e = 0.016709 - 1.151e-9 * d            # eccentricity of Earth's orbit
    M = (356.0470 + 0.9856002585 * d) % 360.0  # mean anomaly
    E = _kepler(M, e)
    # Position in the orbital plane, then true anomaly v, then add w.
    x = math.cos(math.radians(E)) - e
    y = math.sin(math.radians(E)) * math.sqrt(1.0 - e * e)
    v = math.degrees(math.atan2(y, x))
    return (v + w) % 360.0, M, w


def moon_longitude(d: float, sun_M: float, sun_w: float) -> float:
    """Moon's geocentric ecliptic longitude (degrees, 0-360).

    Keplerian orbit plus Schlyter's principal perturbation terms
    (Evection, Variation, Yearly Equation and two smaller terms).
    Without the perturbations the error can reach a degree; with them
    it is a few arcminutes -- verified against the 2000 eclipses.
    """
    N = (125.1228 - 0.0529538083 * d) % 360.0  # longitude of ascending node
    i = 5.1454                                  # inclination to ecliptic
    w = (318.0634 + 0.1643573223 * d) % 360.0  # argument of perigee
    e = 0.054900
    M = (115.3654 + 13.0649929509 * d) % 360.0  # mean anomaly
    E = _kepler(M, e)
    x = math.cos(math.radians(E)) - e
    y = math.sin(math.radians(E)) * math.sqrt(1.0 - e * e)
    v = math.degrees(math.atan2(y, x))
    # Rotate from the orbital plane into ecliptic coordinates.
    vw = math.radians(v + w)
    Nr, ir = math.radians(N), math.radians(i)
    xh = math.cos(Nr) * math.cos(vw) - math.sin(Nr) * math.sin(vw) * math.cos(ir)
    yh = math.sin(Nr) * math.cos(vw) + math.cos(Nr) * math.sin(vw) * math.cos(ir)
    lon = math.degrees(math.atan2(yh, xh)) % 360.0
    # Perturbations: the Sun tugs the Moon's orbit; these terms correct it.
    Ms = sun_M
    Mm = M
    Lm = (N + w + Mm) % 360.0   # Moon's mean longitude
    Ls = (sun_M + sun_w) % 360.0  # Sun's mean longitude
    D = (Lm - Ls) % 360.0       # mean elongation of Moon from Sun
    lon += (-1.274 * math.sin(math.radians(Mm - 2 * D))   # Evection
            + 0.658 * math.sin(math.radians(2 * D))        # Variation
            - 0.186 * math.sin(math.radians(Ms))          # Yearly Equation
            - 0.059 * math.sin(math.radians(2 * Mm - 2 * D))
            - 0.057 * math.sin(math.radians(Mm - 2 * D + Ms)))
    return lon % 360.0


def march_equinox_utc(year: int) -> datetime:
    """The northern vernal equinox: the instant the Sun crosses 0 deg Aries.

    Found numerically -- scan March 10-26 for the day the Sun's longitude
    wraps from ~359.x to ~0.x, then bisect to the minute. The Thelemic
    year (and the PERSONA V civil year) begins here, not on January 1.
    """
    prev_d = _day_number(datetime(year, 3, 10, tzinfo=timezone.utc))
    prev_lon = sun_position(prev_d)[0]
    for day in range(11, 27):
        d_cur = _day_number(datetime(year, 3, day, tzinfo=timezone.utc))
        lon = sun_position(d_cur)[0]
        if lon < prev_lon:  # wrapped 359.x -> 0.x: the crossing lies between
            lo, hi = prev_d, d_cur
            for _ in range(50):
                mid = (lo + hi) / 2.0
                # Before the crossing the Sun sits near 359 ( > 180);
                # after, near 0 ( < 180). Bisect on that test.
                if sun_position(mid)[0] < 180.0:
                    hi = mid
                else:
                    lo = mid
            return _from_day_number((lo + hi) / 2.0)
        prev_d, prev_lon = d_cur, lon
    raise ValueError(f"equinox not found for {year}")


def roman(n: int, upper: bool = True) -> str:
    """Integer to Roman numerals (0 renders as '0', by authorial decree)."""
    if n == 0:
        return "0"
    out = ""
    for v, sym in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
                   (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
                   (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += sym
            n -= v
    return out if upper else out.lower()


def _fmt_lon(lon: float) -> tuple[int, int, str, str]:
    """Split an ecliptic longitude into (degree, minute, sign, glyph)."""
    total_min = lon * 60.0
    deg = int(total_min // 60) % 30
    minutes = int(total_min % 60)
    sign = SIGNS[int(lon // 30) % 12]
    glyph = GLYPHS[int(lon // 30) % 12]
    return deg, minutes, sign, glyph


@dataclass(frozen=True)
class ThelemicMoment:
    """One computed Thelemic date: the luminaries, the day, the year.

    ``sun_lon`` / ``moon_lon`` are raw ecliptic longitudes (0-360) for
    further calculation; ``stamp`` is the canonical display string.
    ``thelemic_year`` is the zero-based count from 1904 e.v.
    """

    sun_lon: float
    moon_lon: float
    latin_day: str
    anno: str
    thelemic_year: int
    stamp: str

    @property
    def elongation(self) -> float:
        """Moon's elongation from the Sun (0=new, 180=full), in degrees."""
        return (self.moon_lon - self.sun_lon) % 360.0


def sun_longitude(dt: datetime) -> float:
    """Ecliptic longitude of the Sun at ``dt`` (any tz; 0-360 deg)."""
    d = _day_number(dt.astimezone(timezone.utc))
    return sun_position(d)[0]


def moon_longitude_at(dt: datetime) -> float:
    """Ecliptic longitude of the Moon at ``dt`` (any tz; 0-360 deg)."""
    d = _day_number(dt.astimezone(timezone.utc))
    sun_lon, sun_M, sun_w = sun_position(d)
    return moon_longitude(d, sun_M, sun_w)


def thelemic_moment(dt: datetime) -> ThelemicMoment:
    """
    Compute the full Thelemic date for the datetime dt.
    
    Hypothesis: Sun and Moon, truly computed, stamp any moment.
    Method: Schlyter's low-precision algorithms (tropical, geocentric),
    planetary weekday, Anno base-22 from the 1904 reception, the year
    beginning at the numerically solved northern vernal equinox.
    Observation: a ThelemicMoment -- the traditional stamp. Result: the
    stamp the whole system signs its workings with.
    """
    dt_utc = dt.astimezone(timezone.utc)
    d = _day_number(dt_utc)
    sun_lon, sun_M, sun_w = sun_position(d)
    moon_lon = moon_longitude(d, sun_M, sun_w)

    latin = LATIN_BY_WEEKDAY[dt.weekday()]

    # The Thelemic year turns at the equinox: if we have not yet reached
    # this civil year's equinox, we still belong to the previous one.
    eq = march_equinox_utc(dt.year)
    t_year = (dt.year - 1904) if dt_utc >= eq else (dt.year - 1904 - 1)
    anno = f"Anno {roman(t_year // 22, True)}:{roman(t_year % 22, False)}"

    sd, sm, ssign, _ = _fmt_lon(sun_lon)
    md, mm, msign, _ = _fmt_lon(moon_lon)
    stamp = (f"\u2609 in {sd}\u00b0 {sm}\u2032 {ssign}  "
             f"\u263d in {md}\u00b0 {mm}\u2032 {msign}  "
             f"{latin.lower()}  {anno} e.n.")
    return ThelemicMoment(sun_lon=sun_lon, moon_lon=moon_lon,
                          latin_day=latin, anno=anno,
                          thelemic_year=t_year, stamp=stamp)
