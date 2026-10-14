import React from "react";
import {
  Compass,
  Zap,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Activity,
  Volume2,
  Gauge,
  Pause,
  Target,
  Ear,
  Mic,
  Cpu,
} from "lucide-react";
import styles from "./About.module.css";

const STEPS = [
  {
    step: "01",
    title: "Millisecond Word Alignment",
    desc: "Uses Torchaudio MMS_FA forced alignment to locate the exact start and end millisecond of every single word in your audio.",
    icon: Clock,
    color: "var(--c-pacing)",
    tint: "var(--c-pacing-tint)",
  },
  {
    step: "02",
    title: "Acoustic Signal Extraction",
    desc: "Extracts physical voice metrics: pitch contours in semitones (Praat F0), loudness (LUFS/dB), syllable speed, pause duration, and vocal clarity.",
    icon: Activity,
    color: "var(--c-pitch)",
    tint: "var(--c-pitch-tint)",
  },
  {
    step: "03",
    title: "Contrastive Baseline Comparison",
    desc: "Instead of generic guesses, we contrast your delivery against an ideal human baseline delivering the exact same script.",
    icon: Compass,
    color: "var(--c-energy)",
    tint: "var(--c-energy-tint)",
  },
  {
    step: "04",
    title: "Temporal Flaw Grounding",
    desc: "Flags the exact intervals where you deviated—such as rushed sentences, dead air pauses, monotone pitch, or dropped volume.",
    icon: Zap,
    color: "var(--c-emphasis)",
    tint: "var(--c-emphasis-tint)",
  },
];

const DIMENSIONS = [
  { name: "Pacing", desc: "Syllables/sec tempo", icon: Gauge, color: "var(--c-pacing)", tint: "var(--c-pacing-tint)" },
  { name: "Pausing", desc: "Rhythm & silence", icon: Pause, color: "var(--c-pausing)", tint: "var(--c-pausing-tint)" },
  { name: "Pitch", desc: "Melody & inflection", icon: Activity, color: "var(--c-pitch)", tint: "var(--c-pitch-tint)" },
  { name: "Energy", desc: "Vocal power & volume", icon: Volume2, color: "var(--c-energy)", tint: "var(--c-energy-tint)" },
  { name: "Emphasis", desc: "Key phrase stress", icon: Target, color: "var(--c-emphasis)", tint: "var(--c-emphasis-tint)" },
  { name: "Clarity", desc: "Harmonics & diction", icon: Ear, color: "var(--c-clarity)", tint: "var(--c-clarity-tint)" },
  { name: "Fluency", desc: "Hesitation & flow", icon: Mic, color: "var(--c-fluency)", tint: "var(--c-fluency-tint)" },
];

export default function AboutProject() {
  return (
    <div className={styles.sectionBlock}>
      {/* Intro Mission Card */}
      <div className={styles.missionCard}>
        <div className={styles.badgePill}>
          <Compass size={16} />
          <span>Why SpeechCoach?</span>
        </div>
        <h2 className={styles.missionTitle}>
          Speech coaching based on physics and contrast, not guesswork.
        </h2>
        <p className={styles.missionText}>
          Most public speaking feedback is vague and frustrating: <em>"sound more confident"</em> or <em>"speak with more energy"</em>. Even modern AI tools often run your transcript through a generic text LLM that cannot truly hear your pauses, your pitch modulation, or your vocal strain.
        </p>
        <p className={styles.missionText}>
          <strong>SpeechCoach changes that.</strong> We built a contrastive speech evaluation system. You recite a script, and our engine compares your voice against a calibrated, high-quality reference delivery of the <strong>exact same text</strong>. We pinpoint the exact timestamps where delivery strayed and explain every flaw with reproducible numbers and acoustic formulas.
        </p>
      </div>

      {/* How It Works 4-Step Cards */}
      <div className={styles.sectionHeader}>
        <div className={styles.badgePill}>
          <Cpu size={16} />
          <span>Pipeline Architecture</span>
        </div>
        <h2 className={styles.sectionTitle}>How It Works in 4 Steps</h2>
        <p className={styles.sectionSubtitle}>
          From raw waveform to pinpoint flaw detection in under 1.5 seconds.
        </p>
      </div>

      <div className={styles.stepsGrid}>
        {STEPS.map((s) => {
          const IconComp = s.icon;
          return (
            <div key={s.step} className={styles.stepCard}>
              <div className={styles.stepTopRow}>
                <span className={styles.stepNumber} style={{ color: s.color }}>{s.step}</span>
                <div className={styles.stepIconBadge} style={{ backgroundColor: s.tint, color: s.color }}>
                  <IconComp size={18} />
                </div>
              </div>
              <h3 className={styles.stepTitle}>{s.title}</h3>
              <p className={styles.stepDesc}>{s.desc}</p>
            </div>
          );
        })}
      </div>

      {/* 7 Dimensions of Speech */}
      <div className={styles.dimensionsCard}>
        <div className={styles.dimensionsHeader}>
          <h3 className={styles.dimensionsTitle}>The 7 Pillars of Vocal Delivery</h3>
          <p className={styles.dimensionsSubtitle}>
            Our acoustic engine evaluates every recording across seven independent speech axes.
          </p>
        </div>
        <div className={styles.dimensionsGrid}>
          {DIMENSIONS.map((d) => {
            const IconComp = d.icon;
            return (
              <div key={d.name} className={styles.dimensionItem}>
                <div className={styles.dimensionIcon} style={{ backgroundColor: d.tint, color: d.color }}>
                  <IconComp size={16} />
                </div>
                <div className={styles.dimensionTextGroup}>
                  <div className={styles.dimensionName}>{d.name}</div>
                  <div className={styles.dimensionDesc}>{d.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Trust & Ethics Strips */}
      <div className={styles.guaranteeRow}>
        <div className={styles.guaranteeCard}>
          <CheckCircle2 size={20} color="var(--ok)" />
          <div>
            <strong>100% Deterministic</strong>
            <p>No random model seeds or changing outputs. The same recording always produces the identical score.</p>
          </div>
        </div>
        <div className={styles.guaranteeCard}>
          <ShieldCheck size={20} color="var(--c-pitch)" />
          <div>
            <strong>Zero Black-Box LLMs</strong>
            <p>Every single flaw explanation is derived from proven digital signal processing formulas and Praat pitch tracking.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
