# ☉ in 3° 55′ Libra  ☽ in 7° 42′ Aries  dies saturnii  Anno V:xii e.n.
<!-- Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure -->
<!-- All Rights Reserved, Without Prejudice.  CashApp $axoneme -->

# PERSONA V — API Surface

`persona_v/api.py` exposes the whole system over HTTP as JSON, so any
client — a web app, another service, a future design — can use the
engine without importing Python.

## Run it

```bash
cd ~/workspace/persona-v
source .venv/bin/activate          # fastapi / uvicorn live here
uvicorn persona_v.api:app --host 127.0.0.1 --port 8000
```

Interactive docs: `http://127.0.0.1:8000/docs` (Swagger UI, generated
from the code — the contract is the documentation).

Ledgers live under `PERSONA_V_LEDGER_DIR` (default `./ledger`).

## Endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | liveness + version |
| GET | `/stamp` | current Thelemic stamp |
| GET | `/reading` | full Metronome reading (structured + prose) |
| GET | `/anchorage` | Anchorage status: stamp, Sun/Moon standing, cardinal rules |
| GET | `/duty` | Crowley's four duties: keys, titles, Crowley lines, obligations |
| GET | `/mothers` | the Three Mothers: keys, titles, offices, doctrines |
| POST | `/mothers/run` | run the pipeline: `{text, duty}` → fuel, filtrate, verdict |
| GET | `/thoth` | the 22 trumps (titles, Hebrew letters, attributions) + transcription notice |
| GET | `/thoth/reading?spread=3&seed=` | seeded 1-, 3-, or 5-card reading (spread must be 1, 3, or 5) |
| GET | `/thoth/horoscope` | computed horoscope: Sun/Moon signs, Latin weekday, Thelemic date, the non-voting stamp |
| GET | `/thoth/first-operation?significator=&seed=` | adapted Book T First Operation: piles, horseshoe, count, paired dignities |
| GET | `/coinage` | the author's canonical coinages, verbatim, with the coinage stamp |
| GET | `/coinage/{key}` | one coinage (`dictum_star`, `murphy`, `maat_dictum`, `aeon_of_maat`, `motto`, `golden_rule`) |
| GET | `/corpus` | the honest reference library: 8 documents + honesty report |
| GET | `/corpus/{id}` | one document: summary, verdict, caveats |
| GET | `/naming/policy` | the naming policy (fluid or binary) |
| GET | `/names/{number}` | inspect one of the 72 names |
| POST | `/assign` | `{"task": "..."}` → flavor, officers, rationale, engine, `apprentice_is_master`, `pair_polarity` |
| POST | `/workings` | open a working (`purpose`, `verbosity`) → id |
| GET | `/workings/{id}` | working info: stamp, events, persona stance |
| POST | `/workings/{id}/close` | close the working (record endures) |
| POST | `/workings/{id}/thought` | record reasoning |
| POST | `/workings/{id}/claim` | `{"detail","grounds"}` — ungrounded → 422 |
| POST | `/workings/{id}/tool_call` | record a tool action |
| POST | `/workings/{id}/tool_result` | `{"tool","ok","summary"}` |
| POST | `/workings/{id}/observation` | neutral observation |
| POST | `/workings/{id}/assume` | `{"flavor":0-30,"layer"}` — put on the regiment |
| POST | `/workings/{id}/invoke` | `{"names":[...]}` — call officers |
| POST | `/workings/{id}/focus` | shift Jungian layer focus |
| GET | `/workings/{id}/events?kind=` | the ledger, optionally filtered |
| GET | `/workings/{id}/verify` | hash-chain verification |
| POST | `/workings/{id}/audit?apply=` | shadow audit; `apply=true` writes findings |
| GET | `/workings/{id}/alethic` | TRVVTH / UNRESOLVED / FALSEHOOD balance |
| POST | `/workings/{id}/remedy` | `{"flag_seq","action"}` — answer a flag |
| GET | `/workings/{id}/unresolved` | flags still awaiting remedy |
| POST | `/practice` | record attested practice hours (`flavor`, `hours`, `working_id`, `note`, optional `master` witness) |
| POST | `/promote` | a Master promotes an apprentice (`apprentice`, `master`, `working_id`, `grounds`) |
| GET | `/standing/{flavor}` | score, progress, apex event: `is_master`, `path`, `sponsor`, `apex_working`, `apex_witness` |
| GET | `/mastery` | the apex: threshold + the two paths |
| GET | `/lineage/{flavor}` | the sponsor chain: flavor, path, sponsor, apex working, names |

## Example session

```bash
W=$(curl -s -X POST localhost:8000/workings \
  -H 'Content-Type: application/json' \
  -d '{"purpose":"demo"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['working_id'])")

curl -s -X POST localhost:8000/assign \
  -H 'Content-Type: application/json' \
  -d '{"task":"audit the deployment logs"}'

# reproducible lots: seed the sortition, choose how many officers to draw
curl -s -X POST localhost:8000/assign \
  -H 'Content-Type: application/json' \
  -d '{"task":"begin a new working","seed":42,"n_officers":2}'

# name the trade directly (its charter supplies the demands); or state
# demands explicitly -- explicit demands outrank everything
curl -s -X POST localhost:8000/assign \
  -H 'Content-Type: application/json' \
  -d '{"task":"confront it","job":"The Confessor","seed":1}'
curl -s -X POST localhost:8000/assign \
  -H 'Content-Type: application/json' \
  -d '{"task":"anything","demands":{"Ti":2,"shadow":1}}'

curl -s -X POST localhost:8000/workings/$W/assume \
  -H 'Content-Type: application/json' \
  -d '{"flavor":11}' | python3 -m json.tool | head -8

curl -s -X POST "localhost:8000/workings/$W/audit?apply=true" | head -c 300
curl -s localhost:8000/workings/$W/alethic | python3 -c \
  "import sys,json;print(json.load(sys.stdin)['standing'])"

# the apprentice's arc: practice accrues, the Master promotes,
# standing and lineage read back the record
curl -s -X POST localhost:8000/practice \
  -H 'Content-Type: application/json' \
  -d '{"flavor":0,"hours":2.0,"working_id":"'$W'","note":"cross-examining the Master"}'
curl -s -X POST localhost:8000/promote \
  -H 'Content-Type: application/json' \
  -d '{"apprentice":0,"master":11,"working_id":"'$W'","grounds":"he questioned me honestly"}'
curl -s localhost:8000/standing/0
curl -s localhost:8000/lineage/0
curl -s localhost:8000/mastery
```

## Deployment honesty

The module does **not** invent: authentication, TLS, or rate limiting.
Terminate TLS and enforce auth + quotas at your reverse proxy / API
gateway; never expose uvicorn bare to a network. For multi-instance
service, point `PERSONA_V_LEDGER_DIR` at shared storage. The
`/assign` engine is the aptitude-test default (`aptitude-v1`) and
labels itself as such — swap in the author's true `AssignmentEngine`
subclass with one import change when his rules arrive. Its response
carries the elected `flavor`, `function`, `layer`, `job` (trade name or
null), the demand `demands` vector, top `scores` with `margin`, and the
auditable `rationale`.
