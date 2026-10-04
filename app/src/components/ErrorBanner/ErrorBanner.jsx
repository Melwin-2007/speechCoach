import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import styles from "./ErrorBanner.module.css";

const ERROR_MAP = {
  "File too large": "This audio file exceeds the maximum 25 MB limit. Please trim it or use a lower bitrate.",
  "Failed to fetch": "Could not connect to the analysis engine. Is the backend running?",
  "HTTP 500": "The DSP engine encountered an error analyzing your recording.",
  "HTTP 422": "The provided transcript is invalid or does not match the audio.",
  "default": "An unexpected error occurred during analysis.",
};

export default function ErrorBanner({ error, onRetry }) {
  if (!error) return null;

  // Find a friendly message mapping
  let friendlyMessage = ERROR_MAP.default;
  for (const [key, msg] of Object.entries(ERROR_MAP)) {
    if (error.includes(key) || error.includes(key.toLowerCase())) {
      friendlyMessage = msg;
      break;
    }
  }

  return (
    <div className={styles.banner}>
      <div className={styles.iconCol}>
        <AlertTriangle size={24} color="var(--bad)" />
      </div>
      <div className={styles.contentCol}>
        <h4 className="h4" style={{ color: "var(--bad)" }}>Analysis Failed</h4>
        <p className="body" style={{ color: "var(--ink-2)", margin: "var(--s-2) 0" }}>
          {friendlyMessage}
        </p>
        <span className="mono-sm" style={{ color: "var(--muted)", wordBreak: "break-all" }}>
          Details: {error}
        </span>
      </div>
      {onRetry && (
        <div className={styles.actionCol}>
          <button type="button" className={styles.retryBtn} onClick={onRetry}>
            <RefreshCw size={16} /> Retry
          </button>
        </div>
      )}
    </div>
  );
}
