import React, { useState, useEffect, useRef } from "react";
import {
  Upload,
  ArrowRight,
  BookOpen,
  CheckCircle,
  AlertTriangle,
  FileAudio,
  ArrowLeft,
  Download,
  X,
} from "lucide-react";
import Styleguide from "./components/Styleguide/Styleguide";
import ScoreCard from "./components/ScoreCard/ScoreCard";
import RadarCard from "./components/Charts/RadarCard";
import WaveformPanel from "./components/WaveformPanel/WaveformPanel";
import WordRibbon from "./components/WordRibbon/WordRibbon";
import ChartStack from "./components/Charts/ChartStack";
import TranscriptPanel from "./components/TranscriptPanel/TranscriptPanel";
import FlawList from "./components/FlawList/FlawList";
import ExplanationCard from "./components/ExplanationCard/ExplanationCard";
import { fmtTime } from "./lib/format";
import styles from "./App.module.css";

const SAMPLE_TRANSCRIPTS = {
  T4: "Where the mind is without fear and the head is held high. Where knowledge is free. Where the world has not been broken up into fragments by narrow domestic walls. Where words come out from the depth of truth. Where tireless striving stretches its arms towards perfection. Where the clear stream of reason has not lost its way into the dreary desert sand of dead habit. Where the mind is led forward by thee into ever-widening thought and action. Into that heaven of freedom, my Father, let my country awake. We speak not only for ourselves, but for generations yet unborn who look to us for courage, clarity, and truth.",
};

export default function App() {
  const [route, setRoute] = useState(window.location.hash || "#/");
  const [activeTab, setActiveTab] = useState("upload"); // 'upload' | 'sample'
  const [preset, setPreset] = useState("botched");

  // File & input state
  const [file, setFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState("/demo-audio/botched.wav");
  const [isDragOver, setIsDragOver] = useState(false);
  const [baselineId, setBaselineId] = useState("auto");
  const [transcript, setTranscript] = useState("");

  // Analysis state
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFlawId, setSelectedFlawId] = useState(null);
  const [currentTime, setCurrentTime] = useState(0);

  const fileInputRef = useRef(null);

  useEffect(() => {
    const handleHashChange = () => {
      setRoute(window.location.hash || "#/");
    };
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  // Default load botched mock dataset on mount so full graphs are instantly visible
  useEffect(() => {
    fetch("/mock_result.json")
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        if (json.flaws && json.flaws.length > 0) {
          setSelectedFlawId(json.flaws[0].id);
        }
      })
      .catch((err) => console.error("Could not load default mock data:", err));
  }, []);

  // Cleanup object URLs
  useEffect(() => {
    return () => {
      if (audioUrl && audioUrl.startsWith("blob:")) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return;
    const allowed = [".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"];
    const ext = selectedFile.name.substring(selectedFile.name.lastIndexOf(".")).toLowerCase();

    if (!allowed.includes(ext)) {
      setError("Please choose a supported audio file (WAV, MP3, M4A, FLAC, OGG, or WEBM).");
      return;
    }

    if (selectedFile.size > 25 * 1024 * 1024) {
      setError("Audio file is larger than 25 MB. Please select a smaller file.");
      return;
    }

    setError(null);
    setFile(selectedFile);
    const url = URL.createObjectURL(selectedFile);
    setAudioUrl(url);
  };

  const handleRemoveFile = () => {
    setFile(null);
    if (audioUrl && audioUrl.startsWith("blob:")) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleUseSampleTranscript = () => {
    setTranscript(SAMPLE_TRANSCRIPTS.T4);
  };

  const handleAnalyze = () => {
    setLoading(true);
    setError(null);

    let jsonUrl = "/mock_result.json";
    let wavUrl = "/demo-audio/botched.wav";

    if (activeTab === "sample") {
      jsonUrl = `/demo/${preset}.json`;
      wavUrl = `/demo-audio/${preset}.wav`;
    }

    setTimeout(() => {
      fetch(jsonUrl)
        .then((res) => {
          if (!res.ok) throw new Error(`HTTP ${res.status} reading ${jsonUrl}`);
          return res.json();
        })
        .then((json) => {
          setData(json);
          setAudioUrl(wavUrl);
          if (json.flaws && json.flaws.length > 0) {
            setSelectedFlawId(json.flaws[0].id);
          } else {
            setSelectedFlawId(null);
          }
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message);
          setLoading(false);
        });
    }, 400);
  };

  const handleDownloadJson = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `speechcoach_analysis_${data.meta.baseline_id || "result"}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const selectedFlaw = data?.flaws?.find((f) => f.id === selectedFlawId) || null;
  const wordCount = transcript.trim() ? transcript.trim().split(/\s+/).length : 0;
  const isAnalyzeDisabled = activeTab === "upload" ? (!file || wordCount < 5) : false;

  if (route === "#/styleguide") {
    return <Styleguide />;
  }

  return (
    <div className={styles.appLayout}>
      <nav className={styles.nav}>
        <div className={styles.logoRow}>
          <div className={styles.logoBars}>
            <div className={styles.logoBar1}></div>
            <div className={styles.logoBar2}></div>
            <div className={styles.logoBar3}></div>
          </div>
          <span className={styles.logoText}>SpeechCoach</span>
        </div>
        <div className={styles.navLinks}>
          <a href="#/styleguide" className={styles.styleguideBtn}>
            <BookOpen size={16} /> Design System & Styleguide
          </a>
        </div>
      </nav>

      <main className={styles.mainContent}>
        <div className={styles.heroSection}>
          <h1 className="display-xl">See exactly where your speech goes wrong.</h1>
          <p className={styles.subtitle}>
            Upload a recording and its text. We compare your delivery with a strong reference and point to the exact seconds that need work.
          </p>
        </div>

        {/* 1. Main Input Card */}
        <div className={styles.inputCard}>
          {/* Segmented Tabs */}
          <div className={styles.tabBar}>
            <div className={styles.segmentedTabs}>
              <button
                type="button"
                className={`${styles.tabBtn} ${activeTab === "upload" ? styles.tabBtnActive : ""}`}
                onClick={() => {
                  setActiveTab("upload");
                  setError(null);
                }}
              >
                Analyze a recording
              </button>
              <button
                type="button"
                className={`${styles.tabBtn} ${activeTab === "sample" ? styles.tabBtnActive : ""}`}
                onClick={() => {
                  setActiveTab("sample");
                  setError(null);
                }}
              >
                Try a sample
              </button>
            </div>
          </div>

          {activeTab === "upload" ? (
            <>
              {/* Drop Zone */}
              <input
                ref={fileInputRef}
                type="file"
                accept=".wav,.mp3,.m4a,.flac,.ogg,.webm"
                style={{ display: "none" }}
                onChange={(e) => handleFileSelect(e.target.files[0])}
              />

              {!file ? (
                <div
                  className={`${styles.dropZone} ${isDragOver ? styles.dropZoneActive : ""}`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current && fileInputRef.current.click()}
                >
                  <div className={styles.dropIconCircle}>
                    <Upload size={24} />
                  </div>
                  <div className={styles.dropTitle}>Drop your recording here</div>
                  <div className={styles.dropHelper}>
                    WAV, MP3, M4A, FLAC, OGG or WEBM · up to 25 MB
                  </div>
                  <button type="button" className={styles.chooseFileBtn}>
                    Choose an audio file
                  </button>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "var(--s-4)", marginBottom: "var(--s-6)" }}>
                  <div className={styles.fileChip}>
                    <div className={styles.fileChipInfo}>
                      <FileAudio size={20} color="var(--c-pitch)" />
                      <div>
                        <div className={styles.fileName}>{file.name}</div>
                        <div className={styles.fileSize}>{(file.size / (1024 * 1024)).toFixed(2)} MB</div>
                      </div>
                    </div>
                    <button
                      type="button"
                      className={styles.removeFileBtn}
                      onClick={handleRemoveFile}
                      aria-label="Remove file"
                    >
                      <X size={18} />
                    </button>
                  </div>
                  {audioUrl && (
                    <audio controls src={audioUrl} style={{ width: "100%", maxWidth: "520px", borderRadius: "var(--r-md)" }} />
                  )}
                </div>
              )}

              {/* Form Controls */}
              <div className={styles.formRow}>
                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>Which speech is this?</label>
                  <select
                    className={styles.selectInput}
                    value={baselineId}
                    onChange={(e) => setBaselineId(e.target.value)}
                  >
                    <option value="auto">Auto-detect matching baseline</option>
                    <option value="T1">T1 — Indian Pep Talk (Indian English)</option>
                    <option value="T2">T2 — Martin Luther King Jr. "I Have a Dream"</option>
                    <option value="T3">T3 — Dr. A.P.J. Abdul Kalam "Culture of Excellence"</option>
                    <option value="T4">T4 — Abraham Lincoln "Gettysburg Address"</option>
                    <option value="prior">Other speech, no reference (General Norms)</option>
                  </select>
                  <span className={styles.fieldHelper}>
                    Pick the matching text for the most precise baseline comparison.
                  </span>
                </div>

                <div className={styles.fieldGroup}>
                  <div className={styles.fieldLabelRow}>
                    <label className={styles.fieldLabel}>Transcript</label>
                    <span className={styles.fieldLink} onClick={handleUseSampleTranscript}>
                      Use sample transcript
                    </span>
                  </div>
                  <textarea
                    className={styles.textareaInput}
                    placeholder="Paste the exact spoken words with punctuation (minimum 5 words)..."
                    value={transcript}
                    onChange={(e) => setTranscript(e.target.value)}
                  />
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span className={styles.fieldHelper}>
                      Accurate punctuation ensures exact pause boundary analysis.
                    </span>
                    <span className="mono-sm" style={{ color: wordCount < 5 ? "var(--bad)" : "var(--muted)" }}>
                      {wordCount} words
                    </span>
                  </div>
                </div>
              </div>

              {/* Action */}
              <div className={styles.actionRow}>
                <span className="small">
                  {!file
                    ? "Add an audio recording to continue"
                    : wordCount < 5
                    ? "Add at least 5 words of transcript"
                    : "Ready to analyze"}
                </span>
                <button
                  type="button"
                  className={styles.analyzeBtn}
                  disabled={isAnalyzeDisabled || loading}
                  onClick={handleAnalyze}
                >
                  {loading ? "Analyzing..." : "Analyze recording"} <ArrowRight size={18} />
                </button>
              </div>
            </>
          ) : (
            /* Try a sample tab */
            <div>
              <p className="body" style={{ color: "var(--muted)", marginBottom: "var(--s-4)", textAlign: "center" }}>
                Select a precomputed benchmark recording to preview instant acoustic feedback:
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "var(--s-4)", marginBottom: "var(--s-6)" }}>
                <div
                  style={{
                    backgroundColor: "var(--blush)",
                    borderRadius: "var(--r-card)",
                    padding: "var(--s-5)",
                    cursor: "pointer",
                    border: preset === "botched" ? "2px solid var(--ink)" : "1px solid transparent",
                  }}
                  onClick={() => setPreset("botched")}
                >
                  <h3 className="h3">Botched Take</h3>
                  <p className="small" style={{ margin: "var(--s-2) 0" }}>Rushed pace, flat pitch, volume dips, and missing pauses.</p>
                  <span className="mono-sm">Score: ~42.1</span>
                </div>

                <div
                  style={{
                    backgroundColor: "var(--butter)",
                    borderRadius: "var(--r-card)",
                    padding: "var(--s-5)",
                    cursor: "pointer",
                    border: preset === "almost" ? "2px solid var(--ink)" : "1px solid transparent",
                  }}
                  onClick={() => setPreset("almost")}
                >
                  <h3 className="h3">Almost Perfect</h3>
                  <p className="small" style={{ margin: "var(--s-2) 0" }}>High quality delivery with one minor pacing rush.</p>
                  <span className="mono-sm">Score: ~88.4</span>
                </div>

                <div
                  style={{
                    backgroundColor: "var(--mint)",
                    borderRadius: "var(--r-card)",
                    padding: "var(--s-5)",
                    cursor: "pointer",
                    border: preset === "ideal" ? "2px solid var(--ink)" : "1px solid transparent",
                  }}
                  onClick={() => setPreset("ideal")}
                >
                  <h3 className="h3">Ideal Baseline</h3>
                  <p className="small" style={{ margin: "var(--s-2) 0" }}>Canonical baseline reading matching standard tempo and pitch variation.</p>
                  <span className="mono-sm">Score: ~94.2</span>
                </div>
              </div>

              <div style={{ textAlign: "center" }}>
                <button
                  type="button"
                  className={styles.analyzeBtn}
                  onClick={handleAnalyze}
                  disabled={loading}
                >
                  {loading ? "Loading sample..." : `Open ${preset} sample`} <ArrowRight size={18} />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Reassurance Ticks */}
        <div className={styles.reassuranceRow}>
          <span className={styles.tickItem}>
            <CheckCircle size={16} className={styles.tickIcon} /> Pinpoints the exact seconds
          </span>
          <span className={styles.tickItem}>
            <CheckCircle size={16} className={styles.tickIcon} /> Explains each flaw with numbers
          </span>
          <span className={styles.tickItem}>
            <CheckCircle size={16} className={styles.tickIcon} /> Free to try
          </span>
        </div>

        {/* Error message */}
        {error && (
          <div style={{ backgroundColor: "var(--blush)", padding: "var(--s-4)", borderRadius: "var(--r-md)", color: "var(--bad)", maxWidth: "880px", margin: "0 auto var(--s-6)" }}>
            <AlertTriangle size={18} style={{ verticalAlign: "middle", marginRight: "8px" }} /> {error}
          </div>
        )}

        {/* Results Section */}
        {data && !loading && (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--s-6)", marginTop: "var(--s-8)" }}>
            {/* 1. Results Header */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "var(--s-4)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "var(--s-4)" }}>
                <button
                  type="button"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--line)",
                    borderRadius: "var(--r-pill)",
                    padding: "8px 16px",
                    cursor: "pointer",
                    fontWeight: 600,
                    fontSize: "13px",
                  }}
                  onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
                >
                  <ArrowLeft size={16} /> Analyze another
                </button>
                <div style={{ display: "flex", flexDirection: "column" }}>
                  <span style={{ fontWeight: 700, fontSize: "16px", color: "var(--ink)" }}>
                    {file ? file.name : `${preset.toUpperCase()} Demo Take`}
                  </span>
                  <span style={{ fontSize: "13px", color: "var(--muted)" }}>
                    Duration: {fmtTime(data.meta.duration_s)} · Reference: {data.meta.baseline_id}
                  </span>
                </div>
              </div>

              <button
                type="button"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  backgroundColor: "var(--paper)",
                  border: "1px solid var(--line)",
                  borderRadius: "var(--r-pill)",
                  padding: "8px 16px",
                  cursor: "pointer",
                  fontWeight: 600,
                  fontSize: "13px",
                }}
                onClick={handleDownloadJson}
              >
                <Download size={16} /> Download JSON
              </button>
            </div>

            {/* 2. Top Graphs Row: ScoreCard + 7-Axis RadarCard */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "var(--s-6)" }}>
              <ScoreCard scores={data.scores} meta={data.meta} flawCount={data.flaws.length} />
              <RadarCard scores={data.scores} />
            </div>

            {/* 3. Main Split Layout: Left Charts & Waveform / Right Flaw Explanations */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "var(--s-6)", alignItems: "start" }}>
              {/* Left Column (Waveform, Ribbon, Time Series Graphs, Transcript) */}
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--s-6)" }}>
                {/* Waveform Panel */}
                <WaveformPanel
                  audioUrl={audioUrl}
                  duration={data.meta.duration_s}
                  flaws={data.flaws}
                  selectedFlawId={selectedFlawId}
                  onSelectFlaw={(id) => setSelectedFlawId(id)}
                  onTimeUpdate={(t) => setCurrentTime(t)}
                />

                {/* Word Alignment Ribbon */}
                <WordRibbon
                  words={data.words}
                  duration={data.meta.duration_s}
                  selectedFlaw={selectedFlaw}
                  onSelectWord={(w) => setCurrentTime(w.start)}
                />

                {/* 3-Tier Acoustic Time Series Charts */}
                <ChartStack
                  series={data.series}
                  meta={data.meta}
                  flaws={data.flaws}
                />

                {/* Interactive Transcript Panel */}
                <TranscriptPanel
                  words={data.words}
                  currentTime={currentTime}
                  selectedFlaw={selectedFlaw}
                  onWordClick={(w) => setCurrentTime(w.start)}
                />
              </div>

              {/* Bottom/Right Inspection: Flaw List & Detailed Math Explanation */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "var(--s-6)" }}>
                <FlawList
                  flaws={data.flaws}
                  selectedFlawId={selectedFlawId}
                  onSelectFlaw={(id) => setSelectedFlawId(id)}
                />
                <ExplanationCard
                  flaw={selectedFlaw}
                  onPlayFlaw={(f) => setCurrentTime(f.start)}
                />
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className={styles.footer}>
        Built for the Multimodal AI Hackathon 2026, Track C · SpeechCoach
      </footer>
    </div>
  );
}
