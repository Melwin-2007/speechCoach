import React, { useState } from "react";
import {
  Gauge,
  Pause,
  Activity,
  Volume2,
  Target,
  Ear,
  Mic,
  ArrowRight,
  ArrowLeft,
  Play,
  RotateCcw,
  CheckCircle,
  Sliders,
} from "lucide-react";
import { DIMENSIONS } from "../../lib/colors";
import { fmtNum, fmtTime, scoreLabel } from "../../lib/format";
import { useCountUp } from "../../lib/motion";
import Select from "../Select/Select";
import styles from "./Styleguide.module.css";

const ICON_MAP = {
  Gauge,
  Pause,
  Activity,
  Volume2,
  Target,
  Ear,
  Mic,
};

export default function Styleguide() {
  const [demoTrigger, setDemoTrigger] = useState(0);
  const [selectVal, setSelectVal] = useState("auto");
  const countVal = useCountUp(88, { enabled: true, key: demoTrigger });

  const surfaces = [
    { name: "Paper", token: "--paper", desc: "Page background surface" },
    { name: "Paper-2", token: "--paper-2", desc: "Recessed tracks and tabs" },
    { name: "Card", token: "--card", desc: "Main white container" },
    { name: "Mint", token: "--mint", desc: "Hero banner and drop zone" },
    { name: "Mint-2", token: "--mint-2", desc: "Baseline reference band" },
    { name: "Butter", token: "--butter", desc: "Actionable fix panel" },
    { name: "Blush", token: "--blush", desc: "Botched preset and soft errors" },
  ];

  const inks = [
    { name: "Ink", token: "--ink", desc: "Primary text and solid headers" },
    { name: "Ink-2", token: "--ink-2", desc: "Secondary strong headers" },
    { name: "Muted", token: "--muted", desc: "Body and secondary descriptions" },
    { name: "Faint", token: "--faint", desc: "Tertiary labels and disabled" },
  ];

  const severityRamp = [
    { name: "Sev-0 Fine", token: "--sev-0", z: "|z| < 2.0", bg: "var(--sev-0)" },
    { name: "Sev-1 Minor", token: "--sev-1", z: "2.0 ≤ |z| < 3.0", bg: "var(--sev-1)" },
    { name: "Sev-2 Moderate", token: "--sev-2", z: "3.0 ≤ |z| < 4.5", bg: "var(--sev-2)" },
    { name: "Sev-3 Major", token: "--sev-3", z: "|z| ≥ 4.5", bg: "var(--sev-3)" },
    { name: "Sev-4 Severe", token: "--sev-4", z: "Severe deviation", bg: "var(--sev-4)" },
  ];

  const radii = [
    { name: "xs (8px)", token: "--r-xs", value: "8px" },
    { name: "sm (12px)", token: "--r-sm", value: "12px" },
    { name: "md (16px)", token: "--r-md", value: "16px" },
    { name: "lg (24px)", token: "--r-lg", value: "24px" },
    { name: "card (28px)", token: "--r-card", value: "28px" },
    { name: "xl (32px)", token: "--r-xl", value: "32px" },
    { name: "2xl (40px)", token: "--r-2xl", value: "40px" },
    { name: "pill (999px)", token: "--r-pill", value: "999px" },
  ];

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.logoRow}>
          <div className={styles.logoBars}>
            <div className={styles.logoBar1}></div>
            <div className={styles.logoBar2}></div>
            <div className={styles.logoBar3}></div>
          </div>
          <span className={styles.title}>SpeechCoach Design System & Styleguide</span>
        </div>
        <a href="#/" className={styles.backLink}>
          <ArrowLeft size={16} /> Back to App
        </a>
      </header>

      {/* 1. Surfaces & Inks */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>1. Surface & Ink Palette</h2>
        <p className={styles.sectionDesc}>
          Calm, warm, tactile palette with zero blue or purple hues (190°–320°).
        </p>
        <div className={styles.card}>
          <h3 className="h3" style={{ marginBottom: "var(--s-4)" }}>Surfaces</h3>
          <div className={styles.grid4} style={{ marginBottom: "var(--s-6)" }}>
            {surfaces.map((s) => (
              <div key={s.token} className={styles.swatchCard}>
                <div className={styles.swatchBox} style={{ backgroundColor: `var(${s.token})` }} />
                <span className={styles.swatchLabel}>{s.name}</span>
                <span className={styles.swatchToken}>{s.token}</span>
              </div>
            ))}
          </div>

          <h3 className="h3" style={{ marginBottom: "var(--s-4)" }}>Inks & Lines</h3>
          <div className={styles.grid4}>
            {inks.map((s) => (
              <div key={s.token} className={styles.swatchCard}>
                <div className={styles.swatchBox} style={{ backgroundColor: `var(${s.token})` }} />
                <span className={styles.swatchLabel}>{s.name}</span>
                <span className={styles.swatchToken}>{s.token}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 2. Flaw Dimension Colors */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>2. Flaw Dimension Colors & Tokens</h2>
        <p className={styles.sectionDesc}>
          7 clinical dimensions with dedicated semantic color, 16% tint tokens, and Lucide icons.
        </p>
        <div className={styles.card}>
          <div className={styles.grid3}>
            {Object.entries(DIMENSIONS).map(([key, dim]) => {
              const IconComp = ICON_MAP[dim.icon] || Gauge;
              return (
                <div key={key} className={styles.dimCard}>
                  <div
                    className={styles.dimIconWrap}
                    style={{ backgroundColor: dim.tint, color: dim.color }}
                  >
                    <IconComp size={20} />
                  </div>
                  <div className={styles.dimMeta}>
                    <span className={styles.dimName}>{dim.label}</span>
                    <span className={styles.dimToken}>{dim.color}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 3. Severity Ramp */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>3. Severity Ramp</h2>
        <p className={styles.sectionDesc}>
          Calibrated severity bands based on signed z-score thresholds (Minor ≥ 2.0, Moderate ≥ 3.0, Major ≥ 4.5).
        </p>
        <div className={styles.card}>
          <div className={styles.sevBar}>
            {severityRamp.map((sev) => (
              <div key={sev.token} className={styles.sevBlock} style={{ backgroundColor: sev.bg }}>
                <span className={styles.sevName}>{sev.name}</span>
                <span className={styles.sevZ}>{sev.z}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 4. Typography Scale */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>4. Typography Scale</h2>
        <p className={styles.sectionDesc}>
          Bricolage Grotesque (headings), DM Sans (body UI), and IBM Plex Mono (tabular metrics).
        </p>
        <div className={styles.card}>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--s-5)" }}>
            <div>
              <span className="micro" style={{ textTransform: "uppercase" }}>display-xl</span>
              <h1 className="display-xl">See exactly where your speech goes wrong.</h1>
            </div>
            <div>
              <span className="micro" style={{ textTransform: "uppercase" }}>h1</span>
              <h1 className="h1">Speech Evaluation Results</h1>
            </div>
            <div>
              <span className="micro" style={{ textTransform: "uppercase" }}>h2</span>
              <h2 className="h2">Acoustic Deviation Overview</h2>
            </div>
            <div>
              <span className="micro" style={{ textTransform: "uppercase" }}>h3</span>
              <h3 className="h3">Rushing detected (0:08.5 – 0:16.2)</h3>
            </div>
            <div>
              <span className="micro" style={{ textTransform: "uppercase" }}>body</span>
              <p className="body">
                We compare your vocal delivery with high-performing reference speakers and pinpoint every millisecond of deviation.
              </p>
            </div>
            <div>
              <span className="micro" style={{ textTransform: "uppercase" }}>small / micro</span>
              <p className="small">Reference model: Lincoln (T4) · 4.1 syl/s baseline tempo.</p>
              <p className="micro">Timecode resolution: 20 Hz (50 ms hop grid).</p>
            </div>
            <div>
              <span className="micro" style={{ textTransform: "uppercase" }}>mono-sm (tabular numbers)</span>
              <p className="mono-sm">
                z = {fmtNum(-4.8, 1)} · Time: {fmtTime(42.1)} / {fmtTime(58.4)} · Score: {fmtNum(88.4, 1)} ({scoreLabel(88.4)})
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Buttons & Controls */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>5. Buttons & Interaction States</h2>
        <p className={styles.sectionDesc}>
          Pill-shaped primary buttons, secondary outlines, ghost links, and circular playback controls.
        </p>
        <div className={styles.card}>
          <div className={styles.btnRow}>
            <button type="button" className={styles.btnPrimary}>
              Analyze recording <ArrowRight size={18} />
            </button>
            <button type="button" className={styles.btnPrimary} disabled>
              Disabled state
            </button>
            <button type="button" className={styles.btnSecondary}>
              Choose another file
            </button>
            <button type="button" className={styles.btnGhost}>
              Use sample transcript
            </button>
            <button type="button" className={styles.btnIcon} aria-label="Settings">
              <Sliders size={20} />
            </button>
            <button type="button" className={styles.btnPlay} aria-label="Play recording">
              <Play size={24} style={{ marginLeft: "3px" }} />
            </button>
          </div>
        </div>
      </section>

      {/* 6. Chips & Severity Badges */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>6. Chips & Badges</h2>
        <p className={styles.sectionDesc}>
          Semantic flaw chips and severity indicator pills.
        </p>
        <div className={styles.card}>
          <div className={styles.chipRow}>
            <span
              className={styles.flawChip}
              style={{ backgroundColor: "var(--c-pacing-tint)", color: "var(--ink)" }}
            >
              <Gauge size={16} color="var(--c-pacing)" /> Rushing (+44%)
            </span>
            <span
              className={styles.flawChip}
              style={{ backgroundColor: "var(--c-pitch-tint)", color: "var(--ink)" }}
            >
              <Activity size={16} color="var(--c-pitch)" /> Flat pitch (0:13.0)
            </span>
            <span
              className={styles.flawChip}
              style={{ backgroundColor: "var(--c-energy-tint)", color: "var(--ink)" }}
            >
              <Volume2 size={16} color="var(--c-energy)" /> Volume drop (−8.6 dB)
            </span>
            <span className={styles.pillMinor}>Minor</span>
            <span className={styles.pillModerate}>Moderate</span>
            <span className={styles.pillMajor}>Major</span>
          </div>
        </div>
      </section>

      {/* 7. Form Controls */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>7. Custom Select & Form Inputs</h2>
        <p className={styles.sectionDesc}>
          Custom animated Select dropdown with rich hover states, badges, and keyboard navigation.
        </p>
        <div className={styles.card}>
          <div className={styles.grid2}>
            <div className={styles.formGroup}>
              <label className={styles.label}>Custom Speech Selector (Select)</label>
              <Select value={selectVal} onChange={setSelectVal} />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>Transcript Input</label>
              <textarea
                className={styles.textarea}
                defaultValue="Where the mind is without fear and the head is held high..."
                readOnly
              />
            </div>
          </div>
        </div>
      </section>

      {/* 8. Radii & Shadows */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>8. Radii & Shadow Scales</h2>
        <p className={styles.sectionDesc}>
          Strict minimum radius of 8px. Warm, soft multi-layer shadows without harsh black.
        </p>
        <div className={styles.card}>
          <div className={styles.grid4} style={{ marginBottom: "var(--s-6)" }}>
            {radii.map((r) => (
              <div
                key={r.token}
                className={styles.sampleBox}
                style={{ borderRadius: `var(${r.token})` }}
              >
                <span style={{ fontWeight: 600, fontSize: "14px" }}>{r.name}</span>
                <span className="mono-sm" style={{ color: "var(--muted)" }}>{r.token}</span>
              </div>
            ))}
          </div>

          <div className={styles.grid3}>
            <div className={styles.shadowBox} style={{ boxShadow: "var(--shadow-1)" }}>
              <span style={{ fontWeight: 600 }}>--shadow-1</span>
              <span className="small">Subtle surface lift</span>
            </div>
            <div className={styles.shadowBox} style={{ boxShadow: "var(--shadow-2)" }}>
              <span style={{ fontWeight: 600 }}>--shadow-2</span>
              <span className="small">Prominent card shadow</span>
            </div>
            <div className={styles.shadowBox} style={{ boxShadow: "var(--shadow-pop)" }}>
              <span style={{ fontWeight: 600 }}>--shadow-pop</span>
              <span className="small">Floating interactive modal</span>
            </div>
          </div>
        </div>
      </section>

      {/* 9. Live Motion Demos */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>9. Motion Demos</h2>
        <p className={styles.sectionDesc}>
          Catalogued animation primitives: M14 (Count-up), M12 (Breathing bars), M20 (SVG draw-in).
        </p>
        <div className={styles.card}>
          <div className={styles.grid3}>
            <div className={styles.motionCard}>
              <span className="small" style={{ fontWeight: 600 }}>M14: Score Count-Up</span>
              <div className={styles.scoreCircle}>
                {Math.round(countVal)}
              </div>
              <button
                type="button"
                className={styles.btnSecondary}
                onClick={() => setDemoTrigger((prev) => prev + 1)}
                style={{ height: "36px", padding: "0 14px", fontSize: "13px" }}
              >
                <RotateCcw size={14} /> Replay
              </button>
            </div>

            <div className={styles.motionCard}>
              <span className="small" style={{ fontWeight: 600 }}>M12: Breathing Loader (.bars)</span>
              <div className={styles.barsLoader}>
                <div className={styles.bar}></div>
                <div className={styles.bar}></div>
                <div className={styles.bar}></div>
                <div className={styles.bar}></div>
                <div className={styles.bar}></div>
                <div className={styles.bar}></div>
                <div className={styles.bar}></div>
              </div>
              <span className="micro" style={{ color: "var(--muted)" }}>Analyzing audio...</span>
            </div>

            <div className={styles.motionCard}>
              <span className="small" style={{ fontWeight: 600 }}>M20: Line Draw-in (.draw)</span>
              <svg width="160" height="40" viewBox="0 0 160 40" fill="none">
                <path
                  d="M 10 30 Q 40 5 80 20 T 150 10"
                  stroke="var(--ink)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  className="draw"
                  pathLength="1"
                />
              </svg>
              <span className="micro" style={{ color: "var(--muted)" }}>Pitch contour spline</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
