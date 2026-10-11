import React, { useRef, useEffect, useState } from "react";
import { scaleLinear } from "d3-scale";
import { line as d3Line, area as d3Area, curveMonotoneX } from "d3-shape";
import { fmtNum, fmtTime } from "../../lib/format";
import styles from "./ChartStack.module.css";

export default function TimeChart({
  title,
  unit,
  unitAbbr = "",
  t,
  duration,
  participantData,
  baselineData,
  baselineLo,
  baselineHi,
  flaws = [],
  currentTime,
  onSeek,
  hoverTime,
  onHoverTime,
  color = "var(--c-pacing)",
  minY,
  maxY,
  icon: IconComponent,
}) {
  const containerRef = useRef(null);
  const chartId = React.useId().replace(/[:]/g, "_");
  const clipId = `chart_clip_${chartId}`;
  const [width, setWidth] = useState(800);
  const height = 130;
  const padding = { top: 12, right: 16, bottom: 20, left: 40 };

  useEffect(() => {
    if (!containerRef.current) return;
    if (containerRef.current.clientWidth > 50) {
      setWidth(containerRef.current.clientWidth);
    }
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.contentRect.width > 50) {
          setWidth(entry.contentRect.width);
        }
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  if (!t || t.length === 0) return null;

  const totalDuration = duration || (t.length > 0 ? t[t.length - 1] : 58.4);

  // Scales
  const innerWidth = Math.max(50, width - padding.left - padding.right);
  const innerHeight = Math.max(30, height - padding.top - padding.bottom);

  const xScale = scaleLinear().domain([0, totalDuration]).range([padding.left, width - padding.right]);

  // Compute Y domain
  let computedMin = minY;
  let computedMax = maxY;

  if (computedMin === undefined || computedMax === undefined) {
    const validPart = participantData.filter((v) => v != null && !isNaN(v));
    const validBase = baselineData ? baselineData.filter((v) => v != null && !isNaN(v)) : [];
    const allVals = [...validPart, ...validBase];
    if (baselineLo) allVals.push(...baselineLo.filter((v) => v != null));
    if (baselineHi) allVals.push(...baselineHi.filter((v) => v != null));

    if (allVals.length > 0) {
      const minVal = Math.min(...allVals);
      const maxVal = Math.max(...allVals);
      const span = Math.max(1, maxVal - minVal);
      computedMin = minVal - span * 0.15;
      computedMax = maxVal + span * 0.15;
    } else {
      computedMin = 0;
      computedMax = 10;
    }
  }

  const yScale = scaleLinear().domain([computedMin, computedMax]).range([height - padding.bottom, padding.top]);

  // Generators
  const lineGen = d3Line()
    .defined((d) => d.val != null && !isNaN(d.val))
    .x((d) => xScale(d.t))
    .y((d) => yScale(d.val))
    .curve(curveMonotoneX);

  const partPoints = t.map((timePt, i) => ({ t: timePt, val: participantData[i] }));
  const basePoints = baselineData ? t.map((timePt, i) => ({ t: timePt, val: baselineData[i] })) : [];

  let areaPath = null;
  if (baselineLo && baselineHi) {
    const areaGen = d3Area()
      .x((d) => xScale(d.t))
      .y0((d) => yScale(d.lo))
      .y1((d) => yScale(d.hi))
      .curve(curveMonotoneX);

    const areaPoints = t.map((timePt, i) => ({
      t: timePt,
      lo: baselineLo[i],
      hi: baselineHi[i],
    }));
    areaPath = areaGen(areaPoints);
  }

  const participantPath = lineGen(partPoints);
  const baselinePath = baselineData ? lineGen(basePoints) : null;

  // Grid ticks
  const yTicks = yScale.ticks(4);

  // Live Playhead & Value Lookup
  let liveInfo = null;
  if (currentTime != null && currentTime >= 0 && t.length > 0) {
    const clampedTime = Math.max(0, Math.min(totalDuration, currentTime));
    const idx = Math.min(
      t.length - 1,
      Math.max(0, Math.round((clampedTime / totalDuration) * (t.length - 1)))
    );
    const pVal = participantData[idx];
    const bVal = baselineData ? baselineData[idx] : null;
    const isValid = pVal != null && !isNaN(pVal);

    liveInfo = {
      x: xScale(clampedTime),
      val: isValid ? pVal : null,
      y: isValid ? yScale(pVal) : null,
      baseVal: bVal != null && !isNaN(bVal) ? bVal : null,
    };
  }

  // Hover data lookup
  let hoverInfo = null;
  if (hoverTime != null) {
    const idx = Math.min(
      t.length - 1,
      Math.max(0, Math.round((hoverTime / totalDuration) * (t.length - 1)))
    );
    const pVal = participantData[idx];
    const bVal = baselineData ? baselineData[idx] : null;
    hoverInfo = {
      time: t[idx],
      participant: pVal,
      baseline: bVal,
    };
  }

  const handlePointerDown = (e) => {
    if (!containerRef.current || !onSeek) return;
    const rect = containerRef.current.getBoundingClientRect();
    const xPos = e.clientX - rect.left;
    const timeVal = Math.max(0, Math.min(totalDuration, xScale.invert(xPos)));
    onSeek(timeVal);
  };

  const handlePointerMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const xPos = e.clientX - rect.left;
    const timeVal = Math.max(0, Math.min(totalDuration, xScale.invert(xPos)));
    if (onHoverTime) onHoverTime(timeVal);
    if (e.buttons === 1 && onSeek) {
      onSeek(timeVal);
    }
  };

  const handlePointerLeave = () => {
    if (onHoverTime) onHoverTime(null);
  };

  return (
    <div className={styles.chartContainer} ref={containerRef}>
      <div className={styles.chartTopRow}>
        <div className={styles.chartTitle}>
          {IconComponent && <IconComponent size={16} color={color} />}
          <span>{title}</span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "var(--s-3)", flexWrap: "wrap" }}>
          {liveInfo && (
            <div
              className={styles.liveBadge}
              title={`Live acoustic telemetry at ${fmtTime(currentTime)}`}
            >
              <span className={styles.livePulseDot} />
              <span>
                {liveInfo.val != null
                  ? `${fmtNum(liveInfo.val, 1)} ${unitAbbr}`
                  : "Unvoiced"}
              </span>
            </div>
          )}
          <span className={styles.chartUnit}>{unit}</span>
        </div>
      </div>

      {hoverInfo && (
        <div className={styles.tooltip}>
          <span>Time: <span className={styles.tooltipVal}>{fmtTime(hoverInfo.time)}</span></span>
          <span>You: <span className={styles.tooltipVal}>{hoverInfo.participant != null ? fmtNum(hoverInfo.participant, 1) : "Unvoiced"}</span></span>
          {hoverInfo.baseline != null && (
            <span>Ref: <span className={styles.tooltipVal}>{fmtNum(hoverInfo.baseline, 1)}</span></span>
          )}
        </div>
      )}

      <div
        className={styles.svgWrap}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerLeave={handlePointerLeave}
        title="Click or drag anywhere on the contour to jump audio"
      >
        <svg className={styles.svg} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
          <defs>
            <clipPath id={clipId}>
              <rect
                x={padding.left}
                y={padding.top}
                width={innerWidth}
                height={innerHeight}
              />
            </clipPath>
          </defs>

          {/* Horizontal Grid lines */}
          {yTicks.map((tickVal) => (
            <g key={tickVal}>
              <line
                x1={padding.left}
                y1={yScale(tickVal)}
                x2={width - padding.right}
                y2={yScale(tickVal)}
                className={styles.gridLine}
              />
              <text
                x={padding.left - 6}
                y={yScale(tickVal) + 3}
                textAnchor="end"
                className={styles.axisText}
              >
                {fmtNum(tickVal, 0)}
              </text>
            </g>
          ))}

          {/* Strictly bounded data series layer */}
          <g clipPath={`url(#${clipId})`}>
            {/* Flaw region highlight boxes */}
            {flaws.map((flaw) => {
              const rx = xScale(flaw.start);
              const rw = Math.max(4, xScale(flaw.end) - rx);
              return (
                <rect
                  key={flaw.id}
                  x={rx}
                  y={padding.top}
                  width={rw}
                  height={innerHeight}
                  fill={color}
                  className={styles.flawRect}
                />
              );
            })}

            {/* Baseline Area Corridor */}
            {areaPath && <path d={areaPath} className={styles.baselineAreaAnimated} />}

            {/* Baseline Center Line */}
            {baselinePath && <path d={baselinePath} className={styles.baselinePathAnimated} />}

            {/* Dynamic Participant Line with animated stroke draw */}
            {participantPath && (
              <path
                d={participantPath}
                pathLength="1"
                className={styles.participantPathAnimated}
              />
            )}
          </g>

          {/* Hover Crosshair Line */}
          {hoverTime != null && (
            <line
              x1={xScale(hoverTime)}
              y1={padding.top}
              x2={xScale(hoverTime)}
              y2={height - padding.bottom}
              className={styles.crosshair}
            />
          )}

          {/* Dynamic Synchronized Audio Playhead & Live Contour Tracer */}
          {liveInfo && (
            <g className={styles.playheadGroup}>
              <line
                x1={liveInfo.x}
                y1={padding.top}
                x2={liveInfo.x}
                y2={height - padding.bottom}
                className={styles.playheadLine}
              />
              <circle
                cx={liveInfo.x}
                cy={padding.top}
                r={3.5}
                className={styles.playheadHandle}
              />
              {liveInfo.y != null && (
                <g>
                  <circle
                    cx={liveInfo.x}
                    cy={liveInfo.y}
                    r={9}
                    className={styles.tracerPulse}
                    style={{ stroke: color }}
                  />
                  <circle
                    cx={liveInfo.x}
                    cy={liveInfo.y}
                    r={4.5}
                    className={styles.tracerDot}
                    style={{ fill: color }}
                  />
                </g>
              )}
            </g>
          )}
        </svg>
      </div>
    </div>
  );
}

