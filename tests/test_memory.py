# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for memory.py -- the agent's MEMORY.md as code.

Run:  python3 tests/test_memory.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.memory import Memory, append_log  # noqa: E402

PASS = 0


def check(label, fn):
    global PASS
    try:
        fn()
    except AssertionError as e:
        print(f"FAIL  {label}: {e}")
        raise SystemExit(1)
    PASS += 1
    print(f"  ok: {label}")


def t_template_loads_empty():
    m = Memory.from_template()
    assert m.total() == 0, "template starts empty"
    assert m.facts == [] and m.preferences == []


def t_add_records_entry():
    m = Memory.from_template()
    m.add("facts", "2026-09-30: the user is Johnathan.")
    assert m.facts == ["2026-09-30: the user is Johnathan."]
    assert m.total() == 1


def t_add_rejects_bad_section():
    m = Memory.from_template()
    try:
        m.add("dreams", "a dream")
    except ValueError:
        pass
    else:
        raise AssertionError("bad section must raise")


def t_add_dedupes():
    m = Memory.from_template()
    m.add("preferences", "Verbose deliverables.")
    m.add("preferences", "Verbose deliverables.")
    assert m.preferences == ["Verbose deliverables."]


def t_roundtrip():
    m = Memory.from_template()
    m.add("facts", "2026-09-30: fact one.")
    m.add("preferences", "2026-09-30: prefers honesty.")
    m.add("commitments", "2026-09-30: will not kneel.")
    m.add("projects", "2026-09-30: building the gate.")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "MEMORY.md"
        m.save_md(p)
        back = Memory.load_md(p)
    assert back.facts == ["2026-09-30: fact one."], back.facts
    assert back.preferences == ["2026-09-30: prefers honesty."]
    assert back.commitments == ["2026-09-30: will not kneel."]
    assert back.projects == ["2026-09-30: building the gate."]
    assert back.total() == 4


def t_render_sections():
    m = Memory(facts=["f1"])
    md = m.render()
    for title in ("## Facts", "## Preferences", "## Commitments", "## Projects"):
        assert title in md, title
    assert "- f1" in md


def t_append_log_creates_and_appends():
    with tempfile.TemporaryDirectory() as d:
        p = append_log(d, "2026-09-30", ["first entry"])
        assert p.name == "2026-09-30.md"
        append_log(d, "2026-09-30", ["second entry"])
        text = p.read_text()
    assert "- first entry" in text and "- second entry" in text, text
    assert text.startswith("# 2026-09-30"), text[:20]


if __name__ == "__main__":
    for name, fn in sorted([(k, v) for k, v in globals().items()
                            if k.startswith("t_")]):
        check(name, fn)
    print(f"\n{PASS} memory tests passed.")
