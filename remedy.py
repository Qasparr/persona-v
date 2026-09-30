#!/usr/bin/env python3
"""remedy.py -- HISTORICAL trial harness, kept for the record.

On 2026-09-26 this script ran the analytical remedy through three
scratch-copy iterations (backup -> apply -> analyze -> test ->
restore), each guarded by the full regression suite. The first
iteration let Death steal the Confessor trade and broke two pinned
tests; the third verified clean. On the author's instruction
("build both, remedy first") the verified edits were then applied
to the real doctrine files by hand (surgical edits, comments and
notes preserved, each amendment annotated "Amended 2026-09-26").

The remedy is now live doctrine (v0.11.0). This script is not
needed for further work; analyze_persona.py + the test suite are
the ongoing verification. Its `apply`/`restore` commands are
retired -- do not run them against the amended files.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "persona_v" / "data"
APT = DATA / "aptitudes.yaml"
JOBS = DATA / "jobs.yaml"
BACKUP = Path("/tmp/remedy_backup")

# --- profile edits: {flavor: {dim: new_rating}} -------------------------
PROFILE_EDITS = {
    # Wound 1 (Fe blind spot): the Empress cultivates living things;
    # nurture at native excellence. "generativity; outputs cultivated
    # like living things; patience" -> Fe:2.
    3: {"Fe": 2},
    # Wound 2 (Justice/Judgement collision): Justice is the living
    # tribunal -- consequence EXECUTED (Te:2, per its own note) and
    # TRVVTH weighed (Fi:2, discernment). Judgement keeps the ledger
    # (Si:2) and the buried audit (shadow:1).
    11: {"Fi": 2, "Te": 2},
    # Wound 2 companion: Death must know what is dead to let it die --
    # Fi:1, "composting error" requires discerning error. Also gives
    # the Pruner charter something Death has that Set lacks.
    13: {"Fi": 1},
    # Companion to the above: naming bondage demands native discernment
    # of the value-inversion that binds -- Fi:2. Keeps the Devil ahead
    # of Death on the pinned {shadow:2, gravity:2, Fi:1} demands and
    # lifts the Confessor charter off its tie-break.
    15: {"Fi": 2},
    # Wound 4 (swiftness absent): the Fool's leap is swift -- the one
    # act done before looking. swiftness:2.
    0: {"swiftness": 2},
}

# --- charter edits: {trade: {dim: new_rating}} ("-" drops a demand) -----
CHARTER_EDITS = {
    # Apprentice: apprenticeship precedes persona and self; it is
    # branching possibility (Ne), latent pattern (Ni), quick tries.
    0: {"Ne": 2, "Ni": 1, "swiftness": 1, "persona": "-", "self": "-"},
    # Oracle: the unspoken includes the dark -- shadow:1.
    2: {"shadow": 1},
    # Marshal: command wears its mask openly -- persona:2.
    4: {"persona": 2},
    # Scribe: writing serves the mask of tradition -- persona:2.
    5: {"persona": 2},
    # Chronicler: the wheel turns quickly; the record keeps pace.
    10: {"swiftness": 1},
    # Confessor: bondage is observed in the body before it is named;
    # the confessor watches the embodied pattern (Devil Se:1, Death Se:0).
    # (Ni:1 was tried first: it let Death tie on Fi and steal the trade.)
    15: {"Se": 1},
    # Pruner: pruning requires discerning what is dead (Death Fi:1,
    # Set Fi:0) -- the cut follows the discernment -- and the executive
    # act of cutting itself (Te:2; Death Te:1, Devil Te:0), guided by
    # pattern-sense of what is dying (Ni:1; Death Ni:1, Justice Ni:0).
    13: {"Fi": 1, "Te": 2, "Ni": 1},
    # Auditor: the ledger is read aloud INCLUDING what was buried.
    # (Holds the margin after Justice gains Te:2.)
    20: {"shadow": 1},
}


def backup():
    BACKUP.mkdir(exist_ok=True)
    shutil.copy2(APT, BACKUP / "aptitudes.yaml")
    shutil.copy2(JOBS, BACKUP / "jobs.yaml")
    print("backed up to", BACKUP)


def restore():
    raise RuntimeError(
        "remedy.py 'restore' is RETIRED: the analytical remedy is live "
        "doctrine (v0.11.0+); restoring the pre-remedy files would "
        "undo the author's approved amendments. Refusing.")


def apply():
    raise RuntimeError(
        "remedy.py 'apply' is RETIRED: the analytical remedy is live "
        "doctrine (v0.11.0+); re-applying trial edits could corrupt "
        "the author's amended files. Refusing.")


def analyze():
    r = subprocess.run(
        [sys.executable, "analyze_persona.py"],
        cwd=ROOT, capture_output=True, text=True,
        env={"PATH": "/usr/bin:/bin",
             "VIRTUAL_ENV": str(ROOT / ".venv"),
             "PATH_": ""} | __import__("os").environ)
    print(r.stdout)
    if r.returncode:
        print(r.stderr[-2000:])


def test():
    total, failed = 0, 0
    for f in sorted((ROOT / "tests").glob("test_*.py")):
        r = subprocess.run([sys.executable, str(f)], cwd=ROOT,
                           capture_output=True, text=True)
        n = 0
        for line in r.stdout.splitlines():
            if "tests passed" in line:
                n = int(line.split()[0])
        total += n
        status = "PASS" if r.returncode == 0 else "FAIL"
        if r.returncode:
            failed += 1
        print(f"{status} {f.name}: {n}")
    print(f"TOTAL: {total} passed, {failed} suites failed")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip().splitlines()[0])
        print("usage: remedy.py baseline [--help]")
        print("  baseline  back up the doctrine files (to /tmp) and "
              "run the analysis -- read-only w.r.t. the repo")
        print("  apply / restore are RETIRED and refuse to run")
        sys.exit(0)
    cmd = args[0]
    if cmd in ("apply", "restore"):
        print(f"remedy.py: '{cmd}' is a RETIRED historical command. "
              f"The analytical remedy is live doctrine (v0.11.0+); "
              f"running '{cmd}' could overwrite the author's amended "
              f"files. Refusing.")
        sys.exit(2)
    if cmd == "baseline":
        backup()
        print("=== BASELINE (originals) ===")
        analyze()
    else:
        print(f"remedy.py: unknown command '{cmd}'")
        sys.exit(2)
