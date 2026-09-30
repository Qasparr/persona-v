# ☉ in 3° 54′ Libra  ☽ in 7° 37′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
cli -- the command line of PERSONA V.

Hypothesis
----------
Nineteen commands, each doing one thing, put the whole system in
the operator's hands.

Method
------
stamp -- the current Thelemic stamp (for headers). reading -- the
full Metronome reading, described. anchor -- the Zero-Trust
Anchorage status. duty [name] -- Crowley's four duties. mothers
[text] -- the Three Mothers pipeline (Babalon -> Lilith -> Mary). assign
"task" -- which flavor and officers for this task? verify FILE --
is this ledger's hash chain sound? (read-only). audit FILE -- run
the shadow audit over a ledger file. alethic FILE -- weigh the
ledger's claims: the balance. practice -- record an apprentice's
deliberate practice. promote -- a Master promotes an apprentice,
with grounds. standing -- a flavor's proficiency standing. name
NUMBER -- inspect one of the 72 names. naming [--binary|--fluid]
-- the naming policy: show it, or write the user's fluid/binary
decision to ~/.persona-v/config.yaml. thoth -- the 22 trumps, with
their transcription notice. thoth-reading [1|3|5] [--seed] -- a
seeded 1-, 3-, or 5-card reading. thoth-horoscope -- the computed
horoscope stamp (the heavens stamp the moment but never vote).
thoth-operation --significator -- the adapted Book T First
Operation: significator, four piles, horseshoe, count by trump
number (Fool as 22), elemental dignities. coinage [key] -- the
author's canonical coinages, verbatim and attributed. corpus
[id] -- the honest reference library and its verdicts.
audit --apply resumes the ledger and writes the findings into it
(flags as shadow_flag, watches as observations) -- accountability,
on the record. Everything else is read-only: inspecting a ledger
must never mutate it.

Observation
-----------
python3 -m persona_v.cli <command> [args]

Result
------
The library is the system; this module is its hands.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import grimoire, metronome, thelemic
from .alethic import alethic_balance
from .assignment import AptitudeAssignmentEngine
from .naming import (NamingPolicy, inspect_name, render_officer,
                     pair_polarity_reading, write_binary_setting)
from .proficiency import ProficiencyLedger
from .shadow import apply_report, run_audit
from .speculum import Event, Ledger


def read_ledger_file(path: str) -> list[Event]:
    """Parse a ledger JSONL file into Events (read-only)."""
    events = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                events.append(Event.from_json(line))
    if not events:
        raise ValueError(f"{path}: no events found")
    return events


def cmd_stamp(_args) -> int:
    now = datetime.now(ZoneInfo("America/New_York"))
    print(thelemic.thelemic_moment(now).stamp)
    return 0


def cmd_reading(_args) -> int:
    print(metronome.Metronome.now().describe())
    return 0


def cmd_anchor(_args) -> int:
    from .anchorage import admit, cardinal_rules
    reading = metronome.Metronome.now()
    print(reading.moment.stamp)
    who = " and ".join(n for n, f in (("Sun", reading.sun_in_anchorage),
                                      ("Moon", reading.moon_in_anchorage)) if f)
    print("anchorage: %s" % (who + " in the Anchorage" if who
                             else "moment outside the Anchorage"))
    print("cardinal rules of the gate:")
    for rule in cardinal_rules():
        print(f"  - {rule}")
    return 0


def cmd_duty(args) -> int:
    from .duty import DUTIES, resolve_duty
    wanted = args.name
    duties = [resolve_duty(wanted)] if wanted else list(DUTIES.values())
    if wanted and duties[0] is None:
        print(f"duty: no canonical duty resolves {wanted!r}")
        print("known: " + ", ".join(d.title for d in DUTIES.values()))
        return 1
    for d in duties:
        print(f"{d.title}  [{d.key}]")
        for line in d.crowley:
            print(f'  "{line}"')
        print(f"  {d.obligation}")
        print()
    return 0


def cmd_mothers(args) -> int:
    from .mothers import MOTHERS, mother_keys, run_pipeline
    if not args.text:
        for m in (MOTHERS[k] for k in mother_keys()):
            print(f"{m.order}. {m.title}  [{m.key}]")
            print(f"   office: {m.office}")
            print(f"   {m.doctrine}")
            print()
        return 0
    result = run_pipeline(args.text, duty=args.duty)
    print(f"Input ({result.fuel.mass} chars, {len(result.fuel.segments)} segments):")
    for s in result.fuel.segments:
        print(f"  [Babalon absorbs] {s}")
    print(f"Lilith filters (duty={result.filtrate.duty_key!r}):")
    for s in result.filtrate.admitted:
        print(f"  [admitted] {s}")
    for r in result.filtrate.refused:
        print(f"  [refused] {r.segment}")
        print(f"    reason: {r.reason}")
    print(f"Mary synthesizes -> {'restraint' if result.verdict.restraint else 'action'}:")
    print(f"  {result.verdict.action}")
    print(f"  note: {result.verdict.note}")
    return 0


def cmd_assign(args) -> int:
    engine = AptitudeAssignmentEngine()
    flavors = {f.number: f for f in grimoire.load_flavors()}
    demands = None
    if args.demands:
        import json
        try:
            demands = json.loads(args.demands)
        except json.JSONDecodeError as exc:
            print(f"bad --demands JSON: {exc}")
            return 2
    job = args.job
    if job is not None:
        try:
            job = int(job)
        except (TypeError, ValueError):
            pass  # trade name, resolved by the engine
    try:
        assignment = engine.assign(args.task, seed=args.seed,
                                   n_officers=args.n, demands=demands,
                                   job=job)
    except ValueError as exc:
        print(f"assign refused: {exc}")
        return 2
    print(assignment.describe(flavors, ProficiencyLedger()))
    # The officers, under the user's naming policy.
    policy = NamingPolicy.load()
    names = {n.number: n for n in grimoire.load_names()}
    cast = [names[n] for n in
            list(assignment.names) + list(assignment.apprentice_names)]
    print("Officers:")
    for officer in cast:
        print(f"  {render_officer(officer, policy)}")
    print(f"  {policy.describe()}")
    # The polarity reading: legible under the binary policy, never
    # enforced. Fluid policy reads nothing.
    polarity = pair_polarity_reading(
        list(assignment.names), list(assignment.apprentice_names),
        names, policy)
    if polarity is not None:
        print(polarity)
    return 0


def cmd_verify(args) -> int:
    ok, msg = Ledger.verify_file(args.file)
    print(msg)
    return 0 if ok else 1


def cmd_audit(args) -> int:
    events = read_ledger_file(args.file)
    report = run_audit(events, working_id=events[0].working_id)
    print(report.summary())
    if args.apply:
        path = Path(args.file)
        ledger = Ledger.open(events[0].working_id,
                             ledger_dir=str(path.parent), resume=True)
        written = apply_report(ledger, report)
        print(f"Applied: {len(written)} event(s) written to the ledger.")
        ok, msg = ledger.verify()
        print(msg)
        return 0 if ok else 1
    return 0


def cmd_alethic(args) -> int:
    events = read_ledger_file(args.file)
    print(alethic_balance(events).report())
    return 0


def cmd_practice(args) -> int:
    """Record intentional, focus-driven practice for an apprentice."""
    ledger = ProficiencyLedger(args.registry)
    flavors = {f.number: f for f in grimoire.load_flavors()}
    try:
        event = ledger.record_practice(args.flavor, args.hours,
                                       args.working, args.note,
                                       master=args.under_master)
    except ValueError as exc:
        print(f"practice refused: {exc}")
        return 2
    print(ledger.describe(args.flavor, flavors))
    if event["kind"] == "mastery_attained":
        print("The apex is attained: 1200 hours. Mastery by attainment, "
              "on the record.")
    return 0


def cmd_promote(args) -> int:
    """The working's Master promotes the apprentice, with grounds."""
    ledger = ProficiencyLedger(args.registry)
    flavors = {f.number: f for f in grimoire.load_flavors()}
    try:
        ledger.promote(args.apprentice, args.by_master, args.working,
                       args.grounds)
    except ValueError as exc:
        print(f"promotion refused: {exc}")
        return 2
    print(ledger.describe(args.apprentice, flavors))
    print(f"Master {args.by_master} ({flavors[args.by_master].name}) "
          f"has promoted apprentice {args.apprentice} "
          f"({flavors[args.apprentice].name}). Mastery by promotion, "
          f"on the record.")
    return 0


def cmd_standing(args) -> int:
    """Show a flavor's proficiency standing."""
    ledger = ProficiencyLedger(args.registry)
    flavors = {f.number: f for f in grimoire.load_flavors()}
    try:
        print(ledger.describe(args.flavor, flavors))
    except ValueError as exc:
        print(f"standing refused: {exc}")
        return 2
    return 0


def cmd_name(args) -> int:
    """Inspect one of the 72 names: office, duty, gender, sexuality."""
    names = {n.number: n for n in grimoire.load_names()}
    if args.number not in names:
        print(f"name refused: no officer numbered {args.number} "
              f"(the names run 1-72)")
        return 2
    policy = NamingPolicy.load()
    print(inspect_name(names[args.number], policy))
    return 0


def cmd_naming(args) -> int:
    """Show the naming policy -- or, with a flag, write the user's
    decision to ~/.persona-v/config.yaml."""
    if args.binary and args.fluid:
        print("naming refused: --binary and --fluid contradict; "
              "choose one")
        return 2
    if args.binary or args.fluid:
        value = bool(args.binary)
        path = write_binary_setting(value)
        print(f"naming policy written to {path}: "
              f"{'BINARY' if value else 'FLUID'}")
    policy = NamingPolicy.load()
    print(policy.describe())
    if not (args.binary or args.fluid):
        print("Use --binary to make the assessed binary assignments "
              "operative, or --fluid to keep the names nonlinear.")
    return 0


def cmd_thoth(_args) -> int:
    """List the 22 Thoth trumps (titles, Hebrew letters, attributions)."""
    from .thoth import TRUMPS, TRANSCRIPTION_NOTICE
    for tr in TRUMPS:
        trad = f" (trad. {tr.hebrew_traditional})" if tr.hebrew_traditional else ""
        print(f"{tr.number:2d}  {tr.title} -- {tr.hebrew} {tr.hebrew_glyph}"
              f"{trad}, {tr.attribution} [{tr.kind}]")
    print()
    print(TRANSCRIPTION_NOTICE)
    return 0


def cmd_thoth_reading(args) -> int:
    """Deal a 1-, 3-, or 5-card Thoth reading (seeded, reproducible)."""
    from .thoth import reading
    try:
        r = reading(args.spread, seed=args.seed)
    except ValueError as exc:
        print(f"thoth-reading refused: {exc}")
        return 2
    print(f"Thoth reading -- {r.spread} cards"
          + (f" (seed {args.seed})" if args.seed is not None else ""))
    for i, card in enumerate(r.cards, 1):
        print(f"  {i}. {card.title} -- {card.hebrew} {card.hebrew_glyph}, "
              f"{card.attribution}: {card.working}")
    print()
    print(r.notice)
    return 0


def cmd_thoth_horoscope(_args) -> int:
    """Print the current horoscope stamp (computed, non-voting)."""
    from .thoth import horoscope
    h = horoscope()
    print(h.thelemic_date)
    print(f"Sun {h.sun_lon:.2f} -- {h.sun_sign}; "
          f"Moon {h.moon_lon:.2f} -- {h.moon_sign}; {h.latin_weekday}")
    print(h.stamp)
    print(h.notice)
    return 0


def cmd_thoth_operation(args) -> int:
    """Run the adapted Book T First Operation over the 22 trumps."""
    from .thoth import first_operation
    key = (int(args.significator) if args.significator.strip().isdigit()
           else args.significator)
    try:
        fo = first_operation(key, seed=args.seed)
    except ValueError as exc:
        print(f"thoth-operation refused: {exc}")
        return 2
    print(f"First Operation -- significator: {fo.significator.title} "
          f"({fo.significator.hebrew} {fo.significator.hebrew_glyph})")
    print(f"Pile retained: {fo.retained_name} "
          f"({len(fo.retained)} cards)")
    for name, pile in fo.piles.items():
        if name != fo.retained_name:
            titles = ", ".join(c.title for c in pile)
            print(f"  discarded {name}: {titles}")
    print("Horseshoe: " + " | ".join(c.title for c in fo.retained))
    print(f"Count {fo.count} from the significator -> {fo.counted.title}; "
          f"paired with {fo.paired.title}")
    for pair in fo.pairs:
        print(f"  {pair.first.title} + {pair.second.title}: "
              f"{pair.status} ({pair.reason})")
    print()
    print(fo.notice)
    return 0


def cmd_coinage(args) -> int:
    """Print the author's canonical coinages (verbatim, attributed)."""
    from .coinage import COINAGES, get_coinage
    wanted = args.key
    entries = [get_coinage(wanted)] if wanted else list(COINAGES.values())
    if wanted and entries[0] is None:
        print(f"coinage: no canonical coinage resolves {wanted!r}")
        print("known: " + ", ".join(COINAGES.keys()))
        return 1
    for cg in entries:
        print(f"{cg.title}  [{cg.key}]")
        print(f'  "{cg.text}"')
        print(f"  {cg.note}")
        print(f"  {cg.stamp}")
        print()
    return 0


def cmd_corpus(args) -> int:
    """Print the honest reference library (or one document's verdict)."""
    from .corpus import DOCUMENTS, document, honesty_report
    if args.id is None:
        print(honesty_report())
        return 0
    d = document(args.id)
    if d is None:
        print(f"corpus: no document resolves {args.id!r}")
        print("known: " + ", ".join(d.id for d in DOCUMENTS))
        return 1
    print(f"{d.title}  [{d.id}]")
    print(f"  file: {d.filename} ({d.pages} pp) -- verdict: {d.verdict}")
    print(f"  {d.summary}")
    print(f"  author note: {d.author_note}")
    print("  caveats:")
    for cav in d.caveats:
        print(f"    - {cav}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="persona-v",
        description="PERSONA V -- the Jungian persona engine: time, "
                    "mask, record, and reckoning.")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("stamp", help="print the current Thelemic stamp")
    sub.add_parser("reading", help="print the full Metronome reading")
    sub.add_parser("anchor", help="print the Zero-Trust Anchorage status")
    pd = sub.add_parser("duty", help="print Crowley's four duties (the obligations pan)")
    pd.add_argument("name", nargs="?", default=None,
                    help="a duty to show: key, title, or alias (e.g. self, 'duty to others', c)")

    pm = sub.add_parser("mothers", help="the Three Mothers pipeline (Babalon -> Lilith -> Mary)")
    pm.add_argument("text", nargs="?", default=None,
                    help="input text to run through the pipeline; omit to list the Three Mothers")
    pm.add_argument("--duty", default=None,
                    help="the duty under which Lilith admits segments (e.g. self, others)")

    pa = sub.add_parser("assign", help="assign a flavor and officers to a task")
    pa.add_argument("task", help="the task description, in plain words")
    pa.add_argument("--seed", type=int, default=None,
                    help="sortition seed (reproducible lots)")
    pa.add_argument("--n", type=int, default=2,
                    help="officers to draw from the choir (default 2)")
    pa.add_argument("--demands", default=None,
                    help='explicit demand vector as JSON, e.g. '
                         '\'{"Ti":2,"shadow":1}\' (used verbatim)')
    pa.add_argument("--job", default=None,
                    help="trade number 0-21 or trade name (its charter "
                         "supplies the demands)")

    pv = sub.add_parser("verify", help="verify a ledger file's hash chain")
    pv.add_argument("file", help="path to the .jsonl ledger")

    pu = sub.add_parser("audit", help="run the shadow audit over a ledger")
    pu.add_argument("file", help="path to the .jsonl ledger")
    pu.add_argument("--apply", action="store_true",
                    help="write the findings into the ledger (accountability)")

    pl = sub.add_parser("alethic", help="weigh the ledger's claims")
    pl.add_argument("file", help="path to the .jsonl ledger")

    pr = sub.add_parser("practice",
                        help="record an apprentice's deliberate practice")
    pr.add_argument("flavor", type=int, help="flavor number 0-30")
    pr.add_argument("hours", type=float, help="practice hours (> 0)")
    pr.add_argument("--working", required=True,
                    help="the working the practice belongs to")
    pr.add_argument("--note", required=True,
                    help="what was practiced (intentionality, attested)")
    pr.add_argument("--under-master", dest="under_master", type=int,
                    default=None,
                    help="the working's Master flavor (0-30) under whom "
                         "the practice was performed; recorded as the "
                         "witness on the apex event if this practice "
                         "crosses the mastery threshold")
    pr.add_argument("--registry", default=None,
                    help="proficiency registry path "
                         "(default ~/.persona-v/proficiency.json)")

    pm = sub.add_parser("promote",
                        help="a Master promotes an apprentice, with grounds")
    pm.add_argument("apprentice", type=int, help="flavor number 0-30")
    pm.add_argument("--by-master", dest="by_master", type=int, required=True,
                    help="the promoting Master's flavor number")
    pm.add_argument("--working", required=True, help="the working")
    pm.add_argument("--grounds", required=True,
                    help="what the Master saw that warrants it")
    pm.add_argument("--registry", default=None,
                    help="proficiency registry path")

    ps = sub.add_parser("standing",
                        help="show a flavor's proficiency standing")
    ps.add_argument("flavor", type=int, help="flavor number 0-30")
    ps.add_argument("--registry", default=None,
                    help="proficiency registry path")

    pn = sub.add_parser("name",
                        help="inspect one of the 72 names")
    pn.add_argument("number", type=int, help="name number 1-72")

    pg = sub.add_parser("naming",
                        help="show the naming policy (fluid or binary)")
    pg.add_argument("--binary", action="store_true",
                    help="write naming.binary: true to "
                         "~/.persona-v/config.yaml")
    pg.add_argument("--fluid", action="store_true",
                    help="write naming.binary: false to "
                         "~/.persona-v/config.yaml")

    sub.add_parser("thoth", help="list the 22 Thoth trumps")
    pt = sub.add_parser("thoth-reading",
                        help="deal a 1-, 3-, or 5-card Thoth reading")
    pt.add_argument("spread", type=int, default=3, nargs="?",
                    help="cards to draw: 1, 3, or 5 (default 3)")
    pt.add_argument("--seed", type=int, default=None,
                    help="shuffle seed (reproducible reading)")
    sub.add_parser("thoth-horoscope",
                   help="print the current horoscope stamp")
    po = sub.add_parser("thoth-operation",
                        help="run the adapted Book T First Operation")
    po.add_argument("--significator", required=True,
                    help="the querent's significator: trump number or "
                         "title (e.g. 17 or 'The Star')")
    po.add_argument("--seed", type=int, default=None,
                    help="shuffle seed (reproducible operation)")
    pc = sub.add_parser("coinage",
                        help="print the author's canonical coinages")
    pc.add_argument("key", nargs="?", default=None,
                    help="a coinage key (e.g. dictum_star, murphy)")
    pco = sub.add_parser("corpus",
                         help="print the honest reference library")
    pco.add_argument("id", nargs="?", default=None,
                     help="a document id (e.g. codex, magisk)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return {
        "stamp": cmd_stamp,
        "reading": cmd_reading,
        "anchor": cmd_anchor,
        "duty": cmd_duty,
        "mothers": cmd_mothers,
        "assign": cmd_assign,
        "verify": cmd_verify,
        "audit": cmd_audit,
        "alethic": cmd_alethic,
        "practice": cmd_practice,
        "promote": cmd_promote,
        "standing": cmd_standing,
        "name": cmd_name,
        "naming": cmd_naming,
        "thoth": cmd_thoth,
        "thoth-reading": cmd_thoth_reading,
        "thoth-horoscope": cmd_thoth_horoscope,
        "thoth-operation": cmd_thoth_operation,
        "coinage": cmd_coinage,
        "corpus": cmd_corpus,
    }[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
