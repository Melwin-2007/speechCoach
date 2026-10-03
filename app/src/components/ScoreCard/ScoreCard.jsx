import React from "react";
import {
  Gauge,
  Pause,
  Activity,
  Volume2,
  Target,
  Ear,
  Mic,
  CheckCircle,
} from "lucide-react";
import { DIMENSIONS } from "../../lib/colors";
import { scoreLabel, fmtNum } from "../../lib/format";
import styles from "./ScoreCard.module.css";

const ICON_MAP = {
  Gauge,
  Pause,
  Activity,
  Volume2,
  Target,
  Ear,
  Mic,
};

export default function ScoreCard({ scores, meta, flawCount = 0 }) {
  if (!scores) return null;

  const overall = scores.overall || 0;
  const radius = 54;
  const strokeWidth = 12;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (overall / 100) * circumference;

  return (
    <div className={styles.scoreCard}>
      {/* Left: Overall Score Ring */}
      <div className={styles.ringSection}>
        <div className={styles.ringWrapper}>
          <svg className={styles.ringSvg} width="140" height="140" viewBox="0 0 140 140">
            <circle
              cx="70"
              cy="70"
              r={radius}
              className={styles.ringTrack}
              strokeWidth={strokeWidth}
            />
            <circle
              cx="70"
              cy="70"
              r={radius}
              className={styles.ringProgress}
              strokeWidth={strokeWidth}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
            />
          </svg>
          <div className={styles.ringContent}>
            <span className={styles.scoreNumber}>{Math.round(overall)}</span>
            <span className={styles.scoreMax}>/100</span>
          </div>
        </div>
        <div className={styles.scoreMeta}>
          <div className={styles.scoreBadge}>{scoreLabel(overall)}</div>
          <div className={styles.flawSummary}>
            {flawCount === 0 ? (
              <span className={styles.noFlaws}>
                <CheckCircle size={14} className={styles.checkIcon} /> Within baseline tolerances
              </span>
            ) : (
              <span>{flawCount} {flawCount === 1 ? "flaw flagged" : "flaws flagged"}</span>
            )}
          </div>
        </div>
      </div>

      {/* Right: 7 Dimension Score Progress Bars */}
      <div className={styles.dimensionsSection}>
        <h3 className={styles.sectionHeading}>Dimension Scores</h3>
        <div className={styles.dimGrid}>
          {Object.entries(scores.dimensions || {}).map(([dimKey, scoreVal]) => {
            const dimMeta = DIMENSIONS[dimKey] || { label: dimKey, color: "var(--ink)", tint: "var(--paper-2)" };
            const IconComp = ICON_MAP[dimMeta.icon] || Gauge;
            const clampedScore = Math.max(0, Math.min(100, scoreVal));

            return (
              <div key={dimKey} className={styles.dimItem}>
                <div className={styles.dimHeader}>
                  <div className={styles.dimLabelGroup}>
                    <div className={styles.dimIconWrap} style={{ backgroundColor: dimMeta.tint, color: dimMeta.color }}>
                      <IconComp size={14} />
                    </div>
                    <span className={styles.dimName}>{dimMeta.label}</span>
                  </div>
                  <span className={styles.dimScoreMono}>{Math.round(clampedScore)}</span>
                </div>
                <div className={styles.track}>
                  <div
                    className={styles.bar}
                    style={{
                      width: `${clampedScore}%`,
                      backgroundColor: dimMeta.color,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
