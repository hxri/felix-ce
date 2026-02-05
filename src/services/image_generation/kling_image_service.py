from src.clients.fal_client import FalClient
from src.schemas.generation import ImageGenerationRequest
from pathlib import Path
from datetime import datetime
import time
import json
from loguru import logger

from src.utils.file_utils import download_file
from src.utils.image_encoding import local_image_to_data_uri


class KlingImageService:
    """Image generation/editing using FAL's Kling Image/o3 model."""

    MODEL_NAME = "fal-ai/kling-image/o3/image-to-image"

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

        # Resolve reference images
        image_urls = self._resolve_refs(req.reference_images or [])

        arguments = {
            "prompt": req.prompt,
            "image_urls": image_urls,
            "resolution": "1K",  # Kling uses 1K, 2K, 4K
            "aspect_ratio": "auto",
            "result_type": "single",
            "num_images": 1,
            "output_format": "png",
        }

        logger.info(f"[KlingImageService] Calling {self.MODEL_NAME}")
        logger.info(f"  Prompt: {req.prompt[:80]}...")
        logger.info(f"  Images: {len(image_urls)}")

        try:
            result = self.client.subscribe(
                model=self.MODEL_NAME,
                arguments=arguments
            )
        except Exception as e:
            logger.error(f"[KlingImageService] API call failed: {e}")
            raise

        latency = time.time() - start_time

        # -----------------------
        # Save images locally
        # -----------------------
        saved_files = []
        today = datetime.now().strftime("%Y_%m_%d")
        ts = int(time.time())

        base_dir = Path(f"outputs/images/{today}/kling_image")
        base_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"[KlingImageService] Response type: {type(result)}")
        logger.debug(f"[KlingImageService] Response keys: {result.keys() if isinstance(result, dict) else 'N/A'}")

        # Kling returns result["images"][0]["url"] (array)
        images = result.get("images", [])
        if images:
            for idx, img in enumerate(images):
                url = img.get("url") if isinstance(img, dict) else img
                if url:
                    save_path = base_dir / f"img_{ts}_{idx}.png"
                    logger.info(f"[KlingImageService] Downloading image to {save_path}...")
                    try:
                        download_file(url, save_path)
                        saved_files.append(str(save_path))
                    except Exception as e:
                        logger.error(f"[KlingImageService] Download failed: {e}")
                        raise
        else:
            logger.error(f"[KlingImageService] No images in response. Full response: {result}")

        if not saved_files:
            logger.error(f"[KlingImageService] No images were saved")

        # -----------------------
        # Save metadata JSON
        # -----------------------
        metadata = {
            "prompt": req.prompt,
            "model": self.MODEL_NAME,
            "latency_sec": latency,
            "timestamp": datetime.utcnow().isoformat(),
            "reference_images": req.reference_images,
            "raw_response": result,
        }

        meta_path = base_dir / f"meta_{ts}.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        logger.info(f"[KlingImageService] Saved metadata to {meta_path}")

        return {
            "raw": result,
            "local_files": saved_files,
            "metadata_file": str(meta_path),
            "latency_sec": latency,
        }