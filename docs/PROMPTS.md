# PROMPTS.md: Prompt library (copy, fill the <PLACEHOLDERS>, paste into your AI)

How to use: start a NEW chat per task. Paste **P0** first. Wait for the AI's plan. Approve with **P2**. After it reports, run the checks yourself. Keep each chat focused on one task ID.

Replace `<X>` with your letter and role file:
- A -> `docs/roles/MEMBER_A_DATA.md`
- B -> `docs/roles/MEMBER_B_PIPELINE.md`
- C -> `docs/roles/MEMBER_C_APP.md`

---
## P0. Session opener (ALWAYS first)
```
You are working on the SpeechCoach hackathon repo. I am Member <X>.
Read these files fully before anything else, in this order:
1. AGENTS.md
2. docs/CONTRACTS.md
3. <my role file>
4. The task <TASK_ID> in docs/TASKS.md
5. The last 3 entries of docs/HANDOFF.md
Also skim docs/ARCHITECTURE.md, docs/FLAW_SPEC.md, docs/STRESS_TESTS.md and docs/RECORDING_PROTOCOL.md if relevant to the task. Check docs/TASKS.md status board first: a task marked [~] is unverified.

Task: <TASK_ID> <one-line description>.
Extra instructions: <anything specific, or "none">.

Do NOT write code yet. First reply with:
(a) the task in your own words,
(b) the exact files you will create or edit (all inside my ownership area),
(c) the tests you will write and what they assert,
(d) risks and anything in the docs that is unclear or contradictory,
(e) questions for me (max 3).
Then wait for me to say "go".
```

## P1. Plan-only follow-up (if the plan is too big)
```
That plan is too large. Split it into steps of at most ~3 files each. Give me the step list, then do ONLY step 1 after I say "go". Do not touch anything outside step 1.
```

## P2. Approve and implement
```
Go. Implement exactly the approved plan, nothing more.
Rules: smallest change; no refactors of other files; no new dependencies; no contract changes; numbers from configs only.
After implementing: run it on a real file, run `make check`, and report using this format:
1. Files changed (list)
2. Command to run it and its REAL output (paste, shortened)
3. Tests added and their results
4. What is NOT done or not verified
5. Anything you were tempted to change but did not
```

## P3. Verify library APIs before using them
```
Before writing code that uses <library/function>, check the INSTALLED version: run `pip show <library>` and `python -c "import <lib>; help(<lib>.<func>)"`. Show me the real signature and use exactly that. If it differs from your memory, say so. Never guess an API.
```

## P4. Write tests with known answers
```
Write pytest tests for <module/function> using synthetic signals with known answers (for example: a 150 Hz sine wave must give F0 within 2 Hz; a signal with a 0.5 s silence must report a pause of 0.5 s +/- 20 ms; the same signal sped up 1.5x must give a pace signal of about -log(1.5)).
Rules: assert on actually computed values; no hard-coded expected outputs copied from the code; no network; runtime under 10 seconds. Run them and show the output. If a test fails, fix the CODE (or explain precisely why the test is wrong), never weaken the assertion.
```

## P5. Debugging (when something fails)
```
It fails. Do not rewrite anything yet.
Exact error (full traceback):
<PASTE>
What I ran: <command>
Do this:
1. Explain in plain words what the error means.
2. Give your top 3 hypotheses ranked by likelihood, each with one command or print statement that would confirm or reject it.
3. Run the cheapest check first and show the result.
4. Only then propose the smallest fix.
If two attempts fail, stop and summarise what you learned instead of trying a third big change.
```

## P6. Scope guard (when the AI changed too much)
```
You changed files outside the approved plan: <list>. Revert those changes now (use `git checkout -- <file>` only for those specific files, NOT the whole repo), keep only the planned changes, then show me `git status` and `git diff --stat`. From now on touch only the files listed in the plan.
```

## P7. Contract check (run before every pull request)
```
Compare my changes (`git diff main`) against docs/CONTRACTS.md. List every place where a function signature, JSON field name, file name, enum value, unit or sign convention differs from the contract. If there are none, say "No contract violations" and show the evidence (which functions and fields you checked).
```

## P8. Adversarial review (paste into a DIFFERENT AI model than the one that wrote the code)
```
You are a strict senior reviewer for a hackathon repo. Read AGENTS.md and docs/CONTRACTS.md, then review this diff:
<PASTE `git diff main` or the files>
Find: (1) bugs and edge cases (NaN pitch, empty gaps, short files, mismatched transcript), (2) contract or ownership violations, (3) hard-coded numbers that should be in configs, (4) fake or weak tests (tests that cannot fail), (5) non-determinism (random without seed, dict-order dependence, time use), (6) anything that would break reproducibility, (7) security or secrets problems.
Output a table: severity (blocker/major/minor), file:line, problem, suggested fix. Be specific. Do not praise.
```

## P9. "Teach me this code" (everyone must be able to defend their module to the judges)
```
Explain <file or function> to me as if I am a second-year engineering student who must defend it in front of hackathon judges.
Give: (1) what problem it solves in the project, (2) the algorithm in 5 plain-English steps, (3) the formula(s) with each symbol explained, (4) one worked numeric example, (5) 3 questions a judge might ask about it and good answers, (6) its known weaknesses.
Do not change any code.
```

## P10. Session closer (ALWAYS last)
```
We are finishing this session. Do these in order:
1. Run `make check` and show the result.
2. Append an entry to docs/HANDOFF.md using the session template (date, member, task ID, files changed, real outputs, status, what is NOT done, how a teammate can verify, requests).
3. If and only if the task's acceptance criteria in docs/TASKS.md are fully verified, tick that task's checkbox. Otherwise leave it unticked and say why.
4. Print `git status` and a one-line suggested commit message in the format `<area>: <what> (task <ID>)`.
Do not commit; I will.
```

## P11. Resume in a fresh chat (when the chat gets long or confused)
```
New session, same task. Read AGENTS.md, docs/CONTRACTS.md, my role file, task <ID> in docs/TASKS.md, and the last 3 HANDOFF entries. Then run `git status` and `git log --oneline -10` and `git diff --stat`. Summarise: what is already done, what is half-done, what is missing. Propose the next smallest step. Do not write code until I say "go".
```

## P12. Merge conflict help
```
I have a merge conflict in <file>. Show me the conflict regions. For each, explain what main changed and what my branch changed, and propose the resolution that keeps BOTH intentions. Do not resolve anything I did not ask about, and do not touch files outside the conflict.
```

## P13. Recover from "you broke everything"
```
Stop. Do not make further edits. Run `git status`, `git diff --stat`, and `git log --oneline -5`. Tell me the last commit where `make check` passed (use `git stash` to test if needed; do not discard my changes). Propose, in order, the least destructive ways to get back to a working state (selective file revert before branch reset). Wait for my choice.
```

## P14. Write documentation from REAL results only
```
Write <section> of the technical document (target <N> words). Use ONLY facts and numbers from: docs/ARCHITECTURE.md, docs/FLAW_SPEC.md, results/*.csv, dataset/README.md, and the HANDOFF log. If a number is not there, write "[TODO: number]" instead of inventing it. Keep formulas numbered and each symbol defined. Plain academic English, no marketing language.
```

## P15. Tiny-task template for UI work (Member C)
```
Task <ID>. Work ONLY in app/ (and src/speechcoach/api/ if the task says so). Use app/public/mock_result.json as data. Do not compute any analysis in JavaScript. Build <component> with: <exact behaviours>. Show me how to run it and describe what I should see. After I confirm in the browser, we add the next component, one at a time.
```

## P16. Generating synthetic test audio fixtures (any member)
```
Create a helper in tests/fixtures.py that generates (a) a sine wave of given frequency and duration, (b) a "speech-like" signal made of voiced bursts separated by silences of known lengths, (c) a time-stretched version of (b) by a known factor. Deterministic (fixed seed), 16 kHz mono float32, no files written to disk. Add tests proving the helper itself is correct.
```

---
## Prompts added from the Track C build plan (2026-10-06)

## P17. Oracle-vs-real alignment diagnosis (Member B, task B5b)
```
Task B5b. Our dev F1@IoU0.5 is 0.065 and I do not know why. Do NOT change thresholds yet.
1. Run the dev evaluation twice: (a) with word times taken from the label files (oracle), (b) with the real aligner. Same configs, same files. Print precision, recall, F1, mean start/end error, recall by level and by flaw family for both.
2. For 10 missed flaws of level 4-5, print the words, their z-scores per signal and the label region, so we can see whether the signal is weak or the region is lost in merging.
3. Report the false-positive rate on ideal files (regions per minute, share of files with any region).
4. Then propose at most 3 changes (window size, tau per family, region trimming), each with the single number it should improve. Tune on DEV only; test sets stay untouched.
Show real output, not summaries. If oracle F1 is also low, the problem is the detector, not the aligner: say so.
```

## P18. Dataset QC audit (Member A, task D4)
```
You are checking dataset quality. Read docs/RECORDING_PROTOCOL.md section 7, docs/FLAW_SPEC.md section 5 and dataset/metadata/recordings.csv.
List every file where: the file is missing, duration is out of range, sample rate or channels are wrong, the label JSON does not match the file_id, a flaw region is outside the file, words are not monotonic, the speaker appears in two speaker splits, or a text appears in a wrong text split.
Then give a table per text and per flaw family: files, levels present, missing levels. Output a fix list for Member A. Do not change any file.
```

## P19. Stress-test report (Member B, task B6/B7)
```
Run the stress matrix in docs/STRESS_TESTS.md. For each row S1-S13 write the command, the data used, the real numbers, and PASS/FAIL against the expectation in the table. Use only test sets as the matrix says (TEST sets run once). Save results/stress_*.csv and the plots listed in section 2. For every FAIL write one honest sentence on the likely cause. Do not tune anything after this run.
```

## P20. Learned window scorer (Member B, task B6f, optional)
```
Task B6f. Read docs/ARCHITECTURE.md section 11. Build scripts/train_window_model.py and src/speechcoach/models/: one small tree-based classifier per flaw family on z-signal features only (no raw pitch or loudness). Split by SPEAKER (train, val, test per docs/CONTRACTS.md 0.1), never by clip. Fixed random_state. Choose the threshold on validation speakers. Print rules-only vs hybrid precision/recall/F1 on validation. If hybrid does not win, leave it off and say so. Explanations must still come from measured values, not from the model.
```

## P21. Recording-session checklist (Member A, tasks D2/D3)
```
I am coordinating a recording session. Using docs/RECORDING_PROTOCOL.md, produce a one-page checklist for this session: speaker <hN>, texts <list>, flawed cards <letters or none>. Include: setup checks, the take protocol, the exact file names (file_id format from docs/CONTRACTS.md 0.1), the row to add to the recording sheet for each take, and the backup step. Keep it printable. Do not invent steps that are not in the protocol.
```

## P22. Listener test analysis (Member A script and form; task D5)
```
Write scripts/listener_test.py. Input: a CSV of listener ratings (columns: listener, clip, version, rating 1-5). Output: Spearman correlation between the rating and our severity level (per clip and overall), the number of listeners, and a plot. Use only numpy/pandas/scipy; deterministic; test it with a small made-up CSV in tests/.
```
