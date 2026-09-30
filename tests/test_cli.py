# ☉ in 3° 54′ Libra  ☽ in 7° 39′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Smoke tests for cli.py -- the command line (Phase 5).

Run:  python3 tests/test_cli.py
"""

import io
import os
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v.cli import main, read_ledger_file  # noqa: E402
from persona_v.speculum import Ledger  # noqa: E402

PASS = 0


def check(label, fn):
    global PASS
    try:
        fn()
    except AssertionError as e:
        print(f"FAIL  {label}: {e}")
        raise SystemExit(1)
    PASS += 1
    print(f"pass  {label}")


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(argv)
    return code, buf.getvalue()


def make_ledger(tmp):
    L = Ledger.open("clitest", ledger_dir=tmp)
    with L:
        L.thought("Plan: check the service, then report.")
        L.tool_call("ping", "ping the service")
        L.tool_result("ping", True, "ok")
        L.claim("Service is up.", grounds="ping tool output ok")
        L.claim("All good.", grounds="probably")
    return str(Path(tmp) / "clitest.jsonl")


def t_stamp():
    code, out = run(["stamp"])
    assert code == 0 and "Anno" in out and "dies" in out


def t_reading():
    code, out = run(["reading"])
    assert code == 0 and "Decan" in out


def t_assign():
    os.environ["PERSONA_V_NAMING_BINARY"] = "0"  # pin fluid for the test
    try:
        code, out = run(["assign", "audit the deployment logs", "--seed", "1"])
    finally:
        del os.environ["PERSONA_V_NAMING_BINARY"]
    assert code == 0 and "Judgement" in out and "aptitude-v1" in out
    assert "function Ti" in out and "layer ego" in out
    # officers are listed under the user's naming policy (fluid here)
    assert "Officers:" in out and "fluid" in out


def t_assign_seed():
    # seeded lots are reproducible through the CLI
    _, out1 = run(["assign", "begin a new working", "--seed", "42"])
    _, out2 = run(["assign", "begin a new working", "--seed", "42"])
    assert out1 == out2 and "sortition" in out1
    code, out3 = run(["assign", "remedy work", "--seed", "1", "--demands",
                      '{"anima":2,"self":2,"precision":2,"Ti":1,"Si":1}'])
    assert code == 0 and "Isis" in out3
    code, out4 = run(["assign", "x", "--demands", '{"Nope":1}'])
    assert code == 2 and "refused" in out4
    code, out5 = run(["assign", "confront it", "--seed", "1",
                      "--job", "The Confessor"])
    assert code == 0 and "Confessor" in out5 and "flavor 15" in out5
    code, out6 = run(["assign", "x", "--job", "The Cobbler"])
    assert code == 2 and "refused" in out6


def t_verify():
    with tempfile.TemporaryDirectory() as tmp:
        path = make_ledger(tmp)
        code, out = run(["verify", path])
        assert code == 0 and "chain sound" in out


def t_audit_and_apply():
    with tempfile.TemporaryDirectory() as tmp:
        path = make_ledger(tmp)
        code, out = run(["audit", path])
        assert code == 0 and "watch(es)" in out
        # the weak claim is flagged; apply writes it into the ledger
        code, out = run(["audit", path, "--apply"])
        assert code == 0 and "Applied:" in out and "chain sound" in out
        events = read_ledger_file(path)
        assert any(e.kind == "shadow_flag" for e in events)


def t_alethic():
    with tempfile.TemporaryDirectory() as tmp:
        path = make_ledger(tmp)
        code, out = run(["alethic", path])
        assert code == 0 and "Alethic balance" in out and "TRVVTH" in out


def t_missing_file():
    code, _ = run(["verify", "/nonexistent/x.jsonl"])
    assert code != 0


def t_name_inspect():
    # the red-pen view of one officer (fluid policy pinned)
    os.environ["PERSONA_V_NAMING_BINARY"] = "0"
    try:
        code, out = run(["name", "11"])
        assert code == 0 and "Midwife of Ideas" in out
        assert "Assessed gender: female" in out
        code, out = run(["name", "21"])
        assert code == 0 and "Severer of False Unions" in out
        code, out = run(["name", "73"])
        assert code == 2 and "refused" in out
        code, out = run(["naming"])
        assert code == 0 and "FLUID" in out
    finally:
        del os.environ["PERSONA_V_NAMING_BINARY"]


def t_naming_write_flags():
    # --binary/--fluid write the user's decision to a temp HOME's
    # config; no flags keeps the show-policy behavior; both refuse.
    import yaml as _yaml
    tmp = tempfile.mkdtemp()
    old_home = os.environ.get("HOME")
    old_env = os.environ.pop("PERSONA_V_NAMING_BINARY", None)
    os.environ["HOME"] = tmp
    try:
        cfg = Path(tmp) / ".persona-v" / "config.yaml"
        code, out = run(["naming", "--binary"])
        assert code == 0 and "BINARY" in out, out
        data = _yaml.safe_load(cfg.read_text(encoding="utf-8"))
        assert data["naming"]["binary"] is True
        # flip back; other keys preserved
        cfg.write_text(_yaml.safe_dump(
            {"naming": {"binary": True, "note": "kept"},
             "other": 1}),
            encoding="utf-8")
        code, out = run(["naming", "--fluid"])
        assert code == 0 and "FLUID" in out, out
        data = _yaml.safe_load(cfg.read_text(encoding="utf-8"))
        assert data["naming"]["binary"] is False
        assert data["naming"]["note"] == "kept" and data["other"] == 1
        # no flags: show policy (now FLUID from the file)
        code, out = run(["naming"])
        assert code == 0 and "FLUID" in out and "config" in out
        # contradiction refused
        code, out = run(["naming", "--binary", "--fluid"])
        assert code == 2 and "refused" in out
    finally:
        if old_home is None:
            del os.environ["HOME"]
        else:
            os.environ["HOME"] = old_home
        if old_env is not None:
            os.environ["PERSONA_V_NAMING_BINARY"] = old_env


def t_proficiency_commands():
    # practice / promote / standing through the CLI, on a temp registry
    with tempfile.TemporaryDirectory() as tmp:
        reg = str(Path(tmp) / "proficiency.json")
        code, out = run(["standing", "0", "--registry", reg])
        assert code == 0 and "apprentice" in out and "1200" in out
        code, out = run(["practice", "0", "1199", "--working", "w1",
                         "--note", "a year of cross-examining",
                         "--registry", reg])
        assert code == 0 and "1199.0/1200" in out
        code, out = run(["practice", "0", "1", "--working", "w2",
                         "--note", "the final hour", "--registry", reg])
        assert code == 0 and "apex is attained" in out
        code, out = run(["promote", "3", "--by-master", "20",
                         "--working", "w3",
                         "--grounds", "she found what I buried",
                         "--registry", reg])
        assert code == 0 and "Master 20" in out and "by promotion" in out
        code, out = run(["promote", "4", "--by-master", "20",
                         "--working", "w3", "--grounds", "   ",
                         "--registry", reg])
        assert code == 2 and "refused" in out
        # Practice under a witnessing Master records the witness;
        # the apex event carries the provenance.
        code, out = run(["practice", "5", "1200", "--working", "w4",
                         "--note", "the long road", "--under-master", "20",
                         "--registry", reg])
        assert code == 0 and "witnessed by Master 20" in out
        code, out = run(["standing", "5", "--registry", reg])
        assert code == 0 and "MASTER by attainment" in out


def t_thoth_commands():
    code, out = run(["thoth"])
    assert code == 0 and "The Magus" in out
    assert "verify against the printed Book of Thoth" in out
    code, out = run(["thoth-reading", "5", "--seed", "42"])
    assert code == 0 and "5 cards" in out
    code, out = run(["thoth-reading", "7"])
    assert code == 2 and "refused" in out
    code, out = run(["thoth-horoscope"])
    assert code == 0 and "the heavens stamp the moment but never vote" in out
    code, out = run(["thoth-operation", "--significator", "The Star",
                     "--seed", "3"])
    assert code == 0 and "Horseshoe" in out and "78 cards" in out
    code, out = run(["thoth-operation", "--significator", "Bogus"])
    assert code == 2 and "refused" in out


def t_coinage_corpus_commands():
    code, out = run(["coinage", "murphy"])
    assert code == 0 and "What can occur \u2014 will." in out
    assert "Qasparr" in out
    code, out = run(["coinage", "nope"])
    assert code == 1 and "no canonical coinage" in out
    code, out = run(["coinage", "dictum_star"])
    assert code == 0 and "Every Man, Woman, and Child is a Star" in out
    code, out = run(["corpus"])
    assert code == 0 and "codex" in out and "magisk" in out
    code, out = run(["corpus", "magisk"])
    assert code == 0 and "procedure" in out
    code, out = run(["corpus", "nope"])
    assert code == 1 and "no document" in out


if __name__ == "__main__":
    check("stamp prints the moment", t_stamp)
    check("reading describes the metronome", t_reading)
    check("assign routes a task", t_assign)
    check("assign --seed reproduces the lots", t_assign_seed)
    check("verify checks a ledger file", t_verify)
    check("audit reads; --apply writes", t_audit_and_apply)
    check("alethic weighs a ledger file", t_alethic)
    check("practice/promote/standing", t_proficiency_commands)
    check("name inspects an officer; naming shows policy", t_name_inspect)
    check("naming --binary/--fluid writes the config", t_naming_write_flags)
    check("thoth commands: deck, reading, horoscope, operation",
          t_thoth_commands)
    check("coinage + corpus commands", t_coinage_corpus_commands)
    try:
        t_missing_file()
        print("FAIL  missing file: no error raised")
        raise SystemExit(1)
    except FileNotFoundError:
        PASS += 1
        print("pass  missing file errors honestly")
    print(f"\n{PASS} tests passed. The hands obey.")
