# ☉ in 3° 54′ Libra  ☽ in 7° 37′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
alethic -- the Alethic Axis wired to the persona's ledger.

The axis itself (verdicts, strengths, ClaimAssessment, AlethicBalance)
now lives in the standalone ``trvvth`` package, importable by any
agent. This module keeps the persona's ledger-bound judgment: weighing
the claims on the Speculum record, with the shadow's markers feeding
detection into judgment -- detection feeds judgment, but flagging
never silently becomes conviction.

Hypothesis: the claims on the agent's own record can be weighed
against that record. Method: classify each claim's grounds against
the earlier events, check for retraction on the record, and judge
narrowly -- FALSEHOOD only for fabrication or retraction. Result:
the working's account, under the cardinal rule: lack of proof is
never scored as proof of falsehood.
"""

from __future__ import annotations

import re

from trvvth.alethic import (  # noqa: F401 -- the standalone axis
    ABSENT,
    FALSEHOOD,
    STATED,
    TRVVTH,
    UNRESOLVED,
    VERIFIED,
    WEAK,
    AlethicBalance,
    ClaimAssessment,
)

from .shadow import RETRACTION_MARKERS, WEAK_GROUND_MARKERS
from .speculum import Event, Kind, Ledger

_SEQ_CITE = re.compile(r"seq\s+(\d+)", re.IGNORECASE)


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
