import React, { useRef, useEffect, useState, useMemo } from "react";
import WaveSurfer from "wavesurfer.js";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  AlertCircle,
  Gauge,
  Activity,
  Volume2,
  Target,
  Ear,
  Mic,
} from "lucide-react";
import { DIMENSIONS, getFlawMeta } from "../../lib/colors";
import { fmtTime, fmtNum } from "../../lib/format";
import { assignLanes } from "../../lib/lanes";
import styles from "./WaveformPanel.module.css";

const ICON_MAP = {
  pacing: Gauge,
  pausing: Pause,
  pitch: Activity,
  energy: Volume2,
  emphasis: Target,
  clarity: Ear,
  fluency: Mic,
};

export default function WaveformPanel({
  audioUrl,
  duration = 58.4,
  flaws = [],
  selectedFlawId,
  onSelectFlaw,
  onTimeUpdate,
  seekTarget,
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

      let rafId = null;
      ws.on("timeupdate", (t) => {
        setCurrentTime(t);
        if (onTimeUpdate) {
          if (rafId) cancelAnimationFrame(rafId);
          rafId = requestAnimationFrame(() => {
            onTimeUpdate(t);
          });
        }
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

  // Handle external seek requests (from transcript click, flaw click, or chart click)
  useEffect(() => {
    if (seekTarget && wavesurferRef.current && isReady) {
      const dur = wavesurferRef.current.getDuration() || duration;
      const progress = Math.max(0, Math.min(1, seekTarget.time / dur));
      wavesurferRef.current.seekTo(progress);
      if (!isPlaying) {
        wavesurferRef.current.play();
      }
    }
  }, [seekTarget, isReady]);

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

  // Assign lanes to overlapping flaw regions with visual duration footprint (memoized)
  const lanedFlaws = useMemo(() => assignLanes(flaws, 0.5, duration), [flaws, duration]);
  const maxLane = useMemo(() => lanedFlaws.reduce((max, f) => Math.max(max, f.lane || 0), 0), [lanedFlaws]);
  const overlayHeight = flaws.length === 0 ? 34 : (maxLane + 1) * 34;

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
        <div
          className={styles.flawOverlayLayer}
          style={{ height: flaws.length === 0 ? "34px" : `${overlayHeight}px` }}
        >
          {flaws.length === 0 ? (
            <div className={styles.noFlawsBanner}>
              <span className={styles.noFlawsIndicator} />
              <span>All speech intervals within baseline tolerances &middot; No delivery flaws detected</span>
            </div>
          ) : (
            lanedFlaws.map((flaw) => {
              const meta = getFlawMeta(flaw.type);
              const dim = DIMENSIONS[meta.dimension] || DIMENSIONS.pacing;
              const IconComp = ICON_MAP[meta.dimension] || Gauge;
              const rawLeftPct = (flaw.start / duration) * 100;
              const safeLeftPct = Math.max(0, Math.min(88, rawLeftPct));
              const topPx = flaw.lane * 34;
              const isSelected = flaw.id === selectedFlawId;

              return (
                <div
                  key={flaw.id}
                  className={styles.flawBadgeWrapper}
                  style={{
                    left: `${safeLeftPct}%`,
                    top: `${topPx}px`,
                  }}
                >
                  <button
                    type="button"
                    className={`${styles.flawBadge} ${isSelected ? styles.flawBadgeSelected : ""}`}
                    style={{
                      borderColor: isSelected ? "var(--ink)" : dim.color,
                      backgroundColor: isSelected ? "var(--card)" : dim.tint,
                    }}
                    onClick={() => seekToFlaw(flaw)}
                    title={`${meta.label} (${flaw.band}): ${fmtTime(flaw.start)} – ${fmtTime(flaw.end)} (Click to jump)`}
                    aria-label={`${meta.label} flaw from ${fmtTime(flaw.start)} to ${fmtTime(flaw.end)}`}
                  >
                    <span
                      className={styles.badgeSeverityDot}
                      style={{
                        backgroundColor:
                          flaw.band === "major"
                            ? "var(--bad)"
                            : flaw.band === "moderate"
                            ? "var(--warn)"
                            : "var(--butter)",
                      }}
                    />
                    <span className={styles.badgeIcon} style={{ color: dim.color }}>
                      <IconComp size={13} strokeWidth={2.4} />
                    </span>
                    <span className={styles.badgeLabel} style={{ color: "var(--ink)" }}>
                      {meta.label}
                    </span>
                    <span className={styles.badgeTime}>
                      {fmtTime(flaw.start)}
                    </span>
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Waveform Canvas container + direct flaw highlight intervals on audio slider */}
        <div className={styles.waveformCanvasWrap}>
          <div ref={waveformRef} className={styles.waveformContainer} />
          {flaws.length > 0 && (
            <div className={styles.waveformBandsLayer}>
              {flaws.map((flaw) => {
                const meta = getFlawMeta(flaw.type);
                const dim = DIMENSIONS[meta.dimension] || DIMENSIONS.pacing;
                const leftPct = Math.max(0, (flaw.start / duration) * 100);
                const widthPct = Math.max(1.2, ((flaw.end - flaw.start) / duration) * 100);
                const isSelected = flaw.id === selectedFlawId;

                return (
                  <div
                    key={`track-band-${flaw.id}`}
                    className={`${styles.waveformFlawBand} ${isSelected ? styles.waveformFlawBandSelected : ""}`}
                    style={{
                      left: `${leftPct}%`,
                      width: `${widthPct}%`,
                      backgroundColor: isSelected
                        ? `color-mix(in srgb, ${dim.color} 25%, transparent)`
                        : `color-mix(in srgb, ${dim.color} 14%, transparent)`,
                      borderTopColor: dim.color,
                      borderLeftColor: `color-mix(in srgb, ${dim.color} 45%, transparent)`,
                      borderRightColor: `color-mix(in srgb, ${dim.color} 45%, transparent)`,
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      seekToFlaw(flaw);
                    }}
                    title={`${meta.label} (${flaw.band}): ${fmtTime(flaw.start)} – ${fmtTime(flaw.end)} (Click to jump)`}
                  >
                    <div
                      className={styles.bandTopAccent}
                      style={{ backgroundColor: dim.color }}
                    />
                  </div>
                );
              })}
            </div>
          )}
        </div>
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
