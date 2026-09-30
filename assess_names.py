"""One-shot: first-pass behavioral assessment of the 72 names.

Adds gender / sexuality / assessment to every entry in
persona_v/data/names.yaml. Text-based edit (no YAML round-trip),
so header comments and formatting survive.

Rubric (documented in persona_v/naming.py):
  male   -- office behavior at the martial/severing pole: severing,
            breaking, driving, executing, championing, taming, lawgiving.
  female -- office behavior at the containant/tending pole: tending,
            midwifing, weaving, bearing, keeping refuge, nursing,
            gathering, water/deep/earth imagery held and worked.
  nonbinary (default) -- measuring, keeping, watching, guarding
            thresholds, interpreting, weighing, heralding, mixing, or
            any behavior where doubt remains. In doubt, the default stands.
Sexuality: abstinent for all in the first pass -- no office's
behavior carries an erotic character; eros is sublimated into office.
Every entry is marked first-pass; the author's red pen is invited.
"""

import re
import sys
from pathlib import Path

MALE = {
    5: "martial preparation -- the arrow straightened before it flies",
    13: "lawgiving -- bounds commanded outward",
    15: "purging under command -- the purifier's severity",
    18: "martial defense -- the covenant defended",
    21: "severing -- the sword pole",
    22: "driving -- momentum forced onward",
    25: "taming -- force mastered",
    27: "martial championship -- the weak defended in battle",
    34: "executing -- consequence carried out",
    37: "severing -- the dead branch cut away",
    42: "breaking -- chains shattered",
    69: "riding -- the storm mounted and ridden",
}

FEMALE = {
    2: "vessel pole -- the fertile void held ready",
    7: "containment -- the unspoken sealed and kept",
    8: "water pole -- hidden springs guarded",
    10: "tending -- growth nursed",
    11: "the office itself is gendered -- midwife",
    12: "shelter -- refuge kept",
    16: "receptivity -- the received word kept",
    20: "binding -- alignments bound (binder pole)",
    23: "healing -- the course nursed back",
    28: "bearing -- the solitary lamp carried",
    29: "receptivity -- listening held in silence",
    38: "earth pole -- errors composted into renewal",
    41: "binding -- the chain kept (binder pole)",
    43: "bearing -- lightning carried; the behavior is the carrying",
    48: "water pole -- the tide kept",
    53: "loom pole -- completion woven",
    54: "embodied expression -- the whole danced",
    56: "sustaining -- becoming nourished",
    59: "water pole -- deep waters kept",
    62: "tending -- the material nursed",
    63: "vessel pole -- the all held",
    65: "gathering -- the scattered drawn in",
    66: "renewal -- the green kept and renewed",
    67: "loom pole -- remedy woven",
    68: "restoration -- rites of healing kept",
}

SEX_NOTE = ("Sexuality abstinent (default 2026-09-26 -- the office's "
            "behavior carries no erotic character; eros sublimated "
            "into office)")


def note(number: int, gender: str) -> str:
    base = "First pass 2026-09-26 -- "
    if gender == "male":
        g = f"gender male -- {MALE[number]}"
    elif gender == "female":
        g = f"gender female -- {FEMALE[number]}"
    else:
        g = ("gender nonbinary (default -- no binary behavioral marker "
             "in office/duty; in doubt the default stands)")
    return f"{base}{g}. {SEX_NOTE}. Author's red pen invited."


def main() -> None:
    path = Path(__file__).resolve().parent / "persona_v" / "data" / "names.yaml"
    text = path.read_text(encoding="utf-8")
    # Split into entries on "- number: N" boundaries, keeping headers.
    parts = re.split(r"(?m)^(- number: \d+\n)", text)
    out = [parts[0]]
    count = 0
    for i in range(1, len(parts), 2):
        header, body = parts[i], parts[i + 1]
        number = int(re.match(r"- number: (\d+)", header).group(1))
        if "  gender:" in body:
            out += [header, body]
            continue
        gender = "male" if number in MALE else (
            "female" if number in FEMALE else "nonbinary")
        addition = (f"  gender: {gender}\n"
                    f"  sexuality: abstinent\n"
                    f"  assessment: {note(number, gender)}\n")
        # Append after the entry's last line (the gloss line).
        if not body.endswith("\n"):
            body += "\n"
        out += [header, body + addition]
        count += 1
    path.write_text("".join(out), encoding="utf-8")
    print(f"assessed {count} names; male={len(MALE)} "
          f"female={len(FEMALE)} nonbinary={count - len(MALE) - len(FEMALE)}")


if __name__ == "__main__":
    sys.exit(main())
