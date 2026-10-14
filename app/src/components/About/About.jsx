import React from "react";
import { ArrowLeft, Sparkles } from "lucide-react";
import AboutProject from "./AboutProject";
import AboutTeam from "./AboutTeam";
import styles from "./About.module.css";

/**
 * About page presenting project architecture, principles, and team details.
 *
 * @param {Object} props
 * @param {(section?: string) => void} props.onNavigateHome
 */
export default function About({ onNavigateHome }) {
  const handleNavClick = (section) => {
    if (onNavigateHome) {
      onNavigateHome(section);
    } else {
      window.location.hash = section ? `#${section}` : "#/";
    }
  };

  return (
    <div className={styles.aboutPage}>
      <div className={styles.mainColumn}>
        {/* Top Navigation Bar */}
        <nav className={styles.nav}>
          <a
            href="#/"
            className={styles.navBrand}
            onClick={(e) => {
              e.preventDefault();
              handleNavClick("home");
            }}
          >
            <img src="/logo.png" alt="SpeechCoach" className={styles.logoImg} />
            <span className={styles.logoText}>SpeechCoach</span>
          </a>

          <div className={styles.navLinksPill}>
            <button
              type="button"
              className={styles.navLink}
              onClick={() => handleNavClick("home")}
            >
              Home
            </button>
            <button
              type="button"
              className={styles.navLink}
              onClick={() => handleNavClick("analyze")}
            >
              Analyze
            </button>
            <button
              type="button"
              className={styles.navLink}
              onClick={() => handleNavClick("insights")}
            >
              Insights
            </button>
            <button type="button" className={styles.navLinkActive}>
              About
            </button>
          </div>

          <div style={{ width: "80px" }} />
        </nav>

        {/* Main Content Area */}
        <main className={styles.aboutContent}>
          {/* Hero Banner */}
          <section className={styles.heroBanner}>
            <div className={styles.badgePill}>
              <Sparkles size={15} />
              <span>Multimodal AI Hackathon 2026 · Track C</span>
            </div>
            <h1 className={styles.heroTitle}>
              Contrastive Speech Analytics &amp; Temporal Grounding
            </h1>
            <p className={styles.heroSubtitle}>
              An explainable speech evaluation platform comparing human delivery against gold-standard baselines to diagnose and score delivery flaws with acoustic precision.
            </p>
            <button
              type="button"
              className={styles.heroBackBtn}
              onClick={() => handleNavClick("analyze")}
            >
              <ArrowLeft size={16} /> Return to Analyzer
            </button>
          </section>

          {/* Project Details */}
          <AboutProject />

          {/* Team Details */}
          <AboutTeam />
        </main>

        {/* Footer */}
        <footer className={styles.footer}>
          SpeechCoach · Multimodal AI Hackathon 2026 · Built with pride by VTU Belagavi Engineers
        </footer>
      </div>
    </div>
  );
}
