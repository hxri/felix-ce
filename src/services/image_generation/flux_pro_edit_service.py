from src.clients.fal_client import FalClient
from src.schemas.generation import ImageGenerationRequest
from pathlib import Path
from datetime import datetime
import time
import json

from src.utils.file_utils import download_file
from src.utils.image_encoding import local_image_to_data_uri


class FluxProEditService:
    """Image generation/editing using FAL's Flux-2-Pro/Edit model."""

    MODEL_NAME = "fal-ai/flux-2-pro/edit"
    _IMAGE_SIZE_VALUES = {
        "square_hd",
        "square",
        "portrait_4_3",
        "portrait_16_9",
        "landscape_4_3",
        "landscape_16_9",
        "auto",
    }

    def __init__(self):
        self.client = FalClient()

    def _resolve_refs(self, refs):
        """Convert local paths to data URIs if needed."""
        resolved = []
        for r in refs:
            if r.startswith("http://") or r.startswith("https://") or r.startswith("data:"):
                resolved.append(r)
            else:
                resolved.append(local_image_to_data_uri(r))
        return resolved

    def _map_image_size(self, req: ImageGenerationRequest) -> str:
        """Map aspect ratio / resolution to Flux image_size enum."""
        # Prefer explicit aspect_ratio if provided
        ratio_str = (req.aspect_ratio or "").strip()
        if ratio_str and ":" in ratio_str:
            try:
                w_str, h_str = ratio_str.split(":")
                w = float(w_str)
                h = float(h_str)
                if w > 0 and h > 0:
                    return self._ratio_to_size(w, h)
            except Exception:
                pass

        # Fall back to resolution if available
        res = (req.resolution or "").lower()
        if "x" in res:
            try:
                w_str, h_str = res.split("x")
                w = float(w_str)
                h = float(h_str)
                if w > 0 and h > 0:
                    return self._ratio_to_size(w, h)
            except Exception:
                pass

        return "auto"

    def _ratio_to_size(self, w: float, h: float) -> str:
        if abs(w - h) / max(w, h) < 0.05:
            return "square_hd"
        if w > h:
            ratio = w / h
            if abs(ratio - (16 / 9)) < 0.15:
                return "landscape_16_9"
            if abs(ratio - (4 / 3)) < 0.15:
                return "landscape_4_3"
        else:
            ratio = h / w
            if abs(ratio - (16 / 9)) < 0.15:
                return "portrait_16_9"
            if abs(ratio - (4 / 3)) < 0.15:
                return "portrait_4_3"
        return "auto"

    def generate_image(self, req: ImageGenerationRequest, no_download: bool = False):
        start_time = time.time()

        # Resolve reference images
        image_urls = self._resolve_refs(req.reference_images or [])

        arguments = {
            "prompt": req.prompt,
            "image_urls": image_urls,
            "image_size": self._map_image_size(req),
            "safety_tolerance": "2",
            "enable_safety_checker": False,
            "output_format": "png",
        }

        print(f"[FluxProEditService] Calling {self.MODEL_NAME}")
        print(f"  Prompt: {req.prompt[:80]}...")
        print(f"  Images: {len(image_urls)}")

        result = self.client.subscribe(
            model=self.MODEL_NAME,
            arguments=arguments
        )

        latency = time.time() - start_time

        # -----------------------
        # Save images locally (optional)
        # -----------------------
        saved_files = []
        
        if not no_download:
            today = datetime.now().strftime("%Y_%m_%d")
            ts = int(time.time())

            base_dir = Path(f"outputs/images/{today}/flux_pro_edit")
            base_dir.mkdir(parents=True, exist_ok=True)

            # Flux returns result["image"]["url"]
            image_obj = result.get("image")
            if image_obj:
                url = image_obj.get("url")
                if url:
                    save_path = base_dir / f"img_{ts}.png"
                    print(f"[FluxProEditService] Downloading image to {save_path}...")
                    download_file(url, save_path)
                    saved_files.append(str(save_path))
            else:
                # Fallback: check for images array
                for idx, img in enumerate(result.get("images", [])):
                    url = img.get("url")
                    if not url:
                        continue
                    save_path = base_dir / f"img_{ts}_{idx}.png"
                    download_file(url, save_path)
                    saved_files.append(str(save_path))

        # -----------------------
        # Save metadata JSON
        # -----------------------
        metadata = {
            "prompt": req.prompt,
            "model": self.MODEL_NAME,
            "resolution": req.resolution,
            "latency_sec": latency,
            "timestamp": datetime.utcnow().isoformat(),
            "reference_images": req.reference_images,
            "raw_response": result,
        }

        meta_path = None
        if not no_download:
            today = datetime.now().strftime("%Y_%m_%d")
            ts = int(time.time())
            base_dir = Path(f"outputs/images/{today}/flux_pro_edit")
            meta_path = base_dir / f"meta_{ts}.json"
            with open(meta_path, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

        return {
            "raw_response": result,
            "local_files": saved_files,
            "metadata_file": str(meta_path) if meta_path else None,
            "latency_sec": latency,
        }
