from src.clients.fal_client import FalClient
from src.schemas.generation import ImageGenerationRequest
from pathlib import Path
from datetime import datetime
import time
import json

from src.utils.file_utils import download_file
from src.utils.image_encoding import local_image_to_data_uri


class NanoBananaEditService:

    MODEL_NAME = "fal-ai/nano-banana/edit"

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

    def generate_image(self, req: ImageGenerationRequest):
        start_time = time.time()

        # Use the list-style field for edits
        image_urls = self._resolve_refs(req.reference_images or [])

        arguments = {
            "prompt": req.prompt,
            "image_urls": image_urls,
            "resolution": req.resolution,
            "aspect_ratio": req.aspect_ratio,
            "num_images": req.num_images,
        }

        result = self.client.subscribe(
            model=self.MODEL_NAME,
            arguments=arguments
        )

        latency = time.time() - start_time

        # -----------------------
        # Save images locally
        # -----------------------
        saved_files = []
        today = datetime.now().strftime("%Y_%m_%d")
        ts = int(time.time())

        base_dir = Path(f"outputs/images/{today}/nano_banana_edit")
        base_dir.mkdir(parents=True, exist_ok=True)

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
            "seed": result.get("seed"),
            "latency_sec": latency,
            "timestamp": datetime.utcnow().isoformat(),
            "reference_images": req.reference_images,
            "raw_response": result,
        }

        meta_path = base_dir / f"meta_{ts}.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return {
            "raw": result,
            "local_files": saved_files,
            "metadata_file": str(meta_path),
            "latency_sec": latency,
        }
