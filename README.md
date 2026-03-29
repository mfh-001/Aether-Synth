# Aether: Procedural Ambient Synthesizer

Live Link: https://huggingface.co/spaces/MFH-001/Aether

This repository features **Aether**, a browser-based procedural ambient music synthesizer that maps natural language mood descriptions to DSP synthesis parameters in real-time. The system runs entirely client-side via the Web Audio API. No backend, no model weights, no paid APIs, and exports high-quality stereo WAV files directly from the browser.

> **Related projects:** [FinSight AI](https://github.com/mfh-001/FinSight-AI) · [MediScan AI](https://github.com/mfh-001/AI-Medical-Assistant) · [PsoriScan AI](https://github.com/mfh-001/PsoriScan-AI) — projects that share the same philosophy: open-weight models, deployed systems.

## Overview

The system provides an end-to-end audio synthesis pipeline through an interactive browser interface:

- **NLP Parameter Mapping:** Natural language input is tokenised against a weighted keyword lexicon of ~80 acoustic clusters. Each token scores across 12 continuous DSP dimensions, producing a complete synthesis parameter set from free-form text.
- **Preset Blending:** Multi-token inputs (e.g. "dark ocean") trigger interpolation across the DSP parameter space, the two highest-scoring presets are linearly blended by their relative scores, producing genuinely novel parameter combinations rather than nearest-neighbour lookup.
- **Additive Synthesis:** A 5-layer Web Audio graph runs in real-time: sub-bass sine oscillator, a 25-oscillator pad stack with ±6 cent detuning, an FM-modulated shimmer sine, bandpass-filtered white noise, and an LFO-tremolo pulse layer.
- **Procedural Convolution Reverb:** The impulse response is synthesized directly into an `AudioBuffer` as exponentially decaying white noise, decay time τ maps from 1–12 seconds based on the spaciousness score. No IR audio files needed.
- **Offline WAV Export:** `OfflineAudioContext` renders 30s to 5-minute stereo audio faster than real-time (~8s for a 5-minute file). A hand-written 16-bit PCM encoder produces standards-compliant 44.1kHz WAV output with no external libraries.

## Why This Is Interesting Technically

Most text-to-audio systems: **text → neural network → audio tokens → vocoder**

The problem with that approach for a portfolio tool: requires GPU inference, model weights (gigabytes), latency, and API costs.

Aether: **text → token scoring → DSP parameter vector → Web Audio graph → WAV**

The insight is that a well-structured DSP parameter space (12 continuous dimensions covering frequency, timbre, spatiality, and modulation) can produce meaningfully varied and aesthetically coherent outputs purely from rule-based mapping, with zero inference cost, zero latency, and zero dependencies beyond a browser. This makes it a useful demonstration of signal processing fundamentals and the principle that engineering constraints can drive architectural creativity.

## Engineering Logic

### 1. NLP → DSP Tokenizer

Input text is lowercased and split on non-word characters. Each token is matched against 15 preset keyword clusters (dark, bright, ocean, space, forest, tension, rain, mystery, epic, warm, cold, dreamy, cartoon, industrial, meditation). Matching uses both exact lookup and prefix matching (partial token bonus of 0.5× score):

```
for token in tokens:
    if token in cluster.keywords:       score += 1.0
    if any kw.startswith(token):        score += 0.5  # partial match

top_preset     = argmax(scores)
second_preset  = argsort(scores)[1]
blend_ratio    = score[1] / (score[0] + score[1])  # capped at 40%
```

The blend ratio drives linear interpolation across all 12 numeric DSP parameters simultaneously. Scale intervals (modal harmony) and moodNote are taken from the dominant preset without interpolation.

### 2. DSP Parameter Space

12 continuous parameters define the complete synthesis state:

| Parameter | Range | Effect |
|---|---|---|
| `rootFreq` | 40–220 Hz | Bass fundamental; all pad tones derived via equal temperament |
| `scale` | 5× semitone intervals | Modal scale selection (Dorian, Phrygian, Pentatonic major/minor, Locrian) |
| `reverbTime` | 1–12 s | Convolution IR decay constant τ |
| `padWarmth` | 0–1 | Pad LP filter cutoff (400–3400 Hz) |
| `modDepth` | 0–1 | LFO-to-shimmer FM modulation depth |
| `textureAmt` | 0–1 | Bandpass noise amplitude |
| `lowCut` | 20–500 Hz | Global HP filter cutoff |
| `highCut` | 2k–20k Hz | Global LP filter cutoff |
| `subFreq` | 20–80 Hz | Sub-bass oscillator frequency |
| `pulseRate` | 0.02–0.3 Hz | Pulse LFO rate |
| `noiseColor` | 200–4k Hz | Noise BPF centre frequency |
| `layerAmps` | 5× 0–0.3 | Per-layer amplitude envelope |

### 3. Web Audio Synthesis Graph

The real-time graph is constructed fresh on each Play from the current parameter state:

```
LFO (sine, 0.05 Hz)
    └── LFO Gain (modDepth × 0.5) ──────────────────────────────────┐
                                                                      ▼
Sub Osc (sine, subFreq) ──→ Sub Gain ──────────────────────────→ Master Gain
Pad Stack (25× osc, ±6¢) → Pad Mix → LP Filter → Pad Gain ───→ Master Gain
Shimmer (sine, root×4) ←── FM mod ──────────────────────────── Master Gain ←┘
Noise (white) → BPF (noiseColor) → Noise Gain ─────────────→ Master Gain
Pulse (triangle, root×1.5, LFO tremolo) → Pulse Gain ──────→ Master Gain
                                                                      │
                                                             HP Filter → LP Filter
                                                                      │
                                          ┌───────────────────────────┤
                                          ▼                           ▼
                                    Dry Send               Convolution Reverb → Reverb Send
                                          │                           │
                                          └────────── AnalyserNode ───┘
                                                           │
                                                     Destination
```

The pad stack runs 5 scale tones × 5 detune offsets (−6, −3, 0, +3, +6 cents) = 25 oscillators through a single shared LP filter. This creates the characteristic lush pad texture through superposition of slightly detuned partials. This is the same technique used in professional synthesizers for "unison" mode.

### 4. Modal Harmony & Scale Theory

Scale intervals determine which harmonics are active in the pad stack. Different emotional qualities map to different modal scales with well-established psychoacoustic associations:

```javascript
// Mood → scale → acoustic character
dark/ominous    → [0, 3, 5, 8, 10]   // Dorian (minor with raised 6th — melancholic but not hopeless)
tense/thriller  → [0, 1, 5, 6, 10]   // Phrygian dominant fragments (half-step tension)
bright/open     → [0, 2, 4, 7, 9]    // Pentatonic major (no dissonant intervals)
mysterious      → [0, 1, 5, 7, 10]   // Locrian fragments (tritone instability)
neutral/default → [0, 2, 5, 7, 10]   // Pentatonic minor

// Equal temperament frequency calculation
freq(root, interval, octave) = root × 2^((octave × 12 + interval) / 12)
```

### 5. Procedural IR Reverb

Rather than loading an impulse response file, the convolution IR is synthesized directly:

```javascript
for (let i = 0; i < irLen; i++)
    d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / irLen, 2);
//            white noise                  exponential decay envelope
```

This single line produces a physically plausible room response: random early reflections with energy that decays quadratically to zero over the specified τ. The 12-second cathedral IR generates in ~5ms and occupies ~2MB RAM. No audio files, no fetching, no latency.

### 6. Offline Rendering & WAV Encoding

Export uses `OfflineAudioContext`: the same audio graph but rendered at maximum CPU speed rather than real-time. A 5-minute stereo file (44.1kHz × 2 channels × 300s = 26.5M samples) renders in approximately 8 seconds on a mid-range CPU.

The rendered `AudioBuffer` is then encoded to WAV via a hand-written encoder, RIFF header construction, 16-bit PCM interleaving of stereo channels, DataView byte-level writes. No external libraries:

```javascript
// RIFF/WAV header (44 bytes)
ws(0, 'RIFF'); v.setUint32(4, 36 + dataSize, true);
ws(8, 'WAVE'); ws(12, 'fmt ');
v.setUint32(16, 16, true);    // PCM format chunk size
v.setUint16(20, 1, true);     // PCM = 1
v.setUint16(22, numCh, true); // stereo = 2
v.setUint32(24, 44100, true); // sample rate
// ... interleave L/R samples as signed 16-bit integers
```

## Preset Library (15 Acoustic Regions)

| Preset | Root | Reverb τ | Scale | Character |
|---|---|---|---|---|
| dark | 55 Hz | 9s | Dorian | heavy, ominous |
| bright | 165 Hz | 4s | Pentatonic major | crystalline, open |
| ocean | 82 Hz | 11s | Pentatonic minor | deep, fluid |
| space | 110 Hz | 12s | Pentatonic minor | vast, cold |
| forest | 130 Hz | 5s | Pentatonic major | organic, textured |
| tension | 73 Hz | 3s | Phrygian fragments | tense, urgent |
| rain | 98 Hz | 6s | Pentatonic minor | grey, textured |
| mystery | 92 Hz | 8s | Locrian fragments | eerie, unresolved |
| epic | 65 Hz | 7s | Pentatonic major | cinematic, powerful |
| warm | 140 Hz | 5s | Pentatonic major | cozy, amber |
| cold | 88 Hz | 10s | Pentatonic minor | icy, distant |
| dreamy | 120 Hz | 9s | Pentatonic major | floating, hazy |
| cartoon | 196 Hz | 2s | Pentatonic major | bright, bouncy |
| industrial | 55 Hz | 4s | Phrygian fragments | harsh, mechanical |
| meditation | 136 Hz | 8s | Pentatonic major | calm, resonant |

## Project Challenges & Evolution

- **Prompt→sound variety:** Initial implementation used nearest-neighbour preset lookup. "Dark rain" and "dark ocean" produced identical output because both mapped to "dark". Solved by implementing continuous blend interpolation: both tokens score independently and the two highest-scoring presets are linearly interpolated by their relative scores. This produces genuinely different parameter vectors for every distinct combination.

- **Convolution reverb without files:** Standard reverb implementations load a recorded impulse response (WAV file, 1–5MB per room). Loading external files in a single-page static app adds latency and hosting complexity. Synthesized the IR procedurally as exponentially decaying white noise, acoustically equivalent to a diffuse reverberant field, and generates in <5ms with no asset fetching.

- **Export quality for long durations:** Naive approaches to 5-minute WAV export caused browser tab freezes because the audio rendering loop blocked the UI thread. `OfflineAudioContext` runs the render asynchronously in the audio thread, returning a Promise. The `await offCtx.startRendering()` pattern keeps the UI responsive throughout the render.

- **WAV interleaving bug:** Early WAV exports had correct left channel audio but right channel contained corrupted data. Root cause: writing samples in L, L, L..., R, R, R... order (planar) rather than L, R, L, R... (interleaved). Fixed by iterating over samples first, then channels in the inner loop.

- **Streamlit iframe audio context restriction:** Browsers block `AudioContext` creation inside cross-origin iframes without explicit user gesture on the parent page. The `st.components.v1.html()` Streamlit embedding creates an iframe; Play button clicks inside it are treated as user gestures by Chrome but not Firefox. Documented as a known limitation; resolved by noting that the standalone `index.html` works universally.

## Tech Stack

- **Audio synthesis:** Web Audio API (`AudioContext`, `OfflineAudioContext`, `BiquadFilterNode`, `ConvolverNode`, `OscillatorNode`, `AnalyserNode`)
- **NLP mapping:** Rule-based keyword scoring (vanilla JavaScript, zero dependencies)
- **Visualisation:** Canvas 2D API — frequency spectrum (FFT 512pt) + time-domain waveform overlay
- **Deployment:** Streamlit, Hugging Face Spaces
- **Export:** Hand-written 16-bit PCM WAV encoder (RIFF format, DataView)

## 📁 Project Structure

- `index.html` — Complete single-file application (HTML + CSS + JavaScript). Open directly in any browser — no server needed.
- `app.py` — Streamlit wrapper for Hugging Face Spaces deployment. Embeds `index.html` via `st.components.v1.html()`.
- `requirements.txt` — Single dependency: `streamlit>=1.28.0`
- `README.md` — This file

> **Note:** No model weights, no audio files, no external assets. The entire application is self-contained in `index.html`. I have also used AI to add comments in the index file for further understanding and changes. 

## Running Locally

```bash
# Clone
git clone https://github.com/mfh-001/Aether-Synth
cd Aether-Synth

# Option 1: Open directly — no server needed
open index.html          # macOS
start index.html         # Windows
xdg-open index.html      # Linux

# Option 2: Run via Streamlit (identical to HuggingFace Spaces)
pip install streamlit
streamlit run app.py
```

---

## ⚠️ Disclaimer

This repository serves as a showcase of my technical growth and learning journey. The contents are intended strictly for educational and research purposes. All outputs should be treated as conceptual references rather than production-ready solutions.
