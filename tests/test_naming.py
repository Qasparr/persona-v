# ☉ in 3° 57′ Libra  ☽ in 8° 36′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
Validation tests for naming.py -- gender and sexuality of the 72 names.

The attributes are assigned as per behavioral assessment, defaulting
to non-binary and abstinent; whether the binary assignments make a
difference is the device's current user's decision (fluid by default).

Run:  python3 tests/test_naming.py
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona_v import grimoire  # noqa: E402
from persona_v.naming import (  # noqa: E402
    FLUID, GENDERS, SEXUALITIES, NamingPolicy, chair_pole, effective_gender,
    effective_sexuality, inspect_name, pair_polarity_reading,
    render_officer, validate_gender, validate_sexuality,
    write_binary_setting,
)

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


def with_env(**kwargs):
    """Temporarily set env vars; restore afterwards."""
    old = {k: os.environ.get(k) for k in kwargs}
    os.environ.update({k: v for k, v in kwargs.items() if v is not None})
    for k, v in kwargs.items():
        if v is None:
            os.environ.pop(k, None)
    return old


def restore_env(old):
    for k, v in old.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def t_all_72_valid():
    names = grimoire.load_names()
    assert len(names) == 72
    assert [n.number for n in names] == list(range(1, 73))
    for n in names:
        validate_gender(n.gender)
        validate_sexuality(n.sexuality)
        assert n.assessment and "Decided 2026-09-26" in n.assessment, \
            f"name {n.number}: assessment note missing"


def t_first_pass_census():
    # The documented first pass: 12 male, 25 female, 35 nonbinary;
    # all abstinent (no erotic character found in any office).
    names = grimoire.load_names()
    counts = {g: sum(1 for n in names if n.gender == g) for g in GENDERS}
    assert counts == {"nonbinary": 35, "male": 12, "female": 25}, counts
    assert all(n.sexuality == "abstinent" for n in names)
    # spot checks on unambiguous offices
    by_number = {n.number: n for n in names}
    assert by_number[11].gender == "female"  # Midwife of Ideas
    assert by_number[21].gender == "male"    # Severer of False Unions
    assert by_number[33].gender == "nonbinary"  # Weigher of TRVVTH


def t_fluid_is_default():
    old = with_env(PERSONA_V_NAMING_BINARY=None)
    try:
        # no config file in a fresh HOME either: point HOME nowhere real
        policy = NamingPolicy.load(
            config_path=Path(tempfile.mkdtemp()) / "nope.yaml")
        assert policy.binary is False and policy.source == "default"
        names = {n.number: n for n in grimoire.load_names()}
        assert effective_gender(names[11], policy) == FLUID
        assert effective_sexuality(names[21], policy) == FLUID
        # fluid: either male or female names work -- the recorded
        # assignment is not operative
        assert "fluid" in render_officer(names[11], policy)
    finally:
        restore_env(old)


def t_env_override_binary():
    old = with_env(PERSONA_V_NAMING_BINARY="1")
    try:
        policy = NamingPolicy.load()
        assert policy.binary is True and policy.source == "env"
        names = {n.number: n for n in grimoire.load_names()}
        assert effective_gender(names[11], policy) == "female"
        assert effective_gender(names[21], policy) == "male"
        assert effective_gender(names[33], policy) == "nonbinary"
        assert effective_sexuality(names[11], policy) == "abstinent"
        line = render_officer(names[21], policy)
        assert "(male / abstinent)" in line
    finally:
        restore_env(old)


def t_config_file_policy():
    old = with_env(PERSONA_V_NAMING_BINARY=None)
    try:
        cfg = Path(tempfile.mkdtemp()) / "config.yaml"
        cfg.write_text("naming:\n  binary: true\n", encoding="utf-8")
        policy = NamingPolicy.load(config_path=cfg)
        assert policy.binary is True and policy.source == "config"
        assert "BINARY" in policy.describe()
        cfg.write_text("naming:\n  binary: false\n", encoding="utf-8")
        policy = NamingPolicy.load(config_path=cfg)
        assert policy.binary is False and "FLUID" in policy.describe()
    finally:
        restore_env(old)


def t_inspect_renders():
    old = with_env(PERSONA_V_NAMING_BINARY="true")
    try:
        policy = NamingPolicy.load()
        names = {n.number: n for n in grimoire.load_names()}
        text = inspect_name(names[11], policy)
        assert "Midwife of Ideas" in text
        assert "Assessed gender: female" in text
        assert "Effective under current policy: female / abstinent" in text
    finally:
        restore_env(old)


def t_vocab_rejects():
    for bad in ("man", "MALE", "", None):
        try:
            validate_gender(bad)
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError(f"gender {bad!r} accepted")
    try:
        validate_sexuality("celibate")
    except ValueError:
        pass
    else:
        raise AssertionError("sexuality 'celibate' accepted")


def t_name_dataclass_backward_compat():
    # Names built without the new fields still construct (defaults).
    n = grimoire.Name(number=1, name="X", flavor=0, office="O",
                      duty="D", motto="M", gloss="G")
    assert n.gender == "nonbinary" and n.sexuality == "abstinent"
    assert n.assessment is None


def t_polarity_reads_not_enforces():
    # Decided 2026-09-26 (author's leave): binary makes the
    # assignments legible, not operative. The reading gates nothing
    # and weights nothing -- it reads the working's invoked faces.
    names = {n.number: n for n in grimoire.load_names()}
    fluid = NamingPolicy(binary=False)
    binary = NamingPolicy(binary=True)
    # Fluid policy: no reading at all.
    assert pair_polarity_reading([5, 13], [2, 7], names, fluid) is None
    assert chair_pole([5, 13], names, fluid) == "unmarked"
    # Binary: the pole is the majority of the binary-marked officers.
    assert chair_pole([5, 13], names, binary) == "masculine"  # both male
    assert chair_pole([2, 7], names, binary) == "feminine"   # both female
    assert chair_pole([5, 2], names, binary) == "unmarked"   # tie
    assert chair_pole([1, 3], names, binary) == "unmarked"   # nonbinary
    # Cross-wise syzygy: masculine Master, feminine Apprentice.
    reading = pair_polarity_reading([5, 13], [2, 7], names, binary)
    assert "cross-wise" in reading and "masculine" in reading
    assert "feminine" in reading
    # Same pole: intramural cross-examination.
    reading = pair_polarity_reading([5, 13], [15, 18], names, binary)
    assert "intramural" in reading
    # Unmarked chairs: the reading declines honestly.
    reading = pair_polarity_reading([1, 3], [2, 7], names, binary)
    assert "unmarked" in reading


def t_write_binary_setting():
    # writes naming.binary, creating dirs, preserving other keys
    import yaml as _yaml
    tmp = Path(tempfile.mkdtemp())
    cfg = tmp / "sub" / "config.yaml"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("naming:\n  other: kept\nuser: someone\n",
                   encoding="utf-8")
    out = write_binary_setting(True, config_path=cfg)
    assert out == cfg
    data = _yaml.safe_load(cfg.read_text(encoding="utf-8"))
    assert data["naming"]["binary"] is True
    assert data["naming"]["other"] == "kept"  # preserved
    assert data["user"] == "someone"          # preserved
    write_binary_setting(False, config_path=cfg)
    data = _yaml.safe_load(cfg.read_text(encoding="utf-8"))
    assert data["naming"]["binary"] is False
    assert data["naming"]["other"] == "kept"
    # fresh file, no pre-existing content
    fresh = tmp / "fresh.yaml"
    write_binary_setting(True, config_path=fresh)
    data = _yaml.safe_load(fresh.read_text(encoding="utf-8"))
    assert data == {"naming": {"binary": True}}
    # the written file is honored by NamingPolicy.load
    policy = NamingPolicy.load(config_path=fresh)
    assert policy.binary is True and policy.source == "config"


def main():
    check("all 72 names carry valid gender/sexuality/assessment",
          t_all_72_valid)
    check("first-pass census: 12/25/35, all abstinent", t_first_pass_census)
    check("fluid is the default; nothing operative", t_fluid_is_default)
    check("env override makes binary assignments operative",
          t_env_override_binary)
    check("config file carries the user's decision", t_config_file_policy)
    check("inspect_name renders the red-pen view", t_inspect_renders)
    check("vocab rejects impostors", t_vocab_rejects)
    check("Name dataclass backward compatible", t_name_dataclass_backward_compat)
    check("write_binary_setting preserves other keys",
          t_write_binary_setting)
    check("polarity reads, never enforces", t_polarity_reads_not_enforces)
    print(f"{PASS} tests passed. The names stand as assessed.")


if __name__ == "__main__":
    main()
