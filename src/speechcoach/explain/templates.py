def explain(region: dict, evidence: dict) -> dict:
    """
    Generate deterministic explanation for a flaw region.
    """
    flaw_type = region["type"]
    obs = evidence["participant"]
    base = evidence["baseline"]
    z = evidence["z"]
    unit = evidence.get("unit", "")
    
    # Format values
    obs_str = f"{obs:.2f}{unit}"
    base_str = f"{base:.2f}{unit}"
    
    where = f"between {region['start']:.1f}s and {region['end']:.1f}s"
    
    deviation = f"Your value was {obs_str} compared to the baseline of {base_str} (z-score: {z:.1f})."
    
    why_fix_map = {
        "PACE_FAST": {
            "why": "Speaking too quickly makes it hard for the audience to digest your points.",
            "fix": "Focus on enunciating each word and pausing between ideas."
        },
        "PACE_SLOW": {
            "why": "Speaking too slowly can cause the audience to lose interest.",
            "fix": "Try to speak at a more conversational, natural tempo."
        },
        "PAUSE_MISSING": {
            "why": "Missing pauses at punctuation blurs sentences together.",
            "fix": "Take a breath at commas and full stops."
        },
        "PAUSE_EXCESS": {
            "why": "Unusually long pauses can feel awkward or like you forgot your lines.",
            "fix": "Keep pauses under a second unless intentionally for dramatic effect."
        },
        "PAUSE_MISPLACED": {
            "why": "Pausing mid-phrase breaks the natural flow of the sentence.",
            "fix": "Group words by meaning and only pause at boundaries."
        },
        "MONOTONE": {
            "why": "Flat pitch makes the delivery sound robotic or disengaged.",
            "fix": "Use pitch variations to highlight important words."
        },
        "PITCH_ERRATIC": {
            "why": "Unnatural pitch variations can be distracting.",
            "fix": "Keep your pitch centered around your natural speaking voice."
        },
        "VOLUME_DROP": {
            "why": "Trailing off makes the end of sentences hard to hear.",
            "fix": "Maintain energy and breath support all the way through the phrase."
        },
        "FLAT_ENERGY": {
            "why": "Lack of loudness dynamics makes the speech less engaging.",
            "fix": "Vary your volume to emphasize key points."
        },
        "CLARITY": {
            "why": "Mumbling or poor articulation reduces comprehensibility.",
            "fix": "Open your mouth more and enunciate consonants clearly."
        },
        "FILLERS": {
            "why": "Filler words or sounds distract from your message.",
            "fix": "Replace fillers with a silent pause."
        }
    }
    
    mapping = why_fix_map.get(flaw_type, {"why": "This deviates from ideal delivery.", "fix": "Try to match the baseline."})
    
    return {
        "observed": obs_str,
        "deviation": deviation,
        "where": where,
        "why": mapping["why"],
        "fix": mapping["fix"]
    }
