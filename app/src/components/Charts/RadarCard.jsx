import React, { useState } from "react";
import { DIMENSIONS } from "../../lib/colors";
import { fmtNum } from "../../lib/format";
import { useCountUp } from "../../lib/motion";
import styles from "./RadarCard.module.css";

const DIMENSION_ORDER = [
  "pacing",
  "pausing",
  "pitch",
  "energy",
  "emphasis",
  "clarity",
  "fluency",
];

function RadarCard({ scores }) {
  const [hoveredIdx, setHoveredIdx] = useState(null);
  const expansion = useCountUp(1, { duration: 900 });

  if (!scores || !scores.dimensions) return null;

  const dims = scores.dimensions;
  const numAxes = DIMENSION_ORDER.length;
  const size = 280;
  const center = size / 2;
  const radius = 95;
  const rings = [25, 50, 75, 100];

  const angleStep = (2 * Math.PI) / numAxes;

  // Compute polygon vertices with dynamic expansion factor
  const polygonPoints = DIMENSION_ORDER.map((dimKey, idx) => {
    const rawVal = dims[dimKey] != null ? Math.max(0, Math.min(100, dims[dimKey])) : 50;
    const val = rawVal * expansion;
    const r = (val / 100) * radius;
    const angle = idx * angleStep - Math.PI / 2;
    const x = center + r * Math.cos(angle);
    const y = center + r * Math.sin(angle);
    return { x, y, rawVal, dimKey, angle, idx };
  });

  const pointsString = polygonPoints.map((p) => `${p.x},${p.y}`).join(" ");
  const hoveredPoint = hoveredIdx != null ? polygonPoints[hoveredIdx] : null;
  const hoveredMeta = hoveredPoint ? (DIMENSIONS[hoveredPoint.dimKey] || { label: hoveredPoint.dimKey }) : null;

  return (
    <div className={styles.radarCard}>
      <div className={styles.titleGroup}>
        <div className={styles.titleTopRow}>
          <h3 className={styles.title}>Dimension Radar</h3>
          {hoveredPoint && (
            <div className={styles.hoverBadge}>
              <span className={styles.hoverDot} />
              <span>{hoveredMeta.label}:</span>
              <strong>{Math.round(hoveredPoint.rawVal)}/100</strong>
            </div>
          )}
        </div>
        <span className={styles.subtitle}>7-axis profile · hover axes to inspect details</span>
      </div>

      <div className={styles.svgWrap}>
        <svg className={styles.radarSvg} viewBox={`0 0 ${size} ${size}`}>
          {/* Concentric reference rings */}
          {rings.map((ringVal) => {
            const r = (ringVal / 100) * radius;
            return (
              <circle
                key={ringVal}
                cx={center}
                cy={center}
                r={r}
                className={styles.ring}
              />
            );
          })}

          {/* Axes from center to perimeter */}
          {DIMENSION_ORDER.map((_, idx) => {
            const angle = idx * angleStep - Math.PI / 2;
            const x2 = center + radius * Math.cos(angle);
            const y2 = center + radius * Math.sin(angle);
            const isHovered = hoveredIdx === idx;
            return (
              <line
                key={idx}
                x1={center}
                y1={center}
                x2={x2}
                y2={y2}
                className={isHovered ? styles.axisLineActive : styles.axisLine}
              />
            );
          })}

          {/* Dynamic filled polygon */}
          <polygon points={pointsString} className={styles.polygon} />

          {/* Vertex dots and labels with hover triggers */}
          {polygonPoints.map((p, idx) => {
            const dimMeta = DIMENSIONS[p.dimKey] || { label: p.dimKey };
            const labelDist = radius + 24;
            const lx = center + labelDist * Math.cos(p.angle);
            const ly = center + labelDist * Math.sin(p.angle);
            const isHovered = hoveredIdx === idx;

            return (
              <g
                key={idx}
                className={styles.interactiveSpoke}
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
              >
                {/* Active spoke highlight halo */}
                {isHovered && (
                  <circle
                    cx={p.x}
                    cy={p.y}
                    r={8}
                    className={styles.dotHalo}
                  />
                )}
                <circle
                  cx={p.x}
                  cy={p.y}
                  r={isHovered ? 5.5 : 4}
                  className={isHovered ? styles.dotActive : styles.dot}
                />
                <text
                  x={lx}
                  y={ly - 4}
                  textAnchor="middle"
                  className={isHovered ? styles.axisLabelActive : styles.axisLabel}
                >
                  {dimMeta.label}
                </text>
                <text
                  x={lx}
                  y={ly + 8}
                  textAnchor="middle"
                  className={isHovered ? styles.axisScoreActive : styles.axisScore}
                >
                  {fmtNum(p.rawVal, 0)}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}

export default React.memo(RadarCard);

