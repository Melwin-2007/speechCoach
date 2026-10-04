import numpy as np

def compute_iou(start1, end1, start2, end2):
    intersection = max(0, min(end1, end2) - max(start1, start2))
    union = max(end1, end2) - min(start1, start2)
    return intersection / union if union > 0 else 0

def match(true_flaws, pred_flaws):
    tp = 0
    fn = 0
    matches = []
    matched_preds = set()
    
    for t_idx, t in enumerate(true_flaws):
        t_start = t.get("start_s", t.get("start", 0))
        t_end = t.get("end_s", t.get("end", 0))
        t_type = t["type"]
        
        best_iou = 0
        best_pred_idx = -1
        
        for i, p in enumerate(pred_flaws):
            if i in matched_preds: continue
            if p["type"] != t_type: continue
            
            iou = compute_iou(t_start, t_end, p["start"], p["end"])
            if iou > best_iou:
                best_iou = iou
                best_pred_idx = i
                
        if best_iou >= 0.5:
            tp += 1
            matched_preds.add(best_pred_idx)
            matches.append((t_idx, best_pred_idx))
        else:
            fn += 1
            
    fp = len(pred_flaws) - len(matched_preds)
    return tp, fp, fn, matches, matched_preds
