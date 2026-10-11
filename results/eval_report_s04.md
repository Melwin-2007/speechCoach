## Phase 5 Evaluation Report

### False Positives (Good Files)
**Total FP/min**: 1.76
- S04: 1.76 FP/min (8 FPs)

### Recall by Flaw Type and Severity
| Flaw | Severity | Recall (IoU>=0.5) | Recall (Time +-1.0s) |
|---|---|---|---|
| ENERGY_LOW | L2 | 0.0% (0/5) | 0.0% (0/5) |
| ENERGY_LOW | L3 | 80.0% (4/5) | 80.0% (4/5) |
| ENERGY_LOW | L4 | 100.0% (5/5) | 100.0% (5/5) |
| PACE_FAST | L2 | 0.0% (0/5) | 0.0% (0/5) |
| PACE_FAST | L3 | 0.0% (0/5) | 0.0% (0/5) |
| PACE_FAST | L4 | 60.0% (3/5) | 60.0% (3/5) |
| PACE_SLOW | L2 | 0.0% (0/5) | 0.0% (0/5) |
| PACE_SLOW | L3 | 0.0% (0/5) | 0.0% (0/5) |
| PACE_SLOW | L4 | 40.0% (2/5) | 40.0% (2/5) |
| PAUSE_LONG | L2 | 0.0% (0/5) | 0.0% (0/5) |
| PAUSE_LONG | L3 | 40.0% (2/5) | 0.0% (0/5) |
| PAUSE_LONG | L4 | 80.0% (4/5) | 80.0% (4/5) |
| PITCH_ERRATIC | L2 | 40.0% (2/5) | 40.0% (2/5) |
| PITCH_ERRATIC | L3 | 0.0% (0/5) | 0.0% (0/5) |
| PITCH_ERRATIC | L4 | 0.0% (0/5) | 0.0% (0/5) |
| PITCH_FLAT | L2 | 0.0% (0/5) | 0.0% (0/5) |
| PITCH_FLAT | L3 | 20.0% (1/5) | 20.0% (1/5) |
| PITCH_FLAT | L4 | 100.0% (5/5) | 100.0% (5/5) |

### Region Lengths vs GT Lengths (IoU >= 0.5 but +-1.0s Low)
| File | Channel | Severity | IoU | Pred Len (s) | GT Len (s) | Diff (s) |
|---|---|---|---|---|---|---|
| S04_T04_PAUSE_LONG_L3 | PAUSE_LONG | L3 | 0.58 | 3.09 | 1.8 | 1.29 |
| S04_T05_PAUSE_LONG_L3 | PAUSE_LONG | L3 | 0.55 | 3.26 | 1.8 | 1.46 |