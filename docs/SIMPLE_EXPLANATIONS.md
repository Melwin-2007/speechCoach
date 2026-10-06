# Simple Explanations: Every Complex Thing in Plain Words

This file does NOT replace any existing document. It is a companion that explains the hard parts in simple language. When in doubt, the original docs are the source of truth.

---

## Table of Contents
1. [The Big Picture](#1-the-big-picture)
2. [Audio and Sound Basics](#2-audio-and-sound-basics)
3. [What the Pipeline Actually Does (Step by Step)](#3-what-the-pipeline-actually-does-step-by-step)
4. [The Math (Every Formula Explained)](#4-the-math-every-formula-explained)
5. [The Dataset and Flaw Engine](#5-the-dataset-and-flaw-engine)
6. [Tools and Libraries](#6-tools-and-libraries)
7. [The Workflow System](#7-the-workflow-system)
8. [Glossary (A-Z)](#8-glossary-a-z)

---

## 1. The Big Picture

### What are we building?
Imagine a speech teacher who listens to your speech and says:
- "You rushed words 24 through 41"
- "Your pitch was flat between 0:15 and 0:28"
- "You scored 71 out of 100"

That's what SpeechCoach does, except the "teacher" is code — no AI guessing, just measuring numbers and comparing them.

### How does it work in one sentence?
We record "perfect" versions of a speech, then compare YOUR version against them mathematically, find where you differ too much, and tell you exactly what went wrong.

### The three big pieces

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  DATASET    │     │   PIPELINE   │     │   DASHBOARD  │
│  (Member A) │────►│  (Member B)  │────►│  (Member C)  │
│             │     │              │     │              │
│ "Good" and  │     │ Listens to   │     │ Shows the    │
│ "bad" audio │     │ your speech  │     │ results in   │
│ with labels │     │ and measures  │     │ the browser  │
│             │     │ everything   │     │              │
└─────────────┘     └──────────────┘     └──────────────┘
```

- **Member A** creates the data: ideal recordings + deliberately bad recordings with exact timestamps of where the flaws are.
- **Member B** builds the analyzer: the code that listens to audio and detects problems.
- **Member C** builds the website and packaging: upload your speech, see the results.
- **Member A** also keeps the data honest and the story clear: organizes the human recordings, listens to samples to check the labels, runs the listener test, and writes the technical document and video script.

### The six families of mistakes
The challenge plan groups speech problems into six families. Each of our flaw types belongs to one:
| Family | What goes wrong | Our flaw types |
|---|---|---|
| Pacing | too fast or too slow | PACE_FAST, PACE_SLOW |
| Pausing | missing, too long, or misplaced pauses (and "uh" fillers) | PAUSE_MISSING, PAUSE_EXCESS, PAUSE_MISPLACED, FILLERS |
| Pitch / monotony | flat or wobbly voice | MONOTONE, PITCH_ERRATIC |
| Volume dynamics | too quiet, or no loudness variation | VOLUME_DROP, FLAT_ENERGY |
| Articulation / clarity | mumbling | CLARITY |
| Emphasis | key words not stressed, or wrong words over-stressed | STRESS_MISSING, STRESS_EXAGGERATED |

### Hybrid idea: the number explains, the model decides
The measured difference from a good reading (the z-score) gives the *reason* in plain numbers. An optional small learned model can add a *confidence* that a stretch really is a flaw. The explanation text always comes from the measured numbers, never from the model.

---

## 2. Audio and Sound Basics

### Sample rate (16000 Hz / 16 kHz)
Sound is a continuous wave. A computer can't store a continuous wave, so it takes "snapshots" of the wave many times per second. **16,000 times per second** is our standard. Each snapshot is called a **sample**.

Think of it like a flipbook — more pages per second = smoother animation. 16 kHz is standard for speech (music uses 44.1 kHz because it has more detail to capture).

### Mono
Stereo = two channels (left ear, right ear). Mono = one channel. We only need mono because we're analyzing speech content, not where the sound is coming from.

### Waveform
The raw shape of the sound wave over time. If you open a file in Audacity, the squiggly line you see is the waveform. Loud = tall squiggles, quiet = short squiggles, silence = flat line.

### Frame
We don't analyze the entire audio at once. We chop it into tiny overlapping slices called **frames**. Our frames are **10 milliseconds** long (0.01 seconds). So a 1-minute speech has 6,000 frames.

Think of it like looking at a movie frame by frame instead of watching the whole thing.

### LUFS (Loudness Units Full Scale)
A standardized way to measure how loud audio is overall. We normalize all audio to **-23 LUFS** so that a quiet recording and a loud recording can be compared fairly. It's like making sure everyone is the same "distance from the microphone" before comparing.

### RMS (Root Mean Square)
A way to measure the "average loudness" of a chunk of audio. You take all the sample values, square them, take the mean, then take the square root. Bigger RMS = louder sound. We use it to compute dB levels.

---

## 3. What the Pipeline Actually Does (Step by Step)

### Step 1: Load and normalize the audio
- Convert to 16 kHz mono
- Adjust loudness to -23 LUFS (so all recordings are equally loud)

### Step 2: Parse the transcript
Take the text of the speech and break it into individual words. Handle punctuation (commas, periods, question marks) — these matter because they tell us where pauses *should* be.

Example: `"Ask not what your country can do for you."` becomes:
```
word 0: "Ask"    punct: ""
word 1: "not"    punct: ""
word 2: "what"   punct: ""
word 3: "your"   punct: ""
word 4: "country" punct: ""
word 5: "can"    punct: ""
word 6: "do"     punct: ""
word 7: "for"    punct: ""
word 8: "you"    punct: "."
```

### Step 3: Forced alignment (mapping words to audio)
This is where we figure out WHEN each word is spoken. The MMS_FA model (a pre-trained neural network from Meta) listens to the audio and the words, and tells us the start and end time of each word.

Example output:
```
"Ask"     → starts at 1.20s, ends at 1.52s
"not"     → starts at 1.55s, ends at 1.78s
"what"    → starts at 1.80s, ends at 2.05s
```

Why is this important? Because we need to know WHERE in the audio to look when we say "words 24-41 were rushed." Without alignment, we'd just have audio with no idea which part is which word.

### Step 4: Extract features (measuring the sound)
For every frame (every 10ms), we measure several things:

| Feature | What it measures | Plain English |
|---|---|---|
| **F0 (pitch)** | How high or low the voice is | Think of a piano — high notes vs. low notes |
| **Semitones (st)** | Pitch relative to the speaker's average | "How much higher/lower than your normal voice" |
| **dB (loudness)** | How loud each moment is | Volume level |
| **dB_rel** | Loudness relative to the speaker's loudest | "How much quieter than your peak volume" |
| **Spectral flux** | How much the sound's texture changes | Crisp articulation = high flux; mumbling = low flux |
| **MFCC** | The "fingerprint" of the sound | Captures the shape of vowels and consonants |
| **HNR** | Harmonic-to-noise ratio | Clear voice = high HNR; breathy/raspy = low HNR |

### Step 5: Compute per-word statistics
Instead of thousands of frame-level numbers, we summarize: for each word, what was the average pitch? Average loudness? How long was the pause before it?

### Step 6: Window statistics (the "neighborhood" view)
Instead of looking at one word alone, we look at a **sliding window of 6 words** centered on each word. This gives us smoother, more meaningful measurements like "how fast is this section?" rather than "how long is this one word?"

Think of it like a moving average — it smooths out random variation.

### Step 7: Build a baseline (what "good" sounds like)
We have multiple ideal recordings of the same text. We average their measurements to create a **baseline** — the "expected" values for each word.

Example: if three good speakers said word 15 with a duration of 0.3s, 0.35s, and 0.32s, the baseline duration for word 15 is about 0.32s.

### Step 8: Compute deviation signals (how different are you?)
For each word, we compare the participant's measurement to the baseline:

```
You spoke at 5.9 syllables/second
Baseline was 4.1 syllables/second
→ You were faster than normal
```

We do this for pace, pauses, pitch variation, loudness, dynamics, and clarity.

### Step 9: Calibration and z-scores (is the difference meaningful?)
Here's the key insight: even GOOD speakers differ from each other. Speaker A might naturally be a bit faster than Speaker B, and that's fine.

**Calibration** measures how much good speakers naturally differ from each other. We call this natural spread **sigma (σ)**.

Then we compute a **z-score**: `z = your_deviation / sigma`

- z = 0 → you're right at the baseline (normal)
- z = 1 → you differ by 1 sigma (still within normal range)
- z = 3 → you differ by 3 sigmas (3× more different than good speakers differ from each other — this is a real problem)

**Example:** If good speakers' pace naturally varies by ±0.1 (that's sigma), and you deviate by 0.3, your z = 0.3 / 0.1 = 3.0. That's a big deal.

### Step 10: Find flaw regions
We scan the z-scores and look for stretches of consecutive words where z is too high (above a threshold). These stretches are **flaw regions**.

Example: words 24–41 all have pace z-scores above 2.5 → that's a "PACE_FAST" flaw region from 12.4s to 19.8s.

### Step 11: Explain each flaw
For each detected region, we fill in a template with the actual measured numbers:
- **Observed:** "You spoke at 5.9 syllables/second"
- **Deviation:** "Baseline is 4.1 syl/s; you were 44% faster (z = -4.5)"
- **Where:** "Words 57–71 (0:42.1 – 0:51.3)"
- **Why:** "Rushing reduces the listener's comprehension time"
- **Fix:** "Practice this section at 80% speed, then gradually increase"

No AI writes these — they're fixed templates filled with real numbers.

### Step 12: Score the delivery
Each of 7 dimensions gets a score from 0–100:
- **Pacing** (are you too fast/slow?)
- **Pausing** (are your pauses right?)
- **Pitch** (is your voice expressive?)
- **Energy** (are you loud enough?)
- **Emphasis** (do you stress the right words?)
- **Clarity** (are you mumbling?)
- **Fluency** (any "umm"s or repetitions?)

The overall score is a weighted average of these.

---

## 4. The Math (Every Formula Explained)

### Pitch normalization: `st = 12 * log2(f0 / median_f0)`

**Problem:** Different people have different voice pitches. A man might speak at 120 Hz, a woman at 220 Hz. We can't directly compare "120 Hz vs 220 Hz."

**Solution:** Convert to **semitones relative to the speaker's own average pitch**. A semitone is a musical half-step. This formula says: "How many half-steps above or below YOUR average are you right now?"

- `f0` = your current pitch in Hz
- `median_f0` = your average pitch over the whole recording
- `12 * log2(...)` = the math that converts a frequency ratio to semitones

**Result:** Both the man and the woman will show values like -2, 0, +3 semitones. Now they're comparable.

**Numeric example:** Speaker's median F0 = 150 Hz. Current F0 = 200 Hz.
`st = 12 × log₂(200/150) = 12 × log₂(1.333) = 12 × 0.415 = 4.98 semitones` above their average.

### Loudness normalization: `db_rel = 20*log10(rms) - P95`

**Problem:** One person recorded close to the mic (loud), another far away (quiet). Raw dB values aren't comparable.

**Solution:** Measure loudness relative to the speaker's own loud moments (95th percentile). So `db_rel = 0` means "as loud as your typical loud moment" and `db_rel = -10` means "10 dB quieter than your loud parts."

**Why 95th percentile and not maximum?** Because maximum might be a one-off spike (a cough, a pop). The 95th percentile is a more stable reference.

### Pace signal: `pace = log(P.win_dur / B.win_dur)`

**Plain English:** How much slower or faster are you than the baseline, in log scale?

- `P.win_dur` = how long it took YOU to say this 6-word window
- `B.win_dur` = how long the baseline speakers took
- `log(...)` = makes the scale symmetric (2× faster gives the same magnitude as 2× slower, just opposite sign)

**Result:** 
- pace = 0 → same speed as baseline
- pace < 0 → you're faster (window took less time)
- pace > 0 → you're slower (window took more time)

**Numeric example:** You took 1.8s, baseline took 2.4s. `pace = log(1.8/2.4) = log(0.75) = -0.288`. That's a negative number → you're faster.

### Pause signal: `pause = P.pause_before - B.pause_before`

Simplest one. Just the difference in seconds.
- 0 → same pause length
- Positive → you paused longer than expected
- Negative → you paused less than expected (or skipped a pause)

### Pitch variability signal: `pitch = log(P.f0_std / B.f0_std)`

How much does your pitch vary compared to the baseline?
- 0 → same amount of pitch variation
- Negative → less variation (monotone, flat, robotic)
- Positive → more variation (erratic, sing-song)

### Calibration (sigma): `sigma = max(1.4826 * MAD(values), floor)`

**MAD = Median Absolute Deviation.** A robust way to measure spread (like standard deviation, but not thrown off by outliers).

How to compute MAD:
1. Take all the values
2. Find the median
3. Compute the absolute distance of each value from the median
4. The median of those distances is the MAD

**1.4826** is a magic constant that makes MAD comparable to standard deviation for normal distributions.

**Floor:** A minimum value for sigma. Without it, if all ideal speakers were nearly identical on some signal, sigma could be tiny, and any small deviation would look like a z = 100 catastrophe. The floor prevents that.

### Z-score: `z = signal / sigma`

How many "standard good-speaker differences" is this deviation?

- |z| < 2 → probably fine (within normal variation)
- |z| ≥ 2 → minor flaw
- |z| ≥ 3 → moderate flaw
- |z| ≥ 4.5 → major flaw

### Severity: `severity = clip((mean|z| - 1.5) / 4.5, 0, 1)`

Converts the average z-score of a flaw region into a 0–1 number.
- mean|z| = 1.5 → severity = 0 (barely a flaw)
- mean|z| = 6.0 → severity = 1.0 (as bad as it gets)
- `clip(x, 0, 1)` means "if x < 0, make it 0; if x > 1, make it 1"

### Scoring formula: `p = clip((|z| - z_free) / (z_max - z_free), 0, 1)`

For each word: how much of a "penalty" does this z-score deserve?

- `z_free = 1` → z-scores below 1 get ZERO penalty (small differences are free)
- `z_max = 4` → z-scores of 4 or above get FULL penalty
- Between 1 and 4, the penalty scales linearly

Then: `dimension_deviation = 0.6 × mean(penalties) + 0.4 × P90(penalties)`
- 60% weight on the average penalty (overall quality)
- 40% weight on the 90th percentile penalty (worst moments matter more)

Then: `dimension_score = 100 × (1 - deviation)`
- deviation = 0 → score = 100 (perfect)
- deviation = 1 → score = 0 (terrible)

---

## 5. The Dataset and Flaw Engine

### What is the WORLD vocoder?
A **vocoder** is software that can take apart a sound and put it back together. WORLD specifically:
1. **Analyzes** speech into three components:
   - **F0**: the pitch at each moment
   - **Spectral envelope (sp)**: the shape of the sound (what makes an "ah" different from an "ee")
   - **Aperiodicity (ap)**: how breathy/noisy the voice is
2. **Modifies** any of these components (flatten the pitch, speed it up, make it quieter)
3. **Synthesizes** a new audio file from the modified components

It's like taking a LEGO house apart, swapping some bricks, and rebuilding it.

### Why synthesize flaws instead of just recording bad speeches?
Three reasons:
1. **Exact timestamps for free.** When we speed up words 24-41 by 1.35×, we KNOW exactly where the flaw is because we put it there. No human annotation needed.
2. **Controlled gradient.** We can make L1 (barely noticeable) through L5 (extremely bad) versions with precise parameter control.
3. **Scale.** We need about 470 files (about 59 per text across 8 texts). Recording and labeling that many by hand would take weeks.

We ALSO record real human flaws to prove the system works on natural speech, not just synthetic tricks.

### The resynth_control
Every synthetic file goes through WORLD (analyze → synthesize). Even the "ideal" gets this treatment, producing a `resynth_control`. Why? Because WORLD adds a subtle "vocoder sound." If we compared raw ideal audio against WORLD-processed flawed audio, a detector might cheat by just hearing the vocoder artifacts. The control ensures fair comparison.

### Time program
When we speed up or slow down part of a recording, we need to keep track of how the original timestamps map to the new timestamps. The **time program** is a list of anchors:

```
Original time → New time
0.0s          → 0.0s        (start, unchanged)
12.4s         → 12.4s       (start of flaw region, still the same)
19.8s         → 17.5s       (end of flaw region — 7.4s of audio compressed into 5.1s)
58.0s         → 55.7s       (end of file — shifted by the time we saved)
```

This lets us know exactly where each word ends up in the new file.

### Severity levels (L0–L5)

| Level | What it sounds like | How much of the clip is affected |
|---|---|---|
| L0 | Perfect (or control) | 0% |
| L1 | You probably wouldn't notice | 10% |
| L2 | Slightly off | 15% |
| L3 | Clearly noticeable | 25% |
| L4 | Quite bad | 40% |
| L5 | Painful to listen to | 70% |

### Composites
Some real speech problems come in combos: someone who rushes AND goes monotone, or someone who mumbles AND has no dynamics. Composites are synthetic files with 2–3 flaw types layered together.

### Splits: by text AND by speaker
- **Dev texts (T1, T2, T4, T5):** used for development and tuning. You run it many times, adjust thresholds, and improve.
- **Test texts (T3, T6):** used ONCE at the end. You never tune on them.
- **Stress texts (T7, T8):** never part of the reference library, so the system must switch to No-reference mode. They test "a speech we have never seen".
- **Speakers:** h1-h8 (and the historical originals) are training voices, h9-h10 are validation voices (used to choose thresholds), h11-h12 are test voices (used once). We never put clips of the same person in both training and test, because the system could then "recognize the voice" instead of finding the flaw.

If you tune on the test set, you're cheating — your numbers look good but won't hold up on truly new data.

### Severity: our 5 levels vs the plan's 4
Our files use L1-L5. In the technical document we also report the plan's 0-4 scale: L0 = 0 good, L1 and L2 = 1 subtle, L3 = 2 noticeable, L4 = 3 strong, L5 = 4 extreme.

### Recording real people (Member A)
Synthetic flaws give exact timestamps, but real people prove the system works on natural speech. A teammate or volunteer reads a text in a quiet room with the phone about 15-20 cm away, with 5 seconds of silence before and 2 after (see `RECORDING_PROTOCOL.md`). Original files are never edited or deleted. Everyone who is recorded agrees that their voice can be published.

---

## 6. Tools and Libraries

### Python libraries

| Library | What it does | Where we use it |
|---|---|---|
| **numpy** | Fast math on arrays of numbers | Everywhere — all our signals are numpy arrays |
| **scipy** | Scientific computing (signal processing, statistics) | Signal filtering, statistical tests |
| **pandas** | Tables of data (like Excel in Python) | metadata.csv, evaluation results |
| **librosa** | Audio analysis toolkit | Loading audio, spectral features, MFCC |
| **soundfile** | Reading/writing audio files | Loading and saving WAV files |
| **pyloudnorm** | Loudness normalization | Making all audio the same perceived loudness (-23 LUFS) |
| **parselmouth** | Python wrapper for Praat (phonetics software) | F0 (pitch) extraction, HNR |
| **pyworld** | Python wrapper for the WORLD vocoder | Analyzing and resynthesizing audio for flaw injection |
| **torch / torchaudio** | Deep learning framework | Running the MMS_FA forced alignment model on GPU |
| **scikit-learn** | Machine learning tools | Possibly for clustering or evaluation metrics |
| **ruptures** | Change-point detection | Potentially for finding transitions in signals |
| **cmudict** | Carnegie Mellon pronunciation dictionary | Counting syllables in words |
| **num2words** | Converts numbers to words | "42" → "forty two" for transcript parsing |
| **FastAPI** | Web framework for the backend API | HTTP endpoints (/analyze, /health, /demo) |
| **uvicorn** | Web server that runs FastAPI | Serving the API |
| **pydantic** | Data validation | Making sure JSON responses match the contract |
| **matplotlib** | Plotting | Generating figures for evaluation and the technical document |
| **pytest** | Testing framework | Running all our unit tests |

### Frontend libraries

| Library | What it does |
|---|---|
| **React** (via Vite) | UI framework — builds the interactive dashboard |
| **wavesurfer.js v7** | Renders the audio waveform with clickable/playable regions |
| **Plotly.js** | Interactive charts (pitch over time, energy over time, etc.) |

### Key tools

| Tool | What it does |
|---|---|
| **Docker** | Packages the entire app (Python + frontend + model) into one container that runs anywhere |
| **Hugging Face Spaces** | Free hosting platform where we deploy the live demo |
| **Audacity** | Free audio editor — used for listening to recordings and manually labeling flaw timestamps |
| **ffmpeg** | Command-line tool for converting audio formats (m4a → wav, stereo → mono, resampling) |
| **Git / GitHub** | Version control — tracks all code changes, enables collaboration |

### What is MMS_FA?
**Massively Multilingual Speech - Forced Alignment.** A neural network model from Meta (Facebook) that aligns text to audio. You give it a WAV file and a transcript, and it tells you the start/end time of each word. It runs on the GPU, which makes it much faster than doing it on CPU.

### What is Praat?
Praat is a phonetics software that's been used by linguists for decades. It's extremely reliable for measuring pitch (F0). We use it through the `parselmouth` Python library rather than the Praat GUI. Its `to_pitch_ac` function uses **autocorrelation** — a mathematical method to find repeating patterns in a signal (which is what pitch is: a repeating wave).

---

## 7. The Workflow System

### Why all these rules?
When four people use AI coding assistants simultaneously:
- Each AI might invent different JSON formats → nothing fits together
- An AI might "helpfully" rewrite files that were working → breaks other people's code
- An AI might make tests pass by cheating → bugs hide until demo day
- Each new AI chat forgets everything → decisions get re-argued

The rules prevent all of this.

### Frozen contracts
The interfaces between Member A, B and C are **locked**. The JSON format, function signatures, file names, and enum values cannot change without all 3 members agreeing. (Proposed additions in v1.1 are tagged in `CONTRACTS.md` until everyone approves.) This is the #1 most important rule. If A's code outputs a JSON that B's code expects, and someone changes the format, everything breaks.

### Ownership
Each member can only edit files in their designated folders. If you need a change in someone else's area, you write a request in HANDOFF.md. This prevents conflicting edits and makes it clear who's responsible for what.

### The work loop
Every single task follows this cycle:
1. **PLAN** → Tell the AI what to do, it writes a plan (NO code yet)
2. **APPROVE** → You read the plan, make sure it makes sense
3. **IMPLEMENT** → AI writes the code
4. **RUN** → You actually run it and see real output
5. **TEST** → Run the tests
6. **REPORT** → Document what was done
7. **COMMIT** → Save to git

### HANDOFF.md
AI assistants have no memory between conversations. HANDOFF.md is the "shared brain" — everyone appends what they did, what's broken, and what they need from others. Every new AI session reads the latest entries to understand the current state.

### Feature freeze
After Day 6, no new features. Only bug fixes, documentation, and video. This prevents the common hackathon trap of "let me just add one more thing" at 3 AM on the last day, which breaks everything.

### make check
One command that runs all tests and a smoke test. It must pass before any code is committed. This is the safety net — if `make check` is green, the project is in a working state.

### Why "no LLM in the product"?
Our explanations (the "why" and "fix" fields) are generated by filling templates with measured numbers, not by asking ChatGPT. This ensures:
- **Determinism:** Same input always gives same output
- **Reproducibility:** A judge can verify the explanation by checking the numbers
- **No hallucination:** LLMs can make things up; our templates can't

---

## 8. Glossary (A-Z)

| Term | Simple explanation |
|---|---|
| **Aperiodicity (ap)** | How "noisy" or "breathy" the voice is at each moment. Pure tone = 0, whispering = high |
| **Autocorrelation** | A math trick to find repeating patterns. Used to detect pitch (the voice's repeating wave) |
| **Baseline** | The "expected" values — what a good speaker sounds like, averaged from multiple ideal recordings |
| **Calibration** | Measuring how much good speakers naturally differ from each other, to know what counts as a real flaw |
| **CMVN** | Cepstral Mean and Variance Normalization — making MFCCs speaker-independent by subtracting each speaker's average |
| **Confidence** | Optional number (0-1) saying how sure the system is that a region is a real flaw (from the learned scorer). Empty when only rules are used |
| **Family (flaw family)** | One of six groups of mistakes: pacing, pausing, pitch, volume, clarity, emphasis |
| **Held-out speaker** | A voice never used for training or tuning (h11, h12), so the test shows the system works on new people |
| **Composite flaw** | A synthetic file with 2–3 flaw types combined (e.g., fast AND monotone) |
| **Contrastive** | Comparing two things side by side — here, "good" vs "bad" versions of the same speech |
| **dB (decibel)** | A logarithmic unit of loudness. +10 dB sounds about twice as loud |
| **Deterministic** | Same input always produces exactly the same output. No randomness |
| **Dev split** | Data used for development and tuning (T1, T2, T4, T5, speakers in train/val) |
| **F0 (fundamental frequency)** | The pitch of the voice in Hz. Higher F0 = higher-pitched voice |
| **F1 score** | A combined measure of precision and recall. F1 = 1 means perfect detection |
| **Feature freeze** | The deadline after which no new features are added (end of Day 6) |
| **FFT** | Fast Fourier Transform — converts a sound wave into a list of frequencies (like a prism splits white light into colors) |
| **Filled pause** | An "um", "uh", or "er" — detected as a voiced gap between words |
| **Floor (sigma floor)** | Minimum allowed value for sigma, prevents division-by-near-zero explosions |
| **Forced alignment** | Matching each word in a transcript to its exact time position in the audio |
| **Frame** | A 10-millisecond slice of audio. We measure features per frame |
| **Geometric mean** | Multiply all values and take the Nth root. Used for ratio-type quantities (durations). Less affected by outliers than arithmetic mean |
| **Ground truth** | The correct answer. For synthetic flaws, we know exactly where the flaw is because we put it there |
| **Hashlib** | Python library for generating deterministic hashes. We use SHA-256 for caching and seeding |
| **HNR** | Harmonic-to-Noise Ratio — measures voice clarity. High = clear voice, low = breathy/raspy |
| **Hop** | The step size between consecutive frames. 0.01s hop = frames at 0.00, 0.01, 0.02, 0.03... |
| **IoU (Intersection over Union)** | How much two time ranges overlap. IoU = 1 means perfect overlap, IoU = 0 means no overlap. We use IoU ≥ 0.5 to count a detection as correct |
| **Leave-one-out** | A calibration technique: remove one ideal recording, build the baseline from the rest, measure how different the removed one is. Repeat for each recording. This tells us the natural spread |
| **Log scale** | A scale where multiplication becomes addition. Makes ratios symmetric: 2× faster and 2× slower are the same distance from 1× |
| **MAD** | Median Absolute Deviation — a robust measure of spread that isn't fooled by outliers |
| **MFCC** | Mel-Frequency Cepstral Coefficients — a compact "fingerprint" of a sound's character at each moment. Captures vowel quality, consonant type, etc. |
| **Mode A (reference)** | Analysis mode when we have ideal recordings of the same text as the participant |
| **Mode B (prior)** | Analysis mode when we DON'T have matching ideal recordings — uses general statistics about what good speech sounds like. The dashboard calls it "No-reference mode" |
| **Oracle alignment** | Using the true word times from the label file instead of the aligner's guess. Comparing results with and without it shows how much error comes from alignment and how much from the detector |
| **Monotone** | Speaking with very little pitch variation. Sounds robotic or boring |
| **NaN** | "Not a Number" — used when pitch can't be measured (silence, unvoiced consonants like "s", "f") |
| **Normalization** | Adjusting values so different speakers can be compared fairly |
| **P90 / P95** | 90th or 95th percentile — the value that 90% or 95% of data falls below |
| **Phrase boundary** | A punctuation mark (period, comma, semicolon, etc.) that indicates a natural pause point |
| **Precision** | Of all the flaws we DETECTED, what fraction were real flaws? High precision = few false alarms |
| **Recall** | Of all the ACTUAL flaws, what fraction did we detect? High recall = few missed flaws |
| **Region** | A stretch of consecutive words identified as having a flaw |
| **Seed** | A starting number for "random" operations that makes them reproducible. Same seed = same "random" result every time |
| **Semitone** | A musical half-step. 12 semitones = 1 octave = double the frequency |
| **Sigma (σ)** | The calibrated natural spread — how much good speakers naturally differ from each other on a given signal |
| **Spectral envelope** | The shape of the sound's frequency content — what gives a vowel its identity |
| **Spectral flux** | How much the sound's frequency content changes from one frame to the next. High flux = crisp articulation. Low flux = mumbling |
| **Spearman correlation** | A measure of whether two rankings agree. We use it to check if our scores decrease as severity increases |
| **Temporal grounding** | Pinpointing WHEN in the audio a flaw occurs (start time, end time) |
| **Test split** | Data used once at the end for final evaluation (texts T3, T6 and test speakers h11-h12). Never tune on this |
| **Threshold** | A cutoff value. If z > threshold → flag as a flaw. Stored in `configs/thresholds.yaml` |
| **Unvoiced** | Speech sounds made without vocal cord vibration (like "s", "f", "t", "k"). These have no pitch |
| **Voiced** | Speech sounds made with vocal cord vibration (all vowels, and consonants like "m", "n", "z"). These have pitch |
| **Vocoder** | Software that can decompose sound into components and resynthesize it. WORLD is our vocoder |
| **Window** | A sliding group of consecutive words (6 plus the centre, about 2-3 seconds of speech) used to compute local statistics; neighbouring windows overlap almost completely |
| **Stress (emphasis)** | Making key words stand out with a bit more pitch movement, loudness and length |
| **z-score** | How many sigmas away from the baseline. z=3 means "3× more different than good speakers normally are" |

---

> **Remember:** if any of this contradicts the original docs (ARCHITECTURE.md, CONTRACTS.md, etc.), the original docs win. This file is just a plain-English companion.
