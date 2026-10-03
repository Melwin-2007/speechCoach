import React from "react";
import { wordBand, fmtTime } from "../../lib/format";
import styles from "./TranscriptPanel.module.css";

const BAND_BG_COLORS = {
  fine: "transparent",
  minor: "var(--butter)",
  moderate: "var(--tangerine)",
  major: "var(--blush)",
};

const BAND_TEXT_COLORS = {
  fine: "var(--ink)",
  minor: "var(--ink)",
  moderate: "var(--ink)",
  major: "var(--bad)",
};

export default function TranscriptPanel({
  words = [],
  currentTime = 0,
  selectedFlaw,
  onWordClick,
}) {
  if (!words || words.length === 0) return null;

  return (
    <div className={styles.transcriptCard}>
      <div className={styles.header}>
        <h2 className={styles.title}>Spoken Transcript Alignment</h2>
        <span className={styles.subtitle}>
          Tokens are shaded by acoustic deviation. Click any word to listen to its pronunciation.
        </span>
      </div>

      <div className={styles.wordFlow}>
        {words.map((word) => {
          const band = wordBand(word.z);
          const isCurrentlyPlaying =
            currentTime >= word.start && currentTime <= word.end;
          const isInsideSelectedFlaw =
            selectedFlaw &&
            word.i >= selectedFlaw.first_word &&
            word.i <= selectedFlaw.last_word;

          return (
            <span
              key={word.i}
              className={`
                ${styles.wordSpan}
                ${isCurrentlyPlaying ? styles.wordPlaying : ""}
                ${isInsideSelectedFlaw ? styles.wordInsideFlaw : ""}
              `}
              style={{
                backgroundColor: BAND_BG_COLORS[band],
                color: BAND_TEXT_COLORS[band],
              }}
              onClick={() => onWordClick && onWordClick(word)}
              title={`${word.w}: ${fmtTime(word.start)} – ${fmtTime(word.end)} (${band})`}
            >
              {word.w}
              {word.punct || " "}
            </span>
          );
        })}
      </div>
    </div>
  );
}
