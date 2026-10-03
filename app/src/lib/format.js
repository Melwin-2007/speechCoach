/**
 * Format time in seconds to m:ss.s format (e.g. 0:42.1).
 * @param {number} s - Time in seconds.
 * @returns {string} Formatted time string.
 */
export function fmtTime(s) {
  if (s == null || isNaN(s)) return "0:00.0";
  const sign = s < 0 ? "−" : "";
  const absS = Math.abs(s);
  const m = Math.floor(absS / 60);
  const rem = (absS % 60).toFixed(1);
  const [sec, frac] = rem.split(".");
  const paddedSec = sec.padStart(2, "0");
  return `${sign}${m}:${paddedSec}.${frac}`;
}

/**
 * Format a number with a fixed number of decimals and true unicode minus sign (U+2212).
 * @param {number} x - The numeric value.
 * @param {number} d - Number of decimal places (default: 1).
 * @returns {string} Formatted number string.
 */
export function fmtNum(x, d = 1) {
  if (x == null || isNaN(x)) return "—";
  const rounded = Math.abs(x).toFixed(d);
  if (x < 0 && parseFloat(rounded) > 0) {
    return `−${rounded}`;
  }
  return rounded;
}

/**
 * Descriptive label for an overall score (Display only).
 * @param {number} score - Overall score from 0 to 100.
 * @returns {string} Human-friendly display label.
 */
export function scoreLabel(score) {
  if (score >= 85) return "Strong delivery";
  if (score >= 70) return "Good, with a few things to fix";
  if (score >= 50) return "Needs work";
  return "Major problems";
}

/**
 * Maps word z-scores to a severity band based on max |z|.
 * Thresholds: minor >= 2.0, moderate >= 3.0, major >= 4.5. Below 2.0 = fine.
 * @param {object|number} z - Either a z object ({pace, pause, pitch, energy, clarity}) or a single number.
 * @returns {"fine"|"minor"|"moderate"|"major"} Severity band name.
 */
export function wordBand(z) {
  if (z == null) return "fine";
  let maxAbs = 0;
  if (typeof z === "number") {
    maxAbs = Math.abs(z);
  } else if (typeof z === "object") {
    for (const val of Object.values(z)) {
      if (typeof val === "number" && !isNaN(val)) {
        maxAbs = Math.max(maxAbs, Math.abs(val));
      }
    }
  }
  
  if (maxAbs >= 4.5) return "major";
  if (maxAbs >= 3.0) return "moderate";
  if (maxAbs >= 2.0) return "minor";
  return "fine";
}
