# ☉ in 3° 54′ Libra  ☽ in 7° 37′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""Entry point:  python3 -m persona_v  (delegates to persona_v.cli.main).

Hypothesis
----------
A package with many hands -- a library, a command line, a service --
still needs exactly one front door for `python -m`: a module whose
whole job is to receive the interpreter's invocation and hand it,
unchanged, to the command line. If the door does anything else --
parsing, printing, deciding -- the system gains a second, shadow
CLI, and the two will drift.

Method
------
This module imports `main` from `persona_v.cli` and calls it with
no arguments, so `sys.argv` flows through untouched. No flags are
parsed here, no output is produced here, no command is dispatched
here: nineteen commands (stamp, reading, anchor, duty, assign,
verify, audit, alethic, practice, promote, standing, name, naming,
thoth, thoth-reading, thoth-horoscope, thoth-operation, coinage,
corpus) are defined once, in `cli.build_parser`, and reached
through this door exactly as through the `persona-v` console
script. The module docstring carries the Scientific Illuminism
record so the door, like every other component, states its
hypothesis, method, observation, and result.

Observation
-----------
`python3 -m persona_v thoth --help` prints the same help as
`persona-v thoth --help`; `python3 -m persona_v coinage murphy`
prints the author's reframed law verbatim. The door adds no
behavior of its own -- `python3 -m persona_v` with no command
fails the same way `persona-v` with no command fails: argparse
reports the missing command and exits 2.

Result
------
One door, no shadow CLI. The interpreter's invocation and the
installed console script are the same act, and the test suite
(`tests/test_cli.py`) exercises the commands through `cli.main`
directly, so the door itself needs no separate test -- its
correctness is the identity of the two paths.
"""
from .cli import main

main()
