import React, { useState } from "react";
import { wordBand, fmtTime, fmtNum } from "../../lib/format";
import styles from "./WordRibbon.module.css";

const BAND_COLORS = {
  fine: "var(--sev-0)",
  minor: "var(--sev-1)",
  moderate: "var(--sev-2)",
  major: "var(--sev-4)",
};

export default function WordRibbon({
  words = [],
  duration = 58.4,
  selectedFlaw,
  onSelectWord,
}) {
  const [hoveredWord, setHoveredWord] = useState(null);

  if (!words || words.length === 0) return null;

  return (
    <div className={styles.ribbonContainer}>
      <div className={styles.headerRow}>
        <span className={styles.label}>Acoustic Deviation Pulse</span>
        <div className={styles.legend}>
          <span className={styles.legendItem}>
            <span className={styles.swatch} style={{ backgroundColor: "var(--sev-0)" }} /> Fine
          </span>
          <span className={styles.legendItem}>
            <span className={styles.swatch} style={{ backgroundColor: "var(--sev-1)" }} /> Minor
          </span>
          <span className={styles.legendItem}>
            <span className={styles.swatch} style={{ backgroundColor: "var(--sev-2)" }} /> Moderate
          </span>
          <span className={styles.legendItem}>
            <span className={styles.swatch} style={{ backgroundColor: "var(--sev-4)" }} /> Major
          </span>
        </div>
      </div>

      <div className={styles.tooltipArea}>
        {hoveredWord ? (
          <div className={styles.wordTooltip}>
            <span className={styles.tooltipWord}>"{hoveredWord.w}{hoveredWord.punct || ""}"</span>
            <span className="mono-sm">{fmtTime(hoveredWord.start)} – {fmtTime(hoveredWord.end)}</span>
            {hoveredWord.z && (
              <span className="small" style={{ color: "var(--muted)", fontWeight: 500 }}>
                Pace: {fmtNum(hoveredWord.z.pace, 1)} · Pitch: {fmtNum(hoveredWord.z.pitch, 1)} · Energy: {fmtNum(hoveredWord.z.energy, 1)}
              </span>
            )}
          </div>
        ) : (
          <div className={styles.wordTooltipPlaceholder}>Hover over a pulse block to see acoustic metrics</div>
        )}
      </div>

      <div className={styles.trackWrapper}>
        <div className={styles.track}>
          {words.map((word) => {
            const band = wordBand(word.z);
            const leftPct = Math.max(0, (word.start / duration) * 100);
            
            // Ensure minimum visual width so tiny words aren't invisible
            const rawWidth = ((word.end - word.start) / duration) * 100;
            const widthPct = Math.max(0.2, rawWidth); 
            
            const isInsideSelectedFlaw =
              selectedFlaw &&
              word.i >= selectedFlaw.first_word &&
              word.i <= selectedFlaw.last_word;

            // Height indicates severity
            let heightPct = "24%";
            if (band === "minor") heightPct = "45%";
            else if (band === "moderate") heightPct = "75%";
            else if (band === "major") heightPct = "100%";

            return (
              <div
                key={word.i}
                className={`${styles.wordBlock} ${isInsideSelectedFlaw ? styles.wordInsideFlaw : ""}`}
                style={{
                  left: `${leftPct}%`,
                  width: `${widthPct}%`,
                  height: heightPct,
                  backgroundColor: BAND_COLORS[band] || "var(--sev-0)",
                }}
                onMouseEnter={() => setHoveredWord(word)}
                onMouseLeave={() => setHoveredWord(null)}
                onClick={() => onSelectWord && onSelectWord(word)}
                title={`${word.w}: ${fmtTime(word.start)} – ${fmtTime(word.end)} (${band})`}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
}
