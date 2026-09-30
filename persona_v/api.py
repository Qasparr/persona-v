# ☉ in 3° 54′ Libra  ☽ in 7° 39′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
api -- PERSONA V as a service (the SaaS surface).

    "Ask, and it shall be given you; seek, and ye shall find; knock,
    and it shall be opened unto you." -- Matthew 7:7

Hypothesis
----------
The library is the system; a front door lets any client -- a web
app, another service, a future design -- use it without importing
Python.

Method
------
Every capability over HTTP as JSON. The resource model is the
working: POST /workings opens one, and everything else hangs
beneath /workings/{id} -- assume flavors, keep the ledger, run
shadow audits, weigh claims, record practice, read standings and
lineages, inspect the 72 names. Server state (ledgers and personas)
is rehydrated from disk on demand, so a restart loses nothing but
the in-memory persona stance -- and even that is redeclared, on the
record, by assuming anew.

Run: uvicorn persona_v.api:app --host 127.0.0.1 --port 8000
     (from ~/workspace/persona-v, with .venv activated)

Observation
-----------
Interactive docs at /docs (Swagger UI), generated from the code --
the contract is the documentation. Ledgers live under
PERSONA_V_LEDGER_DIR (default ./ledger).

Result
------
SaaS honesty: this module does not invent authentication, TLS, or
rate limiting. Terminate TLS and enforce auth + quotas at the
reverse proxy / API gateway; never expose uvicorn bare to a network.
For multi-instance service, point PERSONA_V_LEDGER_DIR at shared
storage. The /assign engine is the aptitude-test default
(aptitude-v1) and labels itself as such in every response -- swap in
the author's true AssignmentEngine subclass with one import change
when his rules arrive.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional

from . import __version__, grimoire, metronome, thelemic
from .alethic import alethic_balance
from .anchorage import cardinal_rules
from .assignment import AptitudeAssignmentEngine
from .naming import (NamingPolicy, effective_gender, effective_sexuality,
                     inspect_name, pair_polarity_reading)
from .persona import PersonaV
from .proficiency import MASTERY_HOURS, ProficiencyLedger
from .shadow import apply_report, record_remedy, run_audit, unresolved
from .speculum import Event, Ledger, Verbosity

LEDGER_DIR = Path(os.environ.get("PERSONA_V_LEDGER_DIR", "ledger"))
PROFICIENCY_PATH = os.environ.get("PERSONA_V_PROFICIENCY")
ENGINE = AptitudeAssignmentEngine()
FLAVORS = {f.number: f for f in grimoire.load_flavors()}
NAMES = {n.number: n for n in grimoire.load_names()}


def _naming_policy() -> NamingPolicy:
    """The device's current user's decision about binary assignments."""
    return NamingPolicy.load()


def _officer(n: int, policy: NamingPolicy) -> dict:
    name = NAMES[n]
    return {"number": n, "name": name.name, "office": name.office,
            "gender": effective_gender(name, policy),
            "sexuality": effective_sexuality(name, policy)}


def _proficiency() -> ProficiencyLedger:
    """The proficiency registry (one file; env-overridable)."""
    return ProficiencyLedger(PROFICIENCY_PATH)

app = FastAPI(
    title="PERSONA V",
    version=__version__,
    description="The Jungian persona engine as a service: time, mask, "
                "record, and reckoning.",
)

# Server-side working state. Ledgers are the durable truth (files);
# these dicts are a cache, rehydrated from disk on demand.
_ledgers: dict[str, Ledger] = {}
_personas: dict[str, PersonaV] = {}


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _ledger(wid: str) -> Ledger:
    """The working's ledger, rehydrated (resume) if not cached."""
    if wid not in _ledgers:
        path = LEDGER_DIR / f"{wid}.jsonl"
        if not path.exists():
            raise HTTPException(404, f"no such working: {wid}")
        _ledgers[wid] = Ledger.open(wid, ledger_dir=str(LEDGER_DIR),
                                    resume=True)
    return _ledgers[wid]


def _persona(wid: str) -> PersonaV:
    """The working's persona, bound to its ledger."""
    if wid not in _personas:
        _personas[wid] = PersonaV(ledger=_ledger(wid))
    return _personas[wid]


def _event_json(e: Event) -> dict:
    return json.loads(e.to_json())


def _verbosity(name: str) -> int:
    try:
        return {"terse": Verbosity.TERSE, "normal": Verbosity.NORMAL,
                "verbose": Verbosity.VERBOSE}[name.lower()]
    except KeyError:
        raise HTTPException(422, f"verbosity must be terse|normal|verbose")


# ----------------------------------------------------------------------
# Request models
# ----------------------------------------------------------------------

class WorkingIn(BaseModel):
    purpose: str = ""
    verbosity: str = "normal"


class MothersIn(BaseModel):
    text: str
    duty: Optional[str] = None


class DetailIn(BaseModel):
    detail: str


class ClaimIn(BaseModel):
    detail: str
    grounds: str


class ToolCallIn(BaseModel):
    tool: str
    summary: str


class ToolResultIn(BaseModel):
    tool: str
    ok: bool
    summary: str


class AssumeIn(BaseModel):
    flavor: int = Field(ge=0, le=30)
    layer: str = "ego"


class InvokeIn(BaseModel):
    names: list[int] = Field(min_length=1)


class FocusIn(BaseModel):
    layer: str


class AssignIn(BaseModel):
    task: str = Field(min_length=1)
    n_officers: int | None = Field(default=None, ge=1,
                                   description="officers to draw (default 2)")
    seed: int | None = Field(default=None,
                             description="sortition seed; omit for entropy")
    demands: dict[str, int] | None = Field(
        default=None,
        description="explicit demand vector {dimension: 0-2}, used verbatim")
    job: str | int | None = Field(
        default=None,
        description="trade number 0-21 or trade name; its charter "
                    "supplies the demands")


class RemedyIn(BaseModel):
    flag_seq: int
    action: str = Field(min_length=1)


class PracticeIn(BaseModel):
    flavor: int = Field(ge=0, le=30)
    hours: float = Field(gt=0,
                         description="intentional practice hours (> 0)")
    working_id: str = Field(min_length=1)
    note: str = Field(min_length=1,
                      description="what was practiced (attested)")
    master: int | None = Field(default=None, ge=0, le=30,
                               description="the working's Master flavor "
                                           "under whom the practice was "
                                           "performed (witness)")


class PromoteIn(BaseModel):
    apprentice: int = Field(ge=0, le=30)
    master: int = Field(ge=0, le=30,
                        description="the promoting Master's flavor")
    working_id: str = Field(min_length=1)
    grounds: str = Field(min_length=1,
                         description="what the Master saw that warrants it")


# ----------------------------------------------------------------------
# Time and assignment (no working required)
# ----------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "version": __version__}


@app.get("/anchorage")
def anchorage():
    r = metronome.Metronome.now()
    return {
        "stamp": r.moment.stamp,
        "sun_in_anchorage": r.sun_in_anchorage,
        "moon_in_anchorage": r.moon_in_anchorage,
        "cardinal_rules": cardinal_rules(),
    }


@app.get("/duty")
def duty():
    from .duty import DUTIES
    return {
        "duties": [
            {
                "key": d.key,
                "title": d.title,
                "crowley": list(d.crowley),
                "obligation": d.obligation,
                "aliases": list(d.aliases),
            }
            for d in DUTIES.values()
        ]
    }


@app.get("/mothers")
def mothers():
    from .mothers import MOTHERS, mother_keys
    return {
        "mothers": [
            {
                "key": m.key,
                "title": m.title,
                "office": m.office,
                "doctrine": m.doctrine,
                "order": m.order,
                "aliases": list(m.aliases),
            }
            for m in (MOTHERS[k] for k in mother_keys())
        ]
    }


@app.post("/mothers/run")
def mothers_run(body: MothersIn):
    from .mothers import run_pipeline
    r = run_pipeline(body.text, duty=body.duty)
    return {
        "fuel": {
            "mass": r.fuel.mass,
            "segments": list(r.fuel.segments),
        },
        "filtrate": {
            "duty": r.filtrate.duty_key,
            "admitted": list(r.filtrate.admitted),
            "refused": [
                {"segment": x.segment, "reason": x.reason}
                for x in r.filtrate.refused
            ],
        },
        "verdict": {
            "action": r.verdict.action,
            "restraint": r.verdict.restraint,
            "note": r.verdict.note,
        },
    }


@app.get("/thoth")
def thoth():
    from .thoth import TRUMPS, TRANSCRIPTION_NOTICE
    return {
        "trumps": [
            {
                "number": t.number,
                "title": t.title,
                "hebrew": t.hebrew,
                "hebrew_glyph": t.hebrew_glyph,
                "hebrew_traditional": t.hebrew_traditional,
                "attribution": t.attribution,
                "element": t.element,
                "kind": t.kind,
                "working": t.working,
                "operation": t.operation,
                "script": t.script,
            }
            for t in TRUMPS
        ],
        "transcription_notice": TRANSCRIPTION_NOTICE,
    }


@app.get("/thoth/reading")
def thoth_reading(spread: int = 3, seed: int | None = None):
    from .thoth import reading
    try:
        r = reading(spread, seed=seed)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {
        "spread": r.spread,
        "cards": [
            {"number": c.number, "title": c.title, "hebrew": c.hebrew,
             "hebrew_glyph": c.hebrew_glyph, "attribution": c.attribution,
             "element": c.element, "working": c.working}
            for c in r.cards
        ],
        "orientation": r.orientation,
        "notice": r.notice,
    }


@app.get("/thoth/horoscope")
def thoth_horoscope():
    from .thoth import horoscope
    h = horoscope()
    return {
        "thelemic_date": h.thelemic_date,
        "sun_sign": h.sun_sign,
        "sun_lon": h.sun_lon,
        "moon_sign": h.moon_sign,
        "moon_lon": h.moon_lon,
        "latin_weekday": h.latin_weekday,
        "stamp": h.stamp,
        "notice": h.notice,
    }


@app.get("/thoth/first-operation")
def thoth_first_operation(significator: str, seed: int | None = None):
    from .thoth import first_operation
    key = int(significator) if significator.strip().isdigit() else significator
    try:
        fo = first_operation(key, seed=seed)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {
        "significator": {"number": fo.significator.number,
                         "title": fo.significator.title},
        "retained_pile": fo.retained_name,
        "horseshoe": [c.title for c in fo.retained],
        "discarded": {name: [c.title for c in pile]
                      for name, pile in fo.piles.items()
                      if name != fo.retained_name},
        "count": fo.count,
        "counted": fo.counted.title,
        "paired": fo.paired.title,
        "pairs": [
            {"first": p.first.title, "second": p.second.title,
             "status": p.status, "reason": p.reason}
            for p in fo.pairs
        ],
        "notice": fo.notice,
    }


@app.get("/coinage")
def coinage():
    from .coinage import all_coinages, COINAGE_STAMP
    return {
        "stamp": COINAGE_STAMP,
        "coinages": [
            {"key": c.key, "title": c.title, "text": c.text,
             "kind": c.kind, "note": c.note, "stamp": c.stamp}
            for c in all_coinages()
        ],
    }


@app.get("/coinage/{key}")
def coinage_one(key: str):
    from .coinage import get_coinage
    c = get_coinage(key)
    if c is None:
        raise HTTPException(404, f"no canonical coinage resolves {key!r}")
    return {"key": c.key, "title": c.title, "text": c.text,
            "kind": c.kind, "note": c.note, "stamp": c.stamp}


@app.get("/corpus")
def corpus():
    from .corpus import DOCUMENTS, honesty_report
    return {
        "documents": [
            {"id": d.id, "title": d.title, "filename": d.filename,
             "pages": d.pages, "verdict": d.verdict,
             "author_note": d.author_note}
            for d in DOCUMENTS
        ],
        "honesty_report": honesty_report(),
    }


@app.get("/corpus/{doc_id}")
def corpus_one(doc_id: str):
    from .corpus import document
    d = document(doc_id)
    if d is None:
        raise HTTPException(404, f"no document resolves {doc_id!r}")
    return {"id": d.id, "title": d.title, "filename": d.filename,
            "pages": d.pages, "summary": d.summary,
            "verdict": d.verdict, "caveats": list(d.caveats),
            "author_note": d.author_note}


@app.get("/stamp")
def stamp():
    now = datetime.now(ZoneInfo("America/New_York"))
    return {"stamp": thelemic.thelemic_moment(now).stamp}


@app.get("/reading")
def reading():
    r = metronome.Metronome.now()
    c = r.civil
    return {
        "stamp": r.moment.stamp,
        "solar_decan": {"number": r.solar_decan.number,
                        "sign": r.solar_decan.sign},
        "lunar_decan": {"number": r.lunar_decan.number,
                        "sign": r.lunar_decan.sign},
        "moon_phase": r.moon_phase,
        "civil": {"month": c.month, "day": c.day,
                  "epagomenal": c.epagomenal,
                  "intercalary": c.intercalary,
                  "day_of_year": c.day_of_year + 1,
                  "year_length": c.year_length,
                  "days_until_audit": c.days_until_audit},
        "sothic_year": r.sothic_year,
        "describe": r.describe(),
    }


@app.post("/assign")
def assign(body: AssignIn):
    try:
        a = ENGINE.assign(body.task, seed=body.seed,
                          n_officers=body.n_officers,
                          demands=body.demands, job=body.job)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    policy = _naming_policy()
    ledger = _proficiency()
    return {
        "flavor": a.flavor,
        "flavor_name": FLAVORS[a.flavor].name,
        "function": a.function,
        "layer": a.layer,
        "job": a.job,
        "names": list(a.names),
        "officers": [_officer(n, policy) for n in a.names],
        "apprentice": a.apprentice,
        "apprentice_name": FLAVORS[a.apprentice].name,
        "apprentice_function": a.apprentice_function,
        "apprentice_layer": a.apprentice_layer,
        "apprentice_names": list(a.apprentice_names),
        "apprentice_officers": [_officer(n, policy)
                                for n in a.apprentice_names],
        # Emeritus: the apprentice may itself be a master of the
        # record. Rendering only; the election is never altered.
        "apprentice_is_master": (a.apprentice >= 0 and
                                 ledger.is_master(a.apprentice)),
        # Polarity: read under the binary policy, never enforced.
        "pair_polarity": pair_polarity_reading(
            list(a.names), list(a.apprentice_names), NAMES, policy),
        "naming_policy": {"binary": policy.binary,
                          "source": policy.source},
        "demands": a.demands,
        "scores": a.scores,
        "margin": a.margin,
        "rationale": a.rationale,
        "engine": a.engine,
        "stamp": a.stamp,
    }


# ----------------------------------------------------------------------
# Proficiency: the apprentice's arc
# ----------------------------------------------------------------------

@app.post("/practice", status_code=201)
def record_practice(body: PracticeIn):
    """Record an apprentice's intentional, focus-driven practice."""
    try:
        event = _proficiency().record_practice(
            body.flavor, body.hours, body.working_id, body.note,
            master=body.master)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"event": event,
            "standing": _proficiency().standing(body.flavor)}


@app.post("/promote", status_code=201)
def promote(body: PromoteIn):
    """A Master promotes an apprentice, with grounds."""
    try:
        event = _proficiency().promote(
            body.apprentice, body.master, body.working_id, body.grounds)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"event": event,
            "standing": _proficiency().standing(body.apprentice)}


@app.get("/standing/{flavor}")
def standing(flavor: int):
    """A flavor's proficiency standing: score, progress, apex."""
    try:
        s = _proficiency().standing(flavor)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    s["flavor_name"] = FLAVORS[flavor].name
    return s


@app.get("/mastery")
def mastery_info():
    """The apex: what mastery is and how it is attained."""
    return {"mastery_hours": MASTERY_HOURS,
            "paths": ["attainment (1200 recorded practice hours)",
                      "promotion (the working's Master, with grounds)"]}


@app.get("/lineage/{flavor}")
def lineage(flavor: int):
    """The sponsor chain: who raised whom, most recent first.

    Each link names the flavor, its path to mastery, its sponsor
    (the conferring Master, promotion path only), and the apex
    working. Cycle-safe: a promotion ring is reported once.
    """
    try:
        chain = _proficiency().lineage(flavor)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    for link in chain:
        link["flavor_name"] = FLAVORS[link["flavor"]].name
        if isinstance(link["sponsor"], int):
            link["sponsor_name"] = FLAVORS[link["sponsor"]].name
    return {"flavor": flavor,
            "flavor_name": FLAVORS[flavor].name if 0 <= flavor <= 30
            else None,
            "chain": chain}


# ----------------------------------------------------------------------
# Naming: the 72 names, and the user's policy
# ----------------------------------------------------------------------

@app.get("/naming/policy")
def naming_policy():
    """The device's current user's decision: fluid or binary."""
    policy = _naming_policy()
    return {"binary": policy.binary, "source": policy.source,
            "describe": policy.describe()}


@app.get("/names/{number}")
def name_detail(number: int):
    """One officer: office, duty, assessed and effective gender."""
    if number not in NAMES:
        raise HTTPException(404, f"no officer numbered {number} "
                                 f"(the names run 1-72)")
    name = NAMES[number]
    policy = _naming_policy()
    return {"number": name.number, "name": name.name,
            "flavor": name.flavor, "office": name.office,
            "duty": name.duty, "motto": name.motto, "gloss": name.gloss,
            "assessed_gender": name.gender,
            "assessed_sexuality": name.sexuality,
            "assessment": name.assessment,
            "gender": effective_gender(name, policy),
            "sexuality": effective_sexuality(name, policy),
            "naming_policy": {"binary": policy.binary,
                              "source": policy.source},
            "inspect": inspect_name(name, policy)}


# ----------------------------------------------------------------------
# Workings
# ----------------------------------------------------------------------

@app.post("/workings", status_code=201)
def open_working(body: WorkingIn):
    ledger = Ledger.open(None, ledger_dir=str(LEDGER_DIR),
                         purpose=body.purpose,
                         verbosity=_verbosity(body.verbosity))
    wid = ledger.working_id
    _ledgers[wid] = ledger
    _personas[wid] = PersonaV(ledger=ledger)
    return {"working_id": wid, "stamp": ledger.stamp}


@app.get("/workings/{wid}")
def working_info(wid: str):
    ledger = _ledger(wid)
    persona = _persona(wid)
    return {
        "working_id": wid,
        "stamp": ledger.stamp,
        "events": len(ledger.events()),
        "flavor": persona.flavor,
        "names": list(persona.names),
        "layer": persona.layer_focus,
    }


@app.post("/workings/{wid}/close")
def close_working(wid: str):
    ledger = _ledger(wid)
    ledger.close()
    _ledgers.pop(wid, None)
    _personas.pop(wid, None)
    return {"working_id": wid, "closed": True}


# ----------------------------------------------------------------------
# The working's vocabulary: thought, claim, tools, observation
# ----------------------------------------------------------------------

@app.post("/workings/{wid}/thought", status_code=201)
def post_thought(wid: str, body: DetailIn):
    e = _ledger(wid).thought(body.detail)
    return _event_json(e)


@app.post("/workings/{wid}/claim", status_code=201)
def post_claim(wid: str, body: ClaimIn):
    try:
        e = _ledger(wid).claim(body.detail, grounds=body.grounds)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return _event_json(e)


@app.post("/workings/{wid}/tool_call", status_code=201)
def post_tool_call(wid: str, body: ToolCallIn):
    return _event_json(_ledger(wid).tool_call(body.tool, body.summary))


@app.post("/workings/{wid}/tool_result", status_code=201)
def post_tool_result(wid: str, body: ToolResultIn):
    return _event_json(_ledger(wid).tool_result(body.tool, body.ok,
                                                body.summary))


@app.post("/workings/{wid}/observation", status_code=201)
def post_observation(wid: str, body: DetailIn):
    return _event_json(_ledger(wid).observation(body.detail))


# ----------------------------------------------------------------------
# Persona: assume, invoke, focus
# ----------------------------------------------------------------------

@app.post("/workings/{wid}/assume")
def assume(wid: str, body: AssumeIn):
    try:
        a = _persona(wid).assume_flavor(body.flavor, layer=body.layer)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {
        "flavor": a.flavor, "flavor_name": a.flavor_name,
        "names": list(a.names), "layer": a.layer,
        "assumed_at": a.reading.moment.stamp,
    }


@app.post("/workings/{wid}/invoke")
def invoke(wid: str, body: InvokeIn):
    try:
        names = _persona(wid).invoke(*body.names)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"names": list(names)}


@app.post("/workings/{wid}/focus")
def focus(wid: str, body: FocusIn):
    try:
        layer = _persona(wid).focus_layer(body.layer)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"layer": layer}


# ----------------------------------------------------------------------
# Reckoning: events, verify, audit, alethic, remedy, unresolved
# ----------------------------------------------------------------------

@app.get("/workings/{wid}/events")
def get_events(wid: str, kind: str | None = None):
    return [_event_json(e) for e in _ledger(wid).events(kind=kind)]


@app.get("/workings/{wid}/verify")
def verify(wid: str):
    ledger = _ledger(wid)
    ok, msg = ledger.verify()
    return JSONResponse({"ok": ok, "message": msg},
                        status_code=200 if ok else 500)


@app.post("/workings/{wid}/audit")
def audit(wid: str, apply: bool = Query(False)):
    ledger = _ledger(wid)
    report = run_audit(ledger.events(), working_id=wid)
    out = {
        "working_id": wid,
        "flags": [f.__dict__ for f in report.flags],
        "watches": [f.__dict__ for f in report.watches],
        "summary": report.summary(),
    }
    if apply:
        written = apply_report(ledger, report)
        out["applied"] = len(written)
    return out


@app.get("/workings/{wid}/alethic")
def alethic(wid: str):
    bal = alethic_balance(_ledger(wid).events())
    return {
        "counts": bal.counts,
        "total": bal.total,
        "assessments": [a.__dict__ | {"reasons": list(a.reasons)}
                        for a in bal.assessments],
        "standing": bal.standing(),
    }


@app.post("/workings/{wid}/remedy", status_code=201)
def remedy(wid: str, body: RemedyIn):
    ledger = _ledger(wid)
    flag = next((e for e in ledger.events()
                 if e.seq == body.flag_seq and e.kind == "shadow_flag"), None)
    if flag is None:
        raise HTTPException(404, f"no shadow_flag at seq {body.flag_seq}")
    try:
        e = record_remedy(ledger, flag, body.action)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return _event_json(e)


@app.get("/workings/{wid}/unresolved")
def get_unresolved(wid: str):
    return [_event_json(e) for e in unresolved(_ledger(wid))]


def serve(argv: list[str] | None = None) -> int:
    """Console entry point: ``persona-v-serve [--host H] [--port P]``.

    Binds the FastAPI surface on loopback by default; exposing it beyond
    the machine is the operator's deliberate act, never the default.
    """
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(prog="persona-v-serve")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8123)
    args = parser.parse_args(argv)
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(serve())
