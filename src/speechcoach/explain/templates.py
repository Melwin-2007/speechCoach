TEMPLATES = {
    "PACE_FAST": ("Speaking rate rose to {value:.1f} {unit}, {dev_peak:.1f} robust standard deviations "
                  "{ref}{pct_str}.{band_str}"),
    "PACE_SLOW": ("Speaking rate dropped to {value:.1f} {unit}, {dev_peak:.1f} robust standard deviations "
                  "{ref}{pct_str}.{band_str}"),
    "PITCH_FLAT": ("Pitch variation fell to {value:.1f} {unit}, {dev_peak:.1f} robust standard deviations "
                   "{ref}{band_str}, making the delivery sound monotone."),
    "PITCH_ERRATIC": ("Pitch standard deviation spiked to {value:.1f} {unit}, {dev_peak:.1f} robust standard deviations "
                      "{ref}{band_str}."),
    "ENERGY_LOW": ("Volume dropped to {value:.1f} {unit}, {dev_peak:.1f} robust standard deviations {ref}{band_str}."),
    "ENERGY_FLAT": ("Dynamics were flat, {dev_peak:.1f} robust standard deviations {ref}{band_str}."),
    "PAUSE_LONG": ("Pause duration was {value:.1f} {unit}, {dev_peak:.1f} robust standard deviations {ref}{band_str}."),
    "PAUSE_MISSING": ("Pause was missing or too short, {dev_peak:.1f} robust standard deviations {ref}{band_str}.")
}

def explain(evidence: dict) -> str:
    """Generate causal explanations from templates."""
    r = evidence.copy()
    
    direction = r.get("direction", "above")
    if r.get("source") == "local":
        r["ref"] = f"{direction} your own median"
    else:
        r["ref"] = f"{direction} the typical range for strong speakers"
        
    band = r.get("band")
    if band:
        unit = r.get('unit', '')
        r["band_str"] = f" (typical range {band[0]:.1f} to {band[1]:.1f} {unit})"
    else:
        r["band_str"] = ""
        
    pct = r.get("pct")
    if pct is not None:
        r["pct_str"] = f" ({pct:+.0f}%)"
    else:
        r["pct_str"] = ""
        
    flaw = r.get("flaw", "")
    template = TEMPLATES.get(flaw, "Detected {flaw} deviation.")
    
    try:
        return template.format(**r).replace(" .", ".")
    except Exception as e:
        return f"Detected {flaw} deviation."
