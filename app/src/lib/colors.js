export const DIMENSIONS = {
  pacing:   { label: "Pacing",   color: "var(--c-pacing)",   tint: "var(--c-pacing-tint)",   icon: "Gauge" },
  pausing:  { label: "Pausing",  color: "var(--c-pausing)",  tint: "var(--c-pausing-tint)",  icon: "Pause" },
  pitch:    { label: "Pitch",    color: "var(--c-pitch)",    tint: "var(--c-pitch-tint)",    icon: "Activity" },
  energy:   { label: "Loudness", color: "var(--c-energy)",   tint: "var(--c-energy-tint)",   icon: "Volume2" },
  emphasis: { label: "Emphasis", color: "var(--c-emphasis)", tint: "var(--c-emphasis-tint)", icon: "Target" },
  clarity:  { label: "Clarity",  color: "var(--c-clarity)",  tint: "var(--c-clarity-tint)",  icon: "Ear" },
  fluency:  { label: "Fluency",  color: "var(--c-fluency)",  tint: "var(--c-fluency-tint)",  icon: "Mic" },
};

export const FLAW_TYPES = {
  PACE_FAST:       { dimension: "pacing",   label: "Rushing" },
  PACE_SLOW:       { dimension: "pacing",   label: "Dragging" },
  PAUSE_MISSING:   { dimension: "pausing",  label: "Missing pause" },
  PAUSE_EXCESS:    { dimension: "pausing",  label: "Overlong pause" },
  PAUSE_MISPLACED: { dimension: "pausing",  label: "Awkward pause" },
  MONOTONE:        { dimension: "pitch",    label: "Flat pitch" },
  PITCH_ERRATIC:   { dimension: "pitch",    label: "Wobbly pitch" },
  VOLUME_DROP:     { dimension: "energy",   label: "Volume drop" },
  FLAT_ENERGY:     { dimension: "energy",   label: "Flat loudness" },
  STRESS_MISSING:  { dimension: "emphasis", label: "Missing emphasis" },
  CLARITY:         { dimension: "clarity",  label: "Mumbling" },
  FILLERS:         { dimension: "fluency",  label: "Filler sounds" },
};

export const BANDS = {
  minor: "Minor",
  moderate: "Moderate",
  major: "Major",
};

/**
 * Safe lookup for flaw types that falls back to pacing for unknown types.
 */
export function getFlawMeta(type) {
  return FLAW_TYPES[type] || { dimension: "pacing", label: type };
}
