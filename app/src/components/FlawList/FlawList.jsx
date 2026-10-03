import React from "react";
import {
  Gauge,
  Pause,
  Activity,
  Volume2,
  Target,
  Ear,
  Mic,
  CheckCircle,
} from "lucide-react";
import { DIMENSIONS, getFlawMeta } from "../../lib/colors";
import { fmtTime, fmtNum } from "../../lib/format";
import styles from "./FlawList.module.css";

const ICON_MAP = {
  Gauge,
  Pause,
  Activity,
  Volume2,
  Target,
  Ear,
  Mic,
};

const SEVERITY_COLORS = {
  minor: "var(--butter)",
  moderate: "var(--tangerine)",
  major: "var(--bad)",
};

export default function FlawList({
  flaws = [],
  selectedFlawId,
  onSelectFlaw,
}) {
  if (!flaws || flaws.length === 0) {
    return (
      <div className={styles.emptyCard}>
        <CheckCircle size={28} className={styles.emptyIcon} />
        <div>
          <h3 className={styles.emptyTitle}>No flaws crossed the detection threshold</h3>
          <p className={styles.emptyText}>
            Delivery is well within standard baseline tolerances. Check the dimension scores for fine-grained nuances.
          </p>
        </div>
      </div>
    );
  }

  const sortedFlaws = [...flaws].sort((a, b) => a.start - b.start);
  const count = sortedFlaws.length;

  return (
    <div className={styles.flawListContainer}>
      <h2 className={styles.headerTitle}>
        {count} {count === 1 ? "Thing to Work On" : "Things to Work On"}
      </h2>

      <div className={styles.cardsGrid}>
        {sortedFlaws.map((flaw) => {
          const meta = getFlawMeta(flaw.type);
          const dim = DIMENSIONS[meta.dimension] || DIMENSIONS.pacing;
          const IconComp = ICON_MAP[dim.icon] || Gauge;
          const isSelected = flaw.id === selectedFlawId;
          const bandName = flaw.band.charAt(0).toUpperCase() + flaw.band.slice(1);
          const barColor = SEVERITY_COLORS[flaw.band] || "var(--butter)";
          const barWidthPct = Math.round((flaw.severity || 0.5) * 100);

          return (
            <div
              key={flaw.id}
              className={`${styles.flawCard} ${isSelected ? styles.flawCardSelected : ""}`}
              onClick={() => onSelectFlaw && onSelectFlaw(flaw.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  onSelectFlaw && onSelectFlaw(flaw.id);
                }
              }}
            >
              <div className={styles.topRow}>
                <div className={styles.iconBadge} style={{ backgroundColor: dim.tint, color: dim.color }}>
                  <IconComp size={18} />
                </div>
                <div className={styles.metaCol}>
                  <div className={styles.flawName}>{meta.label}</div>
                  <div className={styles.flawTime}>
                    {fmtTime(flaw.start)} – {fmtTime(flaw.end)}
                  </div>
                </div>
                <span className={`${styles.bandPill} ${styles[`pill_${flaw.band}`]}`}>
                  {bandName}
                </span>
              </div>

              {/* Severity bar */}
              <div className={styles.severityBarTrack}>
                <div
                  className={styles.severityBarFill}
                  style={{
                    width: `${barWidthPct}%`,
                    backgroundColor: barColor,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
