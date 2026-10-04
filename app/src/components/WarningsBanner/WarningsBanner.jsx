import React, { useState } from "react";
import { AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import styles from "./WarningsBanner.module.css";

export default function WarningsBanner({ warnings }) {
  const [expanded, setExpanded] = useState(false);

  if (!warnings || !Array.isArray(warnings) || warnings.length === 0) {
    return null;
  }

  return (
    <div className={styles.banner} role="status">
      <div className={styles.headerRow} onClick={() => setExpanded(!expanded)}>
        <div className={styles.titleCol}>
          <AlertTriangle size={18} color="var(--warn)" />
          <span className="small-strong" style={{ color: "var(--ink)" }}>
            {warnings.length} {warnings.length === 1 ? "Audio Processing Warning" : "Audio Processing Warnings"}
          </span>
        </div>
        <button
          type="button"
          className={styles.toggleBtn}
          aria-expanded={expanded}
          aria-label="Toggle warning details"
        >
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {expanded && (
        <ul className={styles.warningList}>
          {warnings.map((w, idx) => (
            <li key={idx} className={styles.warningItem}>
              <span className="small" style={{ color: "var(--ink-2)" }}>{w}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
