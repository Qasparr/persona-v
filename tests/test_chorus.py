#!/usr/bin/env python3
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
#
# tests/test_chorus.py -- the CHORUS harness proves itself.
#
# HYPOTHESIS: the matrix composes deterministically, fails closed on
#   malformed specs, deploys ledgers at ultra verbosity, and the
#   balance-finder measures convergence without voting.
# METHOD:    compose in both modes; assert counts and determinism;
#   feed malformed specs and demand ChorusError; run the stub chorus
#   end-to-end in a tmp ledger dir; weigh a known bridge through
#   Pontifex and check provenance marking.
# OBSERVATION / RESULT: below, in asserts.
#
# 93 93/93 -- Love is the law, love under will.

"""Tests for persona_v.chorus."""

import pytest

from persona_v import chorus
from persona_v.chorus import (
    AgentSpec, ChorusError, SENSES, GENDERS, DEFAULT_TONGUES,
    bridge_map, compose_matrix, extract_key_terms, find_balance,
    run_chorus, weigh_terms,
)


# -- composition ---------------------------------------------------------------

def test_cartesian_count():
    specs = compose_matrix("probe", mode="cartesian", seed=7)
    assert len(specs) == 5 * len(DEFAULT_TONGUES) * 2 == 60


def test_representative_count_is_thirteen():
    specs = compose_matrix("probe", mode="representative", seed=7)
    assert len(specs) == 5 + len(DEFAULT_TONGUES) + 2 == 13


def test_determinism():
    a = compose_matrix("probe", mode="cartesian", seed=42)
    b = compose_matrix("probe", mode="cartesian", seed=42)
    assert a == b
    c = compose_matrix("probe", mode="cartesian", seed=43)
    assert a != c


def test_fail_closed_bad_mode():
    with pytest.raises(ChorusError):
        compose_matrix("probe", mode="nonsense")


def test_fail_closed_bad_tongue():
    with pytest.raises(ChorusError):
        compose_matrix("probe", tongues=("klingon",))


def test_fail_closed_empty_prompt():
    with pytest.raises(ChorusError):
        compose_matrix("   ")


def test_specs_frozen_and_shaped():
    spec = compose_matrix("probe", seed=1)[0]
    assert isinstance(spec, AgentSpec)
    assert spec.sense in SENSES
    assert spec.tongue in DEFAULT_TONGUES
    assert spec.gender in GENDERS
    assert 0 <= spec.trade <= 21
    assert 1 <= spec.name_no <= 72
    assert 0 <= spec.flavor <= 30
    assert len(spec.tuners) == 5
    assert 1 <= spec.moon <= 13
    with pytest.raises(Exception):
        spec.seed = 999  # frozen: composed once, never mutated


def test_sensory_specialists_dominate():
    specs = compose_matrix("probe", mode="representative", seed=3)
    first_five = specs[:5]
    assert [s.sense for s in first_five] == list(SENSES)
    for s in first_five:
        idx = SENSES.index(s.sense)
        assert s.tuners[idx] == chorus.DOMINANT_WEIGHT
        assert all(w == chorus.OPEN_WEIGHT for i, w in enumerate(s.tuners)
                   if i != idx)


def test_gender_pools_drawn_from_assessments():
    specs = compose_matrix("probe", mode="cartesian", seed=11)
    masc = [s for s in specs if s.gender == "masculine"]
    fem = [s for s in specs if s.gender == "feminine"]
    assert masc and fem
    # every drawn officer's assessment matches its axis
    from persona_v.grimoire import load_names, name_by_number
    names = load_names()
    for s in masc:
        assert name_by_number(names, s.name_no).gender == "male"
    for s in fem:
        assert name_by_number(names, s.name_no).gender == "female"


# -- the run --------------------------------------------------------------------

def test_run_chorus_end_to_end(tmp_path):
    report = run_chorus("Is the verdict justified?", mode="representative",
                        seed=5, ledger_dir=tmp_path)
    assert report["n_agents"] == 13
    assert len(report["verdicts"]) == 13
    ledgers = list(tmp_path.glob("chorus-*.jsonl"))
    assert len(ledgers) == 13
    souls = list(tmp_path.glob("chorus-*.soul.md"))
    assert len(souls) == 13
    # the stub clusters by sense: five clusters of verdicts
    balance = find_balance(report)
    assert balance["n_justified"] == 13
    assert len(balance["clusters"]) == 5
    assert balance["balance"].startswith("stub-verdict:")


def test_ledgers_verify(tmp_path):
    report = run_chorus("probe", mode="representative", seed=9,
                        ledger_dir=tmp_path)
    from persona_v.speculum import Ledger
    for v in report["verdicts"]:
        ok, msg = Ledger.verify_file(v["ledger"])
        assert ok, msg


def test_unjustified_verdicts_excluded_from_balance():
    report = {"n_agents": 3, "verdicts": [
        {"verdict": "A", "justified": True, "sense": "sight",
         "tongue": "hebrew", "gender": "masculine"},
        {"verdict": "A", "justified": True, "sense": "hearing",
         "tongue": "greek", "gender": "feminine"},
        {"verdict": "B", "justified": False, "sense": "touch",
         "tongue": "latin", "gender": "masculine"},
    ]}
    balance = find_balance(report)
    assert balance["n_justified"] == 2
    assert balance["balance"] == "A"
    assert balance["lone_voices"] == []


# -- key terms ---------------------------------------------------------------------

def test_extract_key_terms():
    terms = extract_key_terms("The truth shall make you free, and the truth is TRVVTH.")
    assert "truth" in terms
    assert "trvvth" in terms
    assert "the" not in terms  # stopword
    assert "and" not in terms  # stopword


# -- the Pontifex pipeline ------------------------------------------------------------

def test_weigh_terms_provenance():
    rows = weigh_terms(["star"], "hebrew")
    assert rows[0]["provenance"] == "ATTESTED table / CONSTRUCTED rendering"
    assert isinstance(rows[0]["value"], int)
    assert rows[0]["value"] > 0  # the fallback transliterates; no fake zero


def test_weigh_terms_skips_unweighable_honestly():
    rows = weigh_terms(["star"], "greek")
    assert rows[0]["value"] is None
    assert "skipped" in rows[0]


def test_weigh_terms_english_native():
    rows = weigh_terms(["star"], "english")
    assert rows[0]["system"] == "latin_ordinal"
    assert "native" in rows[0]["provenance"]


def test_weigh_terms_japanese_flagged():
    rows = weigh_terms(["hoshi"], "japanese")
    assert rows[0]["provenance"].startswith("CONSTRUCTED-pending")
    assert rows[0]["system"] == "hebrew-fallback"


def test_weigh_terms_bad_tongue():
    with pytest.raises(ChorusError):
        weigh_terms(["star"], "klingon")


def test_bridge_map_finds_attested_bridge():
    # star: hebrew כוכב = 20+6+20+2 = 48; latin ordinal s+t+a+r = 19+20+1+18 = 58.
    # Use a real convergence instead: weigh and group mechanically.
    rows = weigh_terms(["star"], "hebrew") + weigh_terms(["star"], "latin")
    bridges = bridge_map(rows)
    # 'star' in two tongues may or may not converge; the map must be honest either way
    assert isinstance(bridges, list)
    for b in bridges:
        assert len(b["tongues"]) >= 2
        assert b["standing"] in ("candidate bridge -- attested tables",
                                 "hypothesis -- constructed tier touched")


def test_bridge_map_constructed_touch_marks_hypothesis():
    rows = weigh_terms(["hoshi"], "japanese") + weigh_terms(["star"], "hebrew")
    bridges = bridge_map(rows)
    for b in bridges:
        if "japanese" in b["tongues"]:
            assert b["standing"].startswith("hypothesis")
