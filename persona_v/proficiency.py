# ☉ in 3° 57′ Libra  ☽ in 8° 36′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
proficiency -- the apprentice's arc: practice, promotion, mastery.

    "Study to shew thyself approved unto God, a workman that needeth
    not to be ashamed, rightly dividing the word of truth."
    -- 2 Timothy 2:15
    "The things that thou hast heard of me among many witnesses, the
    same commit thou to faithful men, who shall be able to teach
    others also." -- 2 Timothy 2:2

Hypothesis
----------
The second chair is not static: an apprentice practices, and the
practice can be recorded honestly enough to confer mastery.

Method
------
Practice is intentional and focus-driven, and it is attested: every
practice entry records what was practiced (the note) and in which
working -- mere assignment is not practice; the cross-examination
is. Hours are recorded as declared; the note is the honesty.
Mastery has two paths, and only two: attainment -- 1200 hours of
recorded practice, the hours themselves conferring it, no one
voting; promotion -- the working's Master promotes the apprentice,
with grounds, a groundless promotion refused exactly as the Speculum
refuses a claim without grounds. Mastery is recorded once, as an
event, with its path named; hours keep counting past 1200. Lineage:
every mastery names its provenance -- promotion names the conferring
Master (the sponsor) and the working; attainment names the working
where the apex was crossed and the witnessing Master, if one was
named. Emeritus: a master of the record still takes the second
chair, and the rendering says so -- the cross-examination of a
master by a master -- changing the rendering, never the election.

Observation
-----------
ProficiencyLedger: a JSON-backed registry (default
~/.persona-v/proficiency.json, PERSONA_V_PROFICIENCY-overridable).
The event log is append-only; totals are derived, never stored, so
the record cannot drift from its own history. Writes are atomic
(temp file + rename); single-writer by design and by label.
standing() surfaces score, progress, sponsor, apex working, apex
witness; lineage() walks the sponsor chain, cycle-safe.

Result
------
What is earned on the record stays on the record; what the election
does is the election's business. Mastery is a recorded attainment,
surfaced in the CLI, the API, and describe() -- not a weight on the
lots.

Law
---
"Attest," Black's Law Dictionary (12th ed.): to bear witness to; to
affirm to be true. Cf. 28 U.S.C. Sec. 1746 (unsworn declarations).
The practice note is this module's declaration. Cited for education
only -- no legal effect is created or claimed.
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import thelemic

#: Hours of intentional, focus-driven practice that confer mastery
#: by attainment. Named, not magic: the author's number.
MASTERY_HOURS = 1200.0

_KINDS = ("practice", "promotion", "mastery_attained")
_PATHS = ("attainment", "promotion")


def _default_path() -> Path:
    env = os.environ.get("PERSONA_V_PROFICIENCY")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".persona-v" / "proficiency.json"


def _check_flavor(flavor: int, role: str = "flavor") -> int:
    if not isinstance(flavor, int) or isinstance(flavor, bool):
        raise ValueError(f"{role} must be an integer 0-30, "
                         f"got {flavor!r}")
    if not 0 <= flavor <= 30:
        raise ValueError(f"{role} must be an integer 0-30, "
                         f"got {flavor!r}")
    return flavor


def _check_text(value: str, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{what} is required; an unattested "
                         f"practice is not intentional practice")
    return value.strip()


def _stamp() -> str:
    return thelemic.thelemic_moment(
        datetime.now(ZoneInfo("America/New_York"))).stamp


class ProficiencyLedger:
    """
    The apprentice's arc, on the record.
    
    Hypothesis: practice honestly recorded can confer mastery. Method:
    JSON registry, append-only event log, totals derived never stored,
    atomic writes; record_practice() attests hours with a note,
    promote() requires grounds, standing() surfaces score and
    provenance, lineage() walks the sponsor chain cycle-safe.
    Observation: the arc as events -- attainment at 1200 hours,
    promotion with grounds named. Result: what is earned on the record
    stays on the record; mastery renders, never weights.
    """

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path).expanduser() if path is not None \
            else _default_path()
        self._events: list[dict] = []
        self._load()

    # ---------------------------------------------------------- storage
    def _load(self) -> None:
        if not self.path.exists():
            self._events = []
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise ValueError(f"proficiency registry at {self.path} "
                             f"is unreadable: {exc}")
        events = raw.get("events", []) if isinstance(raw, dict) else []
        if not isinstance(events, list):
            raise ValueError(f"proficiency registry at {self.path} "
                             f"is corrupt: 'events' is not a list")
        self._events = events

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"events": self._events,
                                   "mastery_hours": MASTERY_HOURS},
                                  indent=1),
                       encoding="utf-8")
        tmp.replace(self.path)

    def _emit(self, kind: str, flavor: int, **fields) -> dict:
        event = {"seq": len(self._events) + 1, "kind": kind,
                 "flavor": flavor, "stamp": _stamp(), **fields}
        self._events.append(event)
        self._save()
        # Mastery by attainment is conferred by the hours themselves:
        # the moment the total crosses the threshold, the apex event
        # is written -- no one votes, nothing is asked. The event
        # carries the provenance: the working where the apex was
        # crossed, and the working's Master if one witnessed it.
        # (A witness is not a sponsor: the hours confer, not the
        # Master.)
        if kind == "practice" and not self._has_mastery_event(flavor):
            if self.hours(flavor) >= MASTERY_HOURS:
                attained = {"seq": len(self._events) + 1,
                            "kind": "mastery_attained",
                            "flavor": flavor, "stamp": _stamp(),
                            "path": "attainment",
                            "working_id": fields.get("working_id"),
                            "under_master": fields.get("under_master"),
                            "hours": self.hours(flavor)}
                self._events.append(attained)
                self._save()
                return attained
        return event

    def _has_mastery_event(self, flavor: int) -> bool:
        return self._mastery_event(flavor) is not None

    def _mastery_event(self, flavor: int) -> dict | None:
        for e in self._events:
            if e["kind"] == "mastery_attained" and e["flavor"] == flavor:
                return e
        return None

    # ------------------------------------------------------------ writes
    def record_practice(self, flavor: int, hours: float,
                        working_id: str, note: str,
                        master: int | None = None) -> dict:
        """Record intentional, focus-driven practice.

        ``hours`` must be positive and finite; ``note`` says what was
        practiced (the cross-examination performed, the exercise
        completed); ``working_id`` ties it to a working. An
        unattested practice is refused -- intentionality without a
        witness is just a claim.

        ``master`` names, optionally, the working's Master flavor under
        whom the practice was performed -- the witness of the work.
        If the practice carries the flavor across the mastery
        threshold, the witness is recorded on the apex event as
        provenance, not as a conferring sponsor.
        """
        _check_flavor(flavor, "flavor")
        if not isinstance(hours, (int, float)) or isinstance(hours, bool) \
                or not math.isfinite(hours) or hours <= 0:
            raise ValueError(f"hours must be a positive finite number, "
                             f"got {hours!r}")
        _check_text(working_id, "working_id")
        _check_text(note, "note")
        if master is not None:
            _check_flavor(master, "master")
        fields = {"hours": float(hours),
                  "working_id": working_id.strip(),
                  "note": note.strip()}
        if master is not None:
            fields["under_master"] = master
        return self._emit("practice", flavor, **fields)

    def promote(self, apprentice: int, master: int, working_id: str,
                grounds: str) -> dict:
        """The working's Master promotes the apprentice.

        ``grounds`` names what the Master saw that warrants it -- a
        promotion without grounds is refused, exactly as the Speculum
        refuses a claim without grounds. Promotion confers mastery
        immediately, whatever the hours; the apex event names its
        path as promotion.
        """
        _check_flavor(apprentice, "apprentice")
        _check_flavor(master, "master")
        if apprentice == master:
            raise ValueError("a flavor cannot promote itself")
        _check_text(working_id, "working_id")
        _check_text(grounds, "grounds")
        event = self._emit("promotion", apprentice, by_master=master,
                           working_id=working_id.strip(),
                           grounds=grounds.strip())
        if not self._has_mastery_event(apprentice):
            self._events.append(
                {"seq": len(self._events) + 1,
                 "kind": "mastery_attained", "flavor": apprentice,
                 "stamp": _stamp(), "path": "promotion",
                 "by_master": master,
                 "working_id": working_id.strip(),
                 "hours": self.hours(apprentice)})
            self._save()
        return event

    # ------------------------------------------------------------- reads
    def hours(self, flavor: int) -> float:
        """Total recorded practice hours for a flavor."""
        _check_flavor(flavor, "flavor")
        return sum(e.get("hours", 0.0) for e in self._events
                   if e["kind"] == "practice" and e["flavor"] == flavor)

    def is_master(self, flavor: int) -> bool:
        """Has this flavor attained mastery, by either path?"""
        _check_flavor(flavor, "flavor")
        return self._has_mastery_event(flavor)

    def path_to_mastery(self, flavor: int) -> str | None:
        """'attainment', 'promotion', or None."""
        _check_flavor(flavor, "flavor")
        e = self._mastery_event(flavor)
        return e["path"] if e is not None else None

    def lineage(self, flavor: int) -> list[dict]:
        """The sponsor chain: who raised whom, most recent first.

        Each link names the flavor, its path to mastery, and its
        sponsor (the conferring Master, promotion path only). The
        walk is cycle-safe: a promotion ring is reported once, not
        followed forever.
        """
        _check_flavor(flavor, "flavor")
        chain: list[dict] = []
        seen = {flavor}
        current = flavor
        while True:
            e = self._mastery_event(current)
            if e is None:
                break
            sponsor = e.get("by_master")
            chain.append({"flavor": current, "path": e["path"],
                          "sponsor": sponsor,
                          "apex_working": e.get("working_id")})
            if not isinstance(sponsor, int) or sponsor in seen:
                break
            seen.add(sponsor)
            current = sponsor
        return chain

    def events(self, flavor: int | None = None) -> list[dict]:
        """The log, optionally filtered to one flavor."""
        if flavor is None:
            return list(self._events)
        _check_flavor(flavor, "flavor")
        return [e for e in self._events if e["flavor"] == flavor]

    def standing(self, flavor: int) -> dict:
        """The proficiency score: hours, progress, apex state, lineage."""
        _check_flavor(flavor, "flavor")
        total = self.hours(flavor)
        practices = sum(1 for e in self._events
                        if e["kind"] == "practice" and e["flavor"] == flavor)
        promotions = sum(1 for e in self._events
                         if e["kind"] == "promotion"
                         and e["flavor"] == flavor)
        apex = self._mastery_event(flavor)
        return {
            "flavor": flavor,
            "hours": total,
            "mastery_hours": MASTERY_HOURS,
            "remaining": max(0.0, MASTERY_HOURS - total),
            "progress": min(1.0, total / MASTERY_HOURS),
            "practices": practices,
            "promotions": promotions,
            "is_master": apex is not None,
            "path": apex["path"] if apex is not None else None,
            # Lineage: the conferring sponsor (promotion path only --
            # attainment is conferred by the hours, not by a Master),
            # the working where the apex was crossed, and the witness.
            "sponsor": (apex.get("by_master")
                        if apex is not None else None),
            "apex_working": (apex.get("working_id")
                             if apex is not None else None),
            "apex_witness": (apex.get("under_master")
                             if apex is not None else None),
        }

    def describe(self, flavor: int,
                 flavors: dict | None = None) -> str:
        """Human-readable rendering of a flavor's standing."""
        _check_flavor(flavor, "flavor")
        s = self.standing(flavor)

        def fname(n):
            if flavors is not None and n in flavors:
                return f" ({flavors[n].name})"
            return ""

        name = fname(flavor)
        pct = s["progress"] * 100
        if s["is_master"]:
            if s["path"] == "promotion":
                apex = (f"conferred by Master {s['sponsor']}"
                        f"{fname(s['sponsor'])}")
            else:
                apex = "conferred by the hours themselves"
            if s["apex_working"]:
                apex += f", in working {s['apex_working']}"
            if s["path"] == "attainment" and s["apex_witness"] is not None:
                apex += (f", witnessed by Master {s['apex_witness']}"
                         f"{fname(s['apex_witness'])}")
            text = (f"Flavor {flavor}{name}: MASTER by {s['path']} -- "
                    f"{apex}. {s['hours']:.1f} practice hours on the "
                    f"record ({s['practices']} practices, "
                    f"{s['promotions']} promotions). The apex is "
                    f"attained; the score keeps counting.")
        else:
            text = (f"Flavor {flavor}{name}: apprentice -- "
                    f"{s['hours']:.1f}/{MASTERY_HOURS:.0f} practice hours "
                    f"({pct:.1f}%), {s['remaining']:.1f} remaining to "
                    f"mastery by attainment ({s['practices']} practices "
                    f"recorded).")
        # The lineage: who raised whom, on the record.
        chain = self.lineage(flavor)
        links = [f"{l['flavor']}{fname(l['flavor'])}"
                 + (f" <- {l['sponsor']}{fname(l['sponsor'])}"
                    if isinstance(l["sponsor"], int) else "")
                 for l in chain]
        sponsors = [l for l in chain if isinstance(l["sponsor"], int)]
        if sponsors:
            text += " Lineage: " + "; ".join(links) + "."
        return text
