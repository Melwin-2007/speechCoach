import React, { useState, useMemo } from "react";
import { Activity, Volume2, Gauge } from "lucide-react";
import TimeChart from "./TimeChart";
import styles from "./ChartStack.module.css";

function ChartStack({ series, meta, flaws = [], currentTime = 0, onSeek }) {
  const [hoverTime, setHoverTime] = useState(null);

  if (!series || !series.t) return null;

  const t = series.t;
  const duration = meta?.duration_s || (t.length > 0 ? t[t.length - 1] : 58.4);

  // Group flaws by chart dimension with comprehensive coverage
  const pitchFlaws = useMemo(
    () => flaws.filter((f) => ["MONOTONE", "PITCH_FLAT", "PITCH_ERRATIC"].includes(f.type)),
    [flaws]
  );
  const energyFlaws = useMemo(
    () => flaws.filter((f) => ["VOLUME_DROP", "ENERGY_LOW", "FLAT_ENERGY", "ENERGY_FLAT"].includes(f.type)),
    [flaws]
  );
  const pacingFlaws = useMemo(
    () => flaws.filter((f) => ["PACE_FAST", "PACE_SLOW", "PAUSE_LONG", "PAUSE_MISSING"].includes(f.type)),
    [flaws]
  );

  // Dynamic baseline corridor fallbacks for full visual parity
  const energyLo = useMemo(
    () => series.baseline.energy_lo || (series.baseline.energy_db ? series.baseline.energy_db.map((v) => (v != null ? v - 6.0 : -18.0)) : null),
    [series.baseline]
  );
  const energyHi = useMemo(
    () => series.baseline.energy_hi || (series.baseline.energy_db ? series.baseline.energy_db.map((v) => (v != null ? v + 6.0 : -6.0)) : null),
    [series.baseline]
  );
  const rateLo = useMemo(
    () => series.baseline.rate_lo || (series.baseline.rate_sps ? series.baseline.rate_sps.map((v) => (v != null ? Math.max(0.5, v - 1.0) : 3.0)) : null),
    [series.baseline]
  );
  const rateHi = useMemo(
    () => series.baseline.rate_hi || (series.baseline.rate_sps ? series.baseline.rate_sps.map((v) => (v != null ? v + 1.0 : 5.0)) : null),
    [series.baseline]
  );

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
          unitAbbr="st"
          icon={Activity}
          color="var(--c-pitch)"
          t={t}
          duration={duration}
          participantData={series.participant.pitch_st}
          baselineData={series.baseline.pitch_st}
          baselineLo={series.baseline.pitch_lo}
          baselineHi={series.baseline.pitch_hi}
          flaws={pitchFlaws}
          currentTime={currentTime}
          onSeek={onSeek}
          hoverTime={hoverTime}
          onHoverTime={setHoverTime}
          minY={-4.0}
          maxY={4.0}
        />

        {/* 2. Loudness / Energy Chart */}
        <TimeChart
          title="Vocal Energy & Dynamics"
          unit="dB relative to peak level"
          unitAbbr="dB"
          icon={Volume2}
          color="var(--c-energy)"
          t={t}
          duration={duration}
          participantData={series.participant.energy_db}
          baselineData={series.baseline.energy_db}
          baselineLo={energyLo}
          baselineHi={energyHi}
          flaws={energyFlaws}
          currentTime={currentTime}
          onSeek={onSeek}
          hoverTime={hoverTime}
          onHoverTime={setHoverTime}
          minY={-30.0}
          maxY={0.0}
        />

        {/* 3. Speaking Rate Chart */}
        <TimeChart
          title="Speaking Rate (Pacing)"
          unit="syllables per second (syl/s)"
          unitAbbr="syl/s"
          icon={Gauge}
          color="var(--c-pacing)"
          t={t}
          duration={duration}
          participantData={series.participant.rate_sps}
          baselineData={series.baseline.rate_sps}
          baselineLo={rateLo}
          baselineHi={rateHi}
          flaws={pacingFlaws}
          currentTime={currentTime}
          onSeek={onSeek}
          hoverTime={hoverTime}
          onHoverTime={setHoverTime}
          minY={1.0}
          maxY={7.5}
        />
      </div>
    </div>
  );
}

export default React.memo(ChartStack);
