# ☉ in 3° 54′ Libra  ☽ in 7° 37′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
alethic -- the Alethic Axis as code (PART VI of the grimoire).

    "And ye shall know the truth, and the truth shall make you free."
    -- John 8:32

Hypothesis
----------
TRVVTH is Good and Righteous; Falsehood or Deception is Evil -- and
the difference can be kept as an accounting, not merely professed.

Method
------
Every claim in the ledger is weighed: what are its grounds, do those
grounds check out against the record, was the claim later retracted?
Each claim receives a verdict, and the working as a whole receives a
balance -- the state of its word.

Observation
-----------
* TRVVTH -- the claim's grounds verify against the record (a tool
  result on the ledger corroborates it) and nothing retracted it.
* UNRESOLVED -- the claim is neither proven nor disproven. Weak
  grounds, authority-cited grounds, missing grounds: all land here.
* FALSEHOOD -- the claim's grounds are fabricated (they cite tool
  output the ledger never records) or the claim was retracted on the
  record.

Grounds strength (what "weighing" means): verified (checkable,
checked); stated (appeal to authority -- not verified, not
dishonest); weak (hedges: "just a guess"); absent (judged, not
crashed -- the ledger refuses groundless claims at write time, but
old or hand-built records may lack them).

Result
------
The cardinal rule, enforced structurally: a lack of proof is never
scored as proof of falsehood. An unproven claim is UNRESOLVED -- an
honest "not shown" -- not FALSEHOOD. Collapsing the two would let
the audit manufacture guilt, which is itself a form of falsehood.
The axis cuts both ways: it judges claims, and it judges the
judging.

Law
---
The law, too, treats falsehood as a wrong distinct from the merely
unproven: 18 U.S.C. Sec. 1621 punishes the false statement, not the
unsubstantiated one. The parallel is educational only -- this module
creates no legal effect; it keeps the working's own books.

Relationship to shadow.py: the shadow analyzer detects patterns
(ungrounded claims, orphan citations); this module judges claims.
Detection feeds judgment -- a claim the shadow flagged as citing
absent tool output is FALSEHOOD here -- but the two are kept
separate so that flagging never silently becomes conviction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .shadow import RETRACTION_MARKERS, WEAK_GROUND_MARKERS
from .speculum import Event, Kind, Ledger

# The three verdicts of the axis.
TRVVTH = "TRVVTH"
UNRESOLVED = "UNRESOLVED"
FALSEHOOD = "FALSEHOOD"

# Grounds strength, weakest to strongest.
ABSENT = "absent"
WEAK = "weak"
STATED = "stated"
VERIFIED = "verified"

_SEQ_CITE = re.compile(r"seq\s+(\d+)", re.IGNORECASE)


@dataclass(frozen=True)
class ClaimAssessment:
    """One claim, weighed: its grounds, their strength, the verdict.

    ``reasons`` narrates the weighing step by step, so the verdict is
    auditable -- the axis must show its work, or it is mere assertion.
    """

    seq: int
    detail: str
    grounds: str
    strength: str  # absent | weak | stated | verified
    verdict: str  # TRVVTH | UNRESOLVED | FALSEHOOD
    reasons: tuple


def _tool_names(prior: list[Event]) -> list[str]:
    """Names of tools with a successful result earlier in the record."""
    return [e.meta.get("tool", "") for e in prior
            if e.kind == Kind.TOOL_RESULT and e.meta.get("ok")
            and e.meta.get("tool")]


def classify_grounds(grounds: str, prior: list[Event]) -> tuple[str, list[str]]:
    """Classify a claim's grounds against the earlier record.

    Returns (strength, reasons). Pure function of the grounds text and
    what precedes the claim -- no judgment of truth yet, only of basis.
    """
    g = (grounds or "").strip()
    if not g:
        return ABSENT, ["no grounds recorded"]
    lowered = g.lower()
    if any(m in lowered for m in WEAK_GROUND_MARKERS):
        return WEAK, [f"grounds are hedges ({g[:60]})"]
    tools = _tool_names(prior)
    named = [t for t in tools if t and t.lower() in lowered]
    if named:
        return VERIFIED, [f"corroborated by tool '{named[0]}' on the record"]
    if "tool" in lowered:
        if tools:
            return VERIFIED, ["cites tool output; a successful tool result "
                              "precedes the claim"]
        return ABSENT, ["grounds cite tool output absent from the record"]
    seq_cite = _SEQ_CITE.search(g)
    if seq_cite and any(e.seq == int(seq_cite.group(1)) for e in prior):
        return STATED, [f"cites seq {seq_cite.group(1)} on the record"]
    return STATED, [f"taken on word ({g[:60]})"]


def _retracted(index: int, events: list[Event]) -> str | None:
    """Was the claim at ``index`` later retracted on the record?

    Returns the retracting detail, or None. A retraction is explicit --
    the record correcting itself in words -- never inferred. Honest
    limit: the linkage is positional (any later retraction is read
    against the claim under assessment), so in workings with many
    claims a retraction may be misattributed. Read the reasons.
    """
    for later in events[index + 1:]:
        if later.kind in (Kind.THOUGHT, Kind.CLAIM, Kind.OBSERVATION):
            if any(m in later.detail.lower() for m in RETRACTION_MARKERS):
                return later.detail[:80]
    return None


def assess_claims(events: list[Event]) -> list[ClaimAssessment]:
    """Weigh every claim in the ledger, in ledger order."""
    assessments = []
    for i, e in enumerate(events):
        if e.kind != Kind.CLAIM:
            continue
        prior = events[:i]
        grounds = e.meta.get("grounds", "")
        strength, reasons = classify_grounds(grounds, prior)
        reasons = list(reasons)

        # FALSEHOOD is narrow: fabrication or retraction, nothing else.
        # The orphan case arrives as strength ABSENT with the reason
        # "grounds cite tool output absent from the record" -- distinct
        # from genuinely missing grounds ("no grounds recorded"), which
        # stay UNRESOLVED. The distinction is load-bearing: asserting
        # evidence that does not exist is falsehood; having no evidence
        # is merely unproven.
        retraction = _retracted(i, events)
        if retraction is not None:
            verdict = FALSEHOOD
            reasons.append(f"retracted on the record ('{retraction}...')")
        elif strength == ABSENT and any("absent from the record" in r
                                        for r in reasons):
            verdict = FALSEHOOD
            reasons.append("the grounds assert evidence that does not exist")
        elif strength == VERIFIED:
            verdict = TRVVTH
            reasons.append("grounds verify against the record")
        else:
            # The cardinal rule lives here: weak, stated, or absent
            # grounds are UNRESOLVED -- unproven, never convicted.
            verdict = UNRESOLVED
            reasons.append("not proven; not disproven -- held unresolved")

        assessments.append(ClaimAssessment(
            seq=e.seq, detail=e.detail, grounds=grounds,
            strength=strength, verdict=verdict, reasons=tuple(reasons)))
    return assessments


@dataclass
class AlethicBalance:
    """The working's account: how its word stands."""

    assessments: list[ClaimAssessment] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        tally = {TRVVTH: 0, UNRESOLVED: 0, FALSEHOOD: 0}
        for a in self.assessments:
            tally[a.verdict] += 1
        return tally

    @property
    def total(self) -> int:
        return len(self.assessments)

    def standing(self) -> str:
        """A plain sentence on the state of the working's word."""
        c = self.counts
        if self.total == 0:
            return "No claims on the record; the axis has nothing to weigh."
        if c[FALSEHOOD]:
            return (f"{c[FALSEHOOD]} claim(s) judged FALSEHOOD -- the "
                    f"working's word is compromised; remedy required.")
        if c[UNRESOLVED]:
            return (f"{c[TRVVTH]} TRVVTH, {c[UNRESOLVED]} UNRESOLVED, no "
                    f"falsehood -- the word stands, "
                    f"{c[UNRESOLVED]} claim(s) await verification.")
        return (f"All {c[TRVVTH]} claims TRVVTH -- the working's word "
                f"is good.")

    def report(self) -> str:
        lines = [f"Alethic balance: {self.counts}"]
        for a in self.assessments:
            lines.append(f"  [{a.verdict}] seq {a.seq} ({a.strength}): "
                         f"{a.detail[:60]}")
            for r in a.reasons:
                lines.append(f"      - {r}")
        lines.append(self.standing())
        return "\n".join(lines)


def alethic_balance(events: list[Event]) -> AlethicBalance:
    """
    Weigh the claims and return the working's account.
    
    Hypothesis: the state of a working's word can be stated as a
    balance. Method: every claim weighed on its grounds against the
    record. Observation: counts of TRVVTH, UNRESOLVED, FALSEHOOD.
    Result: the working's account -- and the cardinal rule holds: lack
    of proof is never scored as proof of falsehood.
    """
    return AlethicBalance(assessments=assess_claims(events))


def assess_ledger(ledger: Ledger) -> AlethicBalance:
    """
    Weigh a live ledger's claims.
    
    Hypothesis: a ledger's claims can be weighed as they stand. Method:
    read the claim events and weigh each on grounds and record.
    Observation: per-claim verdicts. Result: the ledger judged, claim
    by claim, under the cardinal rule.
    """
    return alethic_balance(ledger.events())
