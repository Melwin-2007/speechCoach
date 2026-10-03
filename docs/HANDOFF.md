# HANDOFF.md: Shared project memory (append-only)

AI assistants forget everything between chats. **This file is their memory.** Read the newest entries at the start of a session; append at the end. Never delete or rewrite old entries (strike through with `~~text~~` if something becomes wrong).

---
## 1. Current state (humans update this at the evening sync)
- Day: 1
- Last green tag: none
- Milestones: M1 (upload shows real flaw regions): [ ]   M2 (demo mode + explanations): [ ]   Freeze (Day 6): [ ]
- Counts: ideal recordings: 0 | synthetic files: 0 | human flawed: 0
- Latest dev metrics (F1@IoU0.5 / Spearman score-vs-level): n/a
- Biggest risk right now: n/a

## 2. Requests between members
Format: `[date] FROM -> TO: request. Status: open/done`
- (none yet)

## 3. Contract change requests
Format: `[date] who: exact proposed diff to docs/CONTRACTS.md. Approvals: A[ ] B[ ] C[ ]`
- (none yet)

## 4. Decisions log
Format: `[date] decision: reason`
- Stack fixed as in AGENTS.md section 3.
- Dev split T1,T2,T4,T5; test split T3,T6 (never tune on test).
- Focused the primary corpus on the 4 user-provided speeches: T1 (Indian Pep Talk), T2 (Martin Luther King Jr.), T3 (Dr. A.P.J. Abdul Kalam), T4 (Abraham Lincoln), providing a 2-2 accent balance (Indian vs American).
- [2026-10-03] decision: Committed ideal audio files (T1-T4 WAVs, ~23.3 MB) directly to branch a/A1-texts-sources per explicit user instruction so all team members have immediate access to canonical audio.

## 5. Known issues
Format: `[date] who: issue, how to reproduce, status`
- (none yet)

## 6. Session log (newest at the bottom)
Template: copy, fill in, append.
```
### [YYYY-MM-DD HH:MM] Member X, task ID
- Goal:
- Files changed:
- What I ran and what it printed (real output, short):
- Status: done / partial / blocked
- NOT done / open problems:
- How a teammate can verify (exact command):
- Requests for others:
```
