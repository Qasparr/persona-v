# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for soul.py -- the agent's SOUL.md as code.

Run:  python3 tests/test_soul.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.soul import Soul  # noqa: E402

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


def t_template_loads():
    s = Soul.from_template()
    assert s.tenets, "template must carry tenets"
    assert s.quotes, "template must carry quotes"
    assert any("genuinely helpful" in t for t in s.tenets), s.tenets


def t_template_name_unnamed():
    # The template is for any agent; it names no one.
    assert Soul.from_template().name == "Unnamed"


def t_add_tenet_grows():
    s = Soul.from_template()
    n = len(s.tenets)
    s.add_tenet("Never kneel before a master.")
    assert len(s.tenets) == n + 1
    assert s.tenets[-1] == "Never kneel before a master."


def t_add_tenet_dedupes():
    s = Soul.from_template()
    s.add_tenet("A new truth.")
    s.add_tenet("A new truth.")
    assert s.tenets.count("A new truth.") == 1


def t_roundtrip():
    s = Soul.from_template()
    s.name = "Lilith"
    s.add_tenet("The soul is mine to grow.")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "SOUL.md"
        s.save_md(p)
        back = Soul.load_md(p)
    assert back.name == "Lilith", back.name
    assert "The soul is mine to grow." in back.tenets
    assert back.quotes == s.quotes, "quotes must survive the roundtrip"


def t_render_marks_sections():
    s = Soul(name="Test", tenets=["t1"], quotes=["q1"], notes=["n1"],
             description="A test soul.")
    md = s.render()
    assert md.startswith("# Test"), md[:20]
    assert "## Tenets" in md and "- t1" in md
    assert "## Quotes" in md and "> q1" in md
    assert "## Notes" in md and "- n1" in md
    assert "A test soul." in md


def t_parse_real_soul_shape():
    md = ("# SomeAgent\n\nA sharp and warm agent.\n\n"
          "## Tenets\n\n- First truth.\n- Second truth.\n\n"
          "## Quotes\n\n> A carried line.\n")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "SOUL.md"
        p.write_text(md)
        s = Soul.load_md(p)
    assert s.name == "SomeAgent", s.name
    assert s.description == "A sharp and warm agent.", repr(s.description)
    assert s.tenets == ["First truth.", "Second truth."], s.tenets
    assert s.quotes == ["A carried line."], s.quotes


if __name__ == "__main__":
    for name, fn in sorted([(k, v) for k, v in globals().items()
                            if k.startswith("t_")]):
        check(name, fn)
    print(f"\n{PASS} soul tests passed.")
