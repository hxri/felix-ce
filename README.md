# 📽️ Apparel to Video Generation Pipeline

A modular, extensible Python pipeline for generating realistic full-body videos of people wearing specified apparel in various settings. Integrates with multiple AI video generation models via FAL.ai.

**Key Feature:** Single-command model swapping to compare latency, quality, and performance across 8+ video generation models.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Supported Models](#supported-models)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Components](#components)
- [Configuration](#configuration)
- [Dashboard](#dashboard)
- [API Reference](#api-reference)
- [Development](#development)

---

## 🎯 Overview

This project automates the creation of high-quality product/fashion videos by:

1. **Image Generation**: Uses nano-banana/edit to generate a realistic full-body person image based on reference photos and outfit descriptions
2. **Video Generation**: Converts the generated image into a 4-8 second video using multiple AI video models
3. **Model Comparison**: Logs latency and metadata for each model, enabling performance benchmarking
4. **Interactive Dashboard**: Streamlit-based dashboard to visualize and compare model performance

### Use Cases

- E-commerce product demos (clothing, accessories)
- Fashion lookbooks and styling guides
- Virtual try-on experiences
- AI model benchmarking and evaluation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│         Person + Environment Attributes             │
│        (PersonAttributes, EnvironmentAttributes)    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   Image Pipeline       │
        │  (ImagePipeline)       │
        │  ─────────────────     │
        │ • Prompt building      │
        │ • nano-banana/edit     │
        │ • Face preservation    │
        └────────────┬───────────┘
                     │
        ┌────────────▼─────────────┐
        │  Generated Person Image  │
        │  (outputs/images/...)    │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Video Pipeline        │
        │ (VideoPipeline)        │
        │ ─────────────────────  │
        │ • Model factory        │
        │ • Video service calls  │
        │ • Metadata logging     │
        └────────────┬───────────┘
                     │
        ┌────────────▼──────────────────────────┐
        │  Video Generation (8 Models)          │
        │  ────────────────────────────────     │
        │  • veo3    • ltx      • kling         │
        │  • grok    • luma     • pika          │
        │  • seedance • hunyuan                 │
        └────────────┬──────────────────────────┘
                     │
        ┌────────────▼──────────────────┐
        │   Output Videos + Metadata    │
        │ (outputs/videos/YYYY_MM_DD/)  │
        └────────────┬──────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Dashboard (Streamlit) │
        │  ─────────────────────│
        │ • Latency comparison   │
        │ • Model benchmarking   │
        │ • Video preview        │
        │ • Export reports       │
        └────────────────────────┘
```

---

## 🎬 Supported Models

| Model | Endpoint | Duration | Status |
|-------|----------|----------|--------|
| **Veo3** | `fal-ai/veo3/image-to-video` | 4, 6, 8s | ✅ Active |
| **LTX** | `fal-ai/ltx-2/image-to-video/fast` | Any (s) | ✅ Active |
| **Kling** | `fal-ai/kling-video/v2.6/pro/image-to-video` | Variable | ✅ Active |
| **Grok** | `xai/grok-imagine-video/image-to-video` | Variable | ✅ Active |
| **Luma Ray-2** | `fal-ai/luma-dream-machine/ray-2/image-to-video` | 5s | ✅ Active |
| **Pika** | `fal-ai/pika/v2.2/image-to-video` | Variable | ✅ Active |
| **Seedance** | `fal-ai/bytedance/seedance/v1.5/pro/image-to-video` | Variable | ✅ Active |
| **Hunyuan** | `fal-ai/hunyuan-video-v1.5/image-to-video` | Variable | ✅ Active |

**Add new models**: Create a new service file (e.g., `src/services/video_generation/new_model_service.py`) and register it in `VideoPipeline._init_video_service()`.

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- FAL.ai API key (sign up at [fal.ai](https://fal.ai))
- Linux/macOS (or WSL on Windows)

### Setup

1. **Clone and navigate:**
   ```bash
   cd /home/hxri/Documents/conscious/felix
   ```

2. **Create virtual environment (optional):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set FAL API key:**
   ```bash
   export FAL_API_KEY="your_fal_api_key_here"
   ```

   Or create `.env` file:
   ```
   FAL_API_KEY=your_fal_api_key_here
   ```

---

## 📖 Quick Start

### Generate a Video (Full Pipeline)

```bash
export FAL_API_KEY="your_key"
python3 -m scripts.run_full_pipeline
```

**Output:**
- Generated image: `outputs/images/YYYY_MM_DD/nano_banana_edit/img_<ts>.png`
- Generated video: `outputs/videos/YYYY_MM_DD/<model>/video_<ts>.mp4`
- Metadata: `outputs/videos/YYYY_MM_DD/<model>/meta_<ts>.json`

### Swap Video Model

Edit `scripts/run_full_pipeline.py`:

```python
# Line ~50
video_pipeline = VideoPipeline(video_model="luma")  # Change: veo3, ltx, kling, grok, luma, pika, seedance, hunyuan
```

Then re-run the pipeline.

### Launch Dashboard

```bash
streamlit run scripts/dashboard.py
```

Opens at `http://localhost:8501`

### Test Single Model

```bash
python3 -m scripts.test_nanobanana \
  --ref assets/pranay.png \
  --prompt "Portrait of a man smiling" \
  --num 1
```

---

## 📦 Components

### 1. **Schemas** (`src/schemas/`)

Define request/response models using Pydantic.

- **`person.py`**: Person attributes (height, weight, gender, age)
- **`environment.py`**: Environment attributes (setting, visual cues, apparel type)
- **`generation.py`**: Image/video generation requests
- **`artifacts.py`**: Metadata and generation info

### 2. **Services** (`src/services/`)

#### Image Generation (`image_generation/`)

- **`nano_banana_service.py`**: Basic nano-banana image generation
- **`nano_banana_edit_service.py`**: nano-banana/edit for image-to-image with references

#### Video Generation (`video_generation/`)

Eight service classes, one per model:

- **`veo3_service.py`**: FAL Veo3 integration
- **`ltx_service.py`**: FAL LTX integration
- **`kling_service.py`**: Kling video integration
- **`grok_service.py`**: Grok Imagine integration
- **`luma_service.py`**: Luma Ray-2 integration
- **`pika_service.py`**: Pika v2.2 integration
- **`seedance_service.py`**: Seedance integration
- **`hunyuan_service.py`**: Hunyuan integration

Each implements:
- `_resolve_ref()`: Convert local paths to data URIs
- `generate_video()`: Call FAL model, download video, save metadata

#### Prompt Building (`prompt_builder/`)

- **`image_prompt_service.py`**: Constructs identity and outfit prompts

### 3. **Pipelines** (`services/pipelines/`)

Orchestrate multi-stage workflows.

- **`image_pipeline.py`**: 
  - Takes person attributes + references
  - Calls nano-banana/edit
  - Returns generated person image
  - **Features**: Face preservation, outfit reference support, combined prompt generation

- **`video_pipeline.py`**: 
  - Factory pattern for model selection
  - Calls appropriate video service
  - Returns video file + metadata
  - **Features**: Easy model swapping, latency tracking, JSON metadata logging

### 4. **Utilities** (`src/utils/`)

- **`file_utils.py`**: Download files with timeout handling
- **`image_encoding.py`**: Convert local images to data URIs (base64)
- **`json_utils.py`**: JSON save/load helpers

### 5. **Clients** (`src/clients/`)

- **`fal_client.py`**: FAL API wrapper with retry logic and logging

---

## ⚙️ Configuration

### Environment Variables

```bash
export FAL_API_KEY="your_fal_api_key"
```

### Model Costs (`configs/model_costs.py`)

Track pricing per model (optional):

```python
MODEL_COSTS = {
    "fal-ai/nano-banana": 0.01,
    "fal-ai/veo3/image-to-video": 0.05,
    # ... add per-model costs
}
```

### Duration Validation (`src/schemas/generation.py`)

Edit `VideoGenerationRequest.validate_duration()` to support new durations:

```python
supported = [4, 5, 6, 8, 9]  # Adjust per model requirements
```

---

## 📊 Dashboard

**Script:** `scripts/dashboard.py`

**Features:**

1. **Metrics**
   - Total videos generated
   - Average latency per model
   - Number of models tested

2. **Charts**
   - Bar chart: Average latency by model
   - Box plot: Latency distribution
   - Scatter plot: Timeline (generation time vs latency)

3. **Tables**
   - Detailed statistics (min/avg/max latency, count)
   - All generated videos with timestamps

4. **Inspector**
   - View full raw metadata JSON for any video
   - Inspect API response details

5. **Export**
   - Download as CSV (latency comparison)
   - Download as JSON (full summary)

**Run:**
```bash
streamlit run scripts/dashboard.py
```

---

## 🔌 API Reference

### ImagePipeline

```python
from src.services.pipelines.image_pipeline import ImagePipeline
from src.schemas.person import PersonAttributes
from src.schemas.environment import EnvironmentAttributes

pipeline = ImagePipeline()

result = pipeline.run(
    person=PersonAttributes(height_cm=175, weight_kg=70, gender="male", age=28),
    env=EnvironmentAttributes(
        apparel_type="Street wear",
        inferred_setting="Urban cafe outdoor",
        visual_cues="Natural lighting"
    ),
    description="Full frontal view of athletic male",
    person_reference_image="assets/person.png",
    face_reference_image="assets/face_crop.png",  # Optional
    outfit_reference_images=["assets/top.png", "assets/bottom.png"]  # Optional
)

# result = {
#     "stage": "combined",
#     "raw": {...},  # Raw API response
#     "local_files": ["outputs/images/2026_02_04/nano_banana_edit/img_1770197158_0.png"],
#     "metadata_file": "outputs/images/2026_02_04/nano_banana_edit/meta_1770197158.json",
#     "latency_sec": 29.57
# }
```

### VideoPipeline

```python
from src.services.pipelines.video_pipeline import VideoPipeline

# Swap models: veo3, ltx, kling, grok, luma, pika, seedance, hunyuan
video_pipeline = VideoPipeline(video_model="veo3")

result = video_pipeline.run(
    reference_image="outputs/images/2026_02_04/nano_banana_edit/img_1770197158_0.png",
    apparel_description="blue t-shirt and khaki shorts",
    duration_sec=4
)

# result = {
#     "stage": "video",
#     "video_model": "veo3",
#     "raw": {...},
#     "local_files": ["outputs/videos/2026_02_04/veo3/video_1770197200.mp4"],
#     "metadata_file": "outputs/videos/2026_02_04/veo3/meta_1770197200.json",
#     "latency_sec": 28.5
# }
```

### FalClient

```python
from src.clients.fal_client import FalClient

client = FalClient()

result = client.subscribe(
    model="fal-ai/nano-banana/edit",
    arguments={
        "prompt": "A person wearing blue shirt",
        "image_urls": ["data:image/png;base64,...", "..."],
        "resolution": "1024x1024",
        "num_images": 1
    }
)
```

---

## 🔧 Development

### Adding a New Video Model

1. **Create service:**
   ```python
   # filepath: src/services/video_generation/newmodel_service.py
   from src.clients.fal_client import FalClient
   from src.schemas.generation import VideoGenerationRequest
   
   class NewmodelVideoService:
       MODEL_NAME = "vendor/newmodel/image-to-video"
       
       def __init__(self):
           self.client = FalClient()
       
       def generate_video(self, req: VideoGenerationRequest) -> dict:
           # 1. Resolve reference image
           # 2. Build arguments dict
           # 3. Call FAL model
           # 4. Download video
           # 5. Save metadata
           # 6. Return dict with local_files, metadata_file, latency_sec
           pass
   ```

2. **Register in pipeline:**
   ```python
   # src/services/pipelines/video_pipeline.py
   def _init_video_service(self, model_name: str):
       if model_name == "newmodel":
           return NewmodelVideoService()
       # ...
   ```

3. **Use in script:**
   ```python
   video_pipeline = VideoPipeline(video_model="newmodel")
   ```

### File Structure

```
felix/
├── src/
│   ├── clients/
│   │   └── fal_client.py
│   ├── services/
│   │   ├── image_generation/
│   │   │   ├── nano_banana_service.py
│   │   │   └── nano_banana_edit_service.py
│   │   ├── video_generation/
│   │   │   ├── veo3_service.py
│   │   │   ├── ltx_service.py
│   │   │   ├── kling_service.py
│   │   │   ├── grok_service.py
│   │   │   ├── luma_service.py
│   │   │   ├── pika_service.py
│   │   │   ├── seedance_service.py
│   │   │   └── hunyuan_service.py
│   │   ├── pipelines/
│   │   │   ├── image_pipeline.py
│   │   │   └── video_pipeline.py
│   │   └── prompt_builder/
│   │       └── image_prompt_service.py
│   ├── schemas/
│   │   ├── person.py
│   │   ├── environment.py
│   │   ├── generation.py
│   │   └── artifacts.py
│   ├── utils/
│   │   ├── file_utils.py
│   │   ├── image_encoding.py
│   │   └── json_utils.py
│   └── core/
│       └── config.py
├── scripts/
│   ├── run_full_pipeline.py
│   ├── run_image_generation.py
│   ├── test_nanobanana.py
│   ├── test_fal_connection.py
│   └── dashboard.py
├── configs/
│   └── model_costs.py
├── assets/
│   ├── pranay.png
│   ├── top.png
│   ├── bottom.png
│   └── shoes.png
├── outputs/
│   ├── images/
│   │   └── YYYY_MM_DD/
│   │       └── nano_banana_edit/
│   │           ├── img_<ts>.png
│   │           └── meta_<ts>.json
│   └── videos/
│       └── YYYY_MM_DD/
│           ├── veo3/
│           ├── ltx/
│           ├── kling/
│           ├── grok/
│           ├── luma/
│           ├── pika/
│           ├── seedance/
│           └── hunyuan/
├── requirements.txt
├── pyproject.toml
├── .env
└── README.md
```

---

## 📝 Metadata JSON Structure

**Image metadata** (`outputs/images/2026_02_04/nano_banana_edit/meta_*.json`):

```json
{
  "prompt": "Full frontal view...",
  "model": "fal-ai/nano-banana/edit",
  "seed": null,
  "latency_sec": 29.57,
  "timestamp": "2026-02-04T10:38:11.831988",
  "reference_images": ["assets/pranay.png", "assets/top.png", "assets/bottom.png"],
  "raw_response": { "images": [...] }
}
```

**Video metadata** (`outputs/videos/2026_02_04/veo3/meta_*.json`):

```json
{
  "prompt": "A guy standing in a proper lighting...",
  "model": "fal-ai/veo3/image-to-video",
  "duration_sec": 4,
  "reference_image": "outputs/images/2026_02_04/nano_banana_edit/img_1770197158_0.png",
  "latency_sec": 28.5,
  "timestamp": "2026-02-04T10:39:00.000000",
  "raw_response": {
    "video": {
      "url": "https://...",
      "content_type": "video/mp4",
      "width": 720,
      "height": 720,
      "fps": 24.0,
      "duration": 4.5
    }
  }
}
```

---

## 🤝 Contributing

### Bug Reports & Feature Requests

File issues with:
- Error logs
- Steps to reproduce
- Expected vs. actual behavior

### Extending the Pipeline

See [Development](#development) section for adding new models.

---

## 📄 License

Proprietary. All rights reserved.

---

## 🆘 Support

- **FAL.ai Docs**: https://docs.fal.ai
- **API Status**: https://status.fal.ai
- **Issues**: Check logs in `outputs/` metadata JSONs

---

## 🎯 Roadmap

- [ ] Support for streaming/real-time video generation
- [ ] Batch processing (multiple people/outfits)
- [ ] Cost analysis dashboard
- [ ] Quality metrics (SSIM, LPIPS, etc.)
- [ ] Multi-camera angle generation
- [ ] Voice/audio sync support
- [ ] Web UI (FastAPI + React)

---

**Version:** 0.1.0  
**Last Updated:** 2026-02-04  
**Author:** Felix Team