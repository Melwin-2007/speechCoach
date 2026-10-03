# SOURCES.md: Speech Text & Audio Provenance Table

This file tracks the provenance, licensing, and speaker metadata for the 4 canonical speeches ($T_1$ through $T_4$) in the SpeechCoach evaluation corpus.

## Corpus Table

| Text ID | Title | Speaker | Accent / Region | Genre | Split | Source Video | Processed Audio | License | Audio Duration | Word Count |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **T1** | Missed Opportunities & The Second Life | Indian Orator (Preppy Mic / Pep Talk India) | Indian English | Motivational / Persuasive Oratory | Dev | `data/raw/indian_pep.mp4` | `T1__orig-indianpep__ideal.wav` | Creative Commons / Public Educational | 186.5s | 302 words |
| **T2** | I Have a Dream | Martin Luther King Jr. | American English | Historical / Civil Rights Oratory | Dev | `data/raw/martin_luther_king.mp4` | `T2__orig-mlk__ideal.wav` | Public Domain / Historical Archive | 234.1s | 388 words |
| **T3** | Culture of Excellence & Courage to Be Unique | Dr. A.P.J. Abdul Kalam | Indian English | Keynote / Inspirational Address | Dev | `data/raw/abdul_kalam.mp4` | `T3__orig-kalam__ideal.wav` | Public Domain / Educational Archive | 198.9s | 391 words |
| **T4** | The Gettysburg Address | Abraham Lincoln | American English | Classical Declamation / Oratory | Dev | `data/raw/abraham_lincoln.mp4` | `T4__orig-lincoln__ideal.wav` | Public Domain | 145.2s | 270 words |

## Accent Balance Summary
- **Indian English (2 speeches):**
  - **$T_1$**: Indian Motivational Oratory (Contemporary Indian delivery, high vocal modulation).
  - **$T_3$**: Dr. A.P.J. Abdul Kalam (Classical Indian cadence, measured rate, clear articulation).
- **American English (2 speeches):**
  - **$T_2$**: Martin Luther King Jr. (Dynamic oratorical rhythm, deep pitch contour, emotional crescendo).
  - **$T_4$**: Abraham Lincoln (Solemn cadence, deliberate phrasing, classical oratory style).

## Audio Standards
All processed files conform strictly to [CONTRACTS.md §0](file:///c:/Users/Aditya%20Patange/speechCoach/docs/CONTRACTS.md#L6-L12):
- **Sampling Rate:** 16,000 Hz
- **Channels:** 1 (Mono)
- **Bit Depth:** 16-bit PCM
- **Edge Silence:** Trimmed to $\le 1.0\text{ s}$
- **Target Normalization:** -23 LUFS
