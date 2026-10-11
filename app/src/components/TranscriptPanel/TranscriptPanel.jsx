import React, { useMemo } from "react";
import { wordBand, fmtTime } from "../../lib/format";
import styles from "./TranscriptPanel.module.css";

function TranscriptPanel({
  words = [],
  currentTime = 0,
  selectedFlaw,
  onWordClick,
}) {
  // Memoize phrase grouping by punctuation to avoid recalculating on playback ticks
  const phrases = useMemo(() => {
    if (!words || words.length === 0) return [];
    const result = [];
    let currentPhrase = [];

    words.forEach((word) => {
      currentPhrase.push(word);
      if (word.punct && word.punct.match(/[.,?!;:]/)) {
        result.push(currentPhrase);
        currentPhrase = [];
      }
    });
    if (currentPhrase.length > 0) result.push(currentPhrase);
    return result;
  }, [words]);

  if (!words || words.length === 0) return null;

  return (
    <div className={styles.transcriptCard}>
      <div className={styles.header}>
        <h2 className={styles.title}>Spoken Transcript</h2>
        <span className={styles.subtitle}>
          Click a word to hear its delivery. Flaws are underlined.
        </span>
      </div>

      <div className={styles.lyricsContainer}>
        {phrases.map((phrase, pIdx) => (
          <div key={pIdx} className={styles.phrase}>
            {phrase.map((word) => {
              const band = wordBand(word.z);
              const isCurrentlyPlaying =
                currentTime >= word.start && currentTime <= word.end;
              const isInsideSelectedFlaw =
                selectedFlaw &&
                word.i >= selectedFlaw.first_word &&
                word.i <= selectedFlaw.last_word;

              let flawClass = "";
              if (band === "minor") flawClass = styles.flawMinor;
              else if (band === "moderate") flawClass = styles.flawModerate;
              else if (band === "major") flawClass = styles.flawMajor;

              return (
                <span
                  key={word.i}
                  className={`
                    ${styles.wordSpan}
                    ${isCurrentlyPlaying ? styles.wordPlaying : ""}
                    ${isInsideSelectedFlaw ? styles.wordInsideFlaw : ""}
                    ${flawClass}
                  `}
                  onClick={() => onWordClick && onWordClick(word)}
                  title={`${word.w}: ${fmtTime(word.start)} – ${fmtTime(word.end)} (${band})`}
                >
                  {word.w}
                  {word.punct || ""}
                </span>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

export default React.memo(TranscriptPanel);
