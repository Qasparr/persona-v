# ☉ in 3° 54′ Libra  ☽ in 7° 39′ Aries  dies saturnii  Anno V:xii e.n.
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice.  CashApp $axoneme
"""
API tests for api.py -- PERSONA V as a service (Phase 6).

Run:  ~/workspace/persona-v/.venv/bin/python tests/test_api.py
(uses the project venv: fastapi, httpx)
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["PERSONA_V_LEDGER_DIR"] = tempfile.mkdtemp(prefix="pvapi-")
os.environ["PERSONA_V_PROFICIENCY"] = str(
    Path(tempfile.mkdtemp(prefix="pvprof-")) / "proficiency.json")
os.environ["PERSONA_V_NAMING_BINARY"] = "0"  # fluid policy for the suite

# The env var must be set before api import (module reads it at load).
import persona_v.api as api  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

client = TestClient(api.app)
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


def t_health_stamp_reading():
    assert client.get("/health").json()["status"] == "ok"
    s = client.get("/stamp").json()["stamp"]
    assert "Anno" in s and "dies" in s
    r = client.get("/reading").json()
    assert r["moon_phase"] and r["civil"]["month"] == 7
    assert "sothic_year" in r and "describe" in r


def t_assign():
    r = client.post("/assign", json={"task": "audit the deployment logs",
                                     "seed": 1})
    body = r.json()
    assert r.status_code == 200 and body["flavor"] == 20
    assert body["flavor_name"] == "Judgement"
    assert [o["name"] for o in body["officers"]] == ["Hahasiah", "Imamiah"]
    assert body["engine"] == "aptitude-v1"
    assert body["function"] == "Ti" and body["layer"] == "ego"
    assert body["margin"] >= 0 and body["scores"]["20"] == max(
        body["scores"].values())
    # structured demands are honored and validated
    r = client.post("/assign", json={"task": "anything",
                                     "demands": {"shadow": 2, "gravity": 2,
                                                 "Fi": 1}, "seed": 1})
    assert r.status_code == 200 and r.json()["flavor"] == 15
    r = client.post("/assign", json={"task": "x", "demands": {"Nope": 1}})
    assert r.status_code == 422
    r = client.post("/assign", json={"task": "x", "demands": {"Ti": 9}})
    assert r.status_code == 422
    assert body["job"] == "The Auditor"
    # officers carry their gender standing under the naming policy
    assert body["officers"][0]["gender"] == "fluid"
    assert body["officers"][0]["sexuality"] == "fluid"
    assert body["naming_policy"] == {"binary": False, "source": "env"}
    r = client.post("/assign", json={"task": "confront it",
                                     "job": "The Confessor", "seed": 1})
    assert r.status_code == 200 and r.json()["flavor"] == 15
    r = client.post("/assign", json={"task": "x", "job": "The Cobbler"})
    assert r.status_code == 422
    r = client.post("/assign", json={"task": "x", "job": 99})
    assert r.status_code == 422
    r = client.post("/assign", json={"task": ""})
    assert r.status_code == 422


def t_assign_sortition():
    # seeded lots are reproducible over HTTP
    p = {"task": "begin a new working", "seed": 42}
    r1 = client.post("/assign", json=p)
    r2 = client.post("/assign", json=p)
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["officers"] == r2.json()["officers"]
    # contradictory officers are never cast together (flavor 15:
    # structured demands force the Devil; its choir IS the conflict pair)
    r3 = client.post("/assign", json={"task": "confront the pattern",
                                      "demands": {"shadow": 2, "gravity": 2,
                                                  "Fi": 1},
                                      "seed": 7, "n_officers": 2})
    assert r3.json()["flavor"] == 15
    nums = {o["number"] for o in r3.json()["officers"]}
    assert not ({41, 42} <= nums)
    assert "sortition" in r3.json()["rationale"]


def t_working_lifecycle():
    r = client.post("/workings", json={"purpose": "api shakedown"})
    assert r.status_code == 201
    wid = r.json()["working_id"]

    # vocabulary
    assert client.post(f"/workings/{wid}/thought",
                       json={"detail": "plan formed"}).status_code == 201
    assert client.post(f"/workings/{wid}/claim",
                       json={"detail": "x is 1",
                             "grounds": "counted"}).status_code == 201
    # ungrounded claim refused, honestly
    r = client.post(f"/workings/{wid}/claim",
                    json={"detail": "x is 2", "grounds": " "})
    assert r.status_code == 422
    assert client.post(f"/workings/{wid}/tool_call",
                       json={"tool": "t", "summary": "run t"}).status_code == 201
    assert client.post(f"/workings/{wid}/tool_result",
                       json={"tool": "t", "ok": True,
                             "summary": "ok"}).status_code == 201
    assert client.post(f"/workings/{wid}/observation",
                       json={"detail": "all quiet"}).status_code == 201

    # persona
    r = client.post(f"/workings/{wid}/assume", json={"flavor": 11})
    assert r.json()["flavor_name"] == "Justice"
    r = client.post(f"/workings/{wid}/assume", json={"flavor": 99})
    assert r.status_code == 422
    r = client.post(f"/workings/{wid}/invoke", json={"names": [33, 34]})
    assert r.json()["names"] == [33, 34]
    r = client.post(f"/workings/{wid}/invoke", json={"names": [73]})
    assert r.status_code == 422
    r = client.post(f"/workings/{wid}/focus", json={"layer": "shadow"})
    assert r.json()["layer"] == "shadow"

    info = client.get(f"/workings/{wid}").json()
    assert info["flavor"] == 11 and info["layer"] == "shadow"

    # reckoning
    evs = client.get(f"/workings/{wid}/events").json()
    assert len(evs) >= 8
    v = client.get(f"/workings/{wid}/verify").json()
    assert v["ok"] is True
    a = client.get(f"/workings/{wid}/alethic").json()
    assert a["total"] >= 1 and "standing" in a
    u = client.get(f"/workings/{wid}/unresolved").json()
    assert u == []

    r = client.post(f"/workings/{wid}/close")
    assert r.json()["closed"] is True
    # The record endures: closing drops server state, but the ledger
    # file remains and rehydrates on demand (the past is not lost).
    # Rehydration appends working_resumed after the close -- the chain
    # shows both, honestly.
    evs = client.get(f"/workings/{wid}/events")
    assert evs.status_code == 200
    kinds = [e["kind"] for e in evs.json()]
    assert "working_closed" in kinds and kinds[-1] == "working_resumed"


def t_audit_apply_remedy_flow():
    r = client.post("/workings", json={"purpose": "flawed working"})
    wid = r.json()["working_id"]
    client.post(f"/workings/{wid}/tool_call",
                json={"tool": "deploy", "summary": "deploy"})
    client.post(f"/workings/{wid}/tool_result",
                json={"tool": "deploy", "ok": False,
                      "summary": "refused"})
    client.post(f"/workings/{wid}/claim",
                json={"detail": "live", "grounds": "probably"})

    rep = client.post(f"/workings/{wid}/audit").json()
    assert len(rep["flags"]) == 2

    rep = client.post(f"/workings/{wid}/audit?apply=true").json()
    assert rep["applied"] == 2

    flags = client.get(f"/workings/{wid}/unresolved").json()
    assert len(flags) == 2
    seq = flags[0]["seq"]
    r = client.post(f"/workings/{wid}/remedy",
                    json={"flag_seq": seq, "action": "fixed it"})
    assert r.status_code == 201
    assert len(client.get(f"/workings/{wid}/unresolved").json()) == 1

    r = client.post(f"/workings/{wid}/remedy",
                    json={"flag_seq": 9999, "action": "bogus"})
    assert r.status_code == 404
    client.post(f"/workings/{wid}/close")


def t_unknown_working_404():
    assert client.get("/workings/nope/events").status_code == 404
    assert client.post("/workings/nope/thought",
                       json={"detail": "x"}).status_code == 404


def t_proficiency_flow():
    # the apex, over HTTP: practice accrues, promotion confers
    m = client.get("/mastery").json()
    assert m["mastery_hours"] == 1200.0 and len(m["paths"]) == 2
    s = client.get("/standing/0").json()
    assert s["flavor"] == 0 and s["hours"] == 0.0
    assert s["is_master"] is False and s["flavor_name"] == "The Fool"
    r = client.post("/practice", json={"flavor": 0, "hours": 1199.0,
                                       "working_id": "w1",
                                       "note": "a year of cross-examining"})
    assert r.status_code == 201
    assert r.json()["standing"]["hours"] == 1199.0
    assert r.json()["standing"]["is_master"] is False
    # the final hour: attainment confers itself
    r = client.post("/practice", json={"flavor": 0, "hours": 1.0,
                                       "working_id": "w2",
                                       "note": "the final hour"})
    body = r.json()
    assert body["event"]["kind"] == "mastery_attained"
    assert body["event"]["path"] == "attainment"
    assert body["standing"]["is_master"] is True
    # lineage over HTTP: sponsor and apex working are surfaced
    r = client.post("/practice", json={"flavor": 0, "hours": 1.0,
                                       "working_id": "w2b",
                                       "note": "after the apex",
                                       "master": 20})
    assert r.status_code == 201
    assert r.json()["event"]["under_master"] == 20
    # promotion path, with grounds
    r = client.post("/promote", json={"apprentice": 3, "master": 20,
                                      "working_id": "w3",
                                      "grounds": "she found what I buried"})
    assert r.status_code == 201
    assert r.json()["standing"]["path"] == "promotion"
    assert r.json()["standing"]["sponsor"] == 20
    assert r.json()["standing"]["apex_working"] == "w3"
    # refusals: unattested practice, ungrounded promotion, bad flavor
    r = client.post("/practice", json={"flavor": 3, "hours": 1.0,
                                       "working_id": "w", "note": "  "})
    assert r.status_code == 422
    r = client.post("/promote", json={"apprentice": 3, "master": 20,
                                      "working_id": "w", "grounds": ""})
    assert r.status_code == 422
    assert client.get("/standing/31").status_code == 422


def t_lineage_endpoint():
    # the sponsor chain over HTTP: names, paths, apex workings
    r = client.post("/promote", json={"apprentice": 5, "master": 11,
                                      "working_id": "wL1",
                                      "grounds": "he held the line"})
    assert r.status_code == 201
    r = client.post("/promote", json={"apprentice": 11, "master": 20,
                                      "working_id": "wL2",
                                      "grounds": "she judged truly"})
    assert r.status_code == 201
    chain = client.get("/lineage/5").json()["chain"]
    assert [l["flavor"] for l in chain] == [5, 11]
    assert chain[0]["path"] == "promotion"
    assert chain[0]["sponsor"] == 11
    assert chain[0]["sponsor_name"] == "Justice"
    assert chain[0]["apex_working"] == "wL1"
    assert chain[1]["flavor_name"] == "Justice"
    assert chain[1]["sponsor_name"] == "Judgement"
    # no mastery, no chain; bad flavor refused
    assert client.get("/lineage/7").json()["chain"] == []
    assert client.get("/lineage/31").status_code == 422


def t_naming_endpoints():
    # policy + one officer's red-pen view, over HTTP
    p = client.get("/naming/policy").json()
    assert p["binary"] is False and p["source"] == "env"
    assert "FLUID" in p["describe"]
    n = client.get("/names/11").json()
    assert n["name"] == "Lauviah" and n["office"] == "Midwife of Ideas"
    assert n["assessed_gender"] == "female"
    assert n["assessed_sexuality"] == "abstinent"
    assert n["gender"] == "fluid"  # fluid policy: not operative
    assert "Decided 2026-09-26" in n["assessment"]
    assert client.get("/names/73").status_code == 404
    assert client.get("/names/0").status_code == 404


def t_thoth_endpoints():
    r = client.get("/thoth")
    assert r.status_code == 200 and len(r.json()["trumps"]) == 22
    assert ("verify against the printed Book of Thoth"
            in r.json()["transcription_notice"])
    r = client.get("/thoth/reading", params={"spread": 1, "seed": 9})
    assert r.status_code == 200 and len(r.json()["cards"]) == 1
    assert client.get("/thoth/reading",
                      params={"spread": 7}).status_code == 422
    h = client.get("/thoth/horoscope").json()
    assert h["stamp"] == "the heavens stamp the moment but never vote."
    fo = client.get("/thoth/first-operation",
                    params={"significator": "17", "seed": 3}).json()
    assert fo["significator"]["title"] == "The Star"
    assert "78 cards" in fo["notice"]
    assert client.get("/thoth/first-operation",
                      params={"significator": "Bogus"}).status_code == 422


def t_coinage_corpus_endpoints():
    r = client.get("/coinage")
    assert r.status_code == 200 and len(r.json()["coinages"]) == 8
    m = client.get("/coinage/murphy").json()
    assert m["text"] == "What can occur \u2014 will."
    assert client.get("/coinage/nope").status_code == 404
    r = client.get("/corpus")
    assert r.status_code == 200 and len(r.json()["documents"]) == 8
    d = client.get("/corpus/codex").json()
    assert d["verdict"] == "doctrine" and len(d["caveats"]) > 0
    assert client.get("/corpus/nope").status_code == 404


if __name__ == "__main__":
    check("health / stamp / reading", t_health_stamp_reading)
    check("assign routes honestly", t_assign)
    check("assign sortition: seed + conflict rules", t_assign_sortition)
    check("working lifecycle end to end", t_working_lifecycle)
    check("audit -> apply -> remedy -> unresolved", t_audit_apply_remedy_flow)
    check("unknown working -> 404", t_unknown_working_404)
    check("proficiency: practice, promotion, standing", t_proficiency_flow)
    check("lineage: sponsor chain over HTTP", t_lineage_endpoint)
    check("naming: policy + officer detail", t_naming_endpoints)
    check("thoth endpoints: deck, reading, horoscope, operation",
          t_thoth_endpoints)
    check("coinage + corpus endpoints", t_coinage_corpus_endpoints)
    print(f"\n{PASS} tests passed. The front door holds.")
