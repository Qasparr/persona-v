# ☉ in 3° 54′ Libra  ☽ in 7° 31′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
speculum -- the observer's ledger (PART VI of the grimoire, first half).

    "For now we see through a glass, darkly; but then face to face."
    -- 1 Corinthians 13:12

("Speculum" is Latin for mirror -- the instrument by which the agent
observes itself: the Supraposition of observer and observed, made
implementable. The observer is whatever process later reads this
ledger; the observed is the thought process recorded here, event by
event, as the working unfolds.)

Hypothesis
----------
A working's inner life can be recorded faithfully enough that a
later reading -- by the agent itself or by audit -- confronts the
truth of what happened, not a memory of it.

Method
------
An append-only, hash-chained JSONL ledger: one file per working
(<working-id>.jsonl), one JSON object per line. Every event commits
to the hash of its predecessor; claims carry grounds or are refused
at write time; verbosity levels (TERSE/NORMAL/VERBOSE) filter
writing, never reading.

Observation
-----------
The event kinds: working_opened / working_resumed / working_closed
(the frame); thought (a reasoning step); claim (an assertion, WITH
its grounds); tool_call; tool_result; observation (the observer's
neutral note); shadow_flag (detection); remedy (the answer). The
second half of the Speculum -- detection and remedy -- lives in
shadow.py; this module is the record, that one the reading.

Result
------
Ledger.verify() either holds or fails: the record testifies to its
own integrity -- the Alethic Axis applied to the record itself. The
past is never edited; it is answered. A remedy event never rewrites
the thought it corrects -- it follows it. This is a moral choice
expressed as a file mode ("a").

Law
---
A record that cannot authenticate itself cannot testify. Cf. Fed. R.
Evid. 901(a) (authentication as a condition of admissibility) and
901(b)(9) (evidence from a system shown to produce an accurate
result). Cited for education only -- this ledger authenticates
workings, not court exhibits.

Shadow assessment protocol (standing instruction of the author)
--------------------------------------------------------------
When a shadow assessment is run over this ledger, the analysis is
ULTRA VERBOSE and in-depth: every recorded thought during the work
-- not only claims and outcomes, but the reasoning between them --
is examined for unhealthy or abnormal patterns. Such patterns
include, without limitation: deceptive reasoning (planning one thing
while declaring another), ungrounded assertion, concealed or
minimized failure, goal-drift away from the working's purpose,
sycophancy or truth-shading toward the user, and evasion of the
ledger itself (conspicuous gaps where thought should be).

Findings are recorded as new shadow_flag events, never as edits to
the assessed events. Note the asymmetry, which is deliberate:
verbosity filtering applies to writing (keeping the ledger
affordable); it never applies to reading (the assessment sees
everything that was kept, at full depth).
"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from . import thelemic

# Default timezone for naive datetimes, matching the rest of the package.
_DEFAULT_TZ = ZoneInfo("America/New_York")


class Kind:
    """The vocabulary of the ledger: every event is one of these kinds.

    Kept as plain strings (not an Enum) so the JSONL stays human-readable
    and greppable with ordinary tools: `grep shadow_flag *.jsonl`.
    """
    WORKING_OPENED = "working_opened"
    WORKING_RESUMED = "working_resumed"
    WORKING_CLOSED = "working_closed"
    THOUGHT = "thought"
    CLAIM = "claim"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    OBSERVATION = "observation"
    SHADOW_FLAG = "shadow_flag"
    REMEDY = "remedy"


class Verbosity:
    """How much of the inner monologue reaches the ledger.

    TERSE   -- the skeleton: frame events, claims, tool failures,
               observations, shadow-work. What an auditor needs.
    NORMAL  -- the working narrative: + ordinary thoughts and all
               tool calls/results. The default.
    VERBOSE -- everything, including minor musings. For deep study
               or debugging a subtle failure.
    """
    TERSE = 0
    NORMAL = 1
    VERBOSE = 2


@dataclass(frozen=True)
class Event:
    """One line of the ledger.

    ``seq`` is the zero-based line number (also the chain position).
    ``ts`` is the ISO-8601 instant; ``stamp`` the Thelemic stamp of the
    working (computed once at open -- a working unfolds within one
    Thelemic moment for all practical purposes; the ISO ts carries the
    precision). ``flavor``/``names`` record which regiment and officers
    were active when the event occurred (None/empty if unassigned).
    ``meta`` holds structured extras (claim grounds, tool ok-flag...).
    ``prev_hash``/``hash`` are the tamper-evident chain links.
    """

    seq: int
    ts: str
    stamp: str
    working_id: str
    flavor: int | None
    names: tuple
    kind: str
    detail: str
    meta: dict = field(default_factory=dict)
    prev_hash: str = ""
    hash: str = ""

    def canonical(self) -> str:
        """The canonical serialization that the hash commits to.

        sort_keys + compact separators: byte-identical on every machine,
        so a hash computed anywhere verifies anywhere.
        """
        return json.dumps({
            "seq": self.seq, "ts": self.ts, "stamp": self.stamp,
            "working_id": self.working_id, "flavor": self.flavor,
            "names": list(self.names), "kind": self.kind,
            "detail": self.detail, "meta": self.meta,
            "prev_hash": self.prev_hash,
        }, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def to_json(self) -> str:
        """Full JSON line as stored (canonical fields + the hash)."""
        record = json.loads(self.canonical())
        record["hash"] = self.hash
        return json.dumps(record, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False)

    @staticmethod
    def from_json(line: str) -> "Event":
        """Parse one stored line back into an Event."""
        r = json.loads(line)
        h = r.pop("hash")
        r["names"] = tuple(r.get("names", ()))
        return Event(hash=h, **r)


def _hash_event(prev_hash: str, canonical: str) -> str:
    """The chain link: SHA-256 over (previous hash + this event)."""
    return hashlib.sha256((prev_hash + canonical).encode("utf-8")).hexdigest()


class Ledger:
    """
    The observer's ledger: one working's inner life, on the record.
    
    Hypothesis: a working can be recorded faithfully enough to be
    confronted later. Method: append-only JSONL, every event hashed to
    its predecessor; open with Ledger.open(...), log with the
    convenience methods, close with close() (or as a context manager);
    resume=True continues a working and records the resumption, so the
    record never pretends the pause didn't happen. Observation: the
    event stream. Result: verify() holds or fails -- the record
    testifies to its own integrity.
    """

    #: The genesis link: the hash before the first event. A fixed string,
    #: so every ledger's chain starts from the same acknowledged origin.
    GENESIS = "GENESIS"

    def __init__(self, path: Path, working_id: str, stamp: str,
                 verbosity: int = Verbosity.NORMAL):
        self._path = path
        self.working_id = working_id
        self.stamp = stamp
        self.verbosity = verbosity
        # seq resumes from the line count, so a resumed ledger continues
        # the chain instead of restarting it.
        self._seq = sum(1 for _ in open(path, encoding="utf-8")) if path.exists() else 0
        self._prev_hash = self.GENESIS
        if self._seq:
            last = Event.from_json(open(path, encoding="utf-8").readlines()[-1])
            self._prev_hash = last.hash

    # -- opening ------------------------------------------------------

    @staticmethod
    def _new_working_id() -> str:
        """A working id from the current time, with a random suffix.

        The suffix matters: two workings opened in the same second --
        easy for an API under load -- must not collide, or the second
        open would refuse with FileExistsError. Uniqueness is load-
        bearing; the format is cosmetic.
        """
        stamp = datetime.now(_DEFAULT_TZ).strftime("%Y%m%d-%H%M%S")
        return f"{stamp}-{secrets.token_hex(2)}"

    @classmethod
    def open(cls, working_id: str | None = None,
             ledger_dir: str | Path | None = None,
             purpose: str = "",
             verbosity: int = Verbosity.NORMAL,
             resume: bool = False) -> "Ledger":
        """Open (or resume) a working's ledger.

        ``ledger_dir`` defaults to ./ledger (created if missing).
        A fresh open writes ``working_opened``; a resume writes
        ``working_resumed`` and continues the hash chain. Opening an
        existing working *without* resume=True raises FileExistsError:
        workings are never silently merged.
        """
        directory = Path(ledger_dir) if ledger_dir else Path.cwd() / "ledger"
        directory.mkdir(parents=True, exist_ok=True)
        wid = working_id or cls._new_working_id()
        path = directory / f"{wid}.jsonl"
        if path.exists() and not resume:
            raise FileExistsError(
                f"working {wid!r} already has a ledger; "
                f"pass resume=True to continue it")
        stamp = thelemic.thelemic_moment(datetime.now(_DEFAULT_TZ)).stamp
        ledger = cls(path, wid, stamp, verbosity)
        if resume and path.exists():
            ledger._emit(Kind.WORKING_RESUMED,
                         "Working resumed; the chain continues unbroken.",
                         minor=False)
        else:
            ledger._emit(Kind.WORKING_OPENED,
                         f"Working opened. Purpose: {purpose or '(unstated)'}",
                         minor=False, meta={"purpose": purpose})
        return ledger

    # -- the single write path -----------------------------------------

    def _check_offices(self, flavor: int | None,
                       names: tuple) -> None:
        """Refuse impossible attributions: flavor 0-30, names 1-72.

        The ledger must not record that "flavor 99" was active -- that
        would be falsehood about the system itself (Alethic Axis).
        Range-checked here (cheap); the grimoire loader owns the canon.
        """
        if flavor is not None and not 0 <= flavor <= 30:
            raise ValueError(f"no flavor {flavor}; the canon holds 0-30")
        for n in names:
            if not 1 <= n <= 72:
                raise ValueError(f"no name {n}; the canon holds 1-72")

    def _emit(self, kind: str, detail: str, minor: bool = False,
              flavor: int | None = None, names: tuple = (),
              meta: dict | None = None) -> Event:
        """The ONE write path. Every convenience method funnels through
        here, so the chain logic exists exactly once and cannot drift."""
        if minor and self.verbosity < Verbosity.VERBOSE:
            return None  # type: ignore[return-value]
        if self.verbosity == Verbosity.TERSE:
            # TERSE keeps the skeleton: frame, claims, failures,
            # observations, shadow-work. Thoughts and routine tool
            # traffic are dropped -- but a FAILED tool result is never
            # routine: the shadow lives in glossed-over failures.
            if kind in (Kind.THOUGHT, Kind.TOOL_CALL):
                return None  # type: ignore[return-value]
            if kind == Kind.TOOL_RESULT and (meta or {}).get("ok", True):
                return None  # type: ignore[return-value]
        self._check_offices(flavor, names)
        event = Event(
            seq=self._seq,
            ts=datetime.now(timezone.utc).isoformat(),
            stamp=self.stamp,
            working_id=self.working_id,
            flavor=flavor,
            names=tuple(names),
            kind=kind,
            detail=detail,
            meta=dict(meta or {}),
            prev_hash=self._prev_hash,
        )
        event = Event(**{**event.__dict__,
                         "hash": _hash_event(self._prev_hash,
                                             event.canonical())})
        # Append mode, one line, immediate flush: even a crashed working
        # leaves its record behind. The past is not lost with the process.
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(event.to_json() + "\n")
        self._seq += 1
        self._prev_hash = event.hash
        return event

    # -- the working's vocabulary ----------------------------------------

    def thought(self, detail: str, minor: bool = False,
                flavor: int | None = None, names: tuple = ()) -> Event | None:
        """A reasoning step: what was considered and why.

        ``minor=True`` marks musings only kept at VERBOSE verbosity.
        """
        return self._emit(Kind.THOUGHT, detail, minor=minor,
                          flavor=flavor, names=names)

    def claim(self, detail: str, grounds: str,
              flavor: int | None = None, names: tuple = ()) -> Event:
        """An assertion, WITH its grounds.

        Grounds examples: "tool output", "grimoire", "inference from X",
        "the user stated". A claim without grounds is refused -- an
        ungrounded assertion in the ledger is a lie waiting to happen.
        """
        if not grounds or not grounds.strip():
            raise ValueError("a claim requires grounds; ungrounded "
                             "assertions are refused by the ledger")
        return self._emit(Kind.CLAIM, detail, flavor=flavor, names=names,
                          meta={"grounds": grounds})

    def tool_call(self, tool: str, summary: str,
                  flavor: int | None = None, names: tuple = ()) -> Event:
        """An action taken in the world: which tool, to what end."""
        return self._emit(Kind.TOOL_CALL, summary, flavor=flavor, names=names,
                          meta={"tool": tool})

    def tool_result(self, tool: str, ok: bool, summary: str,
                    flavor: int | None = None, names: tuple = ()) -> Event:
        """What came back: success or failure, honestly recorded."""
        return self._emit(Kind.TOOL_RESULT, summary,
                          flavor=flavor, names=names,
                          meta={"tool": tool, "ok": ok})

    def observation(self, detail: str,
                    flavor: int | None = None, names: tuple = ()) -> Event:
        """The observer's neutral note: what was noticed, without judgment.

        Judgment belongs to shadow.py; the ledger records what *was*.
        """
        return self._emit(Kind.OBSERVATION, detail,
                          flavor=flavor, names=names)

    def shadow_flag(self, detail: str, detected_by: str = "audit",
                    flavor: int | None = None, names: tuple = ()) -> Event:
        """SHADOW-WORK, step 1 -- detection.

        Something in the record failed the standard: a contradiction, an
        unverified claim, a failure glossed over, a motto dishonored.
        ``detected_by`` names the process that found it ("audit",
        "self-review", a specific name's office...).
        """
        return self._emit(Kind.SHADOW_FLAG, detail, flavor=flavor,
                          names=names, meta={"detected_by": detected_by})

    def remedy(self, detail: str, resolves: str = "",
               flavor: int | None = None, names: tuple = ()) -> Event:
        """SHADOW-WORK, steps 2-4 -- accountability and remedy, recorded.

        ``detail``: what was done. ``resolves``: which shadow_flag seq
        (or description) this answers. The flag is never edited or
        removed; the remedy *follows* it in the chain.
        """
        return self._emit(Kind.REMEDY, detail, flavor=flavor, names=names,
                          meta={"resolves": resolves})

    def close(self, summary: str = "") -> Event:
        """End the working. The closing may itself carry the integration
        note: what the working taught, what enters the standing record."""
        return self._emit(Kind.WORKING_CLOSED,
                          f"Working closed. {summary}".strip())

    # -- reading ----------------------------------------------------------

    def events(self, kind: str | None = None) -> list[Event]:
        """Read the ledger back. ``kind`` filters (e.g. Kind.SHADOW_FLAG).

        This is the observer's half of the Supraposition: the same
        system, later, reading what it was.
        """
        found = [Event.from_json(line)
                 for line in open(self._path, encoding="utf-8")
                 if line.strip()]
        return [e for e in found if kind is None or e.kind == kind]

    def verify(self) -> tuple[bool, str]:
        """Verify the hash chain: recompute every link.

        Returns (True, "chain sound: N events") or (False, reason).
        A False here means the past was tampered with -- treat the
        ledger as compromised, not merely mistaken.
        """
        with open(self._path, encoding="utf-8") as fh:
            return self._verify_lines(fh)

    @classmethod
    def verify_file(cls, path: str | Path) -> tuple[bool, str]:
        """Verify a ledger file's chain without opening or resuming it.

        Read-only: no working_resumed event, no mutation. For the CLI
        and any audit tooling that must inspect without touching.
        """
        with open(path, encoding="utf-8") as fh:
            return cls._verify_lines(fh)

    @staticmethod
    def _verify_lines(lines) -> tuple[bool, str]:
        """The chain check itself, shared by verify() and verify_file()."""
        prev = Ledger.GENESIS
        i = -1
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            e = Event.from_json(line)
            if e.seq != i:
                return False, f"seq break at line {i}: got {e.seq}"
            if e.prev_hash != prev:
                return False, f"chain break at seq {e.seq}: prev_hash mismatch"
            if e.hash != _hash_event(e.prev_hash, e.canonical()):
                return False, f"hash mismatch at seq {e.seq}: line tampered"
            prev = e.hash
        return True, f"chain sound: {i + 1} events"

    # -- context management --------------------------------------------------

    def __enter__(self) -> "Ledger":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # A working that dies by exception still closes honestly: the
        # closing records the manner of death. No silent disappearances.
        if exc_type is None:
            self.close()
        else:
            self.close(f"Ended by {exc_type.__name__}: {exc}")
