import React, { useState, useEffect } from "react";
import { Loader2, CheckCircle, Circle, X } from "lucide-react";
import styles from "./LoadingCard.module.css";

const PIPELINE_STAGES = [
  { id: "decode", label: "Decoding audio waveform & LUFS loudness leveling", targetSec: 2.0 },
  { id: "tokens", label: "Parsing transcript tokens & word boundaries", targetSec: 4.0 },
  { id: "align", label: "Phonetic forced alignment (TorchAudio MMS_FA)", targetSec: 12.0 },
  { id: "dsp", label: "Extracting Praat F0 pitch, HNR & energy contours", targetSec: 18.0 },
  { id: "bounds", label: "Computing deviation z-scores vs population bounds", targetSec: 23.0 },
  { id: "scoring", label: "Running delivery rubric & dimension scoring model", targetSec: 27.0 },
  { id: "explain", label: "Generating causal feedback & acoustic telemetry", targetSec: 32.0 },
];

export default function LoadingCard({ onCancel }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      setElapsed((Date.now() - startTime) / 1000);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Compute smooth asymptotic progress climbing progressively up to 99%
  // Dynamically adjusts so it never feels stuck or frozen at 98%
  const overallPct = Math.min(
    99,
    Math.max(
      8,
      Math.round(100 * (1 - Math.exp(-elapsed / 15.5)))
    )
  );

  // Find active stage
  let activeIndex = 0;
  for (let i = 0; i < PIPELINE_STAGES.length; i++) {
    if (elapsed >= PIPELINE_STAGES[i].targetSec) {
      activeIndex = Math.min(PIPELINE_STAGES.length - 1, i + 1);
    } else {
      activeIndex = i;
      break;
    }
  }

  const activeStage = PIPELINE_STAGES[activeIndex];

  return (
    <div className={styles.loadingContainer}>
      {/* Header with live dynamic equalizer and timer */}
      <div className={styles.headerRow}>
        <div className={styles.headerLeft}>
          <div className={styles.equalizerWrap} aria-hidden="true">
            <span className={styles.eqBar} style={{ animationDelay: "0ms" }} />
            <span className={styles.eqBar} style={{ animationDelay: "180ms" }} />
            <span className={styles.eqBar} style={{ animationDelay: "360ms" }} />
            <span className={styles.eqBar} style={{ animationDelay: "90ms" }} />
            <span className={styles.eqBar} style={{ animationDelay: "270ms" }} />
          </div>
          <div>
            <h3 className={styles.headerTitle}>Analyzing Speech</h3>
            <p className={styles.headerSubtitle}>
              Running multimodal speech acoustic pipeline in real time
            </p>
          </div>
        </div>
        <div className={styles.timerBadge}>
          <span className={styles.pulseDot} />
          <span>{elapsed.toFixed(1)}s</span>
        </div>
      </div>

      {/* Main Overall Progress Meter */}
      <div className={styles.overallSection}>
        <div className={styles.overallMetaRow}>
          <span className={styles.overallStageName}>
            Stage {activeIndex + 1} of {PIPELINE_STAGES.length}: {activeStage.label}
          </span>
          <span className={styles.overallPercent}>{overallPct}%</span>
        </div>
        <div className={styles.overallTrack}>
          <div
            className={styles.overallFill}
            style={{ width: `${overallPct}%` }}
          />
        </div>
      </div>

      {/* Dynamic 7-Stage Pipeline Breakdown */}
      <div className={styles.stagesList}>
        {PIPELINE_STAGES.map((stage, idx) => {
          const isDone = elapsed >= stage.targetSec;
          const isActive = idx === activeIndex && !isDone;
          const isPending = idx > activeIndex;

          const prevSec = idx === 0 ? 0 : PIPELINE_STAGES[idx - 1].targetSec;
          const stageDuration = stage.targetSec - prevSec;
          const stageElapsed = Math.max(0, elapsed - prevSec);
          const stageFillPct = isDone
            ? 100
            : isActive
            ? Math.min(95, Math.round((stageElapsed / stageDuration) * 100))
            : 0;

          return (
            <div
              key={stage.id}
              className={`${styles.stageCard} ${isActive ? styles.stageCardActive : ""}`}
            >
              <div className={styles.stageTopRow}>
                <div className={styles.stageLabelGroup}>
                  {isDone ? (
                    <CheckCircle size={16} className={styles.stageIconDone} />
                  ) : isActive ? (
                    <Loader2 size={16} className={styles.stageIconActive} />
                  ) : (
                    <Circle size={16} className={styles.stageIconPending} />
                  )}
                  <span
                    className={styles.stageLabel}
                    style={{
                      color: isDone
                        ? "var(--ink)"
                        : isActive
                        ? "var(--ink)"
                        : "var(--muted)",
                    }}
                  >
                    {stage.label}
                  </span>
                </div>

                <div>
                  {isDone ? (
                    <span className={styles.badgeDone}>Done</span>
                  ) : isActive ? (
                    <span className={styles.badgeActive}>Processing</span>
                  ) : (
                    <span className={styles.badgePending}>Queued</span>
                  )}
                </div>
              </div>

              <div className={styles.stageTrack}>
                <div
                  className={styles.stageFill}
                  style={{
                    width: `${stageFillPct}%`,
                    backgroundColor: isDone
                      ? "var(--ok)"
                      : isActive
                      ? "var(--c-pitch)"
                      : "transparent",
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
