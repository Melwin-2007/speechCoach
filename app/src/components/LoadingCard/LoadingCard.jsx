import React, { useState, useEffect } from "react";
import { Loader2, X } from "lucide-react";
import styles from "./LoadingCard.module.css";

const STAGES = [
  { label: "Decoding audio waveform & computing LUFS loudness", weight: "15%" },
  { label: "Parsing transcript & tokenizing words", weight: "28%" },
  { label: "Forced phonetic alignment (torchaudio MMS_FA)", weight: "45%" },
  { label: "Extracting F0 pitch & harmonic-to-noise ratio", weight: "62%" },
  { label: "Building baseline deviation signals (z-scores)", weight: "78%" },
  { label: "Segmenting flaw regions across 7 acoustic dimensions", weight: "90%" },
  { label: "Synthesizing scores & evidence metrics", weight: "98%" },
];

export default function LoadingCard({ onCancel }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const start = Date.now();
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - start) / 100) / 10);
    }, 100);
    return () => clearInterval(interval);
  }, []);

  const formattedElapsed = elapsed.toFixed(1) + "s";

  return (
    <div className={styles.loadingContainer}>
      <div className={styles.headerRow}>
        <div className={styles.spinnerRow}>
          <Loader2 size={24} className={styles.spinIcon} />
          <div>
            <h3 className="h3" style={{ margin: 0 }}>Analyzing Speech</h3>
            <p className="body-sm" style={{ color: "var(--muted)", margin: "4px 0 0 0" }}>
              Evaluating delivery against reference baselines
            </p>
          </div>
        </div>
        <div className={styles.timerBadge}>
          <span className="mono-sm" style={{ color: "var(--ink)" }}>{formattedElapsed}</span>
        </div>
      </div>

      <div className={styles.honestBars}>
        {STAGES.map((stage, idx) => {
          const isActive = elapsed > idx * 0.4;
          return (
            <div key={idx} className={styles.barWrap}>
              <div className={styles.labelRow}>
                <span className="small" style={{ color: isActive ? "var(--ink)" : "var(--muted)" }}>
                  {stage.label}
                </span>
                <span className="mono-sm" style={{ color: "var(--faint)" }}>
                  {stage.weight}
                </span>
              </div>
              <div className={styles.barBg}>
                <div
                  className={styles.barFill}
                  style={{
                    width: isActive ? stage.weight : "0%",
                    transition: "width 0.6s ease",
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {onCancel && (
        <div className={styles.footerRow}>
          <button type="button" className={styles.cancelBtn} onClick={onCancel}>
            <X size={16} /> Cancel Analysis
          </button>
        </div>
      )}
    </div>
  );
}
