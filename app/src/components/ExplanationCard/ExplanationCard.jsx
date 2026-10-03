import React, { useState } from "react";
import {
  Gauge,
  Pause,
  Activity,
  Volume2,
  Target,
  Ear,
  Mic,
  Play,
  ChevronDown,
  ChevronUp,
  HelpCircle,
} from "lucide-react";
import { DIMENSIONS, getFlawMeta } from "../../lib/colors";
import { fmtTime, fmtNum } from "../../lib/format";
import styles from "./ExplanationCard.module.css";

const ICON_MAP = {
  Gauge,
  Pause,
  Activity,
  Volume2,
  Target,
  Ear,
  Mic,
};

export default function ExplanationCard({
  flaw,
  onPlayFlaw,
}) {
  const [showMath, setShowMath] = useState(false);

  if (!flaw) {
    return (
      <div className={styles.emptyCard}>
        <span className={styles.emptyText}>Select a flaw to inspect its acoustic explanation and correction steps.</span>
      </div>
    );
  }

  const meta = getFlawMeta(flaw.type);
  const dim = DIMENSIONS[meta.dimension] || DIMENSIONS.pacing;
  const IconComp = ICON_MAP[dim.icon] || Gauge;
  const exp = flaw.explanation || {};
  const ev = flaw.evidence || {};
  const bandName = flaw.band.charAt(0).toUpperCase() + flaw.band.slice(1);

  return (
    <div className={styles.card}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.titleRow}>
          <div className={styles.iconBadge} style={{ backgroundColor: dim.tint, color: dim.color }}>
            <IconComp size={20} />
          </div>
          <div>
            <h3 className={styles.flawHeading}>{meta.label}</h3>
            <div className={styles.timeMono}>
              {fmtTime(flaw.start)} – {fmtTime(flaw.end)} ({fmtNum(flaw.end - flaw.start, 1)}s duration)
            </div>
          </div>
        </div>
        <span className={`${styles.bandPill} ${styles[`pill_${flaw.band}`]}`}>
          {bandName}
        </span>
      </div>

      {/* 5 Structural Blocks */}
      <div className={styles.blockSection}>
        {/* 1. What we measured */}
        <div className={styles.block}>
          <span className={styles.blockLabel}>1. What we measured</span>
          <p className={styles.blockText}>{exp.observed || "Acoustic variation across this segment."}</p>
        </div>

        {/* 2. How far off */}
        <div className={styles.block}>
          <span className={styles.blockLabel}>2. How far off</span>
          <p className={styles.blockText}>{exp.deviation || `Deviation z-score of ${fmtNum(ev.z, 1)}.`}</p>
        </div>

        {/* 3. Where */}
        <div className={styles.block}>
          <div className={styles.whereRow}>
            <div>
              <span className={styles.blockLabel}>3. Where</span>
              <p className={styles.blockText}>{exp.where || `Between ${fmtTime(flaw.start)} and ${fmtTime(flaw.end)}.`}</p>
            </div>
            {onPlayFlaw && (
              <button
                type="button"
                className={styles.playPartBtn}
                onClick={() => onPlayFlaw(flaw)}
              >
                <Play size={14} /> Play this part
              </button>
            )}
          </div>
        </div>

        {/* 4. Why it matters */}
        <div className={styles.block}>
          <span className={styles.blockLabel}>4. Why it matters</span>
          <p className={styles.blockText}>{exp.why || "Affects listener engagement, clarity, or comprehension."}</p>
        </div>

        {/* 5. How to fix it (Butter Highlight) */}
        <div className={styles.fixPanel}>
          <span className={styles.fixLabel}>5. How to fix it</span>
          <p className={styles.fixText}>{exp.fix || "Adjust inflection, rhythm, or pacing to align with baseline cadence."}</p>
        </div>
      </div>

      {/* Math Disclosure */}
      <div className={styles.mathSection}>
        <button
          type="button"
          className={styles.mathToggleBtn}
          onClick={() => setShowMath(!showMath)}
        >
          <div className={styles.mathBtnLabel}>
            <HelpCircle size={15} />
            <span>Show the math</span>
          </div>
          {showMath ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>

        {showMath && (
          <div className={styles.mathPanel}>
            <div className={styles.mathGrid}>
              <div className={styles.mathCol}>
                <span className={styles.colLabel}>You</span>
                <span className={styles.colVal}>{fmtNum(ev.participant, 1)} <span className={styles.unit}>{ev.unit}</span></span>
              </div>
              <div className={styles.mathCol}>
                <span className={styles.colLabel}>Reference</span>
                <span className={styles.colVal}>{fmtNum(ev.baseline, 1)} <span className={styles.unit}>{ev.unit}</span></span>
              </div>
              <div className={styles.mathCol}>
                <span className={styles.colLabel}>Difference (z)</span>
                <span className={styles.colVal} style={{ color: "var(--bad)" }}>
                  {fmtNum(ev.z, 1)} <span className={styles.unit}>σ</span>
                </span>
              </div>
            </div>

            <p className={styles.mathExplanation}>
              <strong>z</strong> compares your difference with how much two strong speakers normally differ. Beyond about 2.0σ it becomes perceptible to listeners.
            </p>
            <div className={styles.formulaBox}>
              <code>z = (your value − reference value) ÷ normal spread (σ)</code>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
