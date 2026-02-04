from src.clients.fal_client import FalClient
from src.schemas.generation import VideoGenerationRequest
from pathlib import Path
from datetime import datetime
import time
import json

from src.utils.file_utils import download_file
from src.utils.image_encoding import local_image_to_data_uri


class LtxVideoService:
    """Video generation using FAL's LTX video model."""

    MODEL_NAME = "fal-ai/ltx-2/image-to-video/fast"

    def __init__(self):
        self.client = FalClient()

    def _resolve_ref(self, ref: str) -> str:
        """Convert local path to data URI if needed."""
        if ref.startswith("http://") or ref.startswith("https://") or ref.startswith("data:"):
            return ref
        else:
            return local_image_to_data_uri(ref)

    def generate_video(self, req: VideoGenerationRequest) -> dict:
        start_time = time.time()

        # Resolve reference image
        image_url = self._resolve_ref(req.reference_image)

        arguments = {
            "prompt": req.prompt,
            "image_url": image_url,
            "duration": req.duration_sec,
            "aspect_ratio": "9:16",
            "num_videos": req.num_videos,
        }

        print(f"[LtxService] Calling {self.MODEL_NAME} with prompt: {req.prompt[:60]}...")
        result = self.client.subscribe(
            model=self.MODEL_NAME,
            arguments=arguments
        )

        latency = time.time() - start_time

        # -----------------------
        # Save videos locally
        # -----------------------
        saved_files = []
        today = datetime.now().strftime("%Y_%m_%d")
        ts = int(time.time())

        base_dir = Path(f"outputs/videos/{today}/ltx")
        base_dir.mkdir(parents=True, exist_ok=True)

        # FAL ltx returns result["video"]["url"]
        video_obj = result.get("video")
        if video_obj:
            url = video_obj.get("url")
            if not url:
                raise ValueError("No URL in video response")
            save_path = base_dir / f"video_{ts}.mp4"
            print(f"[LtxService] Downloading video to {save_path}...")
            download_file(url, save_path)
            saved_files.append(str(save_path))
        else:
            raise ValueError(f"No video in response. Keys: {result.keys()}")

        # -----------------------
        # Save metadata JSON
        # -----------------------
        metadata = {
            "prompt": req.prompt,
            "model": self.MODEL_NAME,
            "duration_sec": req.duration_sec,
            "reference_image": req.reference_image,
            "latency_sec": latency,
            "timestamp": datetime.utcnow().isoformat(),
            "raw_response": result,
        }

        meta_path = base_dir / f"meta_{ts}.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        return {
            "raw": result,
            "local_files": saved_files,
            "metadata_file": str(meta_path),
            "latency_sec": latency,
        }