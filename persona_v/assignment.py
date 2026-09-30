# ☉ in 3° 54′ Libra  ☽ in 7° 35′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
assignment -- the Assignment engine (PART V of the grimoire, the hinge).

    "The lot is cast into the lap; but the whole disposing thereof is
    of the LORD." -- Proverbs 16:33

Hypothesis
----------
Given a task, the right flavor, officers, function, and layer can be
elected by fit -- and the election can be audited down to the last
point.

Method
------
The contract plus a working default. AssignmentEngine is the
abstract contract: any engine -- the author's true Jungian
Personality Assignment system, a future learned model, anything --
subclasses it and implements assign(); the rest of PERSONA V speaks
only to this contract, so engines are interchangeable.
AptitudeAssignmentEngine ("aptitude-v1") is the shipped default, and
assigns the way aptitude tests do: the task is probed for demands on
sixteen dimensions (eight cognitive functions, five Jungian layers,
three operational axes) -- or the caller supplies an explicit demand
vector, used verbatim -- and classified into one of the 22 Trades of
the Taro, each with a fixed charter (its demand vector). The
charter, being doctrine rather than guesswork, is what the election
runs on. Every flavor holds an aptitude profile on the same
dimensions (data/aptitudes.yaml); the best fit presides as Master,
the most apt function and layer lead, and officers are cast by
sortition (seedable lots) from the winner's choir with conflicting
pairs excluded. The runner-up is assigned as Apprentice -- the
second chair, junior by definition: the Master's anima/animus, the
inner contrarian that cross-examines every major output, while the
Master corrects the Apprentice in turn. Both are recorded in the
Speculum on the same ledger, so mutual oversight is on the record.
The full scorecard lands in the rationale, so every election is
auditable.

Observation
-----------
An Assignment: flavor number, cognitive function, leading layer,
invoked name numbers, the demand vector, top flavor scores, a
rationale naming the evidence, the engine's name, and a Thelemic
stamp. If a ledger is given, the assignment is recorded as a claim
with grounds -- the grounds being the engine's rationale. An
assignment the system cannot explain is an assignment it should not
trust (Alethic Axis).

Result
------
Deterministic: ties break by breadth of fit, then lowest flavor
number; seeded lots reproduce exactly. The aptitude profiles and
trade charters are drafts awaiting the author's red pen; until he
ratifies them the engine is honestly labeled a stand-in, not his
system.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from zoneinfo import ZoneInfo

from . import grimoire, thelemic
from .speculum import Ledger

# Conflicting offices: pairs of names whose duties oppose each other in
# the grimoire's own words. Invoking both in one working is incoherent --
# the engine refuses the pairing, the way a commander refuses
# contradictory orders. Derived from the offices' direct verbal
# opposition (bind/sever, keep/break), not invented: these are the
# author's own titles set against each other.
#
# * 20 Binder of Alignments vs 21 Severer of False Unions (flavor 6)
# * 41 Warden of the Chain vs 42 Breaker of Chains (flavor 15)
#
# Survey 2026-09-26, under the author's leave: all 31 choirs were read
# for intra-choir contradiction, and the cross-choir candidates were
# weighed. The table is COMPLETE at two pairs, by this bar: a conflict
# is a direct verbal opposition of commanded acts within one chair --
# "bind" against "sever", "name the chain" against "break the chain".
# Productive tension is not contradiction, and the system is built to
# hold it: Rehael (39) mixes opposites as an art, Atum's choir (55/56)
# holds being and becoming together, Set's choir (69/70) wields the
# storm it honors. The rejected candidates -- 7 sealed counsel vs 49
# suffer-no-corner, 12 refuge vs 37 pruning, 30 patience vs 67
# swiftness, 55 never-made vs 56 always-making -- are tensions the
# working is meant to sustain, or oppositions that never share a choir
# (the draw pool is one flavor's apportioned names, so a cross-choir
# pair could never fire and would be a dead rule implying false
# coverage). Cross-chair opposition between Master and Apprentice is
# likewise not refused: the Apprentice is the contrarian by design, and
# demanding clarity where the Master seals counsel is the pair working.
# A future opposition enters here only if it meets the bar above.
CONFLICTS: frozenset = frozenset({
    frozenset({20, 21}),
    frozenset({41, 42}),
})


def _has_conflict(drawn) -> frozenset | None:
    """The conflicting pair present in ``drawn``, or None."""
    s = set(drawn)
    for pair in CONFLICTS:
        if pair <= s:
            return pair
    return None


def _draw_officers(pool: list[int], n: int,
                   rng: random.Random) -> tuple[int, ...]:
    """Cast the lots: draw ``n`` officers from ``pool``, sanely.

    * Sampling is *without replacement* -- no officer invoked twice.
    * Every draw is checked against CONFLICTS; a conflicted draw is
      rejected and recast (bounded attempts).
    * If the conflict is unavoidable -- the pool itself is a conflict
      pair, as flavor 15's choir {41, 42} is -- one member is dropped
      at random rather than invoking a contradiction.
    * ``n`` larger than the pool is clamped, never an error.
    * The result is sorted: randomness decides *which* officers, not
      their order on the record.
    """
    pool = list(pool)
    n = min(n, len(pool))
    drawn = None
    for _ in range(64):
        drawn = rng.sample(pool, n)
        if _has_conflict(drawn) is None:
            return tuple(sorted(drawn))
    # Unavoidable conflict: drop one member of the pair at random.
    assert drawn is not None
    pair = _has_conflict(drawn)
    if pair is not None:
        drop = rng.choice(sorted(pair))
        drawn = [x for x in drawn if x != drop]
    return tuple(sorted(drawn))


# ------------------------------------------------------------------
# The aptitude test: sixteen dimensions, one battery, one election.
# ------------------------------------------------------------------
# Every flavor is rated 0-2 on each dimension (data/aptitudes.yaml --
# DRAFT profiles, awaiting the author's red pen). Every task is probed
# for demands on the same dimensions (PROBES below, or an explicit
# demand vector supplied by the caller). The election is
# sum(demand[d] * aptitude[d]) per flavor; the best fit presides.

#: The eightfold lens.
FUNCTIONS = ("Te", "Ti", "Fe", "Fi", "Ne", "Ni", "Se", "Si")
#: The Jungian core.
LAYERS = ("persona", "ego", "shadow", "anima", "self")
#: How the work goes.
OPERATIONAL = ("precision", "swiftness", "gravity")
#: All sixteen, in canonical order.
DIMENSIONS = FUNCTIONS + LAYERS + OPERATIONAL

# Probe stems: the test battery administered to the task text. The task
# is lowercased; each stem found counts once per dimension; two or more
# hits cap the demand at 2. These are *operational* cues, not poetry:
# "audit" probes Ti because auditing is systematic examination.
PROBES: dict[str, tuple[str, ...]] = {
    "Te": ("organiz", "execut", "order", "plan", "manag", "direct",
           "deploy", "coordinat", "orchestrat", "implement", "schedul",
           "priorit"),
    "Ti": ("analyz", "analy", "debug", "diagnos", "model", "logic",
           "reason", "dissect", "investig", "theor", "deduc", "prov",
           "audit", "remed", "repair"),
    "Fe": ("harmon", "counsel", "persuad", "comfort", "negotiat", "team",
           "people", "communi", "empath", "mediat", "collabor"),
    "Fi": ("valu", "integrit", "ethic", "authent", "conscien", "principl",
           "moral", "sincer", "belief"),
    "Ne": ("brainstorm", "idea", "possib", "creat", "invent", "explor",
           "alternat", "imagin", "innovat"),
    "Ni": ("forese", "predict", "pattern", "insight", "distill",
           "synthes", "vision", "strateg", "anticip", "forecast"),
    "Se": ("perform", "present", "demo", "concret", "engag",
           "hands-on", "act now"),
    "Si": ("record", "histor", "rememb", "archiv", "retain", "document",
           "log", "verif", "check", "review", "referen"),
    "persona": ("present", "repres", "interfac", "appear", "speak",
                "announc", "publish"),
    "ego": ("decid", "decis", "commit", "will", "enforc", "lead",
            "drive", "push", "ship", "choos"),
    "shadow": ("fail", "wrong", "bias", "flaw", "blind", "confront",
               "advers", "critic", "risk", "decept", "habit", "chain",
               "bondage", "compul", "addict", "repea", "loop"),
    "anima": ("dream", "meaning", "recept", "listen", "feel", "intuit",
              "soul", "inward", "reflect"),
    "self": ("integrat", "whole", "balanc", "heal", "reconcil",
             "complet", "unif", "align"),
    "precision": ("precis", "exact", "careful", "rigor", "meticul",
                  "thorou", "accura", "detail", "correct"),
    "swiftness": ("quick", "fast", "urgent", "rapid", "soon", "asap",
                  "deadline"),
    "gravity": ("critic", "irrevers", "consequen", "final", "bind",
                "perman", "secur", "high-stakes", "importan"),
}

_APTITUDES: dict[int, dict[str, int]] | None = None


def load_aptitudes() -> dict[int, dict[str, int]]:
    """Flavor number -> {dimension: 0-2}. Cached; read from the YAML
    the author is asked to correct."""
    global _APTITUDES
    if _APTITUDES is None:
        import yaml
        from pathlib import Path
        raw = yaml.safe_load(
            Path(__file__).with_name("data").joinpath(
                "aptitudes.yaml").read_text())
        want = set(DIMENSIONS)
        table: dict[int, dict[str, int]] = {}
        for num, entry in raw["profiles"].items():
            apt = entry.get("aptitudes") or {}
            unknown = set(apt) - want
            if unknown:
                raise ValueError(
                    f"aptitudes.yaml flavor {num}: unknown dimensions "
                    f"{sorted(unknown)}")
            for dim, val in apt.items():
                if val not in (0, 1, 2):
                    raise ValueError(
                        f"aptitudes.yaml flavor {num}/{dim}: "
                        f"rating {val!r} not in 0-2")
            table[int(num)] = {d: int(apt.get(d, 0)) for d in DIMENSIONS}
        _APTITUDES = table
    return _APTITUDES


def probe_demands(task: str) -> dict[str, int]:
    """Administer the battery: task text -> {dimension: 0-2}.

    Each probe stem found counts once per dimension; two or more hits
    cap at 2. A task no probe catches yields all zeros -- and an all
    zero demand vector elects flavor 0 by the tie-break, so the Fool
    default falls out of the mechanism instead of being special-cased.
    """
    lowered = task.lower()
    demands: dict[str, int] = {}
    for dim in DIMENSIONS:
        hits = sum(1 for stem in PROBES[dim] if stem in lowered)
        demands[dim] = min(2, hits)
    return demands


def validate_demands(demands: dict) -> dict[str, int]:
    """Check an explicit demand vector hard. Unknown dimensions or
    values outside 0-2 are refused -- a malformed spec must never
    silently elect."""
    if not isinstance(demands, dict):
        raise ValueError("demands must be a mapping of dimension to 0-2")
    want = set(DIMENSIONS)
    unknown = set(demands) - want
    if unknown:
        raise ValueError(f"unknown demand dimensions: {sorted(unknown)}; "
                         f"valid: {list(DIMENSIONS)}")
    clean: dict[str, int] = {}
    for dim in DIMENSIONS:
        val = demands.get(dim, 0)
        if isinstance(val, bool) or not isinstance(val, int) \
                or val not in (0, 1, 2):
            raise ValueError(f"demand {dim!r}: {val!r} not in 0-2")
        clean[dim] = val
    return clean


_JOBS: dict[int, dict] | None = None


def load_jobs() -> dict[int, dict]:
    """Trade number -> {"trade", "patron", "charter", "note"}. Cached;
    read from the YAML the author is asked to correct."""
    global _JOBS
    if _JOBS is None:
        import yaml
        from pathlib import Path
        raw = yaml.safe_load(
            Path(__file__).with_name("data").joinpath(
                "jobs.yaml").read_text())
        want = set(DIMENSIONS)
        table: dict[int, dict] = {}
        for num, entry in raw["jobs"].items():
            charter = entry.get("charter") or {}
            unknown = set(charter) - want
            if unknown:
                raise ValueError(
                    f"jobs.yaml trade {num}: unknown dimensions "
                    f"{sorted(unknown)}")
            for dim, val in charter.items():
                if val not in (0, 1, 2):
                    raise ValueError(
                        f"jobs.yaml trade {num}/{dim}: "
                        f"rating {val!r} not in 0-2")
            table[int(num)] = {
                "trade": entry["trade"],
                "patron": int(entry["patron"]),
                "note": entry.get("note", ""),
                "charter": {d: int(charter.get(d, 0)) for d in DIMENSIONS},
            }
        _JOBS = table
    return _JOBS


def job_by_name(name: str) -> int | None:
    """Trade name (case-insensitive) -> trade number, or None."""
    wanted = name.strip().lower()
    for num, job in load_jobs().items():
        if job["trade"].lower() == wanted:
            return num
    return None


def resolve_job(job: str | int) -> int:
    """A trade number 0-21 or a trade name -> the trade number.
    Anything else is refused: a misnamed trade must not silently
    elect."""
    if isinstance(job, bool):
        raise ValueError(f"unknown trade: {job!r}")
    if isinstance(job, int):
        if job in load_jobs():
            return job
        raise ValueError(f"unknown trade number: {job!r} (trades are 0-21)")
    if isinstance(job, str):
        num = job_by_name(job)
        if num is not None:
            return num
        raise ValueError(
            f"unknown trade: {job!r}; valid: "
            + ", ".join(j["trade"] for j in load_jobs().values()))
    raise ValueError(f"unknown trade: {job!r}")


def classify_job(demands: dict[str, int],
                 jobs: dict[int, dict] | None = None
                 ) -> tuple[int | None, dict[int, int]]:
    """Which trade does this demand vector belong to? The same
    sum(demand * charter) matching, over charters instead of flavors.
    Returns (trade number or None, scores). No fit at all (every score
    zero) returns None -- the caller falls back to the probed demands.
    Ties break to the lowest trade number, deterministically."""
    jobs = load_jobs() if jobs is None else jobs
    scores = {num: sum(demands[d] * job["charter"][d] for d in DIMENSIONS)
              for num, job in jobs.items()}
    best = max(scores.values())
    if best == 0:
        return None, scores
    winner = min(num for num, s in scores.items() if s == best)
    return winner, scores


def _elect(demands: dict[str, int],
           profiles: dict[int, dict[str, int]]
           ) -> tuple[int, dict[int, int], dict[int, int]]:
    """Score every flavor: sum(demand * aptitude).

    Returns (winner, scores, coverage). Ties break by *breadth of
    fit* -- how many demanded dimensions the flavor is actually apt
    in -- then by lowest flavor number. Deterministic, and the
    runner-up stays visible for the rationale.
    """
    scores: dict[int, int] = {}
    coverage: dict[int, int] = {}
    for num in sorted(profiles):
        apt = profiles[num]
        scores[num] = sum(demands[d] * apt[d] for d in DIMENSIONS)
        coverage[num] = sum(1 for d in DIMENSIONS
                            if demands[d] > 0 and apt[d] > 0)
    winner = max(sorted(scores),
                 key=lambda f: (scores[f], coverage[f], -f))
    return winner, scores, coverage


def _elect_function(demands: dict[str, int],
                    apt: dict[str, int]) -> str:
    """The lens the winning flavor sees through: native strength,
    boosted by demand. ``aptitude * (1 + demand)`` so an undemanded
    task still gets the flavor's best function."""
    return max(FUNCTIONS,
               key=lambda fn: (apt[fn] * (1 + demands[fn]),
                               FUNCTIONS.index(fn) * -1))


def _elect_layer(demands: dict[str, int], apt: dict[str, int]) -> str:
    """Which of the five leads the working. Same rule as function."""
    return max(LAYERS,
               key=lambda ly: (apt[ly] * (1 + demands[ly]),
                               LAYERS.index(ly) * -1))



@dataclass(frozen=True)
class Assignment:
    """The engine's answer: which flavor, which officers, and why.

    ``function`` is the elected cognitive function (one of the eight);
    ``layer`` the leading Jungian layer. ``demands`` is the demand
    vector the election ran on; ``scores`` the top flavor scores;
    ``margin`` how far the winner beat the runner-up. ``rationale``
    names the evidence (never "because I said so"). ``engine`` names
    the engine that produced it, so the ledger shows whether the
    author's true system or the stand-in spoke.

    Every assignment carries a **pair**: the elected flavor presides
    as Master; the runner-up serves as ``apprentice`` -- the second
    chair, with its own elected ``apprentice_function`` /
    ``apprentice_layer`` and its own ``apprentice_names`` drawn by
    sortition from the apprentice's choir. The apprentice is the
    master's anima/animus (the cross-examiner); the master corrects
    the apprentice in turn; both are recorded, so oversight is mutual
    and on the record.
    """

    flavor: int
    names: tuple
    rationale: str
    engine: str
    stamp: str
    function: str = ""
    layer: str = ""
    demands: dict | None = None
    scores: dict | None = None
    margin: int = 0
    job: str | None = None
    apprentice: int = -1
    apprentice_function: str = ""
    apprentice_layer: str = ""
    apprentice_names: tuple = ()

    def describe(self, flavors: dict | None = None,
                 proficiency=None) -> str:
        """Human-readable rendering of the assignment.

        ``proficiency`` is an optional ``ProficiencyLedger``: when the
        elected Apprentice is a master of the record, the rendering
        says so -- emeritus in the second chair, the cross-examination
        of a master by a master. The election is never altered; only
        the rendering knows.
        """
        fname = ""
        if flavors is not None and self.flavor in flavors:
            fname = f" ({flavors[self.flavor].name})"
        lines = [f"[{self.engine}] Flavor {self.flavor}{fname} (Master), "
                 f"function {self.function}, layer {self.layer}, "
                 f"officers {list(self.names)}."]
        if self.apprentice >= 0:
            aname = ""
            if flavors is not None and self.apprentice in flavors:
                aname = f" ({flavors[self.apprentice].name})"
            chair = (f"Apprentice {self.apprentice}{aname}, function "
                     f"{self.apprentice_function}, layer "
                     f"{self.apprentice_layer}, officers "
                     f"{list(self.apprentice_names)} -- the second chair; "
                     f"it cross-examines the Master, the Master corrects it.")
            if proficiency is not None and \
                    proficiency.is_master(self.apprentice):
                chair += (" It is itself a Master of the record -- "
                          "emeritus in the second chair, the "
                          "cross-examination of a master by a master.")
            lines.append(chair)
        if self.job:
            lines.append(f"Trade: {self.job}.")
        if self.demands:
            top = ", ".join(f"{d}:{v}" for d, v in self.demands.items()
                            if v > 0) or "none -- the Fool by default"
            lines.append(f"Demands: {top}.")
        if self.scores:
            board = ", ".join(f"{f}={s}"
                              for f, s in list(self.scores.items())[:5])
            lines.append(f"Scores: {board} (margin {self.margin}).")
        lines.append(f"Rationale: {self.rationale}")
        lines.append(self.stamp)
        return "\n".join(lines)


class AssignmentEngine(ABC):
    """
    The contract every Assignment engine honors.
    
    Hypothesis: engines are interchangeable if the contract is strict.
    Method: subclass this and implement assign(). Observation: the
    author's true Jungian Personality Assignment system enters PERSONA
    V here -- as a subclass, its internal rules intact, its reasoning
    its own. Result: the rest of the system speaks only to this
    contract.
    """

    #: Human-readable name recorded on every Assignment this engine makes.
    name: str = "abstract"

    @abstractmethod
    def assign(self, task: str, ledger: Ledger | None = None, *,
               demands: dict | None = None,
               job: str | int | None = None,
               seed: int | None = None,
               n_officers: int | None = None) -> Assignment:
        """
        Elect the Master and Apprentice for a task.
        
        Hypothesis: one method signature can carry every engine's judgment.
        Method: take the task (and optional explicit demands, seed, officer
        count); return an Assignment whose flavor is 0-30 and whose names
        are 1-72. Observation: the election, with rationale. Result: engines
        differ inside, agree at the boundary -- the contract holds.
        """
        raise NotImplementedError


class AptitudeAssignmentEngine(AssignmentEngine):
    """
    The working default: aptitude-test assignment over the 31 flavors.
    
    Hypothesis: fit can be measured as sum(demand x aptitude). Method:
    probe the task for demands on sixteen dimensions (or take the
    caller's explicit vector verbatim); score every flavor's aptitude
    profile (data/aptitudes.yaml, DRAFT until the author corrects it);
    best fit presides as Master, runner-up serves as Apprentice;
    officers by seeded sortition, conflicts excluded. Observation: an
    Assignment with the full scorecard in the rationale. Result:
    deterministic and auditable -- ties by breadth of fit, then lowest
    flavor; seeded lots reproduce exactly.
    """

    name = "aptitude-v1"

    def __init__(self, seed: int | None = None, n_officers: int = 2,
                 demands: dict | None = None, job: str | int | None = None):
        if n_officers < 1:
            raise ValueError("n_officers must be >= 1")
        self.seed = seed
        self.n_officers = n_officers
        self.demands = (validate_demands(demands)
                        if demands is not None else None)
        self.job = resolve_job(job) if job is not None else None
        self._flavors = {f.number: f for f in grimoire.load_flavors()}
        self._profiles = load_aptitudes()
        self._jobs = load_jobs()

    def _demand_vector(self, task: str, demands: dict | None,
                       job: str | int | None) -> tuple[dict, str, str | None]:
        """The precedence chain, highest first:

        1. explicit ``demands`` (per call, then engine default) -- the
           caller's word is law, used verbatim;
        2. explicit ``job`` (per call, then engine default) -- the named
           trade's charter;
        3. classified job -- the trade best fitting the probed demands,
           whose charter (doctrine) replaces the rough probed vector;
        4. probed demands -- when no trade fits at all.

        Returns (vector, source description, trade name or None).
        """
        use_demands = (validate_demands(demands) if demands is not None
                       else self.demands)
        if use_demands is not None:
            src = ("structured (engine default)" if demands is None
                   else "structured")
            return use_demands, src, None
        use_job = resolve_job(job) if job is not None else self.job
        if use_job is not None:
            trade = self._jobs[use_job]["trade"]
            return (self._jobs[use_job]["charter"],
                    f"charter of {trade} (named)", trade)
        probed = probe_demands(task)
        job_no, _ = classify_job(probed, self._jobs)
        if job_no is None:
            return probed, "probed (no trade fit)", None
        trade = self._jobs[job_no]["trade"]
        rough = ", ".join(f"{d}:{probed[d]}" for d in DIMENSIONS
                          if probed[d] > 0)
        return (self._jobs[job_no]["charter"],
                f"charter of {trade} (classified from probed "
                f"demands {rough or 'none'})", trade)

    def assign(self, task: str, ledger: Ledger | None = None, *,
               demands: dict | None = None,
               job: str | int | None = None,
               seed: int | None = None,
               n_officers: int | None = None) -> Assignment:
        if not task or not task.strip():
            raise ValueError("assign() requires a task description")
        n = self.n_officers if n_officers is None else n_officers
        if n < 1:
            raise ValueError("n_officers must be >= 1")
        # The test battery: demands obeyed, job chartered, or classified.
        use_demands, source, trade = self._demand_vector(task, demands, job)
        winner, scores, coverage = _elect(use_demands, self._profiles)
        flavor = self._flavors[winner]
        function = _elect_function(use_demands, self._profiles[winner])
        layer = _elect_layer(use_demands, self._profiles[winner])
        # Runner-up and margin for the scorecard. The runner-up is not
        # discarded: it is assigned as Apprentice -- the second chair,
        # junior by definition, serving as the Master's anima/animus
        # (the inner contrarian that cross-examines every major
        # output) while the Master corrects it in turn.
        ranked = sorted(scores, key=lambda f: (scores[f], coverage[f], -f),
                        reverse=True)
        runner_up = ranked[1] if len(ranked) > 1 else winner
        margin = scores[winner] - scores[runner_up]
        top_scores = {f: scores[f] for f in ranked[:5]}
        apprentice_function = _elect_function(use_demands,
                                              self._profiles[runner_up])
        apprentice_layer = _elect_layer(use_demands,
                                        self._profiles[runner_up])
        # Sortition: cast lots among the flavor's apportioned choir.
        pool = [ref["number"] for ref in flavor.names]
        use_seed = self.seed if seed is None else seed
        rng = random.Random(use_seed)
        names = _draw_officers(pool, n, rng)
        # The apprentice's lots are a separate, deterministic draw: the
        # master's cast is bit-identical to a master-only election, so
        # seniority is never perturbed by the junior's presence.
        apprentice_pool = [ref["number"]
                           for ref in self._flavors[runner_up].names]
        apprentice_seed = None if use_seed is None else use_seed + 1
        apprentice_names = _draw_officers(
            apprentice_pool, n, random.Random(apprentice_seed))
        top_demands = ", ".join(f"{d}:{v}" for d in DIMENSIONS
                                if (v := use_demands[d]) > 0)
        if not top_demands:
            top_demands = ("none detected -- the lots default to the Fool "
                           "(flavor 0)")
        rationale = (
            f"demands ({source}): {top_demands}; "
            f"flavor {winner} ({flavor.name}) scored {scores[winner]}, "
            f"runner-up {runner_up} "
            f"({self._flavors[runner_up].name}) {scores[runner_up]}, "
            f"margin {margin}; function {function}, layer {layer}; "
            f"sortition drew {list(names)} from the choir of {len(pool)} "
            f"(seed={use_seed!r}); apprentice {runner_up} "
            f"({self._flavors[runner_up].name}), function "
            f"{apprentice_function}, layer {apprentice_layer}, drew "
            f"{list(apprentice_names)} from its choir of "
            f"{len(apprentice_pool)} (seed={apprentice_seed!r}) -- the "
            f"second chair: it cross-examines the master, the master "
            f"corrects it, both on the record")
        stamp = thelemic.thelemic_moment(
            datetime.now(ZoneInfo("America/New_York"))).stamp
        assignment = Assignment(flavor=winner, names=names,
                                rationale=rationale, engine=self.name,
                                stamp=stamp, function=function, layer=layer,
                                demands=use_demands, scores=top_scores,
                                margin=margin, job=trade,
                                apprentice=runner_up,
                                apprentice_function=apprentice_function,
                                apprentice_layer=apprentice_layer,
                                apprentice_names=apprentice_names)
        if ledger is not None:
            officers = ", ".join(str(x) for x in names)
            apprentice_officers = ", ".join(str(x)
                                            for x in apprentice_names)
            job_note = f", trade {trade}" if trade else ""
            ledger.claim(
                f"Assigned flavor {winner} ({flavor.name}), function "
                f"{function}, layer {layer}{job_note}, officers "
                f"[{officers}]; apprentice {runner_up} "
                f"({self._flavors[runner_up].name}), function "
                f"{apprentice_function}, layer {apprentice_layer}, "
                f"officers [{apprentice_officers}] -- mutual oversight "
                f"on the record.",
                grounds=f"{self.name}: {rationale}",
                flavor=winner, names=names)
        return assignment


#: Backward-compatible alias: the old class name still resolves.
HeuristicAssignmentEngine = AptitudeAssignmentEngine
