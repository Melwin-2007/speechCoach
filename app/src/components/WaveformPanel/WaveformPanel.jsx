import React, { useRef, useEffect, useState } from "react";
import WaveSurfer from "wavesurfer.js";
import { Play, Pause, SkipBack, SkipForward, AlertCircle } from "lucide-react";
import { DIMENSIONS, getFlawMeta } from "../../lib/colors";
import { fmtTime, fmtNum } from "../../lib/format";
import { assignLanes } from "../../lib/lanes";
import styles from "./WaveformPanel.module.css";

export default function WaveformPanel({
  audioUrl,
  duration = 58.4,
  flaws = [],
  selectedFlawId,
  onSelectFlaw,
  onTimeUpdate,
}) {
  const containerRef = useRef(null);
  const waveformRef = useRef(null);
  const wavesurferRef = useRef(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [isReady, setIsReady] = useState(false);
  const [loadError, setLoadError] = useState(null);

  // Initialize WaveSurfer
  useEffect(() => {
    if (!waveformRef.current || !audioUrl) return;

    let ws = null;
    try {
      const computed = getComputedStyle(document.documentElement);
      const waveColor = computed.getPropertyValue("--mint-2").trim() || "rgb(196, 235, 215)";
      const progressColor = computed.getPropertyValue("--ink").trim() || "rgb(30, 27, 24)";
      const cursorColor = computed.getPropertyValue("--ink").trim() || "rgb(30, 27, 24)";

      ws = WaveSurfer.create({
        container: waveformRef.current,
        waveColor,
        progressColor,
        cursorColor,
        cursorWidth: 2,
        height: 110,
        barWidth: 3,
        barGap: 3,
        barRadius: 3,
        normalize: true,
        url: audioUrl,
      });

      ws.on("ready", () => {
        setIsReady(true);
        setLoadError(null);
      });

      ws.on("play", () => setIsPlaying(true));
      ws.on("pause", () => setIsPlaying(false));
      ws.on("finish", () => {
        setIsPlaying(false);
        setCurrentTime(0);
      });

      ws.on("timeupdate", (t) => {
        setCurrentTime(t);
        if (onTimeUpdate) onTimeUpdate(t);
      });

      ws.on("error", (err) => {
        console.warn("WaveSurfer error:", err);
        setLoadError("Could not decode audio waveform.");
      });

      wavesurferRef.current = ws;
    } catch (e) {
      console.warn("Failed to create WaveSurfer:", e);
      setLoadError("Audio playback not supported in this browser mode.");
    }

    return () => {
      if (ws) {
        ws.destroy();
      }
    };
  }, [audioUrl]);

  const togglePlay = () => {
    if (!wavesurferRef.current) return;
    wavesurferRef.current.playPause();
  };

  const seekToFlaw = (flaw) => {
    if (!flaw || !wavesurferRef.current) return;
    const dur = wavesurferRef.current.getDuration() || duration;
    const progress = Math.max(0, Math.min(1, flaw.start / dur));
    wavesurferRef.current.seekTo(progress);
    if (!isPlaying) {
      wavesurferRef.current.play();
    }
    if (onSelectFlaw) onSelectFlaw(flaw.id);
  };

  const handlePrevFlaw = () => {
    if (flaws.length === 0) return;
    const currentIndex = flaws.findIndex((f) => f.id === selectedFlawId);
    const prevIndex = currentIndex > 0 ? currentIndex - 1 : flaws.length - 1;
    seekToFlaw(flaws[prevIndex]);
  };

  const handleNextFlaw = () => {
    if (flaws.length === 0) return;
    const currentIndex = flaws.findIndex((f) => f.id === selectedFlawId);
    const nextIndex = currentIndex >= 0 && currentIndex < flaws.length - 1 ? currentIndex + 1 : 0;
    seekToFlaw(flaws[nextIndex]);
  };

  // Assign lanes to overlapping flaw regions
  const lanedFlaws = assignLanes(flaws);
  const maxLane = lanedFlaws.reduce((max, f) => Math.max(max, f.lane || 0), 0);
  const overlayHeight = Math.max(34, (maxLane + 1) * 30);

  return (
    <div className={styles.waveformCard} ref={containerRef}>
      <div className={styles.cardHeader}>
        <div className={styles.titleWrap}>
          <h2 className={styles.title}>Audio Waveform & Flaw Intervals</h2>
          <span className={styles.subtitle}>
            Click any flagged region or word to jump directly to that point in time
          </span>
        </div>
        <div className={styles.timeDisplay}>
          <span className="mono">{fmtTime(currentTime)}</span>
          <span className={styles.timeSeparator}>/</span>
          <span className="mono">{fmtTime(duration)}</span>
        </div>
      </div>

      {loadError && (
        <div className={styles.errorBanner}>
          <AlertCircle size={16} />
          <span>{loadError}</span>
        </div>
      )}

      {/* Main Waveform + Overlay Box */}
      <div className={styles.waveformStage}>
        {/* Flaw region badges overlay layer */}
        <div className={styles.flawOverlayLayer} style={{ height: `${overlayHeight}px` }}>
          {lanedFlaws.map((flaw) => {
            const meta = getFlawMeta(flaw.type);
            const dim = DIMENSIONS[meta.dimension] || DIMENSIONS.pacing;
            const leftPct = Math.max(0, (flaw.start / duration) * 100);
            const widthPct = Math.max(1.5, ((flaw.end - flaw.start) / duration) * 100);
            const topPx = flaw.lane * 28;
            const isSelected = flaw.id === selectedFlawId;

            return (
              <button
                key={flaw.id}
                type="button"
                className={`${styles.flawRegionBtn} ${isSelected ? styles.flawRegionSelected : ""}`}
                style={{
                  left: `${leftPct}%`,
                  width: `${widthPct}%`,
                  top: `${topPx}px`,
                  backgroundColor: dim.tint,
                  borderColor: dim.color,
                }}
                onClick={() => seekToFlaw(flaw)}
                title={`${meta.label} (${flaw.band}): ${fmtTime(flaw.start)} – ${fmtTime(flaw.end)}`}
                aria-label={`${meta.label} flaw from ${fmtTime(flaw.start)} to ${fmtTime(flaw.end)}`}
              >
                <span className={styles.regionLabel} style={{ color: dim.color }}>
                  {meta.label}
                </span>
              </button>
            );
          })}
        </div>

        {/* Waveform Canvas container */}
        <div ref={waveformRef} className={styles.waveformCanvasWrap} />
      </div>

      {/* Player Controls Row */}
      <div className={styles.controlsRow}>
        <div className={styles.playControls}>
          <button
            type="button"
            className={styles.playBtn}
            onClick={togglePlay}
            aria-label={isPlaying ? "Pause audio" : "Play audio"}
          >
            {isPlaying ? <Pause size={22} /> : <Play size={22} style={{ marginLeft: "3px" }} />}
          </button>

          <button
            type="button"
            className={styles.navFlawBtn}
            onClick={handlePrevFlaw}
            disabled={flaws.length === 0}
            title="Previous flaw"
            aria-label="Previous flaw"
          >
            <SkipBack size={18} />
          </button>

          <button
            type="button"
            className={styles.navFlawBtn}
            onClick={handleNextFlaw}
            disabled={flaws.length === 0}
            title="Next flaw"
            aria-label="Next flaw"
          >
            <SkipForward size={18} />
          </button>
        </div>

        <div className={styles.playbackLegend}>
          <div className={styles.legendItem}>
            <div className={styles.legendColorBox} style={{ backgroundColor: "var(--ink)" }} />
            <span>Played</span>
          </div>
          <div className={styles.legendItem}>
            <div className={styles.legendColorBox} style={{ backgroundColor: "var(--mint-2)" }} />
            <span>Unplayed</span>
          </div>
          <div className={styles.legendItem}>
            <div className={styles.legendColorBox} style={{ backgroundColor: "var(--blush)", border: "1px solid var(--coral)" }} />
            <span>Flaw region</span>
          </div>
        </div>
      </div>
    </div>
  );
}
