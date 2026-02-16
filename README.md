# 📽️ Apparel-to-Video Generation Pipeline

A modular, extensible AI pipeline for generating realistic full-body videos of people wearing specific apparel in various settings. Integrates with multiple SOTA video generation models via FAL.ai and provides both a Python SDK/CLI and a full-stack web application.

**Key Features:**
- **Identity Preservation:** Generates consistent full-body images from face references.
- **Apparel Transfer:** seamless integration of reference garments (tops, bottoms).
- **Multi-Model Support:** Single-command model swapping across 8+ video engines (Veo3, Kling, Luma, Grok, etc.).
- **Web Interface:** Next.js frontend + Flask backend for interactive generation.
- **Benchmarking:** Automated tools to compare latency, quality, and failure rates.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Supported Models](#supported-models)
- [Installation](#installation)
- [Web Application](#web-application)
- [CLI & Scripts](#cli--scripts)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Dashboard](#dashboard)
- [Development](#development)

---

## 🎯 Overview

This project automates the creation of high-quality product/fashion videos by:

1.  **Image Generation**: Uses specialized edit models (e.g., `nano-banana/edit`, `qwen-edit`) to create a realistic full-body person image based on reference photos and outfit descriptions.
2.  **Video Generation**: Converts the generated image into a 4-8 second video using multiple AI video models.
3.  **Interactive Web App**: A user-friendly wizard for capturing photos, selecting outfits, and generating results.
4.  **Model Comparison**: Logs latency and metadata for every generation to track performance and cost.

---

## 🏗️ Architecture

```mermaid
graph TD
    User[User / Web App] --> API[Flask API (backend)]
    API --> ImagePipe[ImagePipeline]
    API --> VideoPipe[VideoPipeline]

    subgraph "Image Generation"
        ImagePipe -->|Reference + Prompt| FalImage[FAL.ai: nano-banana/edit]
        FalImage -->|Generated Image| LocalImg[outputs/images/...]
    end

    subgraph "Video Generation (Factory)"
        VideoPipe -->|Adapter Selection| Adapter{Model Adapter}
        Adapter -->|Veo3| M1[Veo3 Service]
        Adapter -->|Kling| M2[Kling Service]
        Adapter -->|Luma| M3[Luma Service]
        Adapter -->|Grok| M4[Grok Service]
        Adapter -->|...| M5[Other Services]
    end

    M1 & M2 & M3 & M4 -->|Video URL| Output[outputs/videos/...]
    Output --> Dashboard[Streamlit Dashboard]
```

---

## 🎬 Supported Models

| Model | Endpoint | Duration | Status |
| :--- | :--- | :--- | :--- |
| **Veo3** | `fal-ai/veo3/image-to-video` | 4, 8s | ✅ Active |
| **Kling** | `fal-ai/kling-video/v2.6/pro/image-to-video` | 5s | ✅ Active |
| **Luma Ray-2** | `fal-ai/luma-dream-machine/ray-2/image-to-video` | 5s | ✅ Active |
| **Grok** | `xai/grok-imagine-video/image-to-video` | 5s | ✅ Active |
| **LTX** | `fal-ai/ltx-2/image-to-video/fast` | 5s | ✅ Active |
| **Pika** | `fal-ai/pika/v2.2/image-to-video` | 3s | ✅ Active |
| **Seedance** | `fal-ai/bytedance/seedance/v1.5/pro/image-to-video` | Variable | ✅ Active |
| **Hunyuan** | `fal-ai/hunyuan-video-v1.5/image-to-video` | Variable | ✅ Active |

---

## 🚀 Installation

### Prerequisites

-   Python 3.10+
-   Node.js 18+ (for frontend)
-   FAL.ai API key

### One-Time Setup

1.  **Clone the repository:**
    ```bash
    git clone <repo-url>
    cd felix
    ```

2.  **Backend Setup (Python):**
    ```bash
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Install Python dependencies
    pip install -r requirements.txt
    pip install -e .
    ```

3.  **Frontend Setup (Node.js):**
    ```bash
    cd app/frontend
    npm install
    # or
    yarn install
    cd ../..
    ```

4.  **Environment Variables:**
    Create a `.env` file in the root directory:
    ```ini
    FAL_KEY="your_fal_api_key_here"
    ```

---

## 🌐 Web Application

The project includes a full-stack demo application.

### 1. Start the Backend
Runs the Flask API on port 5000.
```bash
python app/backend/wsgi.py
```

### 2. Start the Frontend
Runs the Next.js app on port 3000.
```bash
cd app/frontend
npm run dev
```

**Use the App:** Open [http://localhost:3000](http://localhost:3000)
-   **Capture:** Take a photo using your webcam.
-   **Select:** Choose gender, top, bottom, and background.
-   **Generate:** Watch the AI create your digital avatar and video in real-time.

---

## 💻 CLI & Scripts

You can also run pipelines directly from the terminal for testing or batch processing.

### Run Full Pipeline (Image + Video)
Generates an image from assets and then animates it.
```bash
python -m scripts.run_full_pipeline
```

### Quick Benchmark
Runs a fast comparison across selected models defined in the script.
```bash
python -m scripts.quick_benchmark
```

### Test Single Model connection
Simple connectivity check to FAL.ai.
```bash
python -m scripts.test_fal_connection
```

---

## 📂 Project Structure

```text
felix/
├── app/                        # Web Application
│   ├── backend/                # Flask API
│   │   ├── api/                # Route definitions (generate.py, video.py)
│   │   └── wsgi.py             # Entry point
│   └── frontend/               # Next.js Frontend
│       ├── app/                # Pages and layouts
│       └── components/         # React components
├── assets/                     # Static assets (clothing images, references)
├── configs/                    # Configuration files
├── outputs/                    # Generated content (git-ignored)
│   ├── images/
│   └── videos/                 # Contains video files and .json metadata
├── scripts/                    # Utility and benchmark scripts
│   ├── dashboard.py            # Streamlit analytics
│   └── ...
├── src/                        # Core Python Package
│   ├── clients/                # FAL API wrapper
│   ├── services/
│   │   ├── image_generation/   # Image model adapters
│   │   ├── video_generation/   # Video model adapters (8+ models)
│   │   ├── pipelines/          # Orchestration logic (ImagePipeline, VideoPipeline)
│   │   └── prompt_builder/     # Prompt engineering logic
│   ├── schemas/                # Pydantic data models
│   └── utils/                  # Helpers (file I/O, base64)
├── .env                        # Environment secrets
├── pyproject.toml              # Python project config
└── README.md
```

---

## 📊 Dashboard

Analyze generation performance, latency, and costs using the built-in dashboard.

**Run:**
```bash
streamlit run scripts/dashboard.py
```
**Features:**
-   Visual comparison (Bar charts, Box plots) of model latency.
-   Failure rate tracking.
-   JSON inspector for raw API responses.
-   CSV export of benchmark results.

---

## 🔧 Development

### Adding a New Video Model
To add a new model (e.g., "NewModel"):

1.  **Create Service:** Add `src/services/video_generation/new_model_service.py`.
2.  **Implement Class:** Inherit structure from existing services (see `src/services/video_generation/luma_service.py`).
3.  **Register:** Update `src/services/pipelines/video_pipeline.py` to include the new model key in `_init_video_service`.

### Modifying Prompts
Edit `src/services/prompt_builder/image_prompt_service.py` to adjust how prompt strings are constructed from attributes.

---

