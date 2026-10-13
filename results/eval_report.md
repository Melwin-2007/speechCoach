## Phase 5 Evaluation Report

### False Positives (Good Files)
**Total FP/min**: 0.86
- S01: 0.76 FP/min (7 FPs)
- S02: 0.80 FP/min (6 FPs)
- S03: 0.40 FP/min (1 FPs)
- S05: 1.19 FP/min (9 FPs)

### Recall by Flaw Type and Severity
| Flaw | Severity | Recall (IoU>=0.5) | Recall (Time +-1.0s) |
|---|---|---|---|
| PACE_FAST | L2 | 0.0% (0/1) | 0.0% (0/1) |
| PACE_FAST | L3 | 0.0% (0/1) | 0.0% (0/1) |
| PACE_FAST | L4 | 100.0% (1/1) | 100.0% (1/1) |
| PACE_SLOW | L2 | 0.0% (0/1) | 0.0% (0/1) |
| PACE_SLOW | L3 | 0.0% (0/1) | 0.0% (0/1) |
| PACE_SLOW | L4 | 100.0% (1/1) | 100.0% (1/1) |
| PAUSE_LONG | L2 | 0.0% (0/1) | 0.0% (0/1) |
| PAUSE_LONG | L3 | 100.0% (1/1) | 0.0% (0/1) |
| PAUSE_LONG | L4 | 100.0% (1/1) | 100.0% (1/1) |
| PITCH_ERRATIC | L2 | 0.0% (0/1) | 0.0% (0/1) |
| PITCH_ERRATIC | L3 | 0.0% (0/1) | 0.0% (0/1) |
| PITCH_ERRATIC | L4 | 100.0% (1/1) | 100.0% (1/1) |
| PITCH_FLAT | L2 | 0.0% (0/1) | 0.0% (0/1) |
| PITCH_FLAT | L3 | 0.0% (0/1) | 0.0% (0/1) |
| PITCH_FLAT | L4 | 0.0% (0/1) | 0.0% (0/1) |

### Region Lengths vs GT Lengths (IoU >= 0.5 but +-1.0s Low)
| File | Channel | Severity | IoU | Pred Len (s) | GT Len (s) | Diff (s) |
|---|---|---|---|---|---|---|
| S01_T01_PAUSE_LONG_L3 | PAUSE_LONG | L3 | 0.61 | 2.96 | 1.8 | 1.16 |