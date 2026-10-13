## Phase 5 Evaluation Report

### False Positives (Good Files)
**Total FP/min**: 2.75
- S04: 2.75 FP/min (20 FPs)

### Recall by Flaw Type and Severity
| Flaw | Severity | Recall (IoU>=0.5) | Recall (Time +-1.0s) |
|---|---|---|---|
| PACE_FAST | L2 | 100.0% (1/1) | 100.0% (1/1) |
| PACE_FAST | L3 | 100.0% (1/1) | 100.0% (1/1) |
| PACE_FAST | L4 | 100.0% (1/1) | 100.0% (1/1) |
| PACE_SLOW | L2 | 0.0% (0/1) | 0.0% (0/1) |
| PACE_SLOW | L3 | 100.0% (1/1) | 100.0% (1/1) |
| PACE_SLOW | L4 | 100.0% (1/1) | 100.0% (1/1) |

### Region Lengths vs GT Lengths (IoU >= 0.5 but +-1.0s Low)
None (all high-IoU detections satisfied +-1.0s tolerance).