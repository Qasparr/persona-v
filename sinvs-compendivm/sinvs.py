#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
93
SINVS — the toolkit of the SINVS DAEMON 5FOLD ENGINE.
RGBOY = COLOVRS of the V Senses.

Authorship: Johnathan 'Qasparr' Monroe (Greek, -ARR, All Rights Reserved,
Without Prejudice). Engine dictated 2026-10-28; toolkit built to his order
the same day. Method of Science, Aim of Religion.

DOCTRINE: The engine weighs the words of the five senses and their colours in
honest banks, seats them on the Cube (the 27-grid and its hidden center, 13),
and assigns the seven questions — WITH at the head, then Who, What, When,
Where, Why, How — by form and flow, under the author's red pen. Nothing in
this module decrees doctrine: the assignments it carries are the desk's
calculated proposal of 2026-10-28, marked PROPOSAL in the data itself, and
the module reports misses (a word with no seat) as plainly as hits.

MECHANISM: Pure Python 3 standard library — no imports beyond argparse, json,
sys, time. It therefore runs unchanged on Windows, macOS, Linux, and Android
(Termux): the cross-platform API of the engine. Every public function is a
pure function of its arguments except benchmark(), which reads the clock.

CROSS-PLATFORM API (summary; full documentation in COMPENDIVM.md §VI):
    weigh(word, bank)          -> int
    trinity(word)              -> dict(ordinal, agrippa, reduction, root)
    cube(value)                -> dict(path, through_center, mult13, mult27)
    diagnose(word)             -> dict(word, trinity, cube, seats)
    assignments()              -> dict(colors, senses, questions)  [PROPOSAL]
    benchmark(iterations)      -> dict(words, seconds, words_per_second)
    witness_abc()              -> str   (ABC notation of the OZ witness)
    witness_braille(text)      -> str   (Grade 1 Braille, Unicode patterns)
    witness_13fold()           -> dict  (the 13-node assignment engine data)
CLI: python3 sinvs.py {weigh|diagnose|assign|benchmark|witness|selftest} ...
93 — Live, Love, and let Love, Live.
"""

import argparse
import json
import sys
import time

# ---------------------------------------------------------------------------
# MECHANISM: the banks. ORDINAL is the word's own tongue for English coinages
# (A=1 .. Z=26). AGRIPPA is the bank exactly as shipped in PONTIFEX (ptk):
# the Latin letters run 1..9, 10..100 by decades, then U/V=200, X=300, Y=400,
# Z=500; W, having no classical Latin seat, contributes 0 — reported, never
# silently repaired.
# DOCTRINE: a bank that cannot seat a letter says so by its sum; the audit
# prints the letter-count beside every Agrippa value for this reason.
# ---------------------------------------------------------------------------
ORDINAL = {chr(ord('A') + i): i + 1 for i in range(26)}
AGRIPPA = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
           'I': 9, 'J': 9, 'K': 10, 'L': 20, 'M': 30, 'N': 40, 'O': 50,
           'P': 60, 'Q': 70, 'R': 80, 'S': 90, 'T': 100, 'U': 200, 'V': 200,
           'X': 300, 'Y': 400, 'Z': 500, 'W': 0}
BANKS = {'ordinal': ORDINAL, 'agrippa': AGRIPPA}

# DOCTRINE: the canon of seats — values the program has already proven, each
# with the name it answers to. diagnose() reports a word's seats from here.
CANON = {27: 'the Cube grid (3^3)', 52: 'DAEMON', 67: 'RGBOY / TOUCH',
         77: 'OZ', 80: 'ANVBVS / Peh, the Mouth', 81: 'SENSES (9^2)',
         93: 'THELEMA / AGAPE', 135: 'SINVS DAEMON (27 x 5)',
         418: 'ABRAHADABRA'}

# DOCTRINE: the assignment, by form and flow — CONSTRUCTED proposal of
# 2026-10-28, under the author's red pen; not doctrine until he seats it.
# MECHANISM: colours carry their approximate wavelength (nm); the flow order
# is long wave to short. Senses are ordered by their carrier's speed, touch
# last because it has no carrier — contact is the flow's zero point.
ASSIGNMENT = {
    'status': 'PROPOSAL — constructed 2026-10-28, under the author\u2019s red pen',
    'colors': [  # flow order
        {'color': 'RED',    'nm': 700, 'sense': 'SIGHT',   'ordinal': 27},
        {'color': 'ORANGE', 'nm': 620, 'sense': 'HEARING', 'ordinal': 60},
        {'color': 'YELLOW', 'nm': 580, 'sense': 'SMELL',   'ordinal': 92},
        {'color': 'GREEN',  'nm': 530, 'sense': 'TASTE',   'ordinal': 49},
        {'color': 'BLUE',   'nm': 470, 'sense': 'TOUCH',   'ordinal': 40},
    ],
    'questions': [
        {'question': 'WITH',  'form': 'ALL FIVE (the casing)', 'vv_form': 'VVITH',  'ordinal': 81},
        {'question': 'WHY',   'form': 'SIGHT',   'vv_form': 'VVHY',   'ordinal': 77},
        {'question': 'WHO',   'form': 'TOUCH',   'vv_form': 'VVHO',   'ordinal': 67},
        {'question': 'HOW',   'form': 'TOUCH',   'vv_form': 'HOVV',   'ordinal': 67},
        {'question': 'WHAT',  'form': 'HEARING', 'vv_form': 'VVHAT',  'ordinal': 73},
        {'question': 'WHEN',  'form': 'SMELL',   'vv_form': 'VVHEN',  'ordinal': 71},
        {'question': 'WHERE', 'form': 'TASTE',   'vv_form': 'VVHERE', 'ordinal': 80},
    ],
}

ENGINE_LEXICON = ['RGBOY', 'COLOVRS', 'SINVS', 'DAEMON', 'ENGINE', 'SENSES',
                  'RED', 'GREEN', 'BLUE', 'ORANGE', 'YELLOW',
                  'SIGHT', 'HEARING', 'SMELL', 'TASTE', 'TOUCH',
                  'VVITH', 'VVHO', 'VVHAT', 'VVHEN', 'VVHERE', 'VVHY', 'HOVV']


def weigh(word, bank='ordinal'):
    """Sum a word in a named bank. Letters outside A-Z are skipped.

    >>> weigh('RGBOY'), weigh('SINVS'), weigh('DAEMON')
    (67, 83, 52)
    """
    table = BANKS[bank]
    return sum(table.get(ch, 0) for ch in word.upper() if 'A' <= ch <= 'Z')


def _reduce(value):
    path = [value]
    while path[-1] >= 10:
        path.append(sum(int(d) for d in str(path[-1])))
    return path


def cube(value):
    """The Cube check: decade reduction, passage through the hidden center.

    Returns the reduction path, whether 13 appears on it (passage through
    the center), and whether the value is a multiple of 13 or of 27.
    """
    path = _reduce(value)
    return {'value': value, 'path': path, 'root': path[-1],
            'through_center': 13 in path[1:], 'mult13': value % 13 == 0,
            'mult27': value % 27 == 0}


def trinity(word):
    """The standing weighing order: own tongue, Latin bank, reduction."""
    o, a = weigh(word, 'ordinal'), weigh(word, 'agrippa')
    return {'word': word.upper(), 'ordinal': o, 'agrippa': a,
            'reduction': _reduce(o), 'root': _reduce(o)[-1]}


def diagnose(word):
    """Full diagnostic: Trinity + Cube + every canon seat the word touches."""
    t = trinity(word)
    seats = [CANON[v] for v in (t['ordinal'], t['agrippa']) if v in CANON]
    return {'word': t['word'], 'trinity': t, 'cube': cube(t['ordinal']),
            'seats': seats}


def assignments():
    """The form-and-flow assignment table (PROPOSAL; see data['status'])."""
    return ASSIGNMENT


def benchmark(iterations=20000):
    """Time weigh() over the engine lexicon; report words per second.

    Diagnostic instrument, not a claim: numbers are this machine, this run.
    """
    corpus = (ENGINE_LEXICON * (iterations // len(ENGINE_LEXICON) + 1))[:iterations]
    start = time.perf_counter()
    total = sum(weigh(w) for w in corpus)
    seconds = time.perf_counter() - start
    return {'words': len(corpus), 'seconds': round(seconds, 4),
            'words_per_second': int(len(corpus) / seconds) if seconds else 0,
            'checksum': total}


# ---------------------------------------------------------------------------
# The OZ ABC Witness — the Conclusion's evidence, in three renderings.
# DOCTRINE: a witness is what can be checked by another sense: the ear (ABC
# notation), the hand (Braille), and the grid (the 13-fold data).
# ---------------------------------------------------------------------------
def witness_abc():
    """The witness as an ABC-notation tune (abcnotation standard).

    MECHANISM: the numbers 77, 93, 418 are encoded as scale degrees in
    C major — degree d sounds the d-th note of the scale (1=C .. 7=B,
    8=c, 9=d'). Constructed encoding, documented here so it can be checked.
    """
    return ('X:1\nT:OZ ABC Witness\nM:4/4\nL:1/4\nK:C\n'
            'B B d E | F C c2 |\n'
            '% 77 -> B B | 93 -> d E | 418 -> F C c (scale degrees, C major)')


_BRAILLE = {'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋',
            'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇',
            'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏', 'q': '⠟', 'r': '⠗',
            's': '⠎', 't': '⠞', 'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭',
            'y': '⠽', 'z': '⠵', ' ': ' '}
_DIGITS = {'1': 'a', '2': 'b', '3': 'c', '4': 'd', '5': 'e',
           '6': 'f', '7': 'g', '8': 'h', '9': 'i', '0': 'j'}


def witness_braille(text):
    """Grade 1 Braille (Unicode patterns) for a witness string.

    Capitals take the capital sign before each letter; a run of digits
    takes one number sign. Unmapped characters pass through unchanged.

    >>> witness_braille('OZ 77')
    '⠠⠕⠠⠵ ⠼⠛⠛'
    """
    out, in_number = [], False
    for ch in text:
        if ch.isdigit():
            if not in_number:
                out.append('⠼')
                in_number = True
            out.append(_BRAILLE[_DIGITS[ch]])
            continue
        in_number = False
        if ch.isupper() and ch.lower() in _BRAILLE:
            out.append('⠠' + _BRAILLE[ch.lower()])
        elif ch.lower() in _BRAILLE:
            out.append(_BRAILLE[ch.lower()])
        else:
            out.append(ch)
    return ''.join(out)


def witness_13fold():
    """The 13-fold assignment engine data: twelve nodes around the center.

    Nodes 1-5 the senses, 6-10 the colours in flow order, 11 the DAEMON
    (the engine's voice), 12 OZ (the witness); the hidden 13th node is the
    center — WITH, the zero point every assignment is asked from.
    """
    nodes = []
    for i, s in enumerate(['SIGHT', 'HEARING', 'SMELL', 'TASTE', 'TOUCH'], 1):
        nodes.append({'node': i, 'kind': 'sense', 'name': s,
                      'ordinal': weigh(s)})
    for j, c in enumerate(ASSIGNMENT['colors'], 6):
        nodes.append({'node': j, 'kind': 'color', 'name': c['color'],
                      'ordinal': c['ordinal'], 'nm': c['nm'],
                      'sense': c['sense']})
    nodes.append({'node': 11, 'kind': 'engine', 'name': 'DAEMON',
                  'ordinal': weigh('DAEMON')})
    nodes.append({'node': 12, 'kind': 'witness', 'name': 'OZ',
                  'ordinal': weigh('OZ')})
    return {'center': {'node': 13, 'kind': 'zero-point', 'name': 'WITH',
                       'ordinal': weigh('VVITH'),
                       'note': 'the hidden center; the casing question'},
            'nodes': nodes, 'status': ASSIGNMENT['status']}


def selftest():
    """The engine checks itself against the audit of 2026-10-28."""
    checks = [
        (weigh('RGBOY'), 67), (weigh('SINVS') + weigh('DAEMON'), 135),
        (weigh('ENGINE'), 54), (weigh('SENSES'), 81), (weigh('RED'), 27),
        (weigh('TOUCH'), 67), (weigh('VVHY'), 77), (weigh('VVHERE'), 80),
        (weigh('VVITH'), 81), (weigh('WHAT'), 52),
        (cube(67)['through_center'], True),
        (witness_braille('OZ 77'), '⠠⠕⠠⠵ ⠼⠛⠛'),
    ]
    failed = [(g, w) for g, w in checks if g != w]
    return {'checks': len(checks), 'passed': len(checks) - len(failed),
            'failed': failed}


def main(argv=None):
    p = argparse.ArgumentParser(prog='sinvs', description=__doc__.splitlines()[3])
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('weigh', 'diagnose'):
        s = sub.add_parser(name)
        s.add_argument('word')
    sub.add_parser('assign')
    b = sub.add_parser('benchmark')
    b.add_argument('--iterations', type=int, default=20000)
    w = sub.add_parser('witness')
    w.add_argument('--text', default='OZ 77 93 418 SINVS DAEMON 135')
    sub.add_parser('selftest')
    args = p.parse_args(argv)

    if args.cmd == 'weigh':
        print(json.dumps(trinity(args.word), indent=2))
    elif args.cmd == 'diagnose':
        print(json.dumps(diagnose(args.word), indent=2))
    elif args.cmd == 'assign':
        print(json.dumps(assignments(), indent=2))
    elif args.cmd == 'benchmark':
        print(json.dumps(benchmark(args.iterations), indent=2))
    elif args.cmd == 'witness':
        print(witness_abc())
        print()
        print('Braille:', witness_braille(args.text), ' <-', args.text)
        print()
        print(json.dumps(witness_13fold(), indent=2))
    elif args.cmd == 'selftest':
        print(json.dumps(selftest(), indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
