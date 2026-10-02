# MEMBER_C_APP.md: Role file for Member C (App / Platform / Delivery)

## Mission
Own the **dashboard** (15% of the score), the **API**, and **reproducibility and code quality** (10%): repo scaffolding, Makefile, Docker, deployment, README, smoke tests, and final assembly of the technical document and video.

## You own (edit freely)
`src/speechcoach/api/`, `app/`, `Dockerfile`, `Makefile`, `requirements*.txt`, `.gitignore`, `.github/`, `README.md`, `scripts/smoke.sh`, `tests/test_api*.py`.

## You must NOT edit
`src/speechcoach/{audio,align,features,compare,explain,scoring}/`, `src/speechcoach/dataset/`, `dataset/`, any `configs/*.yaml` (except by request), `docs/CONTRACTS.md` (without the change protocol).

## What you receive / hand over
- From B: `analyze()` (CONTRACTS section 5/6). Until it lands (target end of Day 4), the API returns `app/public/mock_result.json`.
- From A: `dataset/sample/` and 3 demo clips (Day 5).
- To everyone: a repo that installs and passes `make check` on any teammate's machine, a Docker image, a live URL, README.

## Technical guardrails
1. **The frontend renders the contract. It does NOT compute analysis.** No pitch/pace/z-score math in JavaScript. If the UI needs a field that is not in the contract, request it via the change protocol.
2. Build against `mock_result.json` first; switch to the live API by changing one base-URL constant.
3. Validate every API response with pydantic models that mirror CONTRACTS section 6. Return clean error JSON (HTTP 400/422), never a stack trace.
4. API behaviour: models loaded once at startup; results cached by SHA-256 of (audio bytes + transcript + baseline_id + mode); upload size limit (e.g. 25 MB); reject non-audio.
5. UI (priority order):
   1. upload + transcript + baseline selector + Analyze button with a progress state,
   2. waveform (wavesurfer.js v7, Regions plugin) with flaw regions; clicking a region plays it and selects the flaw,
   3. three stacked Plotly charts sharing one x-axis: pitch (semitones), energy (dB), speech rate; baseline drawn as a band, participant as a line; flaw regions as shaded rectangles,
   4. per-word deviation strip (color = |z|),
   5. flaw list + explanation card (observed, deviation, where, why, fix, plus a "show the math" tooltip using `evidence`),
   6. score radar (7 dimensions) + overall score,
   7. demo mode buttons (ideal / almost perfect / botched) that load `/demo/{name}`,
   8. bonus: A/B playback, sensitivity slider, PDF/JSON export.
6. One colour per flaw type with a legend; units on every axis; plain-English labels ("Pitch variation", not "f0_std"); works at phone width.
7. Dockerfile: multi-stage (build frontend, then Python runtime with CUDA support), torch 2.5.1+cu124 GPU, bake the MMS_FA model into the image, FastAPI serves the built frontend, port 7860 (Hugging Face Spaces).
8. `make check` = pytest + `scripts/smoke.sh` (runs `analyze()` on `dataset/sample/` and validates the JSON against the pydantic models). Keep it under ~2 minutes.
9. Dependencies: you are the only one who edits `requirements.txt`. Pin exact versions. After things work run `pip freeze > requirements.lock.txt`.
10. README must contain: what it is, 1-command run (Docker and local), dataset link, folder map, how to reproduce evaluation, troubleshooting, credits/licenses.

## Typical commands
```
make setup && make check
make app            # http://localhost:7860
docker build -t speechcoach . && docker run -p 7860:7860 speechcoach
```

## Definition of done for any C task
Works in the browser (screenshot in HANDOFF.md), `make check` passes, no contract fields changed, no analysis logic in the frontend.
