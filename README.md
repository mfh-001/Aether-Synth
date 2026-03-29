---
title: Aether Synth
emoji: 🎛
colorFrom: purple
colorTo: green
sdk: streamlit
sdk_version: "1.28.0"
app_file: app.py
pinned: false
license: mit
python_version: "3.11"
---

# 🎛 Aether — Procedural Ambient Synthesizer

**NLP → DSP parameter mapping · Web Audio API · Real-time synthesis · WAV export**

> Open-source ambient music synthesizer. Describe a mood in natural language — the system maps it to DSP synthesis parameters and generates a unique soundscape entirely in the browser.

**[Live Demo](https://huggingface.co/spaces/MFH-001/Aether-Synth)** · **[GitHub](https://github.com/mfh-001/Aether-Synth)**

---

## What this demonstrates

This project was built as a showcase of applied signal processing and NLP-to-parameter mapping — areas directly relevant to audio ML, generative systems, and real-time inference pipelines.

| Concept | Implementation |
|---|---|
| **NLP tokenization** | Keyword lexicon with ~80 acoustic tokens, weighted scoring across 12 dimensions |
| **DSP parameter space** | 12 continuous parameters: root freq, modal scale, reverb τ, filter Fc, LFO depth/rate, noise color, layer amplitudes |
| **Additive synthesis** | 5-layer graph: sub (sine), pad (25 oscillators, ±6 cent detune), shimmer (FM), texture (bandpass noise), pulse (LFO tremolo) |
| **Convolution reverb** | Procedurally synthesized IR (exponential white noise decay, 1–12s) — no audio files needed |
| **Modal harmony** | Mood-dependent scale selection (Dorian, Phrygian dominant, pentatonic major/minor, Locrian fragments) |
| **Preset blending** | Linear interpolation across DSP parameter space for multi-token inputs ("dark ocean" blends two presets) |
| **Offline rendering** | `OfflineAudioContext` renders 5-minute stereo WAV in ~8s; hand-written 16-bit PCM encoder |
| **Zero backend** | 100% client-side — no server, no API calls, no auth |

---

## Signal Chain

```
Text Input
    │
    ▼
Token Scoring (keyword lexicon × 80 clusters)
    │
    ▼
DSP Parameter Interpolation (12 continuous params)
    │
    ▼
Web Audio Graph Construction
    ├── Sub Oscillator (sine, subFreq Hz)
    ├── Pad Stack (25× sawtooth/triangle, ±6¢ detune → LP filter)
    ├── Shimmer (sine, FM-modulated by LFO)
    ├── Texture (white noise → bandpass, noiseColor Hz)
    └── Pulse (triangle, LFO tremolo, pulseRate Hz)
            │
            ▼
    Master Gain → HP Filter → LP Filter → Convolution IR Reverb
            │
            ▼
    AnalyserNode (FFT 512pt) → Speakers / OfflineContext
            │
            ▼
    16-bit PCM WAV Export (44.1kHz stereo)
```

---

## DSP Parameters

| Parameter | Range | Description |
|---|---|---|
| `rootFreq` | 40–220 Hz | Bass fundamental; all scale tones derived from this |
| `scale` | 5× semitone intervals | Modal scale (0=root, 12=octave) |
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

---

## Preset Library (15 acoustic regions)

| Preset | Root | Reverb | Scale | Character |
|---|---|---|---|---|
| dark | 55 Hz | 9s | Dorian | heavy, ominous |
| bright | 165 Hz | 4s | Pentatonic major | crystalline, open |
| ocean | 82 Hz | 11s | Pentatonic minor | deep, fluid |
| space | 110 Hz | 12s | Pentatonic minor | vast, cold |
| forest | 130 Hz | 5s | Pentatonic major | organic, textured |
| tension | 73 Hz | 3s | Phrygian frags | tense, urgent |
| rain | 98 Hz | 6s | Pentatonic minor | grey, textured |
| mystery | 92 Hz | 8s | Locrian frags | eerie, unresolved |
| epic | 65 Hz | 7s | Pentatonic major | cinematic, powerful |
| warm | 140 Hz | 5s | Pentatonic major | cozy, amber |
| cold | 88 Hz | 10s | Pentatonic minor | icy, distant |
| dreamy | 120 Hz | 9s | Pentatonic major | floating, hazy |
| cartoon | 196 Hz | 2s | Pentatonic major | bright, bouncy |
| industrial | 55 Hz | 4s | Phrygian frags | harsh, mechanical |
| meditation | 136 Hz | 8s | Pentatonic major | calm, resonant |

Blended moods (e.g. "dark ocean") linearly interpolate parameter vectors between the two highest-scoring presets.

---

## Project Structure

```
Aether-Synth/
├── index.html          # Complete single-file app (HTML + CSS + JS)
├── app.py              # Gradio wrapper for HuggingFace Spaces
├── requirements.txt    # gradio only
└── README.md           # This file
```

---

## Running Locally

```bash
# Clone
git clone https://github.com/mfh-001/Aether-Synth.git
cd Aether-Synth

# Option 1: Just open the HTML (no server needed)
open index.html

# Option 2: Run via Gradio (same as HuggingFace Spaces)
pip install gradio
python app.py
```

---