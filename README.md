# AUVISEGTRA 🎬

A production-grade system for audio-visual character tracking, re-identification, and trailer intelligence.

## 🚀 Features

### 1. Character Tracking System
- **Scene-Level Segmentation**: Uses `PySceneDetect` to divide video into coherent scenes.
- **Multimodal Re-Identification**: Fuses face similarity (Visual ReID) and speaker similarity (Audio Diarization) to match characters across scenes.
- **Dynamic Weighting**: Adjust $\alpha$ (Visual) and $\beta$ (Audio) weights in real-time via the UI.
- **Interactive Dashboard**: Visualizes character presence via heatmaps, timelines, and breakdown tables.

### 2. Trailer Intelligence System
- **YouTube Integration**: Download any trailer directly via URL using `yt-dlp`.
- **Multimodal Genre Prediction**: Fuses visual intensity and audio energy with LLM transcript analysis.
- **Storyline Prediction**: Uses Groq (Llama 3) to infer narrative arcs and predict storyline progression.
- **Multilingual Support**: Supports multiple output languages for generated reports.

## 🛠️ Installation

```bash
# 1. Clone or download the repository
# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Set up your Groq API Key
export GROQ_API_KEY="your_key_here"

# 4. Run the application
streamlit run app.py
```

## 🏗️ Architecture

```text
/project
  /app.py              # Main Entry Point
  /tabs/               # UI Components for Tracking & Trailer
  /pipeline/           # Core Logic (Video, Tracking, ReID, Audio, Fusion)
    /video.py          # Scene & Frame processing
    /tracking.py       # YOLOv8 & ByteTrack
    /reid.py           # Person Re-Identification
    /audio.py          # Speaker Diarization & MFCC
    /fusion.py         # Multi-modal Fusion Engine
    /trailer.py        # Trailer Intelligence Logic
  /config/             # Parameter Management
  /requirements.txt    # Dependency List
```

## ⚖️ Multimodal Fusion Formula

The system uses the following score-level fusion strategy:

$$FinalScore(i,j) = \alpha \times VisualSim(i,j) + \beta \times AudioSim(i,j)$$

Where:
- $VisualSim$: Cosine similarity of face/person embeddings.
- $AudioSim$: Cosine similarity of speaker embeddings.
- $\alpha, \beta$: User-defined importance weights.

## ⚠️ Requirements
- Python 3.10+
- FFmpeg (for audio extraction)
- (Optional) GPU for faster inference with YOLO and ReID models.
