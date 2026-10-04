import React from "react";
import styles from "./LoadingCard.module.css";
import { Loader2 } from "lucide-react";

export default function LoadingCard() {
  return (
    <div className={styles.loadingContainer}>
      <div className={styles.spinnerRow}>
        <Loader2 size={24} className={styles.spinIcon} />
        <h3 className="h3">Analyzing Audio & Alignment...</h3>
      </div>
      
      <div className={styles.honestBars}>
        <div className={styles.barWrap}>
          <div className={styles.labelRow}>
            <span className="small">Extracting pitch contours</span>
            <span className="mono-sm" style={{color: "var(--muted)"}}>ms</span>
          </div>
          <div className={`${styles.barBg} skeleton`}>
            <div className={styles.barFill} style={{ animationDuration: "1.2s", width: "100%" }} />
          </div>
        </div>
        
        <div className={styles.barWrap}>
          <div className={styles.labelRow}>
            <span className="small">Aligning words to acoustic boundaries</span>
            <span className="mono-sm" style={{color: "var(--muted)"}}>ms</span>
          </div>
          <div className={`${styles.barBg} skeleton`}>
            <div className={styles.barFill} style={{ animationDuration: "2.4s", width: "65%" }} />
          </div>
        </div>

        <div className={styles.barWrap}>
          <div className={styles.labelRow}>
            <span className="small">Computing baseline comparisons</span>
            <span className="mono-sm" style={{color: "var(--muted)"}}>ms</span>
          </div>
          <div className={`${styles.barBg} skeleton`}>
            <div className={styles.barFill} style={{ animationDuration: "3.5s", width: "30%" }} />
          </div>
        </div>
      </div>
    </div>
  );
}
