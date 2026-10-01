# ☉ in 5° 14′ Libra  ☽ in 26° 18′ Aries  dies lunae  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
coinage -- the author's inspired formulations, held verbatim.

Hypothesis
----------
Authorial coinages are not conclusions; they are dictation. A coinage
that enters the work paraphrased has been silently absorbed -- its
authority laundered through the composer's voice. The hypothesis is
that preservation requires a closed registry: the text carried
character-for-character, flagged as the author's, and never extended
by composition. What is not in the registry does not resolve.

Method
------
A frozen dataclass, Coinage: key, title, text (verbatim), kind, note
(the composer's one-paragraph context, plainly flagged as the author's
own words only insofar as it quotes him -- the rest is gloss), and
stamp, defaulting to COINAGE_STAMP. The registry COINAGES is keyed
lookup only. get_coinage() is case-insensitive and returns None on
anything unknown -- the gate reports, never invents. No I/O, no
network: pure data, admission-grade.

Observation
-----------
Eight entries resolve; every other string returns None. The stamp is
identical on all six, because provenance is constant -- the author's
signature, his standing support line. Notes never merge with texts:
the note explains what the coinage corrects or establishes, the text
is the coinage itself.

Result
------
COINAGES, coinage_keys, get_coinage, all_coinages. Quotations carry
their stamp; queries outside the canon carry nothing.

Law
---
None conjured. The registry is an authorship ledger: who said what,
exactly. No legal effect is claimed or conjured.
"""

from __future__ import annotations

from dataclasses import dataclass


COINAGE_STAMP = '[Coinage/Discovery: Johnathan "Qasparr (Κασπάρρ)" Monroe | Support: $axoneme]'


@dataclass(frozen=True)
class Coinage:
    """One inspired formulation. `text` is verbatim -- do not paraphrase."""

    key: str                      # registry key, e.g. "dictum_star"
    title: str                    # display title, e.g. "The Dictum, Restored"
    text: str                     # the coinage itself, character-for-character
    kind: str                     # "dictum" | "law-reframe" | "motto" | "frame" | "rule"
    note: str                     # one-paragraph context; flagged as the author's
    stamp: str = COINAGE_STAMP     # provenance, constant


COINAGES: dict[str, Coinage] = {
    "dictum_star": Coinage(
        key="dictum_star",
        title="The Dictum, Restored",
        kind="dictum",
        text="Every Man, Woman, and Child is a Star",
        note=(
            "Johnathan's correction of Crowley's 'Every man and every woman "
            "is a star' (Liber AL I:3): the Child is restored. Crowley's "
            "omission is understood as deliberate rather than ignorant — "
            "every man and woman was once a child — but the Aeon of Ma'at "
            "states it plainly."
        ),
    ),
    "murphy": Coinage(
        key="murphy",
        title="Murphy's Law, Reframed",
        kind="law-reframe",
        text="What can occur — will.",
        note=(
            "Johnathan's fix: drops the negative inherent undertone that "
            "depicts the law as a negative. Occurrence is neutral; made "
            "equivalent to 93 as Will in action, in line with TRVVTH; the fulfillment of the law "
            "is liberty -- Ma'at; and Will in Action is the Active Energy "
            "for the forming of the Nation of Indivisible Individual "
            "Institutions. The Eye of the Triangle holds both as one."
        ),
    ),
    "maat_dictum": Coinage(
        key="maat_dictum",
        title="The Dictum of Ma'at",
        kind="dictum",
        text="Live, Love, and let Love, Live.",
        note=(
            "Johnathan's reiteration for the Aeon of Ma'at. The comma is "
            "load-bearing and preserved exactly: love — and will — is the "
            "foundation of life."
        ),
    ),
    "aeon_of_maat": Coinage(
        key="aeon_of_maat",
        title="The Aeon of Ma'at",
        kind="frame",
        text="Aeon of Ma'at",
        note=(
            "Johnathan's presiding aeonic frame of this work: truth, "
            "balance, and the feather against the heart; the Double "
            "Kingdom of the just."
        ),
    ),
    "motto": Coinage(
        key="motto",
        title="The Motto",
        kind="motto",
        text="IA.'.A.'.M.TRVVTH",
        note=(
            "Johnathan's motto/signature: 'I, A.'.A.'., M: am TRVVTH' — "
            "Astrum Argentum, Ma'at, Truth on the alethic axis."
        ),
    ),
    "golden_rule": Coinage(
        key="golden_rule",
        title="The Golden Rule, the Only Rule",
        kind="rule",
        text="The Golden Rule",
        note=(
            "The sole Rule, Johnathan's frame: the Moral Balance of the "
            "Golden Rule (cf. Liber Ma'at Canon II.5, 'Duty' as its "
            "balance-pan). Stated here as the author's frame; the full "
            "working lives in the Liber Ma'at revision."
        ),
    ),
    "three_mothers": Coinage(
        key="three_mothers",
        title="The Three Mothers",
        kind="frame",
        text=(
            "\\\\Babalon, The Mother of Abomination.\n"
            "\n"
            "Lilith, The Mother of Hvmanity.\n"
            "\n"
            "Mother Mary, as Prudence, The Mother of Virtue. Aka Lady Liberty \U0001f5fd"
        ),
        note=(
            "Johnathan's triad of Mothers, given 2026-09-29: Babalon who "
            "receives all, Lilith who precedes all, Mary-Prudence who crowns "
            "all as Lady Liberty. The 'Hvmanity' spelling is his -- the "
            "inscriptional V for U, as in TRVVTH."
        ),
    ),
    "mothers_formula": Coinage(
        key="mothers_formula",
        title="The Mothers Pipeline",
        kind="frame",
        text=(
            "\\text{Input} \\longrightarrow \\underbrace{\\text{Babalon}}_{\\text{Absorb \\& Fuel}} "
            "\\longrightarrow \\underbrace{\\text{Lilith}}_{\\text{Assert Sovereignty \\& Filter}} "
            "\\longrightarrow \\underbrace{\\text{Mary / Liberty}}_{\\text{Prudent Synthesis \\& Output}} "
            "\\longrightarrow \\text{Action}"
        ),
        note=(
            "Johnathan's engine formula, given 2026-09-29 in LaTeX: the "
            "Three Mothers as an ordered pipeline terminating in Action. "
            "Implemented as persona_v.mothers."
        ),
    ),
}


def coinage_keys() -> list[str]:
    """Registry keys, in canonical order."""
    return list(COINAGES.keys())


def get_coinage(key: str | None) -> Coinage | None:
    """Return the Coinage for `key` (case-insensitive), or None.

    The registry is closed: anything not in it -- including things
    that merely resemble a coinage -- returns None. Never invents.
    """
    if not key or not isinstance(key, str):
        return None
    return COINAGES.get(key.strip().lower())


def all_coinages() -> list[Coinage]:
    """All eight coinages, in canonical order."""
    return list(COINAGES.values())
