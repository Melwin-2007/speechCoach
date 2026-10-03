import React, { useState } from "react";
import { Activity, Volume2, Gauge } from "lucide-react";
import TimeChart from "./TimeChart";
import styles from "./ChartStack.module.css";

export default function ChartStack({ series, meta, flaws = [] }) {
  const [hoverTime, setHoverTime] = useState(null);

  if (!series || !series.t) return null;

  const t = series.t;
  const duration = meta?.duration_s || (t.length > 0 ? t[t.length - 1] : 58.4);

  // Group flaws by chart dimension
  const pitchFlaws = flaws.filter((f) => ["MONOTONE", "PITCH_ERRATIC"].includes(f.type));
  const energyFlaws = flaws.filter((f) => ["VOLUME_DROP", "FLAT_ENERGY"].includes(f.type));
  const pacingFlaws = flaws.filter((f) => ["PACE_FAST", "PACE_SLOW"].includes(f.type));

  return (
    <div className={styles.chartStackCard}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h2 className={styles.title}>Acoustic Time Series</h2>
          <span className={styles.subtitle}>
            Synchronized 20 Hz telemetry: delivery (dark line) vs reference baseline corridor (mint band)
          </span>
        </div>
        <div className={styles.legend}>
          <div className={styles.legendItem}>
            <div className={styles.legendLine} />
            <span>Your Voice</span>
          </div>
          <div className={styles.legendItem}>
            <div className={styles.legendDashed} />
            <span>Reference</span>
          </div>
          <div className={styles.legendItem}>
            <div className={styles.legendBand} />
            <span>Normal Corridor</span>
          </div>
        </div>
      </div>

      <div className={styles.chartsWrapper}>
        {/* 1. Pitch Chart */}
        <TimeChart
          title="Pitch Variation (F0)"
          unit="semitones (st) relative to median"
          icon={Activity}
          color="var(--c-pitch)"
          t={t}
          duration={duration}
          participantData={series.participant.pitch_st}
          baselineData={series.baseline.pitch_st}
          baselineLo={series.baseline.pitch_lo}
          baselineHi={series.baseline.pitch_hi}
          flaws={pitchFlaws}
          hoverTime={hoverTime}
          onHoverTime={setHoverTime}
          minY={-4.0}
          maxY={4.0}
        />

        {/* 2. Loudness / Energy Chart */}
        <TimeChart
          title="Vocal Energy & Dynamics"
          unit="dB relative to peak level"
          icon={Volume2}
          color="var(--c-energy)"
          t={t}
          duration={duration}
          participantData={series.participant.energy_db}
          baselineData={series.baseline.energy_db}
          flaws={energyFlaws}
          hoverTime={hoverTime}
          onHoverTime={setHoverTime}
          minY={-30.0}
          maxY={0.0}
        />

        {/* 3. Speaking Rate Chart */}
        <TimeChart
          title="Speaking Rate (Pacing)"
          unit="syllables per second (syl/s)"
          icon={Gauge}
          color="var(--c-pacing)"
          t={t}
          duration={duration}
          participantData={series.participant.rate_sps}
          baselineData={series.baseline.rate_sps}
          flaws={pacingFlaws}
          hoverTime={hoverTime}
          onHoverTime={setHoverTime}
          minY={1.0}
          maxY={7.5}
        />
      </div>
    </div>
  );
}
