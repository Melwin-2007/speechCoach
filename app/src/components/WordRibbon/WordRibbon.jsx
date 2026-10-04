import React, { useState } from "react";
import { wordBand, fmtTime, fmtNum } from "../../lib/format";
import styles from "./WordRibbon.module.css";

const BAND_COLORS = {
  fine: "var(--ok)",
  minor: "var(--butter)",
  moderate: "var(--tangerine)",
  major: "var(--bad)",
};

const BAND_BG_COLORS = {
  fine: "var(--mint)",
  minor: "var(--butter)",
  moderate: "var(--tangerine)",
  major: "var(--blush)",
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
        <span className={styles.label}>Word Alignment & Acoustic Alignment Ribbon</span>
        <div className={styles.legend}>
          <span className={styles.legendItem}>
            <span className={styles.swatch} style={{ backgroundColor: "var(--mint)" }} /> Fine (|z| &lt; 2)
          </span>
          <span className={styles.legendItem}>
            <span className={styles.swatch} style={{ backgroundColor: "var(--butter)" }} /> Minor (z ≥ 2)
          </span>
          <span className={styles.legendItem}>
            <span className={styles.swatch} style={{ backgroundColor: "var(--tangerine)" }} /> Moderate (z ≥ 3)
          </span>
          <span className={styles.legendItem}>
            <span className={styles.swatch} style={{ backgroundColor: "var(--blush)", border: "1px solid var(--bad)" }} /> Major (z ≥ 4.5)
          </span>
        </div>
      </div>

      <div className={styles.tooltipArea}>
        {hoveredWord ? (
          <div className={styles.wordTooltip}>
            <span className={styles.tooltipWord}>"{hoveredWord.w}{hoveredWord.punct || ""}"</span>
            <span className="mono-sm">{fmtTime(hoveredWord.start)} – {fmtTime(hoveredWord.end)}</span>
            {hoveredWord.z && (
              <span className="small" style={{ color: "var(--ink-2)" }}>
                Pace: {fmtNum(hoveredWord.z.pace, 1)} · Pitch: {fmtNum(hoveredWord.z.pitch, 1)} · Energy: {fmtNum(hoveredWord.z.energy, 1)}
              </span>
            )}
          </div>
        ) : (
          <div className={styles.wordTooltipPlaceholder}>Hover over a word block to see details</div>
        )}
      </div>

      <div className={styles.track}>
        {words.map((word) => {
          const band = wordBand(word.z);
          const leftPct = Math.max(0, (word.start / duration) * 100);
          const widthPct = Math.max(0.3, ((word.end - word.start) / duration) * 100);
          const isInsideSelectedFlaw =
            selectedFlaw &&
            word.i >= selectedFlaw.first_word &&
            word.i <= selectedFlaw.last_word;

          return (
            <div
              key={word.i}
              className={`${styles.wordBlock} ${isInsideSelectedFlaw ? styles.wordInsideFlaw : ""}`}
              style={{
                left: `${leftPct}%`,
                width: `${widthPct}%`,
                backgroundColor: BAND_BG_COLORS[band] || "var(--mint)",
                borderColor: BAND_COLORS[band] || "var(--ok)",
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
  );
}
