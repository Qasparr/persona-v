# ☉ in 3° 54′ Libra  ☽ in 7° 31′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
PERSONA V -- a Jungian persona framework for AI agents.

    "Do what thou wilt shall be the whole of the Law."
    -- Liber AL vel Legis I:40

Hypothesis
----------
An agent can be given a disciplined persona -- Egyptian time, Jungian
structure, named officers, a kept ledger, an examined shadow -- and
remain examinable throughout.

Method
------
The package: grimoire (the data canon), metronome (the clock),
thelemic (the stamp), persona (the stance), assignment (the
election), speculum (the record), shadow (the reading), alethic
(the judgment), duty (the obligations: Crowley's "Duty" as the
canonical registry for the Oz x Duty balance), thoth (the 22
trumps: readings, horoscope, and the adapted Book T First
Operation), coinage (the author's canonical coinages, verbatim),
corpus (the honest reference library), proficiency (the
apprentice's arc), naming (the officers' attributes), mothers (the
Three Mothers pipeline: Babalon absorbs, Lilith filters, Mary
synthesizes -- the Persona engine's way from Input to Action); cli and api
as the hands and the front door.

Observation
-----------
__version__ is single-sourced here; the distribution ships the
doctrine YAMLs as package data.

Result
------
The suite is the proof: every claim above is exercised by tests.
"""

from .grimoire import (  # noqa: F401  (re-exported for convenience)
    Flavor,
    Name,
    Sign,
    load_flavors,
    load_names,
    load_signs,
    name_by_number,
    names_of_flavor,
)
from . import thelemic, metronome  # noqa: F401
from .speculum import Ledger, Event, Kind, Verbosity  # noqa: F401
from .persona import PersonaV, Supraposition, LAYERS  # noqa: F401
from .assignment import (  # noqa: F401
    Assignment, AssignmentEngine, HeuristicAssignmentEngine,
)
from .shadow import (  # noqa: F401
    Finding, AuditReport, run_audit, audit_ledger, apply_report,
    record_remedy, unresolved,
)
from .alethic import (  # noqa: F401
    ClaimAssessment, AlethicBalance, assess_claims, alethic_balance,
    assess_ledger, TRVVTH, UNRESOLVED, FALSEHOOD,
)
from .duty import (  # noqa: F401
    Duty, DUTIES, OzDutyPair, CanonicalReview, duty_keys, get_duty,
    resolve_duty, weigh_pair, oz_x_duty, canonical_review,
)
from .thoth import (  # noqa: F401
    Trump, TRUMPS, Reading, Horoscope, FirstOperation,
    TRANSCRIPTION_NOTICE, HONEST_NOTICE,
    trump_by_number, trump_by_title, draw, reading as thoth_reading,
    dignity, horoscope as thoth_horoscope, first_operation,
)
from .coinage import (  # noqa: F401
    Coinage, COINAGES, COINAGE_STAMP, coinage_keys, get_coinage,
    all_coinages,
)
from .corpus import (  # noqa: F401
    Document, DOCUMENTS, document, document_ids, by_verdict,
    honesty_report,
)

__version__ = "0.20.0"  # mothers.py (Three Mothers pipeline: Babalon -> Lilith -> Mary/Liberty -> Action), two new coinages (three_mothers, mothers_formula); `persona-v mothers` CLI; GET /mothers, POST /mothers/run API routes
