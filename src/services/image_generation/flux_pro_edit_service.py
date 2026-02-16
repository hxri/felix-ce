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

        # On Vercel, we can't write to disk - just use FAL CDN URLs
        saved_files = []
        
        # Extract FAL image URL from response
        image_url = None
        if result.get("image", {}).get("url"):
            image_url = result["image"]["url"]
            print(f"[FluxProEditService] Got FAL image URL: {image_url}")
        
        if image_url:
            saved_files = [image_url]  # Use FAL URL as the "file"

        return {
            "raw_response": result,
            "local_files": saved_files,
            "metadata_file": None,
            "latency_sec": latency,
        }
