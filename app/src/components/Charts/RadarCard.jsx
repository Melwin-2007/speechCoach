import React from "react";
import { DIMENSIONS } from "../../lib/colors";
import { fmtNum } from "../../lib/format";
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

export default function RadarCard({ scores }) {
  if (!scores || !scores.dimensions) return null;

  const dims = scores.dimensions;
  const numAxes = DIMENSION_ORDER.length;
  const size = 280;
  const center = size / 2;
  const radius = 95;
  const rings = [25, 50, 75, 100];

  const angleStep = (2 * Math.PI) / numAxes;

  // Compute polygon vertices
  const polygonPoints = DIMENSION_ORDER.map((dimKey, idx) => {
    const val = dims[dimKey] != null ? Math.max(0, Math.min(100, dims[dimKey])) : 50;
    const r = (val / 100) * radius;
    const angle = idx * angleStep - Math.PI / 2;
    const x = center + r * Math.cos(angle);
    const y = center + r * Math.sin(angle);
    return { x, y, val, dimKey, angle };
  });

  const pointsString = polygonPoints.map((p) => `${p.x},${p.y}`).join(" ");

  return (
    <div className={styles.radarCard}>
      <div className={styles.titleGroup}>
        <h3 className={styles.title}>Dimension Radar</h3>
        <span className={styles.subtitle}>7-axis comparative profile</span>
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
            return (
              <line
                key={idx}
                x1={center}
                y1={center}
                x2={x2}
                y2={y2}
                className={styles.axisLine}
              />
            );
          })}

          {/* Filled polygon */}
          <polygon points={pointsString} className={styles.polygon} />

          {/* Vertex dots and labels */}
          {polygonPoints.map((p, idx) => {
            const dimMeta = DIMENSIONS[p.dimKey] || { label: p.dimKey };
            const labelDist = radius + 24;
            const lx = center + labelDist * Math.cos(p.angle);
            const ly = center + labelDist * Math.sin(p.angle);

            return (
              <g key={idx}>
                <circle cx={p.x} cy={p.y} r={4} className={styles.dot} />
                <text
                  x={lx}
                  y={ly - 4}
                  textAnchor="middle"
                  className={styles.axisLabel}
                >
                  {dimMeta.label}
                </text>
                <text
                  x={lx}
                  y={ly + 8}
                  textAnchor="middle"
                  className={styles.axisScore}
                >
                  {fmtNum(p.val, 0)}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
