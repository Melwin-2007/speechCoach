import React, { useState, useEffect } from 'react';
import styles from './TypewriterHero.module.css';

export default function TypewriterHero({ text, subtitle, onComplete }) {
  const [displayedLength, setDisplayedLength] = useState(0);
  const [isTyping, setIsTyping] = useState(true);
  const [showSubtitle, setShowSubtitle] = useState(false);

  useEffect(() => {
    if (displayedLength < text.length) {
      const char = text[displayedLength];
      let delay = 35; // Default typing speed
      if (char === ' ' || char === '.') delay = 20; // Faster for spaces and punctuation

      const timeout = setTimeout(() => {
        setDisplayedLength(prev => prev + 1);
      }, delay);
      return () => clearTimeout(timeout);
    } else {
      setIsTyping(false);
      // Wait for a beat, then fade in subtitle
      const subtitleTimer = setTimeout(() => {
        setShowSubtitle(true);
      }, 300);
      
      // Wait another beat, then tell parent to show CTA
      const ctaTimer = setTimeout(() => {
        if (onComplete) onComplete();
      }, 800);
      
      return () => {
        clearTimeout(subtitleTimer);
        clearTimeout(ctaTimer);
      };
    }
  }, [displayedLength, text, onComplete]);

  return (
    <div className={styles.heroSection} id="home">
      <div className={styles.heroLabel}>AI-Powered Speech Evaluation</div>
      <h1 className={styles.heroTitle}>
        {text.split("").map((char, i) => {
          const isVisible = i < displayedLength;
          return (
            <span key={i} className={styles.charWrapper}>
              {i === 0 && displayedLength === 0 && isTyping && (
                <span className={styles.caret} style={{ left: 0, marginLeft: '-4px' }}></span>
              )}
              <span style={{ opacity: isVisible ? 1 : 0 }}>{char}</span>
              {i === displayedLength - 1 && isTyping && (
                <span className={styles.caret}></span>
              )}
            </span>
          );
        })}
      </h1>
      <div className={`${styles.subtitleWrapper} ${showSubtitle ? styles.subtitleVisible : ''}`}>
        <p className={styles.heroSubtitle}>
          {subtitle}
        </p>
      </div>
    </div>
  );
}
