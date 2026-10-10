# CHANGES.md: What changed in the doc set and why (2026-10-06, task DOC1)

Source: `Track_C_A_to_Z_Complete_Build_Plan.pdf` compared with the existing `Prompts.zip` docs and the progress recorded in `HANDOFF.md`. Nothing was run in the repo; these are documents only.

## 1. Plan versus repo: decisions
| Topic | Plan says | Repo had | Now |
|---|---|---|---|
| Team | 3 members | 3 (A, B, C) | 3 members kept |
| Texts | 8 original texts, 100-130 words | 4 public speeches done, T05-T06 open | 8: T01-T04 kept; T05-T08 original team texts (D1) |
| Speakers | 12, split S01-S08 / S09-S10 / S11-S12 | 3 teammates + originals | S01-S12 with the same split rule (`speaker_split`) |
| GOOD recordings | 96 (12 x 8) | 4 originals | core target T05-T08 x available speakers + teammates on T01-T04; 96 stays a stretch (T01-T04 are 2-4 min) |
| Flaw families | 6 | 12 types | 14 types grouped into the same 6 families; emphasis promoted to core |
| Severity | 0-4 | L0-L5 (30 files exist) | files keep L1-L5; reports map to 0-4 (L1-L2 = 1, L3 = 2, L4 = 3, L5 = 4) |
| Flawed set size | 400-600 | ~290 planned | ~59/text x 8 = ~470 synthetic + human takes |
| Splits | by speaker; unseen text T07-T08 | by text only | both, plus a `stress` text split (T07, T08, forced Mode B) |
| Model | per-family XGBoost | z-score rules, no ML | rules stay primary; optional learned scorer B6f (hybrid) |
| Windows | 2-3 s overlapping | W=6 words, stride 1 | same (about 2-3 s); now stated explicitly |
| Output | confidence, deviation % | severity only | optional `confidence`, `deviation_pct` (contract v1.1) |
| Modes | reference / no-reference (+ optional C) | reference / prior | same; UI label "No-reference mode"; Mode C stays a non-goal |
| Stress tests | explicit matrix + plots | gate list only | `STRESS_TESTS.md` (S1-S13) |
| Recording | protocol, QC, naming | "see guide" (missing) | `RECORDING_PROTOCOL.md` |
| Docs in GitHub | dataset.md, methodology.md, scoring.md, demo.md | none | tasks D6-D9 |
| Schedule | 20 days | 10 days | 10 days kept (Day 1 = 2026-10-03, today = Day 4); set the real deadline |

## 2. Files changed or added
Changed: PROJECT_BRIEF, ARCHITECTURE, CONTRACTS (v1.1 proposal), FLAW_SPEC, TASKS, HANDOFF (appended, old entries untouched), PROMPTS (P17-P22 added), DASHBOARD_PROMPTS (section 6 added), SIMPLE_EXPLANATIONS, roles A/B/C.
Added: RECORDING_PROTOCOL.md, STRESS_TESTS.md, CHANGES.md.
Line endings: ARCHITECTURE, HANDOFF and TASKS kept CRLF as in your originals.

## 3. Progress state recorded (from HANDOFF evidence)
Done: A1, A2, B1-B5, B4b, C1-C3. Newly ticked: C3 (log shows it done). Un-ticked to `[~]`: C4 (no log entry, M1 open), A3 (only 30 files confirmed). Detection quality is the biggest technical gap (dev F1 0.065).

## 4. Inconsistencies found in the old docs (fixed or logged)
- TASKS said T04 = Gitanjali 35; the decision log says T04 = Lincoln (fixed in TASKS).
- `FILLER_WORD` (B4b log) vs `FILLERS` (contract): canonical name is FILLERS.
- C4 ticked without a log; C3 done but unticked.
- `test_dataset_prep.py` failing locally (from the C2 log): logged as a known issue.
- FLAT_ENERGY had no parameters; STRESS_MISSING was bonus with no detector or params; both now specified (values marked "proposed").
- The emphasis dimension had no defined signal; ARCHITECTURE 4.2 proposes one.
- Licence risk: T01-T04 audio is committed in git; check redistribution rights before going public.

## 5. What needs a human decision
1. Approve or reject the contract v1.1 (HANDOFF section 3). All three members must agree before committing `CONTRACTS.md`.
2. Confirm the real submission deadline; this doc set assumes Day 6 = 2026-10-08 is the freeze.
3. Confirm the 3 members are comfortable with the updated plan.
4. Keep L1-L5 (recommended, avoids regenerating files) or move to 0-4.
5. Decide what to do about T01-T04 audio licences.
6. Review the "(proposed)" numbers in FLAW_SPEC (FLAT_ENERGY, STRESS_* parameters) and the targets in B5b (F1 >= 0.5 at L4-L5, FPR <= 1 region/min).

## 6. Edits to make by hand in `AGENTS.md` (not in the zip, so not changed)
1. Section 1/team: keep 3 members.
2. Section 5 ownership: Member A paths: `dataset/QC_LOG.md`, `dataset/texts/T05-T08.txt`, `docs/{dataset,methodology,scoring,demo}.md`, `docs/technical_document/`, `docs/RECORDING_PROTOCOL.md`.
3. Member B paths: add `src/speechcoach/models/`, `scripts/stress_test.py`, `scripts/train_window_model.py`. Member A paths: add `scripts/make_stress_variants.py`, `dataset/metadata/recordings.csv`.
4. Reading order for every session: add `docs/STRESS_TESTS.md` and `docs/RECORDING_PROTOCOL.md` where relevant, and "check the TASKS status board".
5. Rules: "splits are by speaker and text"; "canonical enum FILLERS"; "no clip of one speaker in two speaker splits".
6. Where you copy these files: they live in `docs/` in the repo (roles in `docs/roles/`); the zip keeps them flat.
