## Phase 5 Evaluation Report

### False Positives (Good Files)
**Total FP/min**: 2.35
- S01: 3.28 FP/min (30 FPs)
- S02: 1.33 FP/min (10 FPs)
- S03: 2.02 FP/min (5 FPs)

### Recall by Flaw Type and Severity
| Flaw | Severity | Recall (IoU>=0.5) | Recall (Time +-1.0s) |
|---|---|---|---|
| ENERGY_LOW | L2 | 15.8% (3/19) | 5.3% (1/19) |
| ENERGY_LOW | L3 | 63.2% (12/19) | 68.4% (13/19) |
| ENERGY_LOW | L4 | 94.7% (18/19) | 94.7% (18/19) |
| PACE_FAST | L2 | 21.1% (4/19) | 21.1% (4/19) |
| PACE_FAST | L3 | 36.8% (7/19) | 36.8% (7/19) |
| PACE_FAST | L4 | 78.9% (15/19) | 84.2% (16/19) |
| PACE_SLOW | L2 | 5.3% (1/19) | 0.0% (0/19) |
| PACE_SLOW | L3 | 36.8% (7/19) | 36.8% (7/19) |
| PACE_SLOW | L4 | 100.0% (19/19) | 89.5% (17/19) |
| PAUSE_LONG | L2 | 21.1% (4/19) | 21.1% (4/19) |
| PAUSE_LONG | L3 | 63.2% (12/19) | 47.4% (9/19) |
| PAUSE_LONG | L4 | 84.2% (16/19) | 84.2% (16/19) |
| PITCH_ERRATIC | L2 | 5.3% (1/19) | 5.3% (1/19) |
| PITCH_ERRATIC | L3 | 15.8% (3/19) | 15.8% (3/19) |
| PITCH_ERRATIC | L4 | 21.1% (4/19) | 21.1% (4/19) |
| PITCH_FLAT | L2 | 26.3% (5/19) | 21.1% (4/19) |
| PITCH_FLAT | L3 | 47.4% (9/19) | 47.4% (9/19) |
| PITCH_FLAT | L4 | 68.4% (13/19) | 68.4% (13/19) |

### Region Lengths vs GT Lengths (IoU >= 0.5 but +-1.0s Low)
| File | Channel | Severity | IoU | Pred Len (s) | GT Len (s) | Diff (s) |
|---|---|---|---|---|---|---|
| S01_T01_PAUSE_LONG_L3 | PAUSE_LONG | L3 | 0.61 | 2.96 | 1.8 | 1.16 |
| S01_T02_ENERGY_LOW_L2 | ENERGY_LOW | L2 | 0.56 | 1.6 | 2.84 | 1.24 |
| S01_T04_PACE_SLOW_L4 | PACE_SLOW | L4 | 0.86 | 7.8 | 6.76 | 1.04 |
| S01_T04_ENERGY_LOW_L2 | ENERGY_LOW | L2 | 0.51 | 1.3 | 2.46 | 1.16 |
| S01_T06_PAUSE_LONG_L3 | PAUSE_LONG | L3 | 0.62 | 2.92 | 1.8 | 1.12 |
| S01_T07_PACE_SLOW_L4 | PACE_SLOW | L4 | 0.61 | 2.5 | 4.12 | 1.62 |
| S02_T04_PITCH_FLAT_L2 | PITCH_FLAT | L2 | 0.5 | 1.1 | 2.2 | 1.1 |
| S02_T05_PAUSE_LONG_L3 | PAUSE_LONG | L3 | 0.58 | 3.12 | 1.8 | 1.32 |
| S03_T03_PACE_SLOW_L2 | PACE_SLOW | L2 | 0.59 | 2.4 | 4.08 | 1.68 |