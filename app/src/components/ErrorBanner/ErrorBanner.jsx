import React from "react";
import { AlertTriangle, RefreshCw, FileQuestion, WifiOff, Clock, ShieldAlert } from "lucide-react";
import styles from "./ErrorBanner.module.css";

const ERROR_KIND_MAP = {
  too_large: {
    title: "Audio File Too Large",
    desc: "The audio file exceeds the 25 MB limit. Please trim or compress the file before uploading.",
    icon: ShieldAlert,
  },
  audio: {
    title: "Invalid Audio Format",
    desc: "Could not decode audio. Please ensure the file is a valid WAV, MP3, M4A, FLAC, OGG, or WEBM recording.",
    icon: FileQuestion,
  },
  transcript: {
    title: "Transcript Required",
    desc: "Please provide the spoken text transcript matching the audio recording.",
    icon: FileQuestion,
  },
  validation: {
    title: "Validation Error",
    desc: "The submission parameters could not be validated. Please check the file and transcript.",
    icon: AlertTriangle,
  },
  timeout: {
    title: "Analysis Timed Out",
    desc: "The request took longer than 120 seconds to process. Try analyzing a shorter speech segment.",
    icon: Clock,
  },
  network: {
    title: "Connection Failed",
    desc: "Could not reach the analysis server. Please verify your connection or start the local API service.",
    icon: WifiOff,
  },
  invalid_response: {
    title: "Unexpected Analysis Format",
    desc: "The server response did not match the expected analysis schema. Please retry.",
    icon: AlertTriangle,
  },
  server: {
    title: "Analysis Processing Error",
    desc: "An unexpected error occurred while analyzing the speech. Please try again.",
    icon: AlertTriangle,
  },
};

export default function ErrorBanner({ error, onRetry, onClear }) {
  if (!error) return null;

  const isObj = typeof error === "object" && error !== null;
  const kind = isObj ? error.kind : "server";
  const rawMessage = isObj ? error.message : String(error);

  const config = ERROR_KIND_MAP[kind] || ERROR_KIND_MAP.server;
  const IconComponent = config.icon;

  return (
    <div className={styles.banner} role="alert">
      <div className={styles.iconCol}>
        <IconComponent size={24} color="var(--bad)" />
      </div>
      <div className={styles.contentCol}>
        <h4 className="h4" style={{ color: "var(--bad)", margin: 0 }}>
          {config.title}
        </h4>
        <p className="body" style={{ color: "var(--ink-2)", margin: "var(--s-2) 0" }}>
          {config.desc}
        </p>
        {rawMessage && rawMessage !== config.desc && (
          <span className="mono-sm" style={{ color: "var(--muted)", wordBreak: "break-all" }}>
            Details: {rawMessage}
          </span>
        )}
      </div>
      <div className={styles.actionCol}>
        {onRetry && (
          <button type="button" className={styles.retryBtn} onClick={onRetry}>
            <RefreshCw size={15} /> Try again
          </button>
        )}
        {onClear && (
          <button type="button" className={styles.clearBtn} onClick={onClear}>
            Choose another file
          </button>
        )}
      </div>
    </div>
  );
}
