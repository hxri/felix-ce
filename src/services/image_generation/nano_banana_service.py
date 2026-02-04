from src.clients.fal_client import FalClient
from src.schemas.generation import ImageGenerationRequest
from pathlib import Path
from datetime import datetime
import time
import json

from src.utils.file_utils import download_file
from src.utils.image_encoding import local_image_to_data_uri


class NanoBananaService:

    MODEL_NAME = "fal-ai/nano-banana"

    def __init__(self):
        self.client = FalClient()

    def generate_image(self, req: ImageGenerationRequest):

        start_time = time.time()

        arguments = {
            "prompt": req.prompt,
            "resolution": req.resolution,
            "aspect_ratio": req.aspect_ratio,
            "num_images": req.num_images,
        }

        # Prefer explicit data URI -> singular path -> first of reference_images list
        # Use the plural "image_urls" (list) to match the edit stage / API expectations
        if req.reference_image_data_uri:
            arguments["image_urls"] = [req.reference_image_data_uri]

        elif req.reference_image_path:
            arguments["image_urls"] = [local_image_to_data_uri(req.reference_image_path)]

        elif req.reference_images and len(req.reference_images) > 0:
            first_ref = req.reference_images[0]
            if first_ref.startswith("http") or first_ref.startswith("data:"):
                arguments["image_urls"] = [first_ref]
            else:
                arguments["image_urls"] = [local_image_to_data_uri(first_ref)]

        result = self.client.subscribe(
            model=self.MODEL_NAME,
            arguments=arguments,
        )

        latency = time.time() - start_time

        saved_files = []

        today = datetime.now().strftime("%Y_%m_%d")
        ts = int(time.time())

        base_dir = Path(f"outputs/images/{today}/nano_banana")
        base_dir.mkdir(parents=True, exist_ok=True)

        for idx, img in enumerate(result["images"]):

            url = img["url"]

            save_path = base_dir / f"img_{ts}_{idx}.png"

            download_file(url, save_path)

            saved_files.append(str(save_path))

        # Save metadata JSON
        metadata = {
            "prompt": req.prompt,
            "model": self.MODEL_NAME,
            "seed": result.get("seed"),
            "latency_sec": latency,
            "timestamp": datetime.utcnow().isoformat(),
            "reference_images": req.reference_images or ([req.reference_image_path] if req.reference_image_path else None),
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
