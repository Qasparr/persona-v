#!/usr/bin/env python3
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
#
# persona_v/chorus.py -- the CHORUS stress-test harness.
#
# EPIGRAPH: "In the multitude of counsellors there is safety." -- Proverbs 11:14
# DATE:     Sol in Libra, 2026 e.v.
#
# HYPOTHESIS: one agent's verdict is a sample of one. A matrix of agents
#   varied across sense-pipeline, tongue, and gender -- each carrying the
#   full six-axis deployment personality at ultra verbosity -- converges
#   through TRVVTH on judgments no single agent could justify alone.
# METHOD:    compose the matrix (cartesian or representative) from a seed;
#   deploy every agent (personality + VERBOSE Speculum ledger + soul);
#   run each working through the runner hook; shadow-audit every ledger;
#   weigh key terms through Pontifex per tongue; read the convergence.
# OBSERVATION: the scaffold is fully testable without a model -- the
#   default runner is a deterministic stub; production plugs the LLM.
# RESULT:    prompt in, chorus out: verdicts, shadow outcomes, bridges,
#   and the balance point where the matrix converges.
#
# MECHANISM: stdlib + YAML only. random.Random(seed) drives every draw,
#   so one seed reproduces the chorus bit-for-bit. Pontifex is imported
#   lazily at the pipeline stage -- missing Pontifex raises ChorusError,
#   never a silent skip or a faked weighing.
# DOCTRINE:  fail-closed composition -- a malformed spec raises before
#   any agent exists. Unresolved shadow flags mark a verdict unjustified
#   (record-only), never silenced. The harness measures convergence; it
#   does not vote -- voting is politics, convergence is measurement.
#
# 93 93/93 -- Love is the law, love under will.

"""CHORUS: the PERSONA V multimodal stress-test harness.

For every prompt, deploy an agent per sensory pipeline, per tongue, per
gender -- all at once -- each with the six-axis deployment personality at
ultra verbosity. Logs run through Pontifex; the balance-finder reads where
the matrix converges through TRVVTH.
"""

from __future__ import annotations

import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from . import grimoire
from . import shadow
from . import soul as soul_mod
from .assignment import load_jobs
from .speculum import Ledger, Verbosity


# -- The three axes ----------------------------------------------------------
# DOCTRINE: the five tuners are the author's dictation (Touch, Taste, Sight,
#   Hearing, Smell). The channel mapping is the scribe's (Architecture §IV);
#   the red pen rules on it.

SENSES = ("sight", "hearing", "touch", "taste", "smell")

SENSE_CHANNELS = {
    "sight": "vision input -- images, screens, diagrams, the seen",
    "hearing": "audio input -- voice, sound, the heard",
    "touch": "tool-contact -- tool results, file reads, hands on the world",
    "taste": "discrimination -- qualitative judgment, taste in its older sense",
    "smell": "anomaly detection -- the smell test, off before it is named",
}

# MECHANISM: tongue -> (pontifex system, provenance note). Japanese has no
#   table: the agent still deploys, its weighings travel the Hebrew-fallback
#   path and are marked CONSTRUCTED-pending (the research track, CHORUS.md §VI).
TONGUES = {
    "hebrew": ("hebrew", "ATTESTED"),
    "greek": ("greek", "ATTESTED"),
    "latin": ("latin_ordinal", "ATTESTED"),
    "arabic": ("arabic_abjad", "ATTESTED"),
    "english": ("latin_ordinal", "ATTESTED -- native for English, not a fallback"),
    "japanese": (None, "CONSTRUCTED-pending -- research track; Hebrew-fallback meanwhile"),
}
DEFAULT_TONGUES = tuple(TONGUES)

# DOCTRINE: the binary axes draw on the officers' own gender assessments
#   (names.yaml). Nonbinary officers are never misgendered into the matrix.
GENDER_ASSESSMENT = {"masculine": "male", "feminine": "female"}
GENDERS = tuple(GENDER_ASSESSMENT)

DOMINANT_WEIGHT = 2.0  # the specialist's tuner; the scribe's ratio -- red pen rules
OPEN_WEIGHT = 1.0

_MODES = ("cartesian", "representative")


class ChorusError(Exception):
    """Fail-closed: the harness refuses to compose what it cannot justify."""


# -- The composed agent -------------------------------------------------------

@dataclass(frozen=True)
class AgentSpec:
    """One agent's full composition. Frozen: composed once, never mutated."""
    sense: str
    tongue: str
    gender: str          # "masculine" | "feminine"
    trade: int           # 0-21
    trade_name: str
    name_no: int         # 1-72
    name_title: str
    flavor: int          # 0-30
    flavor_name: str
    tuners: tuple        # five weights in SENSES order
    moon: int            # 1-13
    seed: int
    gender_override: bool = False  # True if the name came from outside its choir


@dataclass
class DeployedAgent:
    """An AgentSpec with its ledger and soul, ready to work."""
    spec: AgentSpec
    ledger: Ledger
    soul: soul_mod.Soul
    ledger_path: Path


# -- Composition ---------------------------------------------------------------

def _canon():
    """MECHANISM: load the canon once per composition; strict loaders raise."""
    flavors = grimoire.load_flavors()
    names = grimoire.load_names()
    jobs = load_jobs()
    return flavors, names, jobs


def _draw_name(names, flavor_no: int, gender: str, rng: random.Random):
    """Sortition from the flavor's choir honoring gender.

    DOCTRINE: a name is never drawn outside its flavor's choir by default.
    If the choir holds no officer of the required gender, the draw falls
    back to the full gender pool and the override is recorded -- the canon
    is not silently broken.
    """
    want = GENDER_ASSESSMENT[gender]
    choir = [n for n in names if n.flavor == flavor_no and n.gender == want]
    override = False
    if not choir:
        choir = [n for n in names if n.gender == want]
        override = True
        if not choir:
            raise ChorusError(f"no {gender} officers in the canon at all")
    return rng.choice(choir), override


def compose_matrix(prompt: str, *, mode: str = "representative",
                   tongues: tuple = DEFAULT_TONGUES,
                   seed: int = 0) -> list[AgentSpec]:
    """Compose the agent matrix for one prompt.

    MECHANISM: cartesian = 5 x L x 2 AgentSpecs; representative = 5 + L + 2.
    Every draw comes from random.Random(seed): one seed, one chorus,
    reproducible bit-for-bit.
    """
    # -- fail-closed: validate before anything exists -------------------------
    if mode not in _MODES:
        raise ChorusError(f"unknown mode {mode!r}; want one of {_MODES}")
    for t in tongues:
        if t not in TONGUES:
            raise ChorusError(f"unknown tongue {t!r}; want one of {tuple(TONGUES)}")
    if not prompt or not prompt.strip():
        raise ChorusError("the chorus needs a prompt; silence is not a prompt")

    flavors, names, jobs = _canon()
    rng = random.Random(seed)
    specs: list[AgentSpec] = []

    def one_agent(sense: str, tongue: str, gender: str, salt: int) -> AgentSpec:
        # MECHANISM: per-agent rng keeps draws independent of matrix order.
        arng = random.Random(f"chorus:{seed}:{salt}")
        trade_no = arng.randrange(0, 22)
        trade_name = jobs[trade_no].get("name", f"Trade {trade_no}")
        flavor_no = arng.randrange(0, 31)
        officer, override = _draw_name(names, flavor_no, gender, arng)
        tuners = tuple(DOMINANT_WEIGHT if s == sense else OPEN_WEIGHT
                       for s in SENSES)
        moon = arng.randrange(1, 14)
        flavor_name = flavors[flavor_no].name
        return AgentSpec(
            sense=sense, tongue=tongue, gender=gender,
            trade=trade_no, trade_name=trade_name,
            name_no=officer.number, name_title=officer.name,
            flavor=flavor_no, flavor_name=flavor_name,
            tuners=tuners, moon=moon, seed=seed,
            gender_override=override,
        )

    salt = 0
    if mode == "cartesian":
        for sense in SENSES:
            for tongue in tongues:
                for gender in GENDERS:
                    specs.append(one_agent(sense, tongue, gender, salt))
                    salt += 1
    else:  # representative: five pipelines + every tongue + both genders
        for sense in SENSES:
            specs.append(one_agent(sense, tongues[0], GENDERS[0], salt)); salt += 1
        for tongue in tongues:
            specs.append(one_agent(SENSES[0], tongue, GENDERS[0], salt)); salt += 1
        for gender in GENDERS:
            specs.append(one_agent(SENSES[0], tongues[0], gender, salt)); salt += 1
    return specs


# -- Deployment -----------------------------------------------------------------

def deploy(spec: AgentSpec, ledger_dir: str | Path, index: int = 0) -> DeployedAgent:
    """Give an AgentSpec its ledger (VERBOSE) and its soul.

    DOCTRINE: the deployment entries are the ledger's first events; the
    soul is grown from the template and seeded with the officer's motto,
    the duty, and the four architectural tenets -- then it is the agent's
    to grow.
    """
    ledger_dir = Path(ledger_dir)
    ledger_dir.mkdir(parents=True, exist_ok=True)
    wid = f"chorus-{spec.seed}-{index:02d}-{spec.sense}-{spec.tongue}-{spec.gender}"
    ledger = Ledger.open(working_id=wid, ledger_dir=ledger_dir,
                         purpose=f"CHORUS working: {spec.sense}/{spec.tongue}/"
                                 f"{spec.gender} -- {spec.trade_name} / {spec.name_title}",
                         verbosity=Verbosity.VERBOSE)
    ledger.thought(
        f"Deployed: trade {spec.trade} ({spec.trade_name}), name {spec.name_no} "
        f"({spec.name_title}), flavor {spec.flavor} ({spec.flavor_name}), "
        f"tuners {dict(zip(SENSES, spec.tuners))}, moon {spec.moon}, seed {spec.seed}."
        + (" Gender drawn outside the flavor's choir -- override recorded." if spec.gender_override else ""),
        minor=False)

    s = soul_mod.Soul.from_template()
    s.name = f"{spec.trade_name} {spec.name_title}"
    s.description = (f"CHORUS agent: {spec.sense}-dominant {spec.gender} officer "
                     f"of the {spec.flavor_name}, working in {spec.tongue}.")
    # The four architectural tenets live in the soul, not just the document.
    for tenet in (
        "The persona is tuned, not worn.",
        "Data is analyzed and recorded, never judged.",
        "Judgment last, never first.",
        "No action until justified.",
    ):
        s.add_tenet(tenet)
    soul_path = ledger_dir / f"{wid}.soul.md"
    s.save_md(soul_path)
    return DeployedAgent(spec=spec, ledger=ledger, soul=s,
                         ledger_path=ledger_dir / f"{wid}.jsonl")


# -- The run ---------------------------------------------------------------------

def stub_runner(ctx: dict) -> str:
    """The deterministic stand-in: no model, no bill, fully testable.

    MECHANISM: the stub verdict clusters by sensory pipeline -- agents of
    one sense agree. This exercises the convergence analysis honestly:
    the harness must find sense-clusters, not invent agreement.
    """
    spec: AgentSpec = ctx["spec"]
    return f"stub-verdict:{spec.sense}"


def run_chorus(prompt: str, *, mode: str = "representative",
               tongues: tuple = DEFAULT_TONGUES, seed: int = 0,
               ledger_dir: str | Path = "ledger",
               runner=stub_runner) -> dict:
    """Prompt in, chorus out.

    For each AgentSpec: deploy, run the working ultra-verbose through the
    runner, record the verdict as a grounded claim, shadow-audit the
    ledger, and mark the verdict justified only if no flags stand
    unresolved. Returns the full report dict.
    """
    specs = compose_matrix(prompt, mode=mode, tongues=tongues, seed=seed)
    agents = [deploy(spec, ledger_dir, index) for index, spec in enumerate(specs)]
    verdicts: list[dict] = []

    for agent in agents:
        spec = agent.spec
        lg = agent.ledger
        lg.thought(f"Prompt received: {prompt!r}", minor=False)
        lg.thought(f"Reasoning as {spec.sense}-dominant ({SENSE_CHANNELS[spec.sense]}), "
                   f"in {spec.tongue}, as {spec.gender}.", minor=True)
        verdict = runner({"spec": spec, "prompt": prompt, "ledger": lg})
        lg.claim(f"Verdict: {verdict}",
                 f"sense={spec.sense} tongue={spec.tongue} gender={spec.gender} "
                 f"trade={spec.trade_name} name={spec.name_title} "
                 f"flavor={spec.flavor_name} seed={spec.seed}")
        # -- the shadow loop ---------------------------------------------------
        report = shadow.run_audit(lg.events())
        shadow.apply_report(lg, report)
        flags = shadow.unresolved(lg)
        justified = not flags
        if not justified:
            lg.observation(f"Verdict marked UNJUSTIFIED: {len(flags)} unresolved "
                           f"shadow flag(s) -- record-only mode.", minor=False)
        lg.close(f"CHORUS working complete; verdict justified={justified}.")
        verdicts.append({
            "sense": spec.sense, "tongue": spec.tongue, "gender": spec.gender,
            "verdict": verdict, "justified": justified,
            "unresolved_flags": len(flags),
            "ledger": str(agent.ledger_path),
        })

    return {
        "prompt": prompt, "mode": mode, "seed": seed,
        "tongues": list(tongues), "n_agents": len(agents),
        "verdicts": verdicts,
    }


# -- Key-term extraction ----------------------------------------------------------

_STOPWORDS = frozenset(
    "the a an of to in on for with and or is are was were be been it its "
    "this that these those as at by from into over after before about "
    "will would should could shall may might must can do does did have "
    "has had not no yes if then than so such only also just".split())


def extract_key_terms(text: str, limit: int = 12) -> list[str]:
    """The deliberately simple extractor: lowercase words, len>=4, no
    stopwords, deduped in order, capped. The red pen may sharpen it."""
    words = re.findall(r"[a-zA-Z']+", text.lower())
    seen: list[str] = []
    for w in words:
        w = w.strip("'")
        if len(w) >= 4 and w not in _STOPWORDS and w not in seen:
            seen.append(w)
        if len(seen) >= limit:
            break
    return seen


# -- The Pontifex pipeline ----------------------------------------------------------

def _pontifex_engine():
    """MECHANISM: lazy import; missing Pontifex is a loud ChorusError,
    never a silent skip or a faked weighing."""
    ws = Path.home() / "workspace" / "pontifex"
    if str(ws) not in sys.path and (ws / "pontifex").exists():
        sys.path.insert(0, str(ws))
    try:
        from pontifex import engine  # noqa
    except ImportError as e:
        raise ChorusError(
            "Pontifex is unavailable: the pipeline cannot weigh without it. "
            f"({e})") from e
    return engine


def weigh_terms(terms: list[str], tongue: str) -> list[dict]:
    """Weigh key terms in the agent's tongue. Provenance on every row.

    DOCTRINE: a term with no letters in the tongue's script is SKIPPED
    with the reason recorded -- a zero would be a lie wearing a number's
    clothes. Hebrew gets the engine's documented latin->hebrew fallback
    (transliteration, mergers reported). Japanese travels the same
    fallback path but stays marked CONSTRUCTED-pending -- the research
    track (CHORUS.md §VI), never presented as a table that does not exist.
    """
    if tongue not in TONGUES:
        raise ChorusError(f"unknown tongue {tongue!r}")
    system, provenance = TONGUES[tongue]
    engine = _pontifex_engine()
    rows = []
    for term in terms:
        if tongue == "hebrew" or tongue == "japanese":
            # MECHANISM: the fallback doctrine -- transliterate to Hebrew,
            # mergers reported, tier marked honestly.
            hebrew_word, mergers = engine.transliterate_latin_to_hebrew(term)
            weighed = engine.weigh(hebrew_word, "hebrew")
            rows.append({"term": term, "tongue": tongue,
                         "system": "hebrew-fallback",
                         "value": weighed["value"], "mergers": mergers,
                         "provenance": ("CONSTRUCTED-pending -- research track"
                                        if tongue == "japanese"
                                        else "ATTESTED table / CONSTRUCTED rendering")})
        else:
            weighed = engine.weigh(term, system)
            if not weighed["breakdown"]:
                # Honest skip: nothing weighable, and we say so.
                rows.append({"term": term, "tongue": tongue, "system": system,
                             "value": None,
                             "skipped": f"no {system} letters in term",
                             "provenance": provenance})
            else:
                rows.append({"term": term, "tongue": tongue, "system": system,
                             "value": weighed["value"],
                             "provenance": provenance})
    return rows


def bridge_map(weighings: list[dict]) -> list[dict]:
    """Group weighed terms by value across tongues: the candidate bridges.

    DOCTRINE: a convergence on attested tables is a candidate bridge; a
    convergence touching the constructed tier is a hypothesis for the red
    pen. The map reports; it does not declare -- declaration is the
    author's, after the canonization chain.
    """
    by_value: dict[int, list[dict]] = {}
    for row in weighings:
        if row.get("value") is None:
            continue  # skipped terms are honest gaps, not bridges
        by_value.setdefault(row["value"], []).append(row)
    bridges = []
    for value in sorted(by_value):
        rows = by_value[value]
        tongues = {r["tongue"] for r in rows}
        if len(tongues) >= 2:  # a bridge needs at least two banks
            tiers = {r["provenance"] for r in rows}
            standing = ("hypothesis -- constructed tier touched"
                        if any("CONSTRUCTED" in t for t in tiers)
                        else "candidate bridge -- attested tables")
            bridges.append({"value": value,
                            "terms": sorted({r["term"] for r in rows}),
                            "tongues": sorted(tongues),
                            "standing": standing})
    return bridges


# -- The balance-finder ---------------------------------------------------------------

def find_balance(report: dict) -> dict:
    """Read where the matrix converges: the honest, justified judgment.

    MECHANISM: only justified verdicts (no unresolved shadow flags) count.
    Verdicts cluster by text; the largest grounded cluster is the balance
    point. A lone grounded verdict is not outvoted -- it is heard, with
    its grounds on the record.
    DOCTRINE: the finder measures convergence; it does not vote. Voting
    is politics.
    """
    justified = [v for v in report["verdicts"] if v["justified"]]
    clusters: dict[str, list[dict]] = {}
    for v in justified:
        clusters.setdefault(v["verdict"], []).append(v)
    ranked = sorted(clusters.items(), key=lambda kv: -len(kv[1]))
    return {
        "n_agents": report["n_agents"],
        "n_justified": len(justified),
        "n_unjustified": report["n_agents"] - len(justified),
        "clusters": [{"verdict": verdict, "n": len(vs),
                      "senses": sorted({v["sense"] for v in vs}),
                      "tongues": sorted({v["tongue"] for v in vs}),
                      "genders": sorted({v["gender"] for v in vs})}
                     for verdict, vs in ranked],
        "balance": ranked[0][0] if ranked else None,
        "lone_voices": [verdict for verdict, vs in ranked[1:] if len(vs) == 1],
    }
